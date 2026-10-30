"""EXP-0044: compare each logged run's reads with the registered predictions.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0044/compare.py RUNS OUT_JSON

RUNS holds `run_mame.py` outputs named ``s<slot>_<partner>_<lang>``. In each
``reads.txt`` (``frame pc offset``):

- the ending begins at the first read by the ending selector (PC
  ``0x04F53C``);
- from there, every read by PC ``0x04F612`` is a page record, in order;
- a selector read in the same frame as a page record, or one frame before
  it, marks that page as a table re-read.

Each run is compared with ``predictions.json`` for its slot and language:
the table address, the record addresses in order, and the re-read pages.
The two partner runs of a slot and language must also read the same
records. Outputs: OUT_JSON (per run: match flags, and what was read where it
differs) and a printed summary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PREDICTIONS = Path("research/experiments/EXP-0044/predictions.json")
TABLE_PC, RECORD_PC = "04f53c", "04f612"


def ending(path: Path) -> dict[str, object]:
    rows = [line.split() for line in path.read_text().splitlines() if line.strip()]
    start = next((i for i, r in enumerate(rows) if r[1] == TABLE_PC), None)
    if start is None:
        return {"reached": False}
    tables = [(int(r[0]), r[2]) for r in rows[start:] if r[1] == TABLE_PC]
    records = [(int(r[0]), r[2]) for r in rows[start:] if r[1] == RECORD_PC]
    rereads = [
        page
        for page, (frame, _) in enumerate(records, start=1)
        if any(frame - 1 <= t <= frame for t, _ in tables)
    ]
    return {
        "reached": True,
        "table": f"{int(tables[0][1], 16):#x}",
        "tables_seen": sorted({f"{int(a, 16):#x}" for _, a in tables}),
        "records": [f"{int(a, 16):#x}" for _, a in records],
        "frames": [f for f, _ in records],
        "rereads": rereads,
    }


def main(runs: Path, out: Path) -> int:
    predictions = {
        (p["slot"], p["language"]): p
        for p in json.loads(PREDICTIONS.read_text())["predictions"]
    }
    results = {}
    for run in sorted(runs.iterdir()):
        slot_text, partner, lang = run.name[1:].split("_")
        slot = int(slot_text)
        got = ending(run / "reads.txt")
        want = predictions[(slot, lang)]
        entry: dict[str, object] = {"slot": slot, "partner": partner, "language": lang}
        if not got["reached"]:
            entry.update({"reached": False, "match": False})
        else:
            entry.update(
                {
                    "reached": True,
                    "table_ok": got["table"] == want["table_read"],
                    "records_ok": got["records"] == want["records"],
                    "rereads_ok": got["rereads"] == want["table_reread_on_pages"],
                    "read": got,
                }
            )
            entry["match"] = all(
                entry[k] for k in ("table_ok", "records_ok", "rereads_ok")
            )
        results[run.name] = entry
    for slot in (0, 11):
        for lang in ("en", "jp"):
            a = results.get(f"s{slot}_default_{lang}", {}).get("read")
            b = results.get(f"s{slot}_right_{lang}", {}).get("read")
            same = (
                isinstance(a, dict)
                and isinstance(b, dict)
                and a["records"] == b["records"]
                and a["rereads"] == b["rereads"]
            )
            results[f"partners_s{slot}_{lang}"] = {"same_reads": same}
    out.write_text(json.dumps(results, indent=1) + "\n")
    bad = [
        k
        for k, v in results.items()
        if v.get("match") is False or v.get("same_reads") is False
    ]
    print(json.dumps({"runs": len(results), "not_as_predicted": bad}))
    for k in bad:
        v = results[k]
        r = v.get("read")
        if isinstance(r, dict):
            print(
                k,
                v.get("table_ok"),
                v.get("records_ok"),
                v.get("rereads_ok"),
                r["table"],
                len(r["records"]),
                r["rereads"],
            )
        else:
            print(k, v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

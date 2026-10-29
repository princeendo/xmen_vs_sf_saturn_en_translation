"""EXP-0030: write each roster character's pairing table from the MAME runs.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0030/make_pairing.py \\
        RUNS OUT_DIR [--check]

Generalized from `research/experiments/EXP-0026/make_pairing.py` (this
repository, commit ``890875d``) to the whole M5 roster
(`data/text/m5_roster.json`). Two changes:

- The Saturn side is given as the MC file and the decompressed offset of its
  table (`data/text/slot_census.json`, `EXP-0029`). A RAM address was known
  only for Ryu and Ken.
- The English record count comes from the census. The next slot's pointer
  gives a wrong count for slot 17, because slot 18 aliases slot 11.

RUNS holds one ``s<slot>/summary.json`` per slot from
`research/experiments/EXP-0022/run_pair.py`. The rule under test
(`EXP-0022`): draw ``r = rand() & 0x0F``; Japanese record ``r``; English
record ``r mod 8``. An entry is CONFIRMED when the forced English run with the
slot forced read exactly the predicted English address. Every forced
Japanese run must also read its predicted address.

For each roster slot without a pairing file yet, the script writes
``OUT_DIR/<name>_pairing.json``, where name is the name-list name in lower
case with ``-`` as ``_``. No file is written for a slot with a failed run.
With ``--check``, it writes nothing and compares the
runs for slots that already have a file (Ryu, Ken). It prints one line per
slot. No game text is written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m5_roster.json")
JP_TABLE, EN_TABLE = 0x17E19C, 0x17E1E8
JP_SIZE, EN_SIZE, RECORDS = 76, 100, 16


def file_name(name: str) -> str:
    return name.lower().replace("-", "_") + "_pairing.json"


def pairs(
    program: bytes, slot: int, mc_file: str, offset: int, runs: list[dict[str, object]]
) -> tuple[list[dict[str, object]], list[str]]:
    def pointer(table: int) -> int:
        return int.from_bytes(program[table + 4 * slot : table + 4 * slot + 4], "big")

    jp_base, en_base = pointer(JP_TABLE), pointer(EN_TABLE)
    failures = []
    entries = []
    for k in range(RECORDS):
        english = k % 8
        tested = []
        for entry in runs:
            lang, run_slot, draw = str(entry["run"]).split(":")
            if run_slot != str(slot) or draw == "-" or int(draw) != k:
                continue
            expected = (
                jp_base + JP_SIZE * k if lang == "jp" else en_base + EN_SIZE * english
            )
            read = entry["first_text_read"]
            match = read == f"{expected:#x}"
            if not match:
                failures.append(f"{lang} draw {k}: read {read}, expected {expected:#x}")
            tested.append(
                {
                    "language": lang,
                    "read": read,
                    "expected": f"{expected:#x}",
                    "match": match,
                }
            )
        en_ok = any(t["match"] and t["language"] == "en" for t in tested)
        entries.append(
            {
                "saturn_record": k,
                "saturn_file": mc_file,
                "saturn_file_offset": f"{offset + JP_SIZE * k:#x}",
                "arcade_draw": k,
                "arcade_jp_record": k,
                "arcade_jp_address": f"{jp_base + JP_SIZE * k:#x}",
                "arcade_en_record": english,
                "arcade_en_address": f"{en_base + EN_SIZE * english:#x}",
                "runs": tested,
                "confidence": "CONFIRMED" if en_ok else "SUPPORTED (rule only)",
            }
        )
    return entries, failures


def main(runs_dir: Path, out_dir: Path, check: bool) -> int:
    program = PROGRAM.read_bytes()
    roster = json.loads(ROSTER.read_text())["roster"]
    status = 0
    for member in roster:
        slot = int(member["slot"])
        name = str(member["name_list"])
        runs = json.loads((runs_dir / f"s{slot}" / "summary.json").read_text())
        offset = int(str(member["table_offset"]), 16)
        entries, failures = pairs(program, slot, member["mc_file"], offset, runs)
        confirmed = sum(e["confidence"] == "CONFIRMED" for e in entries)
        jp_runs = sum(str(r["run"]).startswith(f"jp:{slot}:") for r in runs)
        target = out_dir / file_name(name)
        line = f"slot {slot:2} {name:11} en {confirmed}/16 jp_runs {jp_runs}"
        if failures:
            status = 1
            line += " FAIL " + "; ".join(failures)
        if target.exists():
            # Ryu and Ken: compare the English addresses with the committed file
            old = json.loads(target.read_text())["pairs"]
            same = [p["arcade_en_address"] for p in old] == [
                e["arcade_en_address"] for e in entries
            ]
            line += f" | existing file, English addresses agree: {same}"
            status |= not same
        elif not check and not failures:
            document = {
                "description": (
                    f"{name} (arcade slot {slot}) win quotes: Saturn record k "
                    "pairs with the arcade English record shown for the same "
                    "random draw (EXP-0030)."
                ),
                "rule": (
                    "draw r = rand() & 0x0F; Japanese record r; English record r mod 8"
                ),
                "saturn_table": {
                    "file": member["mc_file"],
                    "offset": member["table_offset"],
                },
                "english_records": member["english_records"],
                "unreachable_english_records": list(
                    range(8, int(member["english_records"]))
                ),
                "pairs": entries,
            }
            target.write_text(json.dumps(document, indent=1) + "\n")
            line += f" -> {target}"
        print(line)
    return status


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), "--check" in sys.argv[3:])
    )

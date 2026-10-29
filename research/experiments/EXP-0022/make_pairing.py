"""EXP-0022: build Ryu's Saturn-to-arcade-English pairing table from the runs.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0022/make_pairing.py OUT_JSON SUMMARY...

Each SUMMARY is a ``summary.json`` from ``run_pair.py``. The rule, read from
the arcade selector at ``0x04F396`` and the Saturn port at ``0x0606665C``, is:

* draw ``r = rand() & 0x0F``;
* Japanese record ``r``;
* English record ``remap[r] = r mod 8`` (table ``0x04F41A``).

Saturn record ``k`` is the arcade Japanese slot 9 record ``k`` (`EXP-0015`), so
it pairs with English slot 9 record ``k mod 8``. The script records, for each
``k``, the arcade addresses and every run that tested that draw with Ryu's slot
forced. An entry is CONFIRMED when a run read exactly the predicted address.
No game text is written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

JP_SLOT9, EN_SLOT9 = 0x180EBC, 0x188DE2  # arcade slot 9 record 0 (EXP-0008)
JP_SIZE, EN_SIZE = 76, 100
SATURN_TABLE = 0x0024F5D8  # WRAM-L, MC09.SHP offset 0x25D8 (EXP-0017)


def main(out: Path, summaries: list[Path]) -> int:
    runs: list[dict[str, object]] = []
    for path in summaries:
        runs += json.loads(path.read_text())
    entries = []
    for k in range(16):
        english = k % 8
        tested = []
        for entry in runs:
            lang, slot, draw = str(entry["run"]).split(":")
            if slot != "9" or draw == "-" or int(draw) != k:
                continue
            expected = (
                JP_SLOT9 + JP_SIZE * k if lang == "jp" else EN_SLOT9 + EN_SIZE * english
            )
            read = entry["first_text_read"]
            tested.append(
                {
                    "language": lang,
                    "read": read,
                    "expected": f"{expected:#x}",
                    "match": read == f"{expected:#x}",
                }
            )
        en_ok = any(t["match"] and t["language"] == "en" for t in tested)
        entries.append(
            {
                "saturn_record": k,
                "saturn_address": f"{SATURN_TABLE + 76 * k:#010x}",
                "arcade_draw": k,
                "arcade_jp_record": k,
                "arcade_jp_address": f"{JP_SLOT9 + JP_SIZE * k:#x}",
                "arcade_en_record": english,
                "arcade_en_address": f"{EN_SLOT9 + EN_SIZE * english:#x}",
                "runs": tested,
                "confidence": "CONFIRMED" if en_ok else "SUPPORTED (rule only)",
            }
        )
    document = {
        "description": (
            "Ryu (arcade slot 9) win quotes: Saturn record k pairs with the arcade "
            "English record shown for the same random draw (EXP-0022)."
        ),
        "rule": "draw r = rand() & 0x0F; Japanese record r; English record r mod 8",
        "unreachable_english_records": [8],
        "fixed_index_mode": (
            "when the byte at A5-0x2F7D (arcade 0xFF5083) is set, Ryu's index is "
            "fixed at 1 in both languages (table 0x04F3E2), with no remap"
        ),
        "pairs": entries,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=1) + "\n")
    print(
        json.dumps(
            [
                (e["saturn_record"], e["arcade_en_record"], e["confidence"])
                for e in entries
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]))

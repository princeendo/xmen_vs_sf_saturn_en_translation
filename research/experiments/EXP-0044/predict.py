"""EXP-0044: write the registered predictions for every M8 roster ending.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0044/predict.py OUT_JSON

For each slot in `data/text/m8_ending_roster.json` and each language, the
prediction is:

- **Table:** the ending selector (PC ``0x04F53C``) reads the slot's entry in
  the English table ``0x17E318`` or the Japanese table ``0x17E2CC``.
- **Records:** page k (PC ``0x04F612``) reads the slot's pointer + size x
  k, for k = 0 to n - 1. The size is 100 bytes in English and 76 in
  Japanese. n is the arcade English count, or the Saturn Japanese count
  (`data/text/ending_census.json`).
- **Scenes:** the table is re-read on exactly the pages where the slot's
  ``MCED`` script of that language starts a scene
  (`data/text/ending_script_census.json`). This held for Nash (D-032,
  D-033).
- **Partners:** the partner changes none of this (checked for slots 0 and
  11 with a second partner).

Written and committed before any read-logged `EXP-0044` run. Only
addresses, counts and page numbers are written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m8_ending_roster.json")
CENSUS = Path("data/text/ending_census.json")
SCRIPTS = Path("data/text/ending_script_census.json")
TABLES = {"en": (0x17E318, 100), "jp": (0x17E2CC, 76)}
PARTNER_CHECKS = (0, 11)


def long(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    roster = json.loads(ROSTER.read_text())["members"]
    census = {r["slot"]: r for r in json.loads(CENSUS.read_text())["slots"]}
    scripts = {r["slot"]: r for r in json.loads(SCRIPTS.read_text())["slots"]}
    predictions = []
    for member in roster:
        slot = member["slot"]
        for lang, (table, size) in TABLES.items():
            pointer = long(program, table + 4 * slot)
            count = (
                census[slot]["arcade_english_records"]
                if lang == "en"
                else census[slot]["saturn_records"]
            )
            script = scripts[slot]["english" if lang == "en" else "japanese"]
            starts, page = [], 1
            for scene in script["records_per_scene"]:
                starts.append(page)
                page += len(scene)
            predictions.append(
                {
                    "slot": slot,
                    "name": member["name"],
                    "language": lang,
                    "table_read": f"{table + 4 * slot:#x}",
                    "records": [f"{pointer + size * k:#x}" for k in range(count)],
                    "table_reread_on_pages": starts,
                    "partner_checked": slot in PARTNER_CHECKS,
                }
            )
    out.write_text(
        json.dumps(
            {"source": "EXP-0044 predict.py", "predictions": predictions}, indent=1
        )
        + "\n"
    )
    print(len(predictions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

"""EXP-0026: build a character's Saturn-to-arcade-English pairing table from MAME runs.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0026/make_pairing.py \\
        OUT_JSON NAME SLOT SATURN_TABLE SUMMARY...

Generalized from `research/experiments/EXP-0022/make_pairing.py` (this
repository, commit ``e54de8c``), which hard-coded Ryu's slot 9. Here SLOT is
the arcade slot and SATURN_TABLE the WRAM-L address of the character's quote
table when it is the first team member (Ken: ``0x0024FA4C``, `EXP-0025`). The
arcade record bases are read from the program's pointer tables (Japanese
``0x17E19C``, English ``0x17E1E8``; `EXP-0008`) in the ignored
``local/ref003/xmvsfu-68k.bin``. Each SUMMARY is a ``summary.json`` from
`research/experiments/EXP-0022/run_pair.py`.

The rule under test (`EXP-0022`): draw ``r = rand() & 0x0F``; Japanese record
``r``; English record ``r mod 8``. Saturn record ``k`` is the arcade Japanese
record ``k`` for the slot (`EXP-0025`), so it pairs with English record
``k mod 8``. An entry is CONFIRMED when a forced English run with the slot
forced read exactly the predicted address. No game text is written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
JP_TABLE, EN_TABLE = 0x17E19C, 0x17E1E8
JP_SIZE, EN_SIZE = 76, 100


def main(
    out: Path, name: str, slot: int, saturn_table: int, summaries: list[Path]
) -> int:
    program = PROGRAM.read_bytes()

    def pointer(table: int, index: int) -> int:
        return int.from_bytes(program[table + 4 * index : table + 4 * index + 4], "big")

    jp_base, en_base = pointer(JP_TABLE, slot), pointer(EN_TABLE, slot)
    en_count = (pointer(EN_TABLE, slot + 1) - en_base) // EN_SIZE
    runs: list[dict[str, object]] = []
    for path in summaries:
        runs += json.loads(path.read_text())
    entries = []
    for k in range(16):
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
                "saturn_address": f"{saturn_table + 76 * k:#010x}",
                "arcade_draw": k,
                "arcade_jp_record": k,
                "arcade_jp_address": f"{jp_base + JP_SIZE * k:#x}",
                "arcade_en_record": english,
                "arcade_en_address": f"{en_base + EN_SIZE * english:#x}",
                "runs": tested,
                "confidence": "CONFIRMED" if en_ok else "SUPPORTED (rule only)",
            }
        )
    document = {
        "description": (
            f"{name} (arcade slot {slot}) win quotes: Saturn record k pairs with the "
            "arcade English record shown for the same random draw (EXP-0026)."
        ),
        "rule": "draw r = rand() & 0x0F; Japanese record r; English record r mod 8",
        "english_records": en_count,
        "unreachable_english_records": list(range(8, en_count)),
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
    raise SystemExit(
        main(
            Path(sys.argv[1]),
            sys.argv[2],
            int(sys.argv[3], 0),
            int(sys.argv[4], 0),
            [Path(p) for p in sys.argv[5:]],
        )
    )

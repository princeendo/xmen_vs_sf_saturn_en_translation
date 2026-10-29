"""EXP-0024: write Ryu's translation record from the arcade program and the pairing.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0024/make_spec.py OUT_JSON

Reads the ignored ``xmvsfu`` program image (`EXP-0008`) and
`data/translations/ryu_pairing.json` (`EXP-0022`). It writes the record that
`tools.disc.build_english` consumes. For each of Ryu's English records 0-7,
the record holds its source address, its SHA-256, its line lengths, and the
Saturn records that show it (``k`` and ``k + 8``, the user's
`GATE-TRANSLATION` pairing). English record 8 is listed as unused. No game
text is written (AGENTS.md rule 21).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.xvsf_text import long
from tools.text.caption import decode_record

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
PAIRING = Path("data/translations/ryu_pairing.json")
EN_TABLE, SLOT = 0x17E1E8, 9


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    pairs = json.loads(PAIRING.read_text())["pairs"]
    base = long(program, EN_TABLE + 4 * SLOT)
    records = []
    for english in range(8):
        address = base + 100 * english
        data = program[address : address + 100]
        lines = decode_record(data)
        saturn = [p["saturn_record"] for p in pairs if p["arcade_en_record"] == english]
        records.append(
            {
                "english_record": english,
                "saturn_records": saturn,
                "source_address": f"{address:#x}",
                "sha256": hashlib.sha256(data).hexdigest(),
                "line_lengths": [len(line) for line in lines],
                "grammar_fix": None,
            }
        )
    unused_address = base + 100 * 8
    spec = {
        "description": (
            "Ryu's win quotes in English (RE-003): the official arcade English, "
            "paired by GATE-TRANSLATION (Saturn record k shows English record "
            "k mod 8), drawn in the game's own English mode (LAYOUT-001)."
        ),
        "character": "Ryu",
        "arcade_slot": SLOT,
        "mc_file": "MC09.SHP;1",
        "table_offset": "0x25d8",
        "source": {
            "set": "xmvsfu (MAME 0.289, references/arcade/)",
            "program_order": "68000 (EXP-0008)",
            "english_table": f"{EN_TABLE:#x}",
            "slot_base": f"{base:#x}",
        },
        "pairing": str(PAIRING),
        "records": records,
        "unused_english_records": [
            {
                "english_record": 8,
                "source_address": f"{unused_address:#x}",
                "sha256": hashlib.sha256(
                    program[unused_address : unused_address + 100]
                ).hexdigest(),
                "reason": "never chosen by the win-quote selector (EXP-0022)",
            }
        ],
    }
    out.write_text(json.dumps(spec, indent=1) + "\n")
    print(
        json.dumps(
            [
                (r["english_record"], r["saturn_records"], r["line_lengths"])
                for r in records
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

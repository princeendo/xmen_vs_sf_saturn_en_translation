"""EXP-0032: write a character's translation record from the arcade program and pairing.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0032/make_spec.py \\
        OUT_JSON NAME SLOT MC_FILE TABLE_OFFSET PAIRING GATE

Copied from `research/experiments/EXP-0028/make_spec.py` (this repository,
commit ``1a6d268``). The one change: the English record count is the distance
to the next higher distinct pointer, bounded by the block's end, as in
`EXP-0029`'s census. The old count used slot + 1's pointer, which is wrong for
slot 17, since slot 18 aliases slot 11. That script was in turn generalized
from `research/experiments/EXP-0024/make_spec.py`, which hard-coded Ryu.

NAME is the character and SLOT the arcade slot. MC_FILE and TABLE_OFFSET are
the Saturn quote file and its decompressed table offset (`EXP-0029`). PAIRING
is the pairing table (`EXP-0022`, `EXP-0026`, `EXP-0030`), and GATE the task
or session that passed `GATE-TRANSLATION` for this character.

The script reads the ignored ``xmvsfu`` program image (`EXP-0008`). For each
English record 0-7 it writes the source address, the SHA-256, the line lengths
and the Saturn records that show it (``k`` and ``k + 8``). Records 8 and up
are listed as unused. No game text is written (AGENTS.md rule 21). Run with
Ryu's arguments, it reproduces `data/translations/ryu_win_quotes.json` except
for the description.
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
EN_TABLE = 0x17E1E8
EN_END = 0x18AD86  # end of the English win-quote block (EXP-0008)
SLOTS = 19
RECORD = 100


def main(
    out: Path,
    name: str,
    slot: int,
    mc_file: str,
    table_offset: int,
    pairing: Path,
    gate: str,
) -> int:
    program = PROGRAM.read_bytes()
    pairs = json.loads(pairing.read_text())["pairs"]
    base = long(program, EN_TABLE + 4 * slot)
    pointers = {long(program, EN_TABLE + 4 * s) for s in range(SLOTS)} | {EN_END}
    count = (min(p for p in pointers if p > base) - base) // RECORD
    records = []
    for english in range(8):
        address = base + RECORD * english
        data = program[address : address + RECORD]
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
    unused = []
    for english in range(8, count):
        address = base + RECORD * english
        unused.append(
            {
                "english_record": english,
                "source_address": f"{address:#x}",
                "sha256": hashlib.sha256(
                    program[address : address + RECORD]
                ).hexdigest(),
                "reason": "never chosen by the win-quote selector (EXP-0022)",
            }
        )
    spec = {
        "description": (
            f"{name}'s win quotes in English: the official arcade English, paired "
            f"by GATE-TRANSLATION ({gate}; Saturn record k shows English record "
            "k mod 8), drawn in the game's own English mode (LAYOUT-001)."
        ),
        "character": name,
        "arcade_slot": slot,
        "mc_file": mc_file,
        "table_offset": f"{table_offset:#x}",
        "source": {
            "set": "xmvsfu (MAME 0.289, references/arcade/)",
            "program_order": "68000 (EXP-0008)",
            "english_table": f"{EN_TABLE:#x}",
            "slot_base": f"{base:#x}",
        },
        "pairing": str(pairing),
        "records": records,
        "unused_english_records": unused,
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
    out, name, slot, mc_file, offset, pairing, gate = sys.argv[1:8]
    raise SystemExit(
        main(
            Path(out), name, int(slot, 0), mc_file, int(offset, 0), Path(pairing), gate
        )
    )

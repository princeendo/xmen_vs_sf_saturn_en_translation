"""EXP-0041: write the ending spec for Nash from his pairing file.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0041/make_spec.py OUT_JSON

Reads ``data/translations/nash_ending_pairing.json`` (`EXP-0037`) and the US
arcade program image. For each page it records the English record's source
address, SHA-256 and line lengths. The records are stored at quote table +
800 (`tools.disc.english_mode.ENDING_RECORDS`, `EXP-0040`). Only addresses,
hashes and lengths are written (AGENTS.md rule 21). The text is compiled
from the program image at build time.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.english_mode import ENDING_RECORDS
from tools.text.caption import decode_record

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
PAIRING = Path("data/translations/nash_ending_pairing.json")
RECORD = 100


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    pairing = json.loads(PAIRING.read_text())
    records = []
    for pair in pairing["pairs"]:
        if pair["confidence"] != "CONFIRMED":
            raise ValueError(f"page {pair['page']} is not confirmed")
        address = int(pair["arcade_en_address"], 16)
        source = program[address : address + RECORD]
        if hashlib.sha256(source).hexdigest() != pair["arcade_en_sha256"]:
            raise ValueError(f"page {pair['page']}: source hash differs")
        records.append(
            {
                "english_record": pair["arcade_en_record"],
                "page": pair["page"],
                "saturn_record": pair["saturn_record"],
                "source_address": pair["arcade_en_address"],
                "sha256": pair["arcade_en_sha256"],
                "line_lengths": [len(line) for line in decode_record(source)],
                "grammar_fix": None,
            }
        )
    spec = {
        "kind": "ending",
        "description": (
            "Nash's ending in English: the official arcade English, paired by "
            "GATE-TRANSLATION (user decision 2026-10-29, SESSION-0058; page k "
            "shows English record k), shown with the Saturn's own English "
            "ending script (LAYOUT-002) through patch version 4 (END-006)."
        ),
        "character": "Nash",
        "arcade_slot": 16,
        "mc_file": "MC10.SHP;1",
        "table_offset": "0x2a00",
        "records_offset": f"{ENDING_RECORDS:#x}",
        "script": "MCED.SHP;1 (tools.disc.english_mode.mced_english_scripts)",
        "source": {
            "set": "xmvsfu (MAME 0.289, references/arcade/)",
            "program_order": "68000 (EXP-0008)",
            "english_endings_table": "0x17e318",
            "slot_base": pairing["pairs"][0]["arcade_en_address"],
        },
        "pairing": str(PAIRING),
        "records": records,
    }
    out.write_text(json.dumps(spec, indent=1) + "\n")
    print(json.dumps([r["line_lengths"] for r in records]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

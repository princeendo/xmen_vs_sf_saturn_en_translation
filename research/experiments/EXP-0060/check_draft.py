r"""EXP-0060: check the boss-box draft against the source records and the layout.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0060/check_draft.py [DRAFT]

DRAFT (default this folder's ``draft.json``) gives English for each distinct
record of Apocalypse's boxes (decoded ``MC08.SHP`` ``0x1090``, 18 slots x 3
records x 76 bytes, `EXP-0058`). For every slot and record the check confirms
that the draft's ``source_sha256`` prefix matches the record's bytes, and that
every English version compiles to a 2 x 25 record
(`tools.text.caption.compile_record`: length and characters). It prints one
line per slot and record and exits non-zero on any problem.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.disc.prs import decompress_file
from tools.text.caption import CaptionError, compile_record

BOXES, SLOT, RECORD, SLOTS = 0x1090, 0xE4, 76, 18
SHARED = {8: 7}  # slot 8 repeats slot 7's records 0 and 1


def versions(entry: dict[str, list[str]]) -> dict[str, list[str]]:
    if "lines" in entry:
        return {"both": entry["lines"]}
    return {name: entry[name] for name in ("us", "saturn")}


def main(path: Path) -> int:
    draft = json.loads(path.read_text())
    decoded, _ = decompress_file(read_file("MC08.SHP;1"))
    problems = 0
    for slot in range(SLOTS):
        for record in range(3):
            offset = BOXES + slot * SLOT + record * RECORD
            digest = hashlib.sha256(decoded[offset : offset + RECORD]).hexdigest()
            if record == 2:
                entry = next(
                    v for v in draft["record_2"].values() if slot in v["slots"]
                )
            else:
                entry = draft["slots"][str(SHARED.get(slot, slot))][f"record_{record}"]
            notes = []
            if not digest.startswith(entry["source_sha256"]):
                notes.append(f"source {digest[:8]} != {entry['source_sha256']}")
            for name, lines in versions(entry).items():
                try:
                    compile_record(lines)
                except CaptionError as error:
                    notes.append(f"{name}: {error}")
            problems += bool(notes)
            print(slot, record, digest[:8], "ok" if not notes else "; ".join(notes))
    print(f"{problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    default = Path(__file__).with_name("draft.json")
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else default))

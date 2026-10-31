r"""EXP-0059: which English record each route run showed after Apocalypse.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0059/post_boss_pairing.py RUNS

RUNS holds the `EXP-0051` route runs (``s<slot>_a<n>/result.json``, each with
the quote pointer's changes). For each run whose load check passed, the first
non-zero pointer after the last boss-box pointer (WRAM-H ``0x060C2xxx`` or
``0x060C3xxx``, `EXP-0058`) is turned into an English record index from the
slot's quote table (WRAM-L ``0x0024D000`` + the SPEC's ``table_offset``,
100 bytes per record) and compared with the slot's fixed index
(`tools.disc.english_mode.FIXED_LOW`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.english_mode import FIXED_LOW

FILE_BASE, RECORD = 0x0024D000, 100


def main(runs: Path) -> int:
    tables = {}
    for spec in Path("data/translations").glob("*_win_quotes.json"):
        data = json.loads(spec.read_text())
        tables[int(data["arcade_slot"])] = FILE_BASE + int(data["table_offset"], 16)
    matches = 0
    for run in sorted(runs.glob("s*_a*")):
        path = run / "result.json"
        if not path.is_file():
            continue
        result = json.loads(path.read_text())
        if not all(result["load_check"].values()):
            continue
        slot, changes = int(result["first"]), result["pointer_changes"]
        boxes = [f for f, p in changes if p.startswith(("0x060c2", "0x060c3"))]
        if not boxes:
            continue
        after = [(f, int(p, 16)) for f, p in changes if f > max(boxes) and int(p, 16)]
        if not after:
            print(run.name, slot, "no pointer after the boxes")
            continue
        frame, pointer = after[0]
        record = (pointer - tables[slot]) / RECORD
        match = record == FIXED_LOW[slot]
        matches += match
        print(run.name, slot, frame, f"{pointer:#x}", record, FIXED_LOW[slot], match)
    print(f"{matches} runs show the fixed record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

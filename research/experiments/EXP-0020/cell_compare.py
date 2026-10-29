"""EXP-0020: compare every drawn quote cell with its glyph decoded from ``FIX.PRS``.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0020/cell_compare.py RUN FIX_PRS

RUN is the output of ``latin_trial.py``. For each run, the 38 codes at the quote
screen (``record_at_quote``) are matched to the VDP1 sprites drawn at the 2 x 19
cell positions (color word ``0x7020``), and each sprite's 128-byte cell is
compared with `tools.text.font`'s decoding of the code from FIX_PRS. Reports
the sprite count per row, the x positions, and the number of exact cells.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.memory.vdp1_sprites import sprites
from tools.text.font import Font

COLOR_WORD = 0x7020
CELLS = 19


def main(run: Path, fix_prs: Path) -> int:
    font = Font(fix_prs.read_bytes(), 0, 0)
    result = json.loads((run / "result.json").read_text())
    report: dict[str, object] = {}
    ok = True
    for name, entry in result.items():
        if not isinstance(entry, dict):
            continue
        record = bytes.fromhex(entry["record_at_quote"])
        codes = [int.from_bytes(record[i : i + 2], "big") for i in range(0, 76, 2)]
        vram = (run / f"{name}-vdp1.bin").read_bytes()
        text = [s for s in sprites(vram) if s.color_word == COLOR_WORD]
        rows = sorted({s.y for s in text})
        xs = sorted({s.x for s in text})
        source = {(s.x, s.y): s.source for s in text}
        exact = 0
        mismatches = []
        for index, code in enumerate(codes):
            key = (xs[index % CELLS], rows[index // CELLS])
            drawn = vram[source[key] : source[key] + 128]
            if drawn == font.glyph(code)[0]:
                exact += 1
            else:
                mismatches.append(f"{index}:{code:#06x}")
        report[name] = {
            "sprites": len(text),
            "rows": rows,
            "x": [xs[0], xs[-1], len(xs)],
            "distinct_cells": len({s.source for s in text}),
            "exact": exact,
            "mismatches": mismatches,
        }
        ok = ok and exact == len(codes)
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

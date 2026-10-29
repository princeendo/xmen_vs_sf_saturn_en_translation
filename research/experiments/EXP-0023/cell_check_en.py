"""EXP-0023: compare drawn English-mode quote cells with the decoded font.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/cell_check_en.py RUN FIX_PRS

RUN is the output of ``english_trial.py`` (or of any run saving ``<name>-vdp1.bin``
and ``codes_at_quote`` in ``result.json``). For each run, the VDP1 sprites
with a quote color word (``0x7020`` in Japanese mode, ``0x7000`` in English
mode, `EXP-0023`) are grouped into rows. Each sprite's cell is placed at
``(x - x_min) / pitch`` in its row, where pitch is the smallest x step seen.
That cell is compared with ``tools.text.font.glyph(code)`` for the code at
that row and column of the shown record (25 per line in English mode, 19 in
Japanese mode). Reports rows, pitch, sprite count, exact matches and the
codes drawn without a sprite (spaces are expected there).
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.memory.vdp1_sprites import sprites
from tools.text.font import Font

COLOR_WORDS = (0x7020, 0x7000)


def main(run: Path, fix_prs: Path) -> int:
    font = Font(fix_prs.read_bytes(), 0, 0)
    result = json.loads((run / "result.json").read_text())
    report: dict[str, object] = {}
    ok = True
    for name, entry in result.items():
        if not isinstance(entry, dict):
            continue
        vram = (run / f"{name}-vdp1.bin").read_bytes()
        text = [s for s in sprites(vram) if s.color_word in COLOR_WORDS and s.y >= 170]
        rows = sorted({s.y for s in text})
        xs = sorted({s.x for s in text})
        pitch = min(b - a for a, b in itertools.pairwise(xs))
        per_line = 25 if pitch == 12 else 19
        size = 100 if per_line == 25 else 76
        record = bytes.fromhex(entry["codes_at_quote"])[:size]
        codes = [int.from_bytes(record[i : i + 2], "big") for i in range(0, size, 2)]
        exact = 0
        mismatches = []
        drawn = set()
        for s in text:
            row = rows.index(s.y)
            column = (s.x - xs[0]) // pitch
            index = row * per_line + column
            drawn.add(index)
            cell = vram[s.source : s.source + 128]
            if index < len(codes) and cell == font.glyph(codes[index])[0]:
                exact += 1
            else:
                mismatches.append(f"{row}:{column}")
        undrawn = sorted(
            {f"{codes[i]:#06x}" for i in range(len(codes)) if i not in drawn}
        )
        report[name] = {
            "rows": rows,
            "pitch": pitch,
            "x_range": [xs[0], xs[-1]],
            "sprites": len(text),
            "exact": exact,
            "mismatches": mismatches,
            "codes_without_sprite": undrawn,
        }
        ok = ok and not mismatches
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

"""EXP-0019: decode the M1 quote's glyphs and compare them with the drawn cells.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0019/cell_check.py DUMP_DIR

DUMP_DIR holds ``mcs_extract`` regions of the `quote_visible` checkpoint
(`EXP-0014`). For each of the 38 cells of record 10 of the quote table
(WRAM-L ``0x0024F8D0``, `EXP-0015`), the script finds the VDP1 sprite drawn at
that cell's position (two rows of 19 at y = 178 and 194, color word ``0x7020``),
decodes the record's code with `tools.text.font` (font base read from the
pointer at WRAM-H ``0x0602586C``), and compares the 128-byte cells.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.memory.mcs_extract import REGIONS
from tools.memory.vdp1_sprites import sprites
from tools.text.font import Font

RECORD = 0x0024F8D0
POINTER = 0x0602586C
COLOR_WORD = 0x7020


def main(dump: Path) -> int:
    wram_l = (dump / "wram_l.bin").read_bytes()
    wram_h = (dump / "wram_h.bin").read_bytes()
    vram = (dump / "vdp1_vram.bin").read_bytes()
    low, high = REGIONS["wram_l"].base_address, REGIONS["wram_h"].base_address
    base = int.from_bytes(wram_h[POINTER - high : POINTER - high + 4], "big")
    font = Font(wram_l, low, base)
    text = [s for s in sprites(vram) if s.color_word == COLOR_WORD]
    xs = sorted({s.x for s in text})
    ys = sorted({s.y for s in text})
    source = {(s.x, s.y): s.source for s in text}
    record = RECORD - low
    results: dict[str, dict[str, object]] = {}
    for index in range(38):
        code = int.from_bytes(
            wram_l[record + 2 * index : record + 2 * index + 2], "big"
        )
        cell_address = source[(xs[index % 19], ys[index // 19])]
        drawn = vram[cell_address : cell_address + 128]
        decoded, kind = font.glyph(code)
        entry = results.setdefault(
            f"{code:#06x}", {"kind": kind, "cell": f"{cell_address:#x}", "equal": True}
        )
        entry["equal"] = bool(entry["equal"]) and decoded == drawn
    report = {
        "font_base": f"{base:#010x}",
        "distinct_codes": len(results),
        "exact": sum(1 for r in results.values() if r["equal"]),
        "codes": results,
    }
    print(json.dumps(report, indent=1))
    return 0 if report["exact"] == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

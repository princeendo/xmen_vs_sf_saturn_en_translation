"""Draw the approved English into the boot-warning pictures ``ERR1``-``ERR5.BIN``.

Promoted from `research/experiments/EXP-0055/render_samples.py` (`BOOT-003`)
for `BOOT-004`. The layout and style come from ``LAYOUT``
(`data/translations/boot_warnings.json`, approved by the user under
`GATE-TRANSLATION`); only the approved style (the original palette) is drawn.

**The pictures** (`EXP-0054`, D-050): a Windows BMP header and 16-colour
palette (``PIXELS`` bytes), then 352 x 240 pixels at 4 bits, bottom row first,
high nibble first. The game shows picture row y at screen row y + 8, and the
display is 224 lines (screen rows 8-231; Mednafen's screenshots pad 8 black
rows above and below), so picture rows 224-239 are never seen (`EXP-0056`).
It converts each palette channel from its low five bits (``shown``).

**Drawing:** the pixels are cleared; "WARNING" is drawn in yellow, centred, at
picture row ``title_top``; the lines follow from ``top`` (the screen's own
``top`` when it has one) as a left-aligned
block centred on the screen, ``line`` rows apart (an empty line is half that).
The glyphs are the ``FIX.PRS`` quote font's (`tools.text.font`, codes from
`tools.text.caption`), ``pitch`` pixels apart. ``{text}`` is cyan and
``[text]`` red. Pens 2-3 take the colour's bright entry, 4-6 and 8 its dim
entry, and 7, the drop shadow, dark grey (index 1), under any letter pixel.

**Checks** (``check``): each result keeps the original's size and its first
``PIXELS`` bytes (header and palette); no line is wider than the screen less
``MARGIN`` on each side; no text falls below picture row ``LAST_ROW``.

The results are game-derived (the font): keep them under ``local/`` or
``build/`` only (`AGENTS.md` rule 21).
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

from tools.text.caption import ENCODE
from tools.text.font import Font, nibble_at

LAYOUT = Path("data/translations/boot_warnings.json")
NAMES = [f"ERR{n}.BIN" for n in range(1, 6)]
WIDTH, HEIGHT, STRIDE, PIXELS = 352, 240, 176, 118
MARGIN, LAST_ROW, GLYPH_ROWS = 8, 223, 12
VISIBLE = LAST_ROW + 1  # picture rows shown (screen rows 8-231)
SHADOW_PEN, SHADOW = 7, 1
# colour: (bright entry for pens 2-3, dim entry for pens 4-6 and 8)
COLOURS = {"white": (6, 5), "yellow": (12, 11), "cyan": (10, 9), "red": (14, 14)}
MARKUP = re.compile(r"\{([^}]*)\}|\[([^\]]*)\]|([^{\[]+)")


def spans(line: str) -> list[tuple[str, str]]:
    """Split a line into (text, colour) pieces; refuse unbalanced marks."""
    out = []
    if sum(len(m.group()) for m in MARKUP.finditer(line)) != len(line):
        raise ValueError(f"unbalanced marks in {line!r}")
    for match in MARKUP.finditer(line):
        cyan, red, plain = match.groups()
        if cyan is not None:
            out.append((cyan, "cyan"))
        elif red is not None:
            out.append((red, "red"))
        else:
            out.append((plain, "white"))
    if any(mark in text for text, _ in out for mark in "{}[]"):
        raise ValueError(f"unbalanced marks in {line!r}")
    return out


class Canvas:
    """A 352 x 240 picture of palette indices, top row first."""

    def __init__(self, font: Font, pitch: int) -> None:
        self.font = font
        self.pitch = pitch
        self.pixels = bytearray(WIDTH * HEIGHT)

    def right(self, char: str) -> int:
        """The rightmost ink column of ``char``'s glyph (-1 if blank)."""
        cell, _ = self.font.glyph(ENCODE[char])
        columns = [c for c in range(16) for r in range(16) if nibble_at(cell, r, c)]
        return max(columns, default=-1)

    def width(self, text: str) -> int:
        if not text:
            return 0
        return self.pitch * (len(text) - 1) + self.right(text[-1]) + 1

    def draw(self, text: str, colour: str, left: int, top: int) -> None:
        bright, dim = COLOURS[colour]
        for i, char in enumerate(text):
            if char == " ":
                continue
            cell, _ = self.font.glyph(ENCODE[char])
            for r in range(16):
                for c in range(16):
                    pen = nibble_at(cell, r, c)
                    if not pen:
                        continue
                    x, y = left + i * self.pitch + c, top + r
                    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                        raise ValueError(f"{text!r} leaves the picture")
                    if pen == SHADOW_PEN:
                        if self.pixels[y * WIDTH + x] == 0:
                            self.pixels[y * WIDTH + x] = SHADOW
                    else:
                        self.pixels[y * WIDTH + x] = bright if pen in (2, 3) else dim


def packed(pixels: bytes) -> bytes:
    """Top-down indices as BMP rows: bottom row first, two pixels a byte."""
    rows = []
    for y in range(HEIGHT - 1, -1, -1):
        row = pixels[y * WIDTH : (y + 1) * WIDTH]
        rows.append(bytes((row[x] << 4) | row[x + 1] for x in range(0, WIDTH, 2)))
    return b"".join(rows)


def render(
    original: bytes, lines: list[str], font: Font, style: dict[str, object]
) -> bytes:
    pitch, step = int(str(style["pitch"])), int(str(style["line"]))
    canvas = Canvas(font, pitch)
    title = str(style["title"])
    title_top, top = int(str(style["title_top"])), int(str(style["top"]))
    canvas.draw(title, "yellow", (WIDTH - canvas.width(title)) // 2, title_top)
    pieces = [spans(line) for line in lines]
    widest = max(canvas.width("".join(text for text, _ in piece)) for piece in pieces)
    if widest > WIDTH - 2 * MARGIN:
        raise ValueError(f"a line is {widest} pixels wide")
    left = (WIDTH - widest) // 2
    bottom = top
    for piece in pieces:
        if not piece:
            top += step // 2
            continue
        column = 0
        for text, colour in piece:
            canvas.draw(text, colour, left + column * pitch, top)
            column += len(text)
        bottom = top + GLYPH_ROWS - 1
        top += step
    if bottom > LAST_ROW:
        raise ValueError(f"the text reaches picture row {bottom}")
    return original[:PIXELS] + packed(bytes(canvas.pixels))


def check(original: bytes, built: bytes) -> None:
    """Refuse a result that does not keep the original's format (`EXP-0054`)."""
    if built[:2] != b"BM" or struct.unpack_from("<I", built, 10)[0] != PIXELS:
        raise ValueError("not the expected BMP header")
    if struct.unpack_from("<iiHH", built, 18) != (WIDTH, HEIGHT, 1, 4):
        raise ValueError("not 352 x 240 at 4 bits")
    if len(built) != len(original) or built[:PIXELS] != original[:PIXELS]:
        raise ValueError("the size, header or palette changed")


def build(
    fix: bytes, originals: dict[str, bytes], layout: dict[str, object]
) -> dict[str, bytes]:
    """The five English pictures, from ``FIX.PRS`` and the untouched files."""
    style = layout["style"]
    screens = layout["screens"]
    assert isinstance(style, dict) and isinstance(screens, dict)
    if style.get("palette") != "japanese":
        raise ValueError("only the approved style (the original palette) is drawn")
    if sorted(screens) != sorted(NAMES):
        raise ValueError(f"the layout must cover {NAMES}")
    font = Font(fix, 0, 0)
    out = {}
    for name in NAMES:
        screen = screens[name]
        original = originals[name]
        if hashlib.sha256(original).hexdigest() != screen["source_sha256"]:
            raise ValueError(f"{name} is not the picture the wording was approved for")
        own = {**style, "top": screen.get("top", style["top"])}
        built = render(original, list(screen["lines"]), font, own)
        check(original, built)
        out[name] = built
    return out


def load_layout(path: Path = LAYOUT) -> dict[str, object]:
    data: dict[str, object] = json.loads(path.read_text())
    return data


def shown(data: bytes) -> bytes:
    """RGB pixels of the 352 x 240 screenshot of ``data`` (224 lines shown)."""
    palette = [data[54 + 4 * i : 54 + 4 * i + 3][::-1] for i in range(16)]
    colours = [bytes((c & 31) << 3 for c in entry) for entry in palette]
    out = bytearray()
    for y in range(HEIGHT):
        row = y - 8
        for x in range(WIDTH):
            if 0 <= row < VISIBLE:
                byte = data[PIXELS + (HEIGHT - 1 - row) * STRIDE + x // 2]
                out += colours[byte >> 4 if x % 2 == 0 else byte & 15]
            else:
                out += bytes(3)
    return bytes(out)

r"""EXP-0055: draw English boot-warning samples in the game's quote font.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0055/render_samples.py \
        LAYOUT OUT [--palette {japanese,corrected}] [--pitch N] [--line N]

For each screen in LAYOUT (``draft.json``), the untouched ``ERRn.BIN`` is
read from the data track and its pixels cleared; then "WARNING" (yellow,
centred, picture row ``TITLE_TOP``) and the lines (white, a left-aligned
block centred on the screen, from ``TOP``) are drawn with the ``FIX.PRS``
quote-font glyphs (`tools.text.font`; codes from `tools.text.caption`), N
pixels apart (default 12, the game's English quote pitch). Lines are N rows
apart (default 14) and an empty line is half that. ``{text}`` is cyan and
``[text]`` red, as the Japanese highlights.

Pens: 2-3 take the colour's bright entry, 4-6 and 8 its dim entry, and 7
(the drop shadow) dark grey (index 1). With ``--palette corrected`` the
file's 16 palette entries are rewritten so that the game's conversion (it
keeps each channel's low five bits, `EXP-0054`) shows the colours the
palette was drawn with: each channel becomes ``value >> 3``.

Writes ``OUT/ERRn.BIN`` (a full file of the original size) and
``OUT/ERRn_screen.png``: the 352 x 240 screen as the game shows it (picture
row y at screen row y + 8, the game's colour rule). Raises if a line is
wider than the screen's margins or the text runs below picture row 231.
OUT is an ignored path: the files hold the game's font.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.text.caption import ENCODE
from tools.text.font import Font, nibble_at

WIDTH, HEIGHT, STRIDE, PIXELS = 352, 240, 176, 118
TITLE_TOP, TOP, MARGIN, LAST_ROW = 24, 52, 8, 231
SHADOW = 1
# colour: (bright entry for pens 2-3, dim entry for pens 4-6 and 8)
COLOURS = {"white": (6, 5), "yellow": (12, 11), "cyan": (10, 9), "red": (14, 14)}
MARKS = {"{": ("}", "cyan"), "[": ("]", "red")}
GLYPH_ROWS = 12


def spans(line: str) -> list[tuple[str, str]]:
    """Split a line into (text, colour) pieces."""
    out = []
    pattern = re.compile(r"\{([^}]*)\}|\[([^\]]*)\]|([^{\[]+)")
    for match in pattern.finditer(line):
        cyan, red, plain = match.groups()
        if cyan is not None:
            out.append((cyan, "cyan"))
        elif red is not None:
            out.append((red, "red"))
        else:
            out.append((plain, "white"))
    if "".join(t for t, _ in out) != re.sub(r"[{}\[\]]", "", line):
        raise ValueError(f"unbalanced marks in {line!r}")
    return out


class Canvas:
    def __init__(self, font: Font, pitch: int) -> None:
        self.font = font
        self.pitch = pitch
        self.pixels = bytearray(WIDTH * HEIGHT)  # one index per pixel, top-down

    def ink(self, char: str) -> tuple[int, int]:
        cell, _ = self.font.glyph(ENCODE[char])
        columns = [c for c in range(16) for r in range(16) if nibble_at(cell, r, c)]
        return (min(columns), max(columns)) if columns else (0, -1)

    def width(self, text: str) -> int:
        if not text:
            return 0
        return self.pitch * (len(text) - 1) + self.ink(text[-1])[1] + 1

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
                    index = SHADOW if pen == 7 else bright if pen in (2, 3) else dim
                    if pen != 7 or self.pixels[y * WIDTH + x] == 0:
                        self.pixels[y * WIDTH + x] = index


def bmp_pixels(pixels: bytes) -> bytes:
    rows = []
    for y in range(HEIGHT - 1, -1, -1):
        row = pixels[y * WIDTH : (y + 1) * WIDTH]
        rows.append(bytes((row[x] << 4) | row[x + 1] for x in range(0, WIDTH, 2)))
    return b"".join(rows)


def corrected(palette: bytes) -> bytes:
    out = bytearray(palette)
    for i in range(16):
        for k in range(3):
            out[4 * i + k] = palette[4 * i + k] >> 3
    return bytes(out)


def screen_png(data: bytes) -> bytes:
    palette = [data[54 + 4 * i : 54 + 4 * i + 3][::-1] for i in range(16)]
    shown = [bytes((c & 31) << 3 for c in p) for p in palette]
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)
        py = y - 8
        for x in range(WIDTH):
            if 0 <= py < HEIGHT:
                byte = data[PIXELS + (HEIGHT - 1 - py) * STRIDE + x // 2]
                raw += shown[byte >> 4 if x % 2 == 0 else byte & 15]
            else:
                raw += bytes(3)

    def chunk(kind: bytes, body: bytes) -> bytes:
        crc = zlib.crc32(kind + body)
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


def render(
    original: bytes, lines: list[str], font: Font, pitch: int, step: int, palette: str
) -> bytes:
    canvas = Canvas(font, pitch)
    title = "WARNING"
    canvas.draw(title, "yellow", (WIDTH - canvas.width(title)) // 2, TITLE_TOP)
    pieces = [spans(line) for line in lines]
    widest = max(canvas.width("".join(t for t, _ in p)) for p in pieces)
    if widest > WIDTH - 2 * MARGIN:
        raise ValueError(f"a line is {widest} pixels wide")
    left = (WIDTH - widest) // 2
    top = TOP
    for line in pieces:
        if not line:
            top += step // 2
            continue
        column = 0
        for text, colour in line:
            canvas.draw(text, colour, left + column * pitch, top)
            column += len(text)
        top += step
    if top - step + GLYPH_ROWS - 1 > LAST_ROW:
        raise ValueError("the text runs below the screen")
    head = original[:PIXELS]
    if palette == "corrected":
        head = head[:54] + corrected(head[54:118])
    out = head + bmp_pixels(bytes(canvas.pixels))
    if len(out) != len(original):
        raise ValueError("size changed")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("layout", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument(
        "--palette", choices=("japanese", "corrected"), default="japanese"
    )
    parser.add_argument("--pitch", type=int, default=12)
    parser.add_argument("--line", type=int, default=14)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=False)
    font = Font(read_file("FIX.PRS;1"), 0, 0)
    screens = json.loads(args.layout.read_text())["screens"]
    for name, screen in screens.items():
        original = read_file(f"{name};1")
        data = render(
            original, screen["lines"], font, args.pitch, args.line, args.palette
        )
        stem = name.split(".")[0]
        (args.out / name).write_bytes(data)
        (args.out / f"{stem}_screen.png").write_bytes(screen_png(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

r"""EXP-0054: compare a screenshot with a 4-bit BMP drawn at 5 bits per channel.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0054/compare_screen.py \
        SCREEN_PNG BMP [--shift ROWS]

The BMP (``ERRn.BIN``) is decoded with `EXP-0053`'s ``render_bmp.decode``.
Screen row y is compared with BMP row y + ROWS (default -8: screen row 8
shows picture row 0, `EXP-0054`); screen rows with no picture row must be
black. The expected colour of a pixel is its palette entry as the game
converts it (``0x060220DC``): each 8-bit channel's low 5 bits, which the
screenshot shows as that value << 3. Prints the pixels compared and the
pixels that differ, with the first few.
"""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path


def read_png(path: Path) -> tuple[int, int, bytes]:
    """RGB pixels of an 8-bit RGB or RGBA PNG (filters 0-4)."""
    data = path.read_bytes()
    at, idat = 8, b""
    width = height = kind = 0
    while at < len(data):
        size = struct.unpack_from(">I", data, at)[0]
        tag, body = data[at + 4 : at + 8], data[at + 8 : at + 8 + size]
        if tag == b"IHDR":
            width, height, _, kind = struct.unpack(">IIBB", body[:10])
        elif tag == b"IDAT":
            idat += body
        at += 12 + size
    raw = zlib.decompress(idat)
    bpp = {2: 3, 6: 4}[kind]
    stride = width * bpp
    out = bytearray()
    previous = bytearray(stride)
    pos = 0
    for _ in range(height):
        kind_ = raw[pos]
        line = bytearray(raw[pos + 1 : pos + 1 + stride])
        pos += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = previous[x]
            c = previous[x - bpp] if x >= bpp else 0
            if kind_ == 1:
                line[x] = (line[x] + a) & 255
            elif kind_ == 2:
                line[x] = (line[x] + b) & 255
            elif kind_ == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif kind_ == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                guess = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[x] = (line[x] + guess) & 255
        out += line
        previous = line
    if bpp == 4:
        out = bytearray(v for i, v in enumerate(out) if i % 4 != 3)
    return width, height, bytes(out)


def compare(screen: Path, bmp: Path, shift: int) -> tuple[int, int, list[str]]:
    sw, sh, s = read_png(screen)
    data = bmp.read_bytes()
    offset = struct.unpack_from("<I", data, 10)[0]
    header = struct.unpack_from("<I", data, 14)[0]
    bw, bh = struct.unpack_from("<ii", data, 18)
    stride = (bw * 4 + 31) // 32 * 4
    palette = [
        data[14 + header + 4 * i : 14 + header + 4 * i + 3][::-1] for i in range(16)
    ]
    shown = [bytes((c & 31) << 3 for c in entry) for entry in palette]
    compared, differ = 0, 0
    notes: list[str] = []
    for y in range(sh):
        by = y + shift
        row = data[offset + (bh - 1 - by) * stride :] if 0 <= by < bh else b""
        for x in range(sw):
            pixel = s[(y * sw + x) * 3 : (y * sw + x) * 3 + 3]
            if row and x < bw:
                index = row[x // 2] >> 4 if x % 2 == 0 else row[x // 2] & 15
                want = shown[index]
            else:
                want = bytes(3)
            compared += 1
            if pixel != want:
                differ += 1
                if len(notes) < 5:
                    notes.append(f"({x},{y}) screen {pixel.hex()} want {want.hex()}")
    return compared, differ, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("screen", type=Path)
    parser.add_argument("bmp", type=Path)
    parser.add_argument("--shift", type=int, default=-8)
    args = parser.parse_args(argv)
    compared, differ, notes = compare(args.screen, args.bmp, args.shift)
    print(f"compared {compared} differ {differ}")
    for note in notes:
        print(" ", note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

r"""EXP-0058: draw 76-byte Japanese quote records with the quote font, for reading.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0058/render_records.py \
        DUMP ADDRESS COUNT OUT_PNG [--stride N]

DUMP is a WRAM-H dump (``0x06000000``); COUNT records of 76 bytes (2 lines of
19 big-endian 16-bit codes, `D-015`) are read from ADDRESS, each ``--stride``
bytes apart (default 76), and drawn one under the other with the ``FIX.PRS``
glyph for each code (`tools.text.font`), white on black, so the agent can read
them. OUT_PNG holds game glyphs: an ignored path.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.text.font import Font, nibble_at

WRAM_H, CELLS, LINES = 0x06000000, 19, 2


def png(width: int, height: int, gray: bytes) -> bytes:
    rows = b"".join(b"\x00" + gray[y * width : (y + 1) * width] for y in range(height))

    def chunk(kind: bytes, body: bytes) -> bytes:
        crc = zlib.crc32(kind + body)
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    head = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", head)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dump", type=Path)
    parser.add_argument("address", type=lambda v: int(v, 16))
    parser.add_argument("count", type=int)
    parser.add_argument("out", type=Path)
    parser.add_argument("--stride", type=int, default=76)
    args = parser.parse_args(argv)
    memory = args.dump.read_bytes()
    font = Font(read_file("FIX.PRS;1"), 0, 0)
    width, line_height = CELLS * 16 + 8, 18
    height = args.count * (LINES * line_height + 10)
    gray = bytearray(width * height)
    for n in range(args.count):
        at = args.address - WRAM_H + n * args.stride
        record = memory[at : at + CELLS * LINES * 2]
        for line in range(LINES):
            for cell in range(CELLS):
                code = int.from_bytes(
                    record[(line * CELLS + cell) * 2 : (line * CELLS + cell) * 2 + 2],
                    "big",
                )
                glyph, _ = font.glyph(code)
                top = n * (LINES * line_height + 10) + line * line_height
                for r in range(16):
                    for c in range(16):
                        pen = nibble_at(glyph, r, c)
                        if pen and pen != 15:
                            gray[(top + r) * width + 4 + cell * 16 + c] = 255
    args.out.write_bytes(png(width, height, bytes(gray)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Decode XvSF Saturn quote-font glyphs from a memory image or ``FIX.PRS``.

Copied from the MSHvSF repository, `tools/text/font.py` at commit `69c666c`
(last changed in `fb4aa51`), where the format was reimplemented from MSHvSF's
renderer. For XvSF it was checked against XvSF's own glyph routine at WRAM-H
``0x06024CF0`` (`EXP-0019`), and it decodes all 22 distinct codes of the M1
quote to the drawn VDP1 cells byte for byte. Changes: this docstring and the
CLI, which reads any `mcs_extract` region (WRAM-L by default) or a raw font
file. The routine reads the font base from the pointer at WRAM-H
``0x0602586C``, which held ``0x002C3EA0`` (WRAM-L) in the tested session. The
font image is the file ``FIX.PRS`` (`EXP-0019`).

For code ``c``:

* The block table at ``base + 16`` holds one big-endian long per block of 16
  codes. It gives the offset (from ``base + 16``) of the block's first glyph.
* The size table at ``base + 16 + 0x380`` holds one byte per code. The sizes of
  the preceding codes in the block are added to reach code ``c``.
* A negative size byte means a raw 128-byte 4 bpp 16x16 cell, and zero means an
  empty cell.
* A positive size means the glyph is compressed:
  1. A 16-bit mask (first byte high), read LSB first, selects up to 16 bytes.
     Selected byte ``b`` for bit ``4·j + k`` provides nibble masks
     ``nib[8k + j] = b & 0xF`` and ``nib[8k + 4 + j] = b >> 4``.
  2. The cell is filled column by column (8 byte columns), top to bottom. Each
     nibble mask covers four rows, LSB first. Bit 1 reads the next stream byte;
     bit 0 repeats the column's previous byte, which starts at 0 for each column.

Decoded cells include the drop shadow (nibble ``F``).
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import REGIONS, encode_png

CELL_BYTES = 128
BLOCK_TABLE = 16
SIZE_TABLE = BLOCK_TABLE + 0x380


class Font:
    """Read glyphs from a memory image (at ``image_base``) with the font at ``base``."""

    def __init__(self, image: bytes, image_base: int, font_base: int) -> None:
        self.image = image
        self.image_base = image_base
        self.base = font_base

    def _read(self, address: int, length: int) -> bytes:
        offset = address - self.image_base
        if not 0 <= offset <= len(self.image) - length:
            raise ValueError(f"address 0x{address:08X} is outside the image")
        return self.image[offset : offset + length]

    def locate(self, code: int) -> tuple[int, int]:
        """Return (data address, size byte) for ``code``."""
        first = code & ~0xF
        table = self.base + BLOCK_TABLE
        address = table + int.from_bytes(self._read(table + (first >> 2), 4), "big")
        sizes = self._read(self.base + SIZE_TABLE + first, 16)
        address += sum(sizes[: code & 0xF])
        return address, sizes[code & 0xF]

    def glyph(self, code: int) -> tuple[bytes, str]:
        """Return the 128-byte 4 bpp cell and its kind (raw/empty/compressed)."""
        address, size = self.locate(code)
        if size & 0x80:
            return self._read(address, CELL_BYTES), "raw"
        if size == 0:
            return bytes(CELL_BYTES), "empty"
        stream = self._read(address, size)
        return decompress(stream), "compressed"


def decompress(stream: bytes) -> bytes:
    mask = (stream[0] << 8) | stream[1]
    pos = 2
    nibbles = [0] * 32
    for j in range(4):
        for k in range(4):
            value = 0
            if mask & 1:
                value = stream[pos]
                pos += 1
            mask >>= 1
            nibbles[8 * k + j] = value & 0xF
            nibbles[8 * k + 4 + j] = value >> 4
    cell = bytearray(CELL_BYTES)
    index = 0
    for column in range(8):
        current = 0
        for group in range(4):
            bits = nibbles[index]
            index += 1
            for bit in range(4):
                if bits & 1:
                    current = stream[pos]
                    pos += 1
                bits >>= 1
                cell[(group * 4 + bit) * 8 + column] = current
    return bytes(cell)


def nibble_at(cell: bytes, row: int, column: int) -> int:
    value = cell[row * 8 + column // 2]
    return value >> 4 if column % 2 == 0 else value & 0xF


def render(
    font: Font, codes: Sequence[int], columns: int = 16, scale: int = 1
) -> bytes:
    """Render glyphs to a grayscale PNG grid (shadow drawn dark gray)."""
    rows = (len(codes) + columns - 1) // columns
    width, height = columns * 18 * scale, rows * 18 * scale
    pixels = bytearray(width * height * 3)
    for index, code in enumerate(codes):
        cell, _ = font.glyph(code)
        left, top = (index % columns) * 18 + 1, (index // columns) * 18 + 1
        for row in range(16):
            for column in range(16):
                nibble = nibble_at(cell, row, column)
                shade = 0 if nibble == 0 else 90 if nibble == 15 else 255 - nibble * 12
                for dy in range(scale):
                    for dx in range(scale):
                        y = (top + row) * scale + dy
                        x = (left + column) * scale + dx
                        offset = (y * width + x) * 3
                        pixels[offset : offset + 3] = bytes((shade, shade, shade))
    return encode_png(width, height, bytes(pixels))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decode quote-font glyphs.")
    parser.add_argument("image", type=Path, help="mcs_extract region or FIX.PRS")
    parser.add_argument(
        "--region",
        choices=[*sorted(REGIONS), "file"],
        default="wram_l",
        help="what IMAGE is; 'file' means the font starts at offset 0",
    )
    parser.add_argument("--font-base", type=lambda v: int(v, 0), default=0x002C3EA0)
    parser.add_argument("--first", type=lambda v: int(v, 0), default=0)
    parser.add_argument("--count", type=int, default=256)
    parser.add_argument("--render", type=Path, help="write an atlas PNG (ignored path)")
    parser.add_argument(
        "--check", type=Path, help="glyph_codes JSON to compare against"
    )
    args = parser.parse_args(argv)
    if args.region == "file":
        font = Font(args.image.read_bytes(), 0, 0)
    else:
        image_base = REGIONS[args.region].base_address
        font = Font(args.image.read_bytes(), image_base, args.font_base)
    codes = list(range(args.first, args.first + args.count))
    kinds: dict[str, int] = {}
    for code in codes:
        kind = font.glyph(code)[1]
        kinds[kind] = kinds.get(kind, 0) + 1
    report: dict[str, object] = {
        "codes": f"0x{codes[0]:04X}-0x{codes[-1]:04X}",
        "kinds": kinds,
    }
    if args.render:
        args.render.write_bytes(render(font, codes))
    if args.check:
        known = json.loads(args.check.read_text())["glyphs"]
        matches = sum(
            1
            for code, cell in known.items()
            if font.glyph(int(code, 16))[0].hex() == cell
        )
        report["check"] = {"known": len(known), "exact_matches": matches}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

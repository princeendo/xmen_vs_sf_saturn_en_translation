r"""EXP-0049: decode cells from the game's compressed cell pack.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/cells.py PACK FIRST COUNT OUT_PNG

A reimplementation of the Saturn cell decoder at ``0x06024CF0`` (read from
its disassembly in WRAM-H, `EXP-0049`). The pack starts at the address held
at ``0x0602586C``; PACK is a file holding the pack from its first byte.

- **Locating cell n:** its block is ``n & ~15``. The block's start is the
  long at ``pack + 16 + block / 4``, plus ``pack + 16``. Within the block,
  the cell's size bytes (``pack + 16 + 0x380 + index``, unsigned) of the
  cells before it are added.
- **Type** (the cell's size byte, signed):
  - negative: 128 raw bytes;
  - zero: a blank cell;
  - positive: a 16-bit mask (big-endian) builds 16 values. Each set bit
    takes the next byte, a clear bit gives 0. Each value v gives two table
    entries, v and v >> 4, at ``j + 8i`` and ``j + 8i + 4`` (j the mask
    group 0-3, i the bit within it). The cell is then filled column by
    column (8 byte columns, 16 rows). Each row takes its bit from the next
    table entry's low nibble: a set bit takes the next byte, a clear bit
    repeats the column's last byte (0 at the column's start).

A cell is 16 x 16 pixels at 4 bits per pixel (128 bytes, 8 bytes a row).
With OUT_PNG, COUNT cells from FIRST are drawn in grayscale, 16 per row.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

CELL = 128
SIZES = 16 + 0x380


def locate(pack: bytes, index: int) -> tuple[int, int]:
    """(offset of the cell's data in the pack, its signed size byte)."""
    block = index & ~15
    start = 16 + struct.unpack_from(">I", pack, 16 + block // 4)[0]
    for i in range(block, index):
        start += pack[SIZES + i]
    kind = pack[SIZES + index]
    return start, kind - 256 if kind >= 128 else kind


def decode(pack: bytes, index: int) -> bytes:
    at, kind = locate(pack, index)
    if kind < 0:
        return pack[at : at + CELL]
    if kind == 0:
        return bytes(CELL)
    mask = pack[at] << 8 | pack[at + 1]
    at += 2
    table = [0] * 32
    for j in range(4):
        for i in range(4):
            value = 0
            if mask & 1:
                value = pack[at]
                at += 1
            mask >>= 1
            table[j + 8 * i] = value
            table[j + 8 * i + 4] = value >> 4
    out = bytearray(CELL)
    k = 0
    for column in range(8):
        last = 0
        for group in range(4):
            bits = table[k]
            k += 1
            for step in range(4):
                if bits & 1:
                    last = pack[at]
                    at += 1
                bits >>= 1
                out[column + 8 * (4 * group + step)] = last
    return bytes(out)


def png(width: int, height: int, gray: bytes) -> bytes:
    rows = b"".join(b"\x00" + gray[y * width : (y + 1) * width] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def sheet(pack: bytes, first: int, count: int, columns: int = 16) -> bytes:
    rows = (count + columns - 1) // columns
    width, height = columns * 17, rows * 17
    gray = bytearray(width * height)
    for n in range(count):
        cell = decode(pack, first + n)
        ox, oy = (n % columns) * 17, (n // columns) * 17
        for y in range(16):
            for x in range(16):
                byte = cell[y * 8 + x // 2]
                nibble = byte >> 4 if x % 2 == 0 else byte & 15
                gray[(oy + y) * width + ox + x] = nibble * 17
    return png(width, height, bytes(gray))


def main(argv: list[str]) -> int:
    pack = Path(argv[0]).read_bytes()
    first, count = int(argv[1], 0), int(argv[2], 0)
    Path(argv[3]).write_bytes(sheet(pack, first, count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

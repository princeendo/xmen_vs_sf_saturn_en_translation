r"""EXP-0053: draw a 4-bit Windows BMP (such as ``ERR5.BIN``) as a PNG.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0053/render_bmp.py BMP OUT_PNG

Reads the BMP header (``BM``; pixel-data offset at 10, width at 18, height
at 22, bits per pixel at 28, 4 only), the 16-entry BGRA palette after the
40-byte info header, and the rows, bottom-up and padded to 4 bytes, high
nibble first. Writes an RGB PNG of the same size. It only reads the file,
for viewing a screen the census could not trigger; whether the game draws
the file as it is belongs to `BOOT-002`. OUT_PNG goes to an ignored path.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path


def decode(data: bytes) -> tuple[int, int, bytes]:
    if data[:2] != b"BM":
        raise ValueError("not a BMP")
    offset = struct.unpack_from("<I", data, 10)[0]
    header = struct.unpack_from("<I", data, 14)[0]
    width, height = struct.unpack_from("<ii", data, 18)
    bits = struct.unpack_from("<H", data, 28)[0]
    if bits != 4:
        raise ValueError(f"{bits} bits per pixel; only 4 is read")
    palette = [
        data[14 + header + 4 * i : 14 + header + 4 * i + 3][::-1] for i in range(16)
    ]
    stride = (width * 4 + 31) // 32 * 4
    rows = []
    for y in range(abs(height)):
        source = height - 1 - y if height > 0 else y
        row = data[offset + source * stride : offset + source * stride + stride]
        pixels = bytearray()
        for x in range(width):
            value = row[x // 2] >> 4 if x % 2 == 0 else row[x // 2] & 15
            pixels += palette[value]
        rows.append(bytes(pixels))
    return width, abs(height), b"".join(rows)


def png(width: int, height: int, rgb: bytes) -> bytes:
    rows = b"".join(
        b"\x00" + rgb[y * width * 3 : (y + 1) * width * 3] for y in range(height)
    )

    def chunk(kind: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body))
            + kind
            + body
            + struct.pack(">I", zlib.crc32(kind + body))
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def main(argv: list[str]) -> int:
    width, height, rgb = decode(Path(argv[0]).read_bytes())
    Path(argv[1]).write_bytes(png(width, height, rgb))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

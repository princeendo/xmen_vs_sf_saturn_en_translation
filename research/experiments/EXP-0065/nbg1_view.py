r"""EXP-0065: render NBG1's visible window from a VDP2 VRAM dump (greyscale).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/nbg1_view.py VRAM X Y OUT

NBG1 as set up in the attract (`EXP-0065`): one plane of 2 x 2 pages at
``0x6C000``, 2 x 2-cell characters, 2-word pattern names, wrapping every
1,024 pixels. Renders the 352 x 240 window at scroll (X, Y), colour index
x 17 as grey (flips honoured), to OUT (PNG, through ffmpeg).
"""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

W, H, PLANE = 352, 240, 0x6C000


def render(vram: bytes, sx: int, sy: int) -> bytes:
    out = bytearray(W * H * 3)
    for y in range(H):
        py = (sy + y) % 1024
        for x in range(W):
            px = (sx + x) % 1024
            page = PLANE + 0x1000 * ((py // 512) * 2 + px // 512)
            e = struct.unpack_from(
                ">I", vram, page + 4 * (((py % 512) // 16) * 32 + (px % 512) // 16)
            )[0]
            char, hflip, vflip = e & 0x7FFF, (e >> 30) & 1, (e >> 31) & 1
            cx, cy = px % 16, py % 16
            if hflip:
                cx = 15 - cx
            if vflip:
                cy = 15 - cy
            cell = ((char + (cy // 8) * 2 + cx // 8) * 32) % len(vram)
            b = vram[cell + (cy % 8) * 4 + (cx % 8) // 2]
            v = (b >> 4 if cx % 2 == 0 else b & 15) * 17
            out[(y * W + x) * 3 : (y * W + x) * 3 + 3] = bytes((v, v, v))
    return bytes(out)


def main(vram: Path, sx: int, sy: int, png: Path) -> int:
    subprocess.run(
        [
            *(
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
            ),
            *("-s", f"{W}x{H}", "-i", "-", str(png)),
        ],
        input=render(vram.read_bytes(), sx, sy),
        check=True,
    )
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), int(a[1]), int(a[2]), Path(a[3])))

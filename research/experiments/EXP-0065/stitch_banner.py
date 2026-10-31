r"""EXP-0065: stitch the arcade's scrolling caption into one image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/stitch_banner.py \
        SNAPS FIRST LAST TOP HEIGHT STEP OUT

SNAPS holds MAME snapshots ``xmvsfu_f<frame>.png`` for every frame FIRST to
LAST. The caption scrolls left STEP pixels a frame (`EXP-0065`: 8, with no
differing pixel between shifted frames). The image is frame FIRST's rows
TOP to TOP + HEIGHT, followed by the rightmost STEP columns of each later
frame; columns that are all background at either end are trimmed. Writes
OUT (PNG, through ffmpeg). Game-derived: OUT goes under ``local/``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WIDTH = 384


def rows(path: Path, top: int, height: int) -> list[bytes]:
    raw = subprocess.run(
        [
            *("ffmpeg", "-loglevel", "error", "-i", str(path)),
            *("-vf", f"crop={WIDTH}:{height}:0:{top}"),
            *("-f", "rawvideo", "-pix_fmt", "rgb24", "-"),
        ],
        capture_output=True,
        check=True,
    ).stdout
    return [raw[r * WIDTH * 3 : (r + 1) * WIDTH * 3] for r in range(height)]


def main(
    snaps: Path, first: int, last: int, top: int, height: int, step: int, out: Path
) -> int:
    canvas = [
        bytearray(r) for r in rows(snaps / f"xmvsfu_f{first:05d}.png", top, height)
    ]
    for frame in range(first + 1, last + 1):
        for line, row in zip(
            canvas, rows(snaps / f"xmvsfu_f{frame:05d}.png", top, height), strict=True
        ):
            line += row[(WIDTH - step) * 3 :]
    width = len(canvas[0]) // 3
    background = canvas[0][:3]
    used = [
        x
        for x in range(width)
        if any(line[x * 3 : x * 3 + 3] != background for line in canvas)
    ]
    left, right = used[0], used[-1] + 1
    trimmed = b"".join(bytes(line[left * 3 : right * 3]) for line in canvas)
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
            *("-s", f"{right - left}x{height}", "-i", "-", str(out)),
        ],
        input=trimmed,
        check=True,
    )
    print(f"{out}: {right - left}x{height}")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            int(a[1]),
            int(a[2]),
            int(a[3]),
            int(a[4]),
            int(a[5]),
            Path(a[6]),
        )
    )

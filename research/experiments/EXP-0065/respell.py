r"""EXP-0065: respell a word of a stitched arcade caption from its own letters.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/respell.py \
        IN START PITCH ORDER OUT

IN is a stitched caption (`stitch_banner.py`). The word's letters sit at a
fixed PITCH from x = START (the first letter's left outline), as in the
arcade's caption lettering, where neighbours share a 3-pixel outline. ORDER
lists, for each letter slot, the index of the source letter to copy into it
(for example ``0,1,2,4,5,5,6`` turns UNCCANY into UNCANNY). Columns outside
the word are kept. Writes OUT (PNG). Game-derived: OUT goes under ``local/``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def size(path: Path) -> tuple[int, int]:
    text = subprocess.run(
        [
            *("ffprobe", "-v", "error", "-show_entries", "stream=width,height"),
            *("-of", "csv=p=0", str(path)),
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    width, height = text.strip().split(",")
    return int(width), int(height)


def main(src: Path, start: int, pitch: int, order: list[int], out: Path) -> int:
    width, height = size(src)
    raw = subprocess.run(
        [
            *("ffmpeg", "-loglevel", "error", "-i", str(src)),
            *("-f", "rawvideo", "-pix_fmt", "rgb24", "-"),
        ],
        capture_output=True,
        check=True,
    ).stdout
    rows = [bytearray(raw[y * width * 3 : (y + 1) * width * 3]) for y in range(height)]
    original = [bytes(r) for r in rows]
    for slot, letter in enumerate(order):
        target, source = start + slot * pitch, start + letter * pitch
        for row, old in zip(rows, original, strict=True):
            row[target * 3 : (target + pitch) * 3] = old[
                source * 3 : (source + pitch) * 3
            ]
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
            *("-s", f"{width}x{height}", "-i", "-", str(out)),
        ],
        input=b"".join(bytes(r) for r in rows),
        check=True,
    )
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            int(a[1]),
            int(a[2]),
            [int(x) for x in a[3].split(",")],
            Path(a[4]),
        )
    )

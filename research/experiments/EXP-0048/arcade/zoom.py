"""EXP-0048 (LOC-001, arcade side): enlarge part of a snapshot, to read labels.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0048/arcade/zoom.py \\
        PNG OUT X Y W H [SCALE]

Crops the W x H region at (X, Y) of PNG and scales it by SCALE (default 4)
with nearest-neighbour sampling (ffmpeg), so no pixel is invented. Prints
the SHA-256 of the source PNG, which is the evidence; OUT is a viewing aid.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


def zoom(png: Path, out: Path, x: int, y: int, w: int, h: int, scale: int) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"crop={w}:{h}:{x}:{y},scale={w * scale}:{h * scale}:flags=neighbor"
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(png), "-vf", vf, str(out)],
        check=True,
    )
    return hashlib.sha256(png.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    png, out = Path(argv[0]), Path(argv[1])
    x, y, w, h = (int(v) for v in argv[2:6])
    scale = int(argv[6]) if len(argv) > 6 else 4
    print(zoom(png, out, x, y, w, h, scale), png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

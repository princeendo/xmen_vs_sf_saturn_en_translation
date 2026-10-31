r"""EXP-0065: gather the arcade caption art the caption build reads.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/caption_art.py SNAPS BANNER OUT

SNAPS holds MAME ``xmvsfu`` snapshots (`stitch_banner.py`'s run, every frame
around the captions); BANNER is the stitched, respelled banner
(`respell.py`, UNCANNY). Writes ``OUT/c1.png``-``c3.png`` (each caption, 352
x 200: arcade columns 16-367, rows 0-199, frames 1,440, 1,800 and 2,055) and
``OUT/banner.png``. Game-derived: OUT goes under ``local/``.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

FRAMES = {"c1": 1440, "c2": 1800, "c3": 2055}


def main(snaps: Path, banner: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    for name, frame in FRAMES.items():
        subprocess.run(
            [
                *(
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-i",
                    str(snaps / f"xmvsfu_f{frame:05d}.png"),
                ),
                *("-vf", "crop=352:200:16:0", str(out / f"{name}.png")),
            ],
            check=True,
        )
    shutil.copy(banner, out / "banner.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))

"""EXP-0048 (LOC-001, arcade side): contact sheets of a run's snapshots, for viewing.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0048/arcade/sheet.py \\
        SNAPDIR OUTDIR FIRST LAST STEP [COLUMNS ROWS]
    ./invenv.sh python research/experiments/EXP-0048/arcade/sheet.py \\
        SNAPDIR OUTDIR F1,F2,... [COLUMNS ROWS]

Takes the snapshots ``<set>_f<frame>.png`` in SNAPDIR with FIRST <= frame <
LAST and frame a multiple of STEP from FIRST, and tiles them (default 6 x 5,
full size, in frame order, left to right then top to bottom) into
``OUTDIR/sheet_<first frame>.png`` with ffmpeg. Each sheet's frame list is
printed, so a tile's frame is its position in that list. The second form
tiles exactly the listed frames, in the order given. Sheets are only for
finding scenes; every reading in `RESULTS.md` is made on the single snapshot.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

FRAME = re.compile(r"_f(\d+)\.png$")


def frames(snapdir: Path, first: int, last: int, step: int) -> list[tuple[int, Path]]:
    found = []
    for path in snapdir.glob("*_f*.png"):
        match = FRAME.search(path.name)
        if match:
            frame = int(match.group(1))
            if first <= frame < last and (frame - first) % step == 0:
                found.append((frame, path))
    return sorted(found)


def listed(snapdir: Path, wanted: list[int]) -> list[tuple[int, Path]]:
    found = {
        int(m.group(1)): p
        for p in snapdir.glob("*_f*.png")
        if (m := FRAME.search(p.name))
    }
    return [(f, found[f]) for f in wanted]


def sheets(
    selected: list[tuple[int, Path]], outdir: Path, cols: int, rows: int
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    per = cols * rows
    for start in range(0, len(selected), per):
        chunk = selected[start : start + per]
        out = outdir / f"sheet_{chunk[0][0]:05d}.png"
        with tempfile.TemporaryDirectory() as tmp:
            for i, (_, path) in enumerate(chunk):
                (Path(tmp) / f"{i:04d}.png").symlink_to(path.resolve())
            pattern = str(Path(tmp) / "%04d.png")
            tile = f"tile={cols}x{rows}"
            command = ["ffmpeg", "-loglevel", "error", "-y", "-i", pattern]
            command += ["-vf", tile, "-frames:v", "1", str(out)]
            subprocess.run(command, check=True)
        print(out, " ".join(str(f) for f, _ in chunk))


def main(argv: list[str]) -> int:
    snapdir, outdir = Path(argv[0]), Path(argv[1])
    if "," in argv[2]:
        selected = listed(snapdir, [int(v) for v in argv[2].split(",")])
        rest = argv[3:]
    else:
        first, last, step = (int(v) for v in argv[2:5])
        selected = frames(snapdir, first, last, step)
        rest = argv[5:]
    cols, rows = (int(v) for v in rest[:2]) if len(rest) >= 2 else (6, 5)
    sheets(selected, outdir, cols, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

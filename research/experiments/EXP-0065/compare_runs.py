r"""EXP-0065: which frames of two forced captures differ, pixel for pixel.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/compare_runs.py \
        OLD NEW [NEW ...]

OLD and each NEW hold ``f<frame>.png`` from `forced_capture.py`. For every
frame present in OLD and in one of the NEW folders, compares the decoded
pixels (through ffmpeg) and prints the differing frames as ranges, with the
number compared.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def pixels(path: Path) -> bytes:
    return subprocess.run(
        [
            *("ffmpeg", "-loglevel", "error", "-i", str(path)),
            *("-f", "rawvideo", "-pix_fmt", "rgb24", "-"),
        ],
        capture_output=True,
        check=True,
    ).stdout


def ranges(frames: list[int]) -> str:
    spans: list[list[int]] = []
    for f in frames:
        if spans and f - spans[-1][1] <= 4:
            spans[-1][1] = f
        else:
            spans.append([f, f])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in spans) or "none"


def main(old: Path, new: list[Path]) -> int:
    found = {p.name: p for folder in new for p in folder.glob("f*.png")}
    compared, differ = 0, []
    for path in sorted(old.glob("f*.png")):
        other = found.get(path.name)
        if other is None:
            continue
        compared += 1
        if pixels(path) != pixels(other):
            differ.append(int(path.stem[1:]))
    print(f"{compared} frames compared; differ: {ranges(differ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), [Path(a) for a in sys.argv[2:]]))

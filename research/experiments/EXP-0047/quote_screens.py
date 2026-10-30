"""EXP-0047: find the win-quote screens in a recorded play session.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0047/quote_screens.py SESSION OUT

A quote screen is found by its speech bubble's colour, as in `EXP-0032`: the
average of a 60 x 6 strip at x = 140, y = 222 within ``TOLERANCE`` of
(224, 160, 32). Consecutive matching screenshots (less than ``GAP`` frames
apart) are one quote. The middle screenshot of each is put in a contact
sheet, ``OUT/quotes.png`` (4 columns, full size), for the agent to read.
Also writes ``OUT/quotes.json``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

STRIP = (140, 222, 60, 6)
BUBBLE = (224, 160, 32)
TOLERANCE, GAP, COLUMNS = 24, 300, 4


def strip_colour(path: Path) -> tuple[float, float, float]:
    x, y, w, h = STRIP
    raw = subprocess.run(
        [
            *("ffmpeg", "-v", "error", "-i", str(path)),
            *("-vf", f"crop={w}:{h}:{x}:{y}", "-f", "rawvideo", "-pix_fmt", "rgb24"),
            "-",
        ],
        check=True,
        capture_output=True,
    ).stdout
    n = len(raw) // 3
    return (
        sum(raw[0::3]) / n,
        sum(raw[1::3]) / n,
        sum(raw[2::3]) / n,
    )


def main(session: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    shots = sorted((session / "shots").glob("f*.png"))
    groups: list[list[Path]] = []
    last = -GAP
    for shot in shots:
        colour = strip_colour(shot)
        if all(abs(c - b) <= TOLERANCE for c, b in zip(colour, BUBBLE, strict=True)):
            frame = int(shot.stem[1:])
            if frame - last >= GAP:
                groups.append([])
            groups[-1].append(shot)
            last = frame
    chosen = [group[len(group) // 2] for group in groups]
    (out / "quotes.json").write_text(
        json.dumps([[p.stem for p in g] for g in groups], indent=1) + "\n"
    )
    print(len(chosen), [p.stem for p in chosen])
    if not chosen:
        return 0
    inputs: list[str] = []
    for path in chosen:
        inputs += ["-i", str(path)]
    layout = "|".join(
        f"{(i % COLUMNS) * 352}_{(i // COLUMNS) * 240}" for i in range(len(chosen))
    )
    tiles = "".join(f"[{i}:v]scale=352:240[v{i}];" for i in range(len(chosen)))
    tiles += "".join(f"[v{i}]" for i in range(len(chosen)))
    stack = f"xstack=inputs={len(chosen)}:layout={layout}:fill=black"
    subprocess.run(
        [
            *("ffmpeg", "-v", "error", "-y", *inputs),
            *("-filter_complex", tiles + stack, str(out / "quotes.png")),
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

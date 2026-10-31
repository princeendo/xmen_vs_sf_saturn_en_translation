r"""EXP-0061: check the boxes of `run_boxes.py`'s runs against the built layout.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0061/check_boxes.py RUNS OUT

For each run in RUNS whose load check passed (the last attempt per slot),
the last three quote-pointer changes inside ``MC08.SHP`` (WRAM-H
``0x060C1000`` to ``0x060D01F7``) are the boxes. Earlier changes in that
range are the partner's ordinary win quotes, from the second team buffer
that the same WRAM-H area holds before the boss stage; they are listed as
``earlier``. Each must equal the record
`tools.disc.boss_boxes` puts there: ``MC08`` + ``BASE`` + 100 x (the slot's
first index + box). For each box the last screenshot before the next
pointer change, and at most ``SHOWN`` frames after its own, is cropped to
the box (the top ``CROP`` rows), and the three crops are stacked into
``OUT/s<slot>.png`` for the agent to read, with ffmpeg. ``OUT/boxes.json``
lists every pointer, frame and screenshot.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.boss_boxes import BASE, MC08, RECORD, first_index

MC08_END = 0x060D01F8
CROP = 70
SHOWN = 120  # a box is on screen about 120-140 frames


def main(runs: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    index = first_index()
    report, problems = [], 0
    latest: dict[int, Path] = {}
    for run in sorted(runs.glob("s*_a*")):
        path = run / "result.json"
        if path.is_file() and all(json.loads(path.read_text())["load_check"].values()):
            latest[int(run.name[1:3])] = run
    for slot, run in sorted(latest.items()):
        changes = json.loads((run / "result.json").read_text())["pointer_changes"]
        frames = [f for f, _ in changes] + [10**9]
        inside = [
            (frame, int(p, 16), frames[i + 1])
            for i, (frame, p) in enumerate(changes)
            if MC08 <= int(p, 16) < MC08_END
        ]
        earlier, boxes = inside[:-3], inside[-3:]
        expected = [MC08 + BASE + RECORD * (index[slot] + n) for n in range(3)]
        crops = []
        for frame, _, until in boxes:
            shots = sorted(
                s
                for s in (run / "shots").glob("r*.png")
                if frame < int(s.stem[1:]) < min(until, frame + SHOWN)
            )
            crops.append(str(shots[-1]) if shots else None)
        ok = [p for _, p, _ in boxes] == expected
        problems += not ok or None in crops
        report.append(
            {
                "slot": slot,
                "run": run.name,
                "pointers": [f"{p:#010x}" for _, p, _ in boxes],
                "expected": [f"{p:#010x}" for p in expected],
                "frames": [f for f, _, _ in boxes],
                "earlier": [[f, f"{p:#010x}"] for f, p, _ in earlier],
                "shots": crops,
                "match": ok,
            }
        )
        print(slot, run.name, "match" if ok else "MISMATCH", [f for f, _, _ in boxes])
        if crops and None not in crops:
            inputs = [arg for c in crops for arg in ("-i", c)]
            chain = "".join(
                f"[{i}]crop=352:{CROP}:0:0[c{i}];" for i in range(len(crops))
            )
            stack = "".join(f"[c{i}]" for i in range(len(crops)))
            subprocess.run(
                [
                    *("ffmpeg", "-loglevel", "error", "-y", *inputs),
                    "-filter_complex",
                    f"{chain}{stack}vstack={len(crops)}",
                    str(out / f"s{slot:02d}.png"),
                ],
                check=True,
            )
    (out / "boxes.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"{len(report)} slots, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

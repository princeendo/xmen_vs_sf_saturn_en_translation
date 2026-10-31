r"""EXP-0061: route every roster slot to Apocalypse's boxes on a built image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0061/run_boxes.py \
        CUE MMPACK OUT [SLOT ...]

Adapted from `EXP-0047/run_endings.py` (same scheduler). For each slot (the
17 roster slots 0-7 and 9-17, or the SLOTs given), one `tools.mednafen.route`
run: the slot picked first and the second cursor's start cell second
(Cyclops, or Wolverine when Cyclops is first), policy ``first``, the
build's ``MMPACK.PCA`` written into RAM (``--mmpack``; ``MC08.SHP`` is read
from CUE's disc at the boss stage), ``FRAMES`` frames (the post-boss quote
came near frame 11,100-11,760 in `EXP-0051`'s runs), and a screenshot every
``SHOT_EVERY`` frames, so that each box (about 130 frames) is caught with
its text complete. A run whose load check fails stops there
(``--stop-on-bad-load``) and is started again, up to ``ATTEMPTS`` times. Up
to ``PARALLEL`` runs go at once, staggered so that no two pick phases
overlap. Writes ``OUT/runs.json``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.route import SECOND_START, WOLVERINE

SLOTS = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17]
FRAMES, SHOT_EVERY = 11000, 40
PARALLEL, STAGGER, ATTEMPTS = 4, 75.0, 3


def command(cue: Path, mmpack: Path, out: Path, slot: int) -> list[str]:
    second = WOLVERINE if slot == SECOND_START else SECOND_START
    return [
        *(sys.executable, "-m", "tools.mednafen.route", str(cue), str(out)),
        *("--first", str(slot), "--second", str(second), "--policy", "first"),
        *("--mmpack", str(mmpack), "--frames", str(FRAMES)),
        *("--shot-every", str(SHOT_EVERY), "--stop-on-bad-load"),
    ]


def main(cue: Path, mmpack: Path, out: Path, chosen: list[int]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    queue = [(slot, 1) for slot in (chosen or SLOTS)]
    running: list[tuple[subprocess.Popen[bytes], int, int, Path]] = []
    runs: list[dict[str, object]] = []
    last_start = 0.0
    env = {**os.environ, "MEDNAFEN_ALLOWMULTI": "1"}
    while queue or running:
        if (
            queue
            and len(running) < PARALLEL
            and time.monotonic() - last_start > STAGGER
        ):
            slot, attempt = queue.pop(0)
            target = out / f"s{slot:02d}_a{attempt}"
            log = (out / f"{target.name}.log").open("wb")
            process = subprocess.Popen(
                command(cue, mmpack, target, slot), stdout=log, stderr=log, env=env
            )
            running.append((process, slot, attempt, target))
            last_start = time.monotonic()
            print(f"started {target.name}", flush=True)
        for entry in list(running):
            process, slot, attempt, target = entry
            if process.poll() is None:
                continue
            running.remove(entry)
            result_path = target / "result.json"
            check = (
                json.loads(result_path.read_text())["load_check"]
                if result_path.exists()
                else None
            )
            ok = bool(check and check["first"] and check["second"])
            runs.append(
                {
                    "run": target.name,
                    "slot": slot,
                    "exit": process.returncode,
                    "load_check": check,
                }
            )
            print(f"finished {target.name} load ok={ok}", flush=True)
            if not ok and attempt < ATTEMPTS:
                queue.append((slot, attempt + 1))
        time.sleep(2)
    (out / "runs.json").write_text(json.dumps(runs, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            Path(sys.argv[3]),
            [int(s) for s in sys.argv[4:]],
        )
    )

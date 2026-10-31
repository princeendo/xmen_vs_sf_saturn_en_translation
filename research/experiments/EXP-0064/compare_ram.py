r"""EXP-0064: compare an offline-decoded block with RAM as the game decodes it.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0064/compare_ram.py \
        CUE STATE OUT BLOCK ADDRESS STEP COUNT [START]

BLOCK is a decoded block (a file written by the offline decoder) and ADDRESS
(hex) where the game writes it in work RAM. STATE is loaded into a silent
Mednafen on CUE; then COUNT times it advances STEP frames, halts, reads that
RAM range over the bus and reports how many leading bytes equal BLOCK and how
many bytes differ in all, with a screenshot ``OUT/f<frame>.png``. STATE ``-``
cold-boots CUE instead (no input); START frames are run first (default 0).
``OUT/steps.json`` lists every step; the RAM at the
first fully equal step, if any, is saved as ``OUT/equal.bin``, and the last
step's as ``OUT/last.bin``. OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home


def main(
    cue: Path,
    state: Path,
    out: Path,
    block: Path,
    address: int,
    step: int,
    count: int,
    start: int = 0,
) -> int:
    want = block.read_bytes()
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = out / "agent"
    agent_dir.mkdir()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(quiet_home().resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
        MEDNAFEN_ALLOWMULTI="1",
    )
    steps: list[dict[str, object]] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            if str(state) != "-":
                agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            if start:
                agent.frames(start)
                agent.wait_halted(max(60.0, start / 30))
            for n in range(count):
                agent.frames(step)
                agent.wait_halted(60.0)
                ram = agent.bus_read(address, len(want))
                prefix = next(
                    (
                        i
                        for i, (a, b) in enumerate(zip(ram, want, strict=True))
                        if a != b
                    ),
                    len(want),
                )
                differ = sum(a != b for a, b in zip(ram, want, strict=True))
                frame = int(agent.status()["frame"])
                agent.screenshot(out / f"f{frame:08d}.png")
                record: dict[str, object] = {
                    "step": n,
                    "frame": frame,
                    "equal_prefix": prefix,
                    "differing_bytes": differ,
                }
                steps.append(record)
                print(json.dumps(record), flush=True)
                if differ == 0:
                    (out / "equal.bin").write_bytes(ram)
                    break
        finally:
            proc.terminate()
            proc.wait(10)
        (out / "last.bin").write_bytes(ram)
    (out / "steps.json").write_text(json.dumps(steps, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            Path(a[3]),
            int(a[4], 16),
            int(a[5]),
            int(a[6]),
            int(a[7]) if len(a) > 7 else 0,
        )
    )

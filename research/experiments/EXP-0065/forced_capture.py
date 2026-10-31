r"""EXP-0065: screenshots of one attract file's opening, the file forced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/forced_capture.py \
        CUE STATE OUT FILE FIRST LAST STEP

Loads STATE into a silent Mednafen on CUE, forces attract file FILE (0-7) as
`snapshots.py` does, then saves ``OUT/f<frame>.png`` at frames FIRST, FIRST +
STEP, ... LAST (counted from the load). OUT is an ignored path.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home

PICK, PICK_OLD = 0x06021736, bytes.fromhex("0003")


def main(
    cue: Path, state: Path, out: Path, file: int, first: int, last: int, step: int
) -> int:
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
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            if agent.bus_read(PICK, 2) != PICK_OLD:
                raise SystemExit("the file pick is not where expected")
            agent.bus_write(PICK, bytes([0xE0, file]))
            frame = int(agent.status()["frame"])
            for target in range(first, last + 1, step):
                agent.frames(target - frame)
                agent.wait_halted(max(60.0, (target - frame) / 30))
                frame = int(agent.status()["frame"])
                agent.screenshot(out / f"f{target:05d}.png")
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), *(int(x) for x in a[3:7]))
    )

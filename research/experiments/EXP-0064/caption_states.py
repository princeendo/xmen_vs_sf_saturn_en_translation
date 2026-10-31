r"""EXP-0064: cold-boot silently and save a state and a screenshot at chosen frames.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0064/caption_states.py \
        CUE OUT FRAME [FRAME ...]

`tools.mednafen.frame_capture`'s loop (silent home, no input, the agent
interface), with its own agent directory ``OUT/agent`` so that it can run
beside another capture. At each FRAME it resumes, saves ``OUT/t<FRAME>.mcs``
(the agent refuses a save while halted, so the state is a frame or so after
FRAME), halts again and saves ``OUT/t<FRAME>_f<halted frame>.png``. States
are checkpoints for `EXP-0049/dump_screen.py`, not RAM evidence themselves.
OUT is an ignored path.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home


def main(cue: Path, out: Path, targets: list[int]) -> int:
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
            agent.pause()
            agent.wait_halted()
            frame = int(agent.status()["frame"])
            for target in sorted(targets):
                agent.frames(target - frame)
                agent.wait_halted(max(60.0, (target - frame) / 30))
                # A state cannot be saved while halted: run, save, halt again.
                agent.run()
                agent.savestate(out / f"t{target:08d}.mcs")
                agent.pause()
                agent.wait_halted()
                frame = int(agent.status()["frame"])
                agent.screenshot(out / f"t{target:08d}_f{frame:08d}.png")
                print(f"target {target} saved, halted at {frame}", flush=True)
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), [int(a) for a in sys.argv[3:]])
    )

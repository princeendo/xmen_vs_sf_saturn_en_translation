"""EXP-0015: controlled change to identify the win-quote renderer.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0015/renderer_test.py OUT

From the `quote_visible` checkpoint (`EXP-0014`), paused, the trial writes 128
zero bytes over one VDP1 VRAM glyph cell (0x4A800, line 1's first glyph); the
control does the same steps without the write. Both then run 2 frames and take
a screenshot. Outputs go to the ignored OUT.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/dbg003/f00010336.mcs")
CELL, CELL_BYTES = 0x4A800, 128


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.status()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            time.sleep(3)
            for run in ("control", "trial"):
                agent.loadstate(STATE.resolve())
                agent.pause()
                before = agent.read("vdp1vram", CELL, CELL_BYTES)
                (out / f"{run}-cell-before.bin").write_bytes(before)
                if run == "trial":
                    agent.write("vdp1vram", CELL, bytes(CELL_BYTES))
                after = agent.read("vdp1vram", CELL, CELL_BYTES)
                (out / f"{run}-cell-after.bin").write_bytes(after)
                agent.frames(2)
                agent.wait_halted(30.0)
                agent.screenshot((out / f"{run}.png").resolve())
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    print(f"done {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

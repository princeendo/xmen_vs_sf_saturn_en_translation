"""EXP-0038: dump work RAM at a checkpoint (optionally after some frames).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/dump_ram.py OUT STATE [FRAMES]

Loads STATE on the untouched image with no input, pauses, runs FRAMES frames
(default 0), and writes ``wram-l.bin`` (``0x00200000``, 1 MiB) and
``wram-h.bin`` (``0x06000000``, 1 MiB) through the agent's bus reads (the
debugger path, not the save-state extractor). Outputs go to the ignored OUT.
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
REGIONS = {"wram-l.bin": 0x00200000, "wram-h.bin": 0x06000000}
SIZE, CHUNK = 0x100000, 0x10000


def main(out: Path, state: Path, frames: int) -> int:
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
            agent.loadstate(state.resolve())
            agent.pause()
            if frames:
                agent.frames(frames)
                agent.wait_halted(300.0)
            for name, base in REGIONS.items():
                data = b"".join(
                    agent.bus_read(base + offset, CHUNK)
                    for offset in range(0, SIZE, CHUNK)
                )
                (out / name).write_bytes(data)
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    return 0


if __name__ == "__main__":
    frames = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), frames))

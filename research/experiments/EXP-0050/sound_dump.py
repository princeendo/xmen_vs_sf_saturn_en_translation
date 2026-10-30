r"""EXP-0050: step from a save state and dump sound RAM, work RAM and a state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/sound_dump.py \
        CUE OUT STATE STEP [STEP ...]

Steps as in ``voice_record.py`` (``wait:N``, ``keys:MOVES``, ``shot:NAME``),
plus ``dump:NAME``, which writes to ``OUT/NAME/``:

- ``scspram.bin`` (SCSP sound RAM, 512 KiB);
- ``wram_l.bin`` and ``wram_h.bin`` (live agent reads while paused);
- ``state.mcs``, a save state taken there (the agent saves while running,
  so the state is a few frames later than the reads). The cart RAM is
  extracted from it with ``tools.memory.mcs_extract`` (unvalidated region:
  search only).

Mednafen runs in the route's pick home (silent). Outputs go to the ignored
OUT.
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
from tools.mednafen.route import BINARY, pick_home, send

SETTLE = 30
WRAM_L, WRAM_H, WRAM_SIZE = 0x00200000, 0x06000000, 0x100000


def main(cue: Path, out: Path, state: Path, steps: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=30.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.status()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            time.sleep(2)
            agent.loadstate(state.resolve())
            agent.pause()
            for step in steps:
                kind, _, value = step.partition(":")
                if kind == "wait":
                    agent.frames(int(value))
                    agent.wait_halted(120.0)
                elif kind == "keys":
                    agent.run()
                    send(process.pid, value)
                    agent.pause()
                    agent.frames(SETTLE)
                    agent.wait_halted(60.0)
                elif kind == "shot":
                    agent.screenshot((out / f"{value}.png").resolve())
                elif kind == "dump":
                    target = out / value
                    target.mkdir()
                    (target / "scspram.bin").write_bytes(
                        agent.read("scspram", 0, 0x80000)
                    )
                    (target / "wram_l.bin").write_bytes(
                        agent.bus_read(WRAM_L, WRAM_SIZE)
                    )
                    (target / "wram_h.bin").write_bytes(
                        agent.bus_read(WRAM_H, WRAM_SIZE)
                    )
                    agent.run()
                    agent.savestate((target / "state.mcs").resolve())
                    agent.pause()
                else:
                    raise ValueError(f"unknown step {step}")
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4:])
    )

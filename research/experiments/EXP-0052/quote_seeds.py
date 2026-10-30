r"""EXP-0052: force a fight's win-quote draw by its random seed, on a built image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0052/quote_seeds.py \
        CUE OUT STATE TABLE_RAM FRAMES SEED [SEED ...]

STATE is a save state made on CUE itself (`EXP-0051` ``cold_walk.py``
``save:``), early in a fight, so the code and files in RAM are the build's
own and nothing but game state is written. For each SEED, from STATE:

- the game is paused at the state's own seed value (``SEED_WORD``; the
  state is reloaded until it is, so every run starts at the same moment);
- the CPU side's vitality words are set to 0 (`tools.mednafen.route.CPU`,
  + 0x10), so the fight ends with no play, and the seed word is set to SEED
  (the method of `EXP-0024`'s ``seed_scan.py``);
- FRAMES frames are run, then a screenshot ``OUT/s<SEED>.png`` is taken,
  and the quote pointer (``POINTER``) is read.

``OUT/result.json`` gives, per seed, the pointer, the English record it
points at ((pointer - TABLE_RAM) / 100, the winner's quote table in the
first buffer), and that record decoded. OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.mednafen.route import BINARY, CPU
from tools.text.caption import CaptionError, decode_record

SEED_WORD, POINTER, VITALITY, RECORD = 0x060F545A, 0x060F2490, 0x10, 100


def main(
    cue: Path, out: Path, state: Path, table_ram: int, frames: int, seeds: list[int]
) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    result: dict[str, object] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            start_seed = None
            for seed in seeds:
                for _ in range(20):
                    agent.loadstate(state.resolve())
                    agent.pause()
                    found = int.from_bytes(agent.bus_read(SEED_WORD, 2), "big")
                    if start_seed is None:
                        start_seed = found
                    if found == start_seed:
                        break
                    agent.run()
                else:
                    raise RuntimeError(f"never paused at seed {start_seed}")
                for block in CPU:
                    agent.bus_write(block + VITALITY, bytes(2))
                agent.bus_write(SEED_WORD, seed.to_bytes(2, "big"))
                agent.frames(frames)
                agent.wait_halted(120.0)
                agent.screenshot((out / f"s{seed}.png").resolve())
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                shown = agent.bus_read(pointer, RECORD)
                try:
                    lines: list[str] | None = decode_record(shown)
                except CaptionError:
                    lines = None
                index, extra = divmod(pointer - table_ram, RECORD)
                result[str(seed)] = {
                    "pointer": f"{pointer:#010x}",
                    "english_record": index if extra == 0 and 0 <= index < 8 else None,
                    "lines": lines,
                }
                agent.run()
            result["state_seed"] = start_seed
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    a = sys.argv
    raise SystemExit(
        main(
            Path(a[1]),
            Path(a[2]),
            Path(a[3]),
            int(a[4], 16),
            int(a[5]),
            [int(s) for s in a[6:]],
        )
    )

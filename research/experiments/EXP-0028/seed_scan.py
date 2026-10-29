"""EXP-0028: find RNG seeds at a `pre_ko` state that make the quote draw each value.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0028/seed_scan.py CASE OUT SEED...

Copied from `research/experiments/EXP-0024/seed_scan.py` (this repository,
commit ``7b02ab1``); the state, its paused seed and the frames to the quote
are now chosen by CASE (``ryu``: `EXP-0013` `pre_ko`, seed 8520, 660 frames;
``ken``: `EXP-0025` `pre_ko`, seed 9501, 700 frames; `EXP-0027`). The rest of
the method is unchanged:

A debugger write right after the draw's store does not reach the selector's
read two instructions later (the read hits the SH-2 data cache; `EXP-0024`).
So the draw is steered earlier instead. At `pre_ko`, paused at a fixed RNG
position (see below), the run writes SEED to the RNG seed word (WRAM-H
``0x060F545A``, `EXP-0021`). It then runs the unpatched game to the quote
screen and reads the draw from the index byte (task + 38, ``0x060F8AE6``;
unpatched, index = draw). It also saves a screenshot. Outputs go to the
ignored OUT, with ``result.json`` mapping each seed to its draw.
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

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
SEED, INDEX = 0x060F545A, 0x060F8AE6
# case -> (pre_ko state, seed word when paused right after loading, frames)
CASES = {
    "ryu": (Path("local/checkpoints/dbg003/f00009769.mcs"), 8520, 660),
    "ken": (Path("local/checkpoints/re004/f00007684.mcs"), 9501, 700),
}


def main(case: str, out: Path, seeds: list[int]) -> int:
    STATE, STATE_SEED, TO_QUOTE = CASES[case]
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {}
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
            for seed in seeds:
                # ``pause`` takes effect a moment after ``loadstate``, so 0 or 1
                # frames may pass. Reload until the paused machine shows the
                # same seed, so every run starts from the same RNG position.
                for _ in range(20):
                    agent.loadstate(STATE.resolve())
                    agent.pause()
                    original = int.from_bytes(agent.bus_read(SEED, 2), "big")
                    if original == STATE_SEED:
                        break
                    agent.run()
                else:
                    raise RuntimeError(f"never paused at seed {STATE_SEED}")
                agent.bus_write(SEED, seed.to_bytes(2, "big"))
                agent.frames(TO_QUOTE)
                agent.wait_halted(60.0)
                agent.screenshot((out / f"seed{seed}.png").resolve())
                result[str(seed)] = {
                    "original_seed": original,
                    "draw": agent.bus_read(INDEX, 1)[0],
                }
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(sys.argv[1], Path(sys.argv[2]), [int(s, 0) for s in sys.argv[3:]])
    )

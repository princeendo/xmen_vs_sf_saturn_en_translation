"""EXP-0014: make the after-quote checkpoint and check every checkpoint reloads.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0014/checkpoints.py OUT

Launches the patched build in the silent home. For each named checkpoint in
``local/checkpoints/dbg003/`` it loads the state, takes a screenshot at once
(the state's own screen), and records the SHA-256 of the state. Then, from the
quote-visible state, it runs ``AFTER_FRAMES`` frames and saves the
after-quote state and screenshot, and reloads that new state to show it is
reproducible. Outputs go to the ignored OUT; states are copied to
``local/checkpoints/dbg003/`` by hand after review.
"""

from __future__ import annotations

import hashlib
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
CHECKPOINTS = Path("local/checkpoints/dbg003")
NAMED = {
    "pre_ko": "f00009769.mcs",
    "after_ko": "f00009874.mcs",
    "win_banner": "f00009975.mcs",
    "pre_quote": "f00010285.mcs",
    "quote_visible": "f00010336.mcs",
}
AFTER_FRAMES = 480  # from quote_visible; EXP-0013 replays reached the stage card


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def connect(agent: Agent, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            agent.status()
            return
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def main(out: Path) -> int:
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
            connect(agent)
            time.sleep(3)
            for name, file in NAMED.items():
                state = (CHECKPOINTS / file).resolve()
                agent.loadstate(state)
                agent.screenshot((out / f"{name}.png").resolve())
                result[name] = {"state": file, "sha256": sha256(state)}
            agent.loadstate((CHECKPOINTS / NAMED["quote_visible"]).resolve())
            agent.frames(AFTER_FRAMES)
            agent.wait_halted(60.0)
            after = (out / "after_quote.mcs").resolve()
            # `savestate` is refused while halted, even after `run` in the same
            # command file; run first, save in the next exchange.
            agent.run()
            agent.savestate(after)
            agent.screenshot((out / "after_quote.png").resolve())
            agent.loadstate(after)
            agent.screenshot((out / "after_quote_reload.png").resolve())
            result["after_quote"] = {
                "state": "after_quote.mcs",
                "from": NAMED["quote_visible"],
                "frames": AFTER_FRAMES,
                "sha256": sha256(after),
            }
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

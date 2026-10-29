"""EXP-0018: log writes to the quote-table range during a cold boot.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0018/boot_trace.py CUE OUT [SECONDS]

Cold-boots CUE in the patched build (silent home, no input) with a log-mode
write breakpoint on WRAM-L ``0x0024F5D8``-``0x0024FC5F`` (and its mirror), runs
SECONDS (default 60) of emulated time, and saves the hit events, then a
screenshot. Tells whether the boot and attract sequence load data into the
buffer that holds Ryu's quote table (`EXP-0017`). Outputs go to the ignored OUT.
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
TABLE = ("0024F5D8-0024FC5F", "2024F5D8-2024FC5F")
FPS = 60


def main(cue: Path, out: Path, seconds: int) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"cue": str(cue), "seconds": seconds}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.pause()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.2)
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("write", TABLE)
            result["start"] = agent.status()
            agent.frames(seconds * FPS)
            result["end"] = agent.wait_halted(seconds * 2.0)
            events = agent.events()
            result["hits"] = len(events)
            result["first_events"] = events[:3]
            (out / "events.log").write_text("\n".join(events) + "\n")
            agent.screenshot((out / "end.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
            (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps({k: v for k, v in result.items() if k != "first_events"}, indent=1)
    )
    return 0


if __name__ == "__main__":
    seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), seconds))

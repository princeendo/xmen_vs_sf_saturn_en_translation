"""EXP-0019: log writes to bus ranges during a cold boot, and read RAM after.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0019/load_trace.py CUE OUT \
        --seconds 60 --bp 002C3EA0-002C3EAF [--read 002C3EA0:209285]

Cold-boots CUE in the patched build (silent home, no input) with a log-mode
write breakpoint on each ``--bp`` range, runs ``--seconds`` of emulated time,
and saves the hit events. Each ``--read ADDRESS:LENGTH`` is then saved as
``read-ADDRESS.bin``, followed by a screenshot. Adapted from
`EXP-0018`'s ``boot_trace.py``. Outputs go to the ignored OUT.
"""

from __future__ import annotations

import argparse
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
FPS = 60


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--bp", action="append", default=[], help="HEX-HEX")
    parser.add_argument("--read", action="append", default=[], help="HEX:LENGTH")
    args = parser.parse_args(argv)
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"cue": str(args.cue), "bp": args.bp}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            if args.bp:
                agent.breakpoints("write", args.bp)
            agent.frames(args.seconds * FPS)
            result["end"] = agent.wait_halted(args.seconds * 2.0)
            events = agent.events()
            result["hits"] = len(events)
            (out / "events.log").write_text("\n".join(events) + "\n")
            for item in args.read:
                address, length = item.split(":")
                data = agent.bus_read(int(address, 16), int(length))
                (out / f"read-{address.upper()}.bin").write_bytes(data)
            agent.screenshot((out / "end.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
            (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

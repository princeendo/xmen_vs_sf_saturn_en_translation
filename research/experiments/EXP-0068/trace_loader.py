r"""EXP-0068: who calls the file loader when a fighter's file loads.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0068/trace_loader.py \
        CUE STATE OUT KEYS [FRAMES [PC]]

Loads STATE in Mednafen on CUE (the route's pick home, so KEYS can be
sent: `tools.mednafen.route.send`), sets a log-mode PC breakpoint on the
loader's sector-read entry ``LOADER`` (`EXP-0017`: ``0x0600D09C``, called
with the file size in R5 and the destination list at ``DESTINATIONS``),
or on PC (hex) if given (``0x0600D056``, the function that calls it),
sends KEYS, runs FRAMES frames (default ``FRAMES``) and records every hit's
frame, PR, R4-R7 and R15. (A halting breakpoint was tried first: the halt
did not hold while the keys were sent.) Writes ``OUT/result.json``. OUT is
an ignored path.
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
from tools.mednafen.route import BINARY, parse_hit, pick_home, send

LOADER, DESTINATIONS, FRAMES = 0x0600D09C, 0x0600D168, 900
FIELDS = ("frame", "PC", "PR", "R4", "R5", "R6", "R7", "R15")


def main(
    cue: Path, state: Path, out: Path, keys: str, frames: int, pc: int = LOADER
) -> int:
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(pick_home().resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    found: list[dict[str, str | None]] = []
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
            agent.loadstate(state.resolve())
            agent.bpmode("log")
            agent.clear_events()
            agent.breakpoints("pc", (f"{pc:08X}",))
            time.sleep(0.5)
            send(process.pid, keys)
            agent.pause()
            agent.frames(frames)
            agent.wait_halted(120.0)
            for line in agent.events():
                if line.startswith("hit"):
                    hit = parse_hit(line)
                    found.append({k: hit.get(k) for k in FIELDS})
            agent.breakpoints("pc", ())
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(found, indent=1) + "\n")
    for row in found:
        print(" ".join(f"{k}={row[k]}" for k in FIELDS))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            a[3],
            int(a[4]) if len(a) > 4 else FRAMES,
            int(a[5], 16) if len(a) > 5 else LOADER,
        )
    )

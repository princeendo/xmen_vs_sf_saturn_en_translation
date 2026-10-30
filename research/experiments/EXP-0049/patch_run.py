r"""EXP-0049: a control run and a patched run from one save state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/patch_run.py \
        CUE OUT STATE FRAMES ADDRESS:OLD:NEW [ADDRESS:OLD:NEW ...]

Each patch writes the bytes NEW (hex) at the work-RAM bus ADDRESS (hex),
after checking that RAM holds OLD there. An item ``keys:MOVES`` instead
sends those keys after the patches (`tools.mednafen.route.KEYS`, Mednafen
in front, the route's pick home), in both runs. Two runs from STATE in a silent
Mednafen on CUE, each FRAMES frames and then a screenshot:

- ``control.png``: no change;
- ``patched.png``: every patch written first.

``OUT/changes.json`` lists the patches (AGENTS.md rule 12) and whether
each still held at the end of the patched run.
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
from tools.mednafen.route import BINARY, pick_home, send


def parse(text: str) -> tuple[int, bytes, bytes]:
    address, old, new = text.split(":")
    before, after = bytes.fromhex(old), bytes.fromhex(new)
    if len(before) != len(after):
        raise ValueError(f"{text}: OLD and NEW differ in length")
    return int(address, 16), before, after


def main(cue: Path, out: Path, state: Path, frames: int, specs: list[str]) -> int:
    patches = [parse(s) for s in specs if not s.startswith("keys:")]
    keys = [s[5:] for s in specs if s.startswith("keys:")]
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str((pick_home() if keys else QUIET_HOME).resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    held: list[bool] = []
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
            time.sleep(3)
            for name in ("control", "patched"):
                agent.loadstate(state.resolve())
                agent.pause()
                if name == "patched":
                    for address, old, new in patches:
                        found = agent.bus_read(address, len(old))
                        if found != old:
                            raise RuntimeError(f"{address:#x}: found {found.hex()}")
                        agent.bus_write(address, new)
                for moves in keys:
                    agent.run()
                    send(process.pid, moves)
                    agent.pause()
                agent.frames(frames)
                agent.wait_halted(120.0)
                agent.screenshot((out / f"{name}.png").resolve())
                if name == "patched":
                    held = [
                        agent.bus_read(address, len(new)) == new
                        for address, _, new in patches
                    ]
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    record = [
        {
            "ram_address": f"{address:#010x}",
            "original": old.hex(),
            "modified": new.hex(),
            "held_to_end": ok,
        }
        for (address, old, new), ok in zip(patches, held, strict=True)
    ]
    (out / "changes.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    a = sys.argv
    raise SystemExit(main(Path(a[1]), Path(a[2]), Path(a[3]), int(a[4]), a[5:]))

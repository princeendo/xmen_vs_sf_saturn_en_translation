r"""EXP-0047: read the quote pointer and fighter blocks from session states.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0047/state_reads.py \
        CUE OUT STATE [STATE ...]

Each STATE (a save state recorded in the play session) is loaded into a
silent Mednafen on CUE and paused. Recorded per state:

- the quote pointer ``0x060F2490`` and which buffer it points into;
- the four fighter blocks' characters (+ ``0x23``, slot x 2; `EXP-0045`);
- whether each team buffer equals CUE's MC file of the character in it
  (decoded, plus fix-ups), for the characters in the player's blocks.

Writes ``OUT/result.json``. Outputs go to the ignored OUT.
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
from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.mednafen.route import (
    BINARY,
    BLOCKS,
    CHAR,
    FIRST_BUFFER,
    POINTER,
    SECOND_BUFFER,
    fixups_match,
    track_file,
)

ROSTER = Path("data/text/m5_roster.json")


def main(cue: Path, out: Path, states: list[Path]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    track = cue.parent / f"{cue.stem} (Track 01).bin"
    files = {
        m["slot"]: decompress_file(track_file(track, m["mc_file"]))[0]
        for m in json.loads(ROSTER.read_text())["roster"]
    }
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
            for state in states:
                agent.loadstate(state.resolve())
                agent.pause()
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                chars = {b: agent.bus_read(b + CHAR, 1)[0] // 2 for b in BLOCKS}
                buffers = {}
                for name, base in (("first", FIRST_BUFFER), ("second", SECOND_BUFFER)):
                    holds = [
                        slot
                        for slot, data in files.items()
                        if fixups_match(
                            data, agent.bus_read(base, len(data)), base + 0x40
                        )
                    ]
                    buffers[name] = holds
                result[state.name] = {
                    "pointer": f"{pointer:#010x}",
                    "pointer_in": (
                        "first buffer"
                        if FIRST_BUFFER <= pointer < FIRST_BUFFER + 0x11000
                        else "second buffer"
                        if SECOND_BUFFER <= pointer < SECOND_BUFFER + 0x11000
                        else "elsewhere"
                    ),
                    "chars": {f"{b:#010x}": c for b, c in chars.items()},
                    "buffers_hold": buffers,
                }
                agent.screenshot((out / f"{state.stem}.png").resolve())
                print(state.name, json.dumps(result[state.name]), flush=True)
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]])
    )

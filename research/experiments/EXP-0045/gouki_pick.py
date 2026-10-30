"""EXP-0045: try cursor moves to Gouki's cell from a state where it is shown.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0045/gouki_pick.py OUT MOVES [MOVES ...]

``local/re004/session/states/f00009348.mcs`` (`EXP-0025`) shows Gouki's cell
above the grid, with the cursor on Cyclops. For each MOVES string the state
is reloaded, the moves are sent, and a screenshot is taken. Then A is
pressed, and after a short wait the first member's buffer is compared with
``MC0F.SHP`` (Gouki) plus fix-ups (`tools.mednafen.route.fixups_match`).
Untouched image. Outputs go to the ignored OUT.
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
from tools.mednafen.route import (
    BINARY,
    FIRST_BUFFER,
    SOURCE_TRACK,
    fixups_match,
    pick_home,
    send,
    track_file,
)

STATE = Path("local/re004/session/states/f00009348.mcs")
CUE = SOURCE_TRACK.parent / "X-Men vs. Street Fighter (Japan) (3M).cue"


def main(out: Path, moves_list: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    gouki, _ = decompress_file(track_file(SOURCE_TRACK, "MC0F.SHP;1"))
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(CUE)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            for moves in moves_list:
                agent.loadstate(STATE.resolve())
                time.sleep(0.5)
                send(process.pid, moves)
                agent.screenshot((out / f"{moves}-cursor.png").resolve())
                send(process.pid, "a")
                time.sleep(4)
                agent.pause()
                ram = agent.bus_read(FIRST_BUFFER, len(gouki))
                agent.screenshot((out / f"{moves}-after.png").resolve())
                result[moves] = fixups_match(gouki, ram, FIRST_BUFFER + 0x40)
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))

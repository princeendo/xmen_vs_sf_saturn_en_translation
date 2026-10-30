r"""EXP-0046: pick from the select state with given cursor moves, then dump.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/gouki_cell.py \
        CUE OUT FIRST SECOND FIRST_SLOT SECOND_SLOT

FIRST and SECOND are cursor move strings (u, d, l, r) sent before each A
press, from the route's select state (`tools.mednafen.route.STATE`). A
screenshot is taken before each A press. Both buffers are saved to OUT, as
`tools.mednafen.route.run` does, for `identify_buffers.py`. Written to test
whether Gouki's cell (seen above Juggernaut's, `EXP-0046`) can be picked
from the ordinary select state. FIRST_SLOT and SECOND_SLOT are the intended
characters, written to ``result.json`` for `identify_buffers.py`.
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
from tools.mednafen.route import (
    BINARY,
    BUFFER_DUMP,
    FIRST_BUFFER,
    PRESS_GAP,
    SECOND_BUFFER,
    STATE,
    pick_home,
    send,
)


def main(cue: Path, out: Path, first: str, second: str, slots: list[int]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
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
            agent.loadstate(STATE.resolve())
            time.sleep(0.5)
            send(process.pid, first)
            agent.screenshot((out / "first_cursor.png").resolve())
            send(process.pid, "a")
            time.sleep(PRESS_GAP * 2)
            agent.screenshot((out / "second_start.png").resolve())
            send(process.pid, second)
            agent.screenshot((out / "second_cursor.png").resolve())
            send(process.pid, "a")
            for _ in range(5):
                time.sleep(PRESS_GAP)
                send(process.pid, "a")
            agent.pause()
            agent.screenshot((out / "after_pick.png").resolve())
            for member, base in (("first", FIRST_BUFFER), ("second", SECOND_BUFFER)):
                ram = agent.bus_read(base, BUFFER_DUMP)
                (out / f"{member}_buffer.bin").write_bytes(ram)
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    result = {
        "first": slots[0],
        "second": slots[1],
        "first_moves": first,
        "second_moves": second,
    }
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    args = sys.argv
    slots = [int(args[5]), int(args[6])]
    raise SystemExit(main(Path(args[1]), Path(args[2]), args[3], args[4], slots))

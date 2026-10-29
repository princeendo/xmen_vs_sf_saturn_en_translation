"""EXP-0025: read the slot word the English-mode test uses when the quote is drawn.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/slot_at_selector.py OUT STATE...

The version-2 patch (`tools/disc/english_mode.py`) tests ``@(6,gbr)`` against
Ryu's slot * 2 (``0x12``) at ``0x06066668``, right after the draw is stored at
``@(2,gbr)``. On the unpatched game, from each pre-K.O. STATE, a halt-mode PC
breakpoint at ``0x06066668`` stops the selector there. The run records GBR,
the words at GBR + 2 (draw) and GBR + 6 (slot * 2, if the hypothesis holds),
and the selector's caller (PR). Outputs go to the ignored OUT.
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
TEST_PC = 0x06066668


def main(out: Path, states: list[Path]) -> int:
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
            for state in states:
                agent.loadstate(state.resolve())
                agent.clear_events()
                agent.bpmode("halt")
                agent.breakpoints("pc", (f"{TEST_PC:08X}",))
                status = agent.wait_halted(120.0)
                regs = agent.regs()
                gbr = regs["GBR"]
                result[state.stem] = {
                    "frame": status.get("frame"),
                    "pc": status.get("pc"),
                    "gbr": f"{gbr:#010x}",
                    "pr": f"{regs['PR']:#010x}",
                    "draw": agent.bus_read(gbr + 2, 2).hex(),
                    "slot_word": agent.bus_read(gbr + 6, 2).hex(),
                }
                agent.breakpoints("pc", ())
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]))

"""EXP-0021: force Ryu's win-quote record from the `pre_ko` checkpoint.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0021/force_record.py OUT [INDEX ...]

The record index is the byte at WRAM-H ``0x060F8AE6`` (quote task + 38). The
store at ``0x06066696`` writes it from the game's random-number generator,
and in the same frame ``0x06066948`` turns it into the record pointer at
``0x060F2490`` (`EXP-0021`). Each run loads `pre_ko`, sets a log-mode write
breakpoint on the index byte, and, for a forced run, an ``onhit`` write of
INDEX that the agent applies right after the store. It then runs 660 frames
to the quote screen and saves a screenshot, VDP1 VRAM, the index, the
pointer, the 38 codes of the shown record, and the breakpoint events. The
control (``control``) sets the same breakpoint with no ``onhit`` write.
Default runs: control, 0, 5, 15. Outputs go to the ignored OUT.
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
STATE = Path("local/checkpoints/dbg003/f00009769.mcs")  # pre_ko
INDEX = 0x060F8AE6
SETTER_PC = 0x06066696
POINTER = 0x060F2490
TO_QUOTE = 660


def main(out: Path, runs: list[str]) -> int:
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
            for run in runs:
                agent.loadstate(STATE.resolve())
                agent.pause()
                agent.onhit_clear()
                agent.clear_events()
                agent.bpmode("log")
                agent.breakpoints("write", [f"{INDEX:08X}-{INDEX:08X}"])
                if run != "control":
                    agent.onhit_write(SETTER_PC, INDEX, bytes([int(run)]))
                agent.frames(TO_QUOTE)
                agent.wait_halted(60.0)
                agent.screenshot((out / f"{run}.png").resolve())
                (out / f"{run}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                result[run] = {
                    "index": agent.bus_read(INDEX, 1)[0],
                    "pointer": f"{pointer:#010x}",
                    "record_at_quote": agent.bus_read(pointer, 76).hex(),
                    "events": agent.events(),
                }
                agent.breakpoints("write")
                agent.onhit_clear()
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    summary = {
        k: {"index": v["index"], "pointer": v["pointer"]}
        for k, v in result.items()
        if isinstance(v, dict)
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), sys.argv[2:] or ["control", "0", "5", "15"])
    )

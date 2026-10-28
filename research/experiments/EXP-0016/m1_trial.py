"""EXP-0016 (M1): write known codes into the quote record in live RAM.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0016/m1_trial.py OUT

From the `pre_ko` checkpoint (`EXP-0014`), paused, the trial writes three
codes over record 10's line-1 cells 3-5 in the WRAM-L quote table
(`EXP-0015`); the control does every step except the write. Each run then
plays on with no input and takes screenshots at the quote screen. The record
is read before and after the write; everything goes to the ignored OUT as
files plus ``result.json``.
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
RECORD = 0x0024F8D0  # table 0x0024F5D8, record 10 (EXP-0015)
RECORD_BYTES = 76
TARGET = RECORD + 2 * 3  # line 1, cells 3-5 (after three blank cells)
# あ い う: hiragana code = Unicode - 0x2661 (EXP-0015)
NEW = b"".join((ord(c) - 0x2661).to_bytes(2, "big") for c in "あいう")
TO_QUOTE, LATER = 660, 60  # frames from pre_ko to the quote screen (EXP-0013)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"target": f"{TARGET:#010x}", "new": NEW.hex()}
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
            for run in ("control", "trial"):
                agent.loadstate(STATE.resolve())
                agent.pause()
                before = agent.bus_read(RECORD, RECORD_BYTES)
                if run == "trial":
                    agent.bus_write(TARGET, NEW)
                after = agent.bus_read(RECORD, RECORD_BYTES)
                agent.frames(TO_QUOTE)
                agent.wait_halted(60.0)
                agent.screenshot((out / f"{run}-1.png").resolve())
                agent.run()
                agent.frames(LATER)
                agent.wait_halted(30.0)
                agent.screenshot((out / f"{run}-2.png").resolve())
                quote_time = agent.bus_read(RECORD, RECORD_BYTES)
                agent.run()
                result[run] = {
                    "record_before": before.hex(),
                    "record_after_write": after.hex(),
                    "record_at_quote": quote_time.hex(),
                }
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

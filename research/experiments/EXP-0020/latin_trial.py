"""EXP-0020: show Latin codes in the win quote, with a no-write control.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0020/latin_trial.py OUT

From the `pre_ko` checkpoint (`EXP-0014`), paused, each trial writes 38 codes
(two full lines of 19 cells) over record 10 of the WRAM-L quote table
(``0x0024F8D0``, `EXP-0015`); the control writes nothing. Codes come from the
arcade English map (`tools.reference.xvsf_text.DECODE`). Each run plays on 660
frames to the quote screen, saves a screenshot and VDP1 VRAM, runs 60 more
frames and saves a second screenshot. Outputs go to the ignored OUT, with the
written codes in ``result.json``.
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
from tools.reference.xvsf_text import DECODE

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/dbg003/f00009769.mcs")  # pre_ko
RECORD = 0x0024F8D0  # table 0x0024F5D8, record 10 (EXP-0015)
CELLS = 19
TO_QUOTE, LATER = 660, 60  # frames from pre_ko to the quote screen (EXP-0013)
ENCODE = {char: code for code, char in DECODE.items()}
TRIALS = {
    "control": None,
    "upper_lower": ("ABCDEFGHIJKLMNOPQRS", "abcdefghijklmnopqrs"),
    "rest_digits": ("TUVWXYZ0123456789!?", "tuvwxyz.,'-:;()&\"/%"),
    "symbols": ("#$*+<=>@[\\]^_`{|}~", ""),
}


def encode(lines: tuple[str, str]) -> bytes:
    codes = [ENCODE[char] for line in lines for char in line.ljust(CELLS)]
    if len(codes) != 2 * CELLS:
        raise ValueError("each line must be at most 19 characters")
    return b"".join(code.to_bytes(2, "big") for code in codes)


def main(out: Path) -> int:
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
            for name, lines in TRIALS.items():
                agent.loadstate(STATE.resolve())
                agent.pause()
                before = agent.bus_read(RECORD, 4 * CELLS)
                written = encode(lines) if lines else b""
                if written:
                    agent.bus_write(RECORD, written)
                after = agent.bus_read(RECORD, 4 * CELLS)
                agent.frames(TO_QUOTE)
                agent.wait_halted(60.0)
                agent.screenshot((out / f"{name}-1.png").resolve())
                (out / f"{name}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                at_quote = agent.bus_read(RECORD, 4 * CELLS)
                agent.run()
                agent.frames(LATER)
                agent.wait_halted(30.0)
                agent.screenshot((out / f"{name}-2.png").resolve())
                agent.run()
                result[name] = {
                    "lines": lines,
                    "record_before": before.hex(),
                    "record_after_write": after.hex(),
                    "record_at_quote": at_quote.hex(),
                }
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items()}, indent=1)[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

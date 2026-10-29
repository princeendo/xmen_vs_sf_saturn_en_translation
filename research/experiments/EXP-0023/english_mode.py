"""EXP-0023: switch the Saturn quote selector to its English mode in live RAM.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/english_mode.py OUT [RUN ...]

The Saturn port of the arcade selector keeps the arcade's English branch
(`EXP-0021`, `EXP-0022`). A nonzero language word (WRAM-H ``0x060F547A``,
R11 + ``0xD47A``) selects the second per-character base list, remaps the
draw to ``r mod 8``, and changes renderer constants. A nonzero size word
(``0x060F5478``) gives 100-byte records. From `pre_ko`, paused, a run writes
the two words, plus 8 synthetic 2 x 25-code records at Ryu's English-mode base
``0x0024FA98`` (the second list's slot 9). Then it plays 660 frames to the
quote screen and saves a screenshot, VDP1 VRAM, the record pointer and the
words. Runs:

* ``control``: no write.
* ``english``: both words = 2 (the arcade's English value), plus the records.
* ``words_only``: both words = 2, no records (what the base area shows as is).

The 800 bytes overwritten at ``0x0024FA98`` are saved first (rule 12). Outputs
go to the ignored OUT.
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
LANGUAGE, SIZE = 0x060F547A, 0x060F5478
ENGLISH_BASE = 0x0024FA98
POINTER = 0x060F2490
TO_QUOTE = 660
ENCODE = {char: code for code, char in DECODE.items()}
LINES = ("ABCDEFGHIJKLMNOPQRSTUVWXY", "abcdefghijklmnopqrstuvwxy")


def record(index: int) -> bytes:
    # Mark each record by its index in the last cell of line 2.
    line2 = LINES[1][:24] + str(index)
    codes = [ENCODE[c] for c in LINES[0] + line2]
    return b"".join(code.to_bytes(2, "big") for code in codes)


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
                entry: dict[str, object] = {
                    "words_before": agent.bus_read(SIZE, 4).hex(),
                    "base_before": agent.bus_read(ENGLISH_BASE, 800).hex(),
                }
                if run in ("english", "words_only"):
                    agent.bus_write(SIZE, bytes.fromhex("00020002"))
                if run == "english":
                    data = b"".join(record(i) for i in range(8))
                    agent.bus_write(ENGLISH_BASE, data)
                agent.frames(TO_QUOTE)
                agent.wait_halted(60.0)
                agent.screenshot((out / f"{run}.png").resolve())
                (out / f"{run}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                entry["pointer"] = agent.bus_read(POINTER, 4).hex()
                entry["words_at_quote"] = agent.bus_read(SIZE, 4).hex()
                result[run] = entry
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: {kk: vv for kk, vv in v.items() if kk != "base_before"}
                for k, v in result.items()
                if isinstance(v, dict)
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    runs = sys.argv[2:] or ["control", "english", "words_only"]
    raise SystemExit(main(Path(sys.argv[1]), runs))

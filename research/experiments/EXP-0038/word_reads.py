"""EXP-0038: log every read of the size and language words during Nash's ending.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/word_reads.py OUT [STATE]

From STATE (default `EXP-0034`'s ``f00220064.mcs``, after the partner
fight's last hit), on the untouched image with no input, read breakpoints in
log mode cover ``WORDS`` (the size word ``0x060F5478`` and the language word
``0x060F547A``, `EXP-0023`) and their cache-through mirror. The emulator runs
to each page frame in ``TARGETS`` (`EXP-0034`), and the hits in each
interval are counted by PC and by address. The first hit of each PC keeps
its registers. Outputs go to the ignored OUT.
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
STATE = Path("local/checkpoints/end001/f00220064.mcs")
WORDS = (0x060F5478, 0x060F547B)
TARGETS = [220654, 220887, 221112, 221342, 221690, 222037, 223044]


def parse(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def main(out: Path, state: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    start = int(state.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    low, high = WORDS
    ranges = [
        f"{low:08X}-{high:08X}",
        f"{low | 0x20000000:08X}-{high | 0x20000000:08X}",
    ]
    intervals: list[dict[str, object]] = []
    result: dict[str, object] = {"state": str(state)}
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
            agent.loadstate(state.resolve())
            agent.pause()
            result["words_at_state"] = agent.bus_read(low, 4).hex()
            agent.bpmode("log")
            agent.breakpoints("read", ranges)
            now = start
            for target in TARGETS:
                agent.clear_events()
                agent.frames(target - now)
                agent.wait_halted(300.0)
                counts: dict[str, int] = {}
                first: dict[str, dict[str, str]] = {}
                for line in agent.events():
                    if not line.startswith("hit"):
                        continue
                    hit = parse(line)
                    key = (
                        f"{hit.get('PC', '?')} {hit.get('addr', hit.get('ADDR', '?'))}"
                    )
                    counts[key] = counts.get(key, 0) + 1
                    first.setdefault(hit.get("PC", "?"), hit)
                intervals.append(
                    {"from": now, "to": target, "counts": counts, "first": first}
                )
                now = target
            agent.breakpoints("read", [])
            agent.bpmode("halt")
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["intervals"] = intervals
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    for interval in intervals:
        print(interval["to"], json.dumps(interval["counts"]))
    return 0


if __name__ == "__main__":
    state = Path(sys.argv[2]) if len(sys.argv) > 2 else STATE
    raise SystemExit(main(Path(sys.argv[1]), state))

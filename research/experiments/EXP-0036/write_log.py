"""EXP-0036: log every CPU write to Nash's ending records between two frames.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/write_log.py OUT STATE END [CUE]

From STATE (a session checkpoint named ``f<frame>.mcs``), with no input, write
breakpoints in log mode cover ``RECORDS`` (the six ending records,
`EXP-0035`) and its cache-through mirror. The emulator runs to frame END,
reading the log every ``STEP`` frames, and keeps each hit's frame, PC, PR and
write address. CUE defaults to the untouched source image. Outputs go to the
ignored OUT.
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
RECORDS = (0x0024FEC0, 0x00250087)  # MC10 records 16-21 in WRAM-L (EXP-0035)
STEP = 600


def parse(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def main(out: Path, state: Path, end: int, image: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    start = int(state.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    low, high = RECORDS
    ranges = [
        f"{low:08X}-{high:08X}",
        f"{low | 0x20000000:08X}-{high | 0x20000000:08X}",
    ]
    result: dict[str, object] = {"state": str(state), "image": str(image)}
    hits: list[dict[str, object]] = []
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(image)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            before = agent.bus_read(low, high - low + 1)
            agent.bpmode("log")
            agent.breakpoints("write", ranges)
            now = start
            while now < end:
                count = min(STEP, end - now)
                agent.clear_events()
                agent.frames(count)
                agent.wait_halted(300.0)
                now += count
                for line in agent.events():
                    if line.startswith("hit"):
                        hit = parse(line)
                        hits.append(
                            {
                                "upto": now,
                                **{
                                    k: hit[k]
                                    for k in ("PC", "PR", "addr", "ADDR")
                                    if k in hit
                                },
                            }
                        )
            agent.breakpoints("write", [])
            agent.bpmode("halt")
            after = agent.bus_read(low, high - low + 1)
            result["records_changed"] = before != after
            result["records_sha_prefix"] = after[:16].hex()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["hits"] = hits
    result["hit_count"] = len(hits)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("hit_count", "records_changed")}))
    return 0


if __name__ == "__main__":
    image = Path(sys.argv[4]) if len(sys.argv) > 4 else IMAGE
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), image)
    )

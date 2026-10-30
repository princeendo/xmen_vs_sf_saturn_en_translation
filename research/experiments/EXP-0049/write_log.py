r"""EXP-0049: log CPU writes (or reads, or executions) after a save state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/write_log.py \
        CUE OUT STATE FIRST:LAST FRAMES [KIND]

KIND is ``write`` (the default), ``read`` or ``pc``. Loads STATE into a
silent Mednafen on CUE, sets a KIND breakpoint in log mode on the bus range
FIRST-LAST (hex, both ends included, with its
cache-through mirror for addresses below ``0x20000000``), runs FRAMES
frames, and writes every hit line to ``OUT/hits.txt`` with a summary of the
PCs to ``OUT/summary.json``. A screenshot is taken at the end.

Only CPU writes trigger the breakpoint; a DMA transfer does not (HYPOTHESIS
to keep in mind when a range shows no hits).
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.mednafen.route import BINARY, parse_hit


def main(
    cue: Path, out: Path, state: Path, area: str, frames: int, kind: str = "write"
) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    low, high = (int(v, 16) for v in area.split(":"))
    ranges = [f"{low:08X}-{high:08X}"]
    if low < 0x20000000:
        ranges.append(f"{low | 0x20000000:08X}-{high | 0x20000000:08X}")
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=30.0)
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
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints(kind, ranges)
            agent.frames(frames)
            agent.wait_halted(300.0)
            agent.breakpoints(kind)
            agent.bpmode("halt")
            hits = [line for line in agent.events() if line.startswith("hit")]
            agent.screenshot((out / "end.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "hits.txt").write_text("\n".join(hits) + "\n")
    pcs = Counter(parse_hit(line).get("PC", "?") for line in hits)
    summary = {"ranges": ranges, "frames": frames, "hits": len(hits), "pcs": pcs}
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    a = sys.argv
    kind = a[6] if len(a) > 6 else "write"
    raise SystemExit(main(Path(a[1]), Path(a[2]), Path(a[3]), a[4], int(a[5]), kind))

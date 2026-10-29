"""EXP-0035: which quote code runs during Nash's ending, and what VDP1 holds per page.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0035/trace_pages.py OUT [STATE]

STATE defaults to `EXP-0034`'s replay checkpoint ``f00220064.mcs`` (after the
last hit of the partner fight, before ``K.O.``), on the untouched source
image, with no input. PC breakpoints in log mode are set on the four quote
selectors and the shared renderer (`EXP-0023`). The emulator runs to each
frame in ``TARGETS`` (`EXP-0034`'s page screenshots), and the hits logged in
each interval are kept. At each target it saves a screenshot, VDP1 VRAM,
VDP2 VRAM, the quote pointer, the 100 bytes it points at, and the 64 bytes
at ``SCRIPT``. Outputs go to the ignored OUT.
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
POINTER = 0x060F2490  # the quote record pointer (EXP-0021)
SCRIPT = 0x060D4D00  # R6 at the ending selector points here (trace1)
CODE = {
    0x0606663C: "win selector (type 0)",
    0x06066728: "hint selector (type 2)",
    0x060668A2: "ending selector (type 4)",
    0x060667B8: "selector type 6",
    0x06066948: "renderer",
}
# EXP-0034 page screenshots 1-6, then the first credits frame
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
    result: dict[str, object] = {"state": str(state), "intervals": []}
    intervals: list[dict[str, object]] = []
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
            agent.bpmode("log")
            agent.breakpoints("pc", [f"{a:08X}" for a in CODE])
            now = start
            for target in TARGETS:
                agent.clear_events()
                agent.frames(target - now)
                agent.wait_halted(180.0)
                hits = [parse(h) for h in agent.events() if h.startswith("hit")]
                counts: dict[str, int] = {}
                first: dict[str, dict[str, str]] = {}
                for hit in hits:
                    pc = hit.get("PC", "?")
                    counts[pc] = counts.get(pc, 0) + 1
                    first.setdefault(pc, hit)
                stem = f"f{target:08d}"
                agent.screenshot((out / f"{stem}.png").resolve())
                (out / f"{stem}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                (out / f"{stem}-vdp2.bin").write_bytes(
                    agent.read("vdp2vram", 0, 0x80000)
                )
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                intervals.append(
                    {
                        "from": now,
                        "to": target,
                        "counts": counts,
                        "first": first,
                        "pointer": f"{pointer:#010x}",
                        "codes": agent.bus_read(pointer, 100).hex(),
                        "script": agent.bus_read(SCRIPT, 0x40).hex(),
                    }
                )
                now = target
            agent.breakpoints("pc", [])
            agent.bpmode("halt")
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["intervals"] = intervals
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps([[i["to"], i["counts"]] for i in intervals]))
    return 0


if __name__ == "__main__":
    state = Path(sys.argv[2]) if len(sys.argv) > 2 else STATE
    raise SystemExit(main(Path(sys.argv[1]), state))

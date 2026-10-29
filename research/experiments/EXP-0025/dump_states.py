"""EXP-0025: dump WRAM-L and WRAM-H at each `RE-004` session checkpoint.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/dump_states.py OUT STATE...

For each STATE (a ``.mcs`` from ``local/checkpoints/re004/``) the run loads it,
pauses, and saves ``<frame>-workraml.bin`` and ``<frame>-workramh.bin`` (1 MB
each, stock agent ``read``) plus a screenshot. It also records the printed
record pointer (``0x060F2490``, `EXP-0021`). States are checkpoints, not RAM
evidence: these dumps are. Outputs go to the ignored OUT.
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
POINTER = 0x060F2490


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
                name = state.stem
                agent.loadstate(state.resolve())
                agent.pause()
                for space in ("workraml", "workramh"):
                    target = (out / f"{name}-{space}.bin").resolve()
                    agent.command(f"read {space} 0 {1 << 20} {target}")
                agent.screenshot((out / f"{name}.png").resolve())
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                result[name] = {"pointer": f"{pointer:#010x}"}
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]))

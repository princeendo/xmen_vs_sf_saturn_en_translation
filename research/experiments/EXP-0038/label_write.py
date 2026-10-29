"""EXP-0038: change one letter of a speaker label in RAM and see what changes.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/label_write.py OUT

From ``f00220917.mcs`` (page 2 of Nash's ending, `EXP-0034`), on the untouched
image with no input, two runs go to frame ``TARGET`` (page 3, label `Nash`):

- **control:** nothing written;
- **written:** the first letter of label entry ``0x11`` (``Nash``) in the
  ``MCED`` label list (``LABELS`` + 32 x index, 16-bit ASCII) is changed from
  ``N`` to ``X`` before page 3 is drawn.

Prediction: the screenshots differ only in the label's first letter. The
pixel diff is `EXP-0035` ``zero_cell.diff_box``. Outputs go to the ignored
OUT.
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
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0035"))
from zero_cell import diff_box

from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00220917.mcs")
TARGET = 221112
LABELS, INDEX = 0x060D5DA8, 0x11
OLD, NEW = b"\x00N", b"\x00X"


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    start = int(STATE.stem[1:])
    address = LABELS + 32 * INDEX
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "address": f"{address:#010x}"}
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
            for run in ("control", "written"):
                agent.loadstate(STATE.resolve())
                agent.pause()
                result[f"{run}_label"] = agent.bus_read(address, 8).hex()
                if run == "written":
                    if agent.bus_read(address, 2) != OLD:
                        raise RuntimeError("label entry is not as expected")
                    agent.bus_write(address, NEW)
                agent.frames(TARGET - start)
                agent.wait_halted(120.0)
                agent.screenshot((out / f"{run}.png").resolve())
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["diff"] = diff_box(out / "control.png", out / "written.png")
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

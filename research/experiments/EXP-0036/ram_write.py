"""EXP-0036: one code written into an ending record in RAM, before its page is drawn.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/ram_write.py OUT FIX_PRS

From ``f00220917.mcs`` (page 2 of Nash's ending, `EXP-0034`), on the untouched
image with no input, two runs go to frame ``TARGET`` (page 3):

- **control:** nothing written;
- **written:** the first code of record 18 (page 3, ``RECORD``, `EXP-0035`)
  replaced with ``NEW``, before page 3 is drawn.

Prediction: the screenshots differ only inside the first cell of the top
row, and that cell's VDP1 character data equals `FIX.PRS`'s glyph for
``NEW``. The pixel diff is `EXP-0035` ``zero_cell.diff_box``. Outputs go to
the ignored OUT.
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
from tools.memory.vdp1_sprites import sprites
from tools.text.font import Font

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00220917.mcs")
TARGET = 221112
RECORD = 0x0024FF58  # record 18 (page 3)
NEW = 0x09F2  # the first code of record 21 (page 6)


def main(out: Path, fix_prs: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    font = Font(fix_prs.read_bytes(), 0, 0)
    start = int(STATE.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "target": TARGET}
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
                old = agent.bus_read(RECORD, 2)
                if run == "written":
                    agent.bus_write(RECORD, NEW.to_bytes(2, "big"))
                    result["original_code"] = old.hex()
                agent.frames(TARGET - start)
                agent.wait_halted(120.0)
                agent.screenshot((out / f"{run}.png").resolve())
                vram = agent.read("vdp1vram", 0, 0x80000)
                (out / f"{run}-vdp1.bin").write_bytes(vram)
                pointer = int.from_bytes(agent.bus_read(0x060F2490, 4), "big")
                text = [
                    s for s in sprites(vram) if s.color_word == 0x7020 and s.y >= 170
                ]
                first = min(text, key=lambda s: (s.y, s.x))
                cell = vram[first.source : first.source + 128]
                result[run] = {
                    "pointer": f"{pointer:#010x}",
                    "first_cell_is_new_glyph": cell == font.glyph(NEW)[0],
                    "first_cell_is_old_glyph": cell
                    == font.glyph(int.from_bytes(old, "big"))[0],
                }
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["diff"] = diff_box(out / "control.png", out / "written.png")
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

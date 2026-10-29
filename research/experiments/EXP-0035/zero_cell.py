"""EXP-0035: zero one VDP1 glyph cell on an ending page and see what disappears.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0035/zero_cell.py OUT [STATE]

STATE defaults to ``f00221258.mcs`` (page 3 of Nash's ending, `EXP-0034`), on
the untouched source image, with no input. Two runs from STATE:

- **control:** load, pause, run ``FRAMES`` frames, screenshot, dump VDP1 VRAM;
- **zeroed:** load, pause, write 128 zero bytes over the character data of
  one quote sprite (the first sprite in the top row whose cell is not
  blank), run ``FRAMES`` frames, screenshot.

The quote sprites are found as in `EXP-0023` ``cell_check_en.py`` (color word
``0x7020``, y >= 170) in a VDP1 dump taken at STATE. The prediction is that
the screenshots differ only inside that sprite's 16 x 16 box, and that the
box becomes the background (no glyph). Outputs go to the ignored OUT.
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
from tools.memory.vdp1_sprites import sprites

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00221258.mcs")
FRAMES, CELL = 2, 128


def rgb(png: Path) -> tuple[int, int, bytes]:
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(png),
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    width, height = (int(v) for v in probe.split(","))
    raw = subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-i",
            str(png),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    return width, height, raw


def diff_box(a: Path, b: Path) -> dict[str, object]:
    width, height, one = rgb(a)
    _, _, two = rgb(b)
    points = [
        (i // 3 % width, i // 3 // width)
        for i in range(0, len(one), 3)
        if one[i : i + 3] != two[i : i + 3]
    ]
    if not points:
        return {"pixels": 0}
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return {
        "pixels": len(points),
        "box": [min(xs), min(ys), max(xs), max(ys)],
        "size": [width, height],
    }


def main(out: Path, state: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(state), "frames": FRAMES}
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
            vram = agent.read("vdp1vram", 0, 0x80000)
            (out / "state-vdp1.bin").write_bytes(vram)
            text = [s for s in sprites(vram) if s.color_word == 0x7020 and s.y >= 170]
            top = min(s.y for s in text)
            target = next(
                s
                for s in sorted(text, key=lambda s: s.x)
                if s.y == top and any(vram[s.source : s.source + CELL])
            )
            result["sprite"] = {
                "x": target.x,
                "y": target.y,
                "source": f"{target.source:#07x}",
                "cell": vram[target.source : target.source + CELL].hex(),
                "sprites": len(text),
                "same_source": sum(1 for s in text if s.source == target.source),
            }
            agent.frames(FRAMES)
            agent.wait_halted(60.0)
            agent.screenshot((out / "control.png").resolve())
            agent.run()
            agent.loadstate(state.resolve())
            agent.pause()
            agent.write("vdp1vram", target.source, bytes(CELL))
            agent.frames(FRAMES)
            agent.wait_halted(60.0)
            agent.screenshot((out / "zeroed.png").resolve())
            result["cell_after"] = agent.read("vdp1vram", target.source, CELL).hex()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["diff"] = diff_box(out / "control.png", out / "zeroed.png")
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("sprite", "diff")}, indent=1))
    return 0


if __name__ == "__main__":
    state = Path(sys.argv[2]) if len(sys.argv) > 2 else STATE
    raise SystemExit(main(Path(sys.argv[1]), state))

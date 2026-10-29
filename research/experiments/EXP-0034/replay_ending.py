"""EXP-0034: replay Nash's ending from a checkpoint with no input and record each page.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0034/replay_ending.py STATE OUT \\
        [FRAMES STEP]

STATE is a session checkpoint named ``f<frame>.mcs``
(`tools.mednafen.session_recorder`).
With FRAMES and STEP, the targets are instead every STEP frames for FRAMES
frames after STATE (used for the no-input partner-fight run).
The untouched source image is loaded in stock-input Mednafen (the quiet home,
no pad mapped), STATE is loaded and paused, and the emulator then runs to each
frame in ``TARGETS``, saving a screenshot there. The page frames are the
END-001 session's screenshots of the six ending pages and the first credits
screen. For each screenshot the script hashes the whole image, the text box
(``BOX``) and the picture window (``PICTURE``), as raw RGB through ffmpeg, so
two replays, and a replay and the session, can be compared region by region.
Outputs go to the ignored OUT.
"""

from __future__ import annotations

import hashlib
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
SESSION_SHOTS = Path("local/end001/session/shots")
# session frames: page 1-6 of the ending, then the first credits screen
TARGETS = [220654, 220887, 221112, 221342, 221690, 222037, 223044]
BOX, PICTURE = "crop=300:44:30:180", "crop=160:96:96:40"


def region_hash(png: Path, crop: str | None) -> str:
    argv = ["ffmpeg", "-loglevel", "error", "-i", str(png)]
    if crop is not None:
        argv += ["-vf", crop]
    argv += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(argv, capture_output=True, check=True).stdout
    return hashlib.sha256(raw).hexdigest()


def hashes(png: Path) -> dict[str, str]:
    return {
        "image": region_hash(png, None),
        "box": region_hash(png, BOX),
        "picture": region_hash(png, PICTURE),
    }


def main(state: Path, out: Path, span: tuple[int, int] | None = None) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    start = int(state.stem[1:])
    targets = TARGETS
    if span is not None:
        frames, step = span
        targets = list(range(start + step, start + frames + 1, step))
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(state), "start": start, "pages": {}}
    pages: dict[str, object] = {}
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
            now = start
            for target in targets:
                agent.frames(target - now)
                agent.wait_halted(120.0)
                now = target
                shot = (out / f"f{target:08d}.png").resolve()
                agent.screenshot(shot)
                entry: dict[str, object] = {"replay": hashes(shot)}
                session = SESSION_SHOTS / f"f{target:08d}.png"
                if session.exists():
                    recorded = hashes(session)
                    entry["session"] = recorded
                    entry["box_matches_session"] = (
                        recorded["box"] == entry["replay"]["box"]  # type: ignore[index]
                    )
                pages[str(target)] = entry
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["pages"] = pages
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {k: v.get("box_matches_session") for k, v in pages.items()}  # type: ignore[attr-defined]
        )
    )
    return 0


if __name__ == "__main__":
    span = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else None
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), span))

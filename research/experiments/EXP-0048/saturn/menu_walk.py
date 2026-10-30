r"""EXP-0048: boot an image cold and walk its screens with scripted keys.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0048/saturn/menu_walk.py \
        CUE OUT STEP [STEP ...]

Each STEP is one of:

- ``wait:N``: run N frames, with a screenshot every ``SHOT_EVERY`` frames;
- ``shot:NAME``: a screenshot named NAME;
- ``await:PNG:N``: run up to N frames, ``AWAIT_STEP`` at a time, until the
  screen matches the reference screenshot PNG (mean absolute difference of
  the two images scaled to 44 x 30, under ``AWAIT_LIMIT``); a screenshot
  is taken when it matches, and the run stops if it never does. Disc
  loading makes fixed frame counts unreliable for reaching a screen;
- ``keys:MOVES``: press the keys for MOVES in turn
  (`tools.mednafen.route.KEYS`: u d l r a b c z s, where s is Start), with
  Mednafen brought to the front, then run ``SETTLE`` frames.

Mednafen runs from the ``local/mednafen_pick`` home (silent, with the
route's key map), booted cold on CUE with no save state. Screenshots go to
``OUT/shots/`` as ``f<frame>.png`` (frames counted by this script from the
first ``wait``) or ``<NAME>.png``. ``OUT/steps.json`` records each step and
its frame.
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
from tools.mednafen.route import BINARY, pick_home, send

SHOT_EVERY, SETTLE = 60, 30
AWAIT_STEP, AWAIT_LIMIT = 30, 12.0


def thumbnail(path: Path) -> bytes:
    return subprocess.run(
        [
            *("ffmpeg", "-v", "error", "-i", str(path)),
            *("-vf", "scale=44:30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"),
        ],
        check=True,
        capture_output=True,
    ).stdout


def difference(a: bytes, b: bytes) -> float:
    return sum(abs(x - y) for x, y in zip(a, b, strict=True)) / len(a)


def main(cue: Path, out: Path, steps: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    (out / "shots").mkdir()
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    record: list[dict[str, object]] = []
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            agent.pause()
            frame = 0
            for step in steps:
                kind, _, value = step.partition(":")
                record.append({"step": step, "frame": frame})
                if kind == "wait":
                    remaining = int(value)
                    while remaining > 0:
                        count = min(SHOT_EVERY, remaining)
                        agent.frames(count)
                        agent.wait_halted(60.0)
                        frame += count
                        remaining -= count
                        agent.screenshot(
                            (out / "shots" / f"f{frame:06d}.png").resolve()
                        )
                elif kind == "await":
                    reference, _, limit = value.rpartition(":")
                    wanted = thumbnail(Path(reference))
                    waited = 0
                    while True:
                        agent.frames(AWAIT_STEP)
                        agent.wait_halted(60.0)
                        frame += AWAIT_STEP
                        waited += AWAIT_STEP
                        shot = (out / "shots" / f"f{frame:06d}.png").resolve()
                        agent.screenshot(shot)
                        if difference(thumbnail(shot), wanted) < AWAIT_LIMIT:
                            break
                        shot.unlink()
                        if waited >= int(limit):
                            raise RuntimeError(f"{reference} never matched")
                elif kind == "shot":
                    agent.screenshot((out / "shots" / f"{value}.png").resolve())
                elif kind == "keys":
                    agent.run()
                    send(process.pid, value)
                    agent.pause()
                    agent.frames(SETTLE)
                    agent.wait_halted(60.0)
                    frame += SETTLE
                else:
                    raise ValueError(f"unknown step {step}")
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "steps.json").write_text(json.dumps(record, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]))

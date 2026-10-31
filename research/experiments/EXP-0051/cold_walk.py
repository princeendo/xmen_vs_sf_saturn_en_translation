r"""EXP-0051: boot an image cold, walk it with scripted keys, and record its sound.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0051/cold_walk.py \
        CUE OUT STEP [STEP ...]

Copied from `research/experiments/EXP-0048/saturn/menu_walk.py` (this
repository, commit ``908f8b4``), with Mednafen's sound recorder
(``-soundrecord``, as in `research/experiments/EXP-0050/voice_record.py`)
and one more step. The steps are:

- ``wait:N``: run N frames, with a screenshot every ``SHOT_EVERY`` frames;
- ``shot:NAME``: a screenshot named NAME;
- ``await:PNG:N``: run up to N frames, ``AWAIT_STEP`` at a time, until the
  screen matches the reference screenshot PNG (mean absolute difference of
  the two images scaled to 44 x 30, under ``AWAIT_LIMIT``);
- ``keys:MOVES``: press the keys for MOVES in turn
  (`tools.mednafen.route.KEYS`: u d l r a b c z s, where s is Start), with
  Mednafen brought to the front, then run ``SETTLE`` frames;
- ``press:KEY:PNG:N``: press KEY, run ``PRESS_WAIT`` frames, and repeat
  until the screen matches PNG (as ``await``), at most N times. Menus take
  a key only at some moments, so a fixed count of presses is unreliable;
- ``chord:MOVES``: hold the keys for MOVES together for a moment
  (`tools.mednafen.route.send_chord`; `SPEC-001`: Start held over a pick),
  then run ``SETTLE`` frames;
- ``peek:ADDRESS:LENGTH``: read LENGTH bytes at the bus ADDRESS (hex) into
  ``steps.json``;
- ``save:NAME``: a save state ``OUT/NAME.mcs`` (the agent saves while
  running, so the state is a few frames after the step);
- ``ko:N``: run N frames, ``STEP`` at a time, setting the CPU side's two
  vitality words to 0 before each step (`tools.mednafen.route.CPU`, + 0x10;
  `EXP-0045`), with a screenshot every ``STEP`` frames (the win banner
  shows for less than ``SHOT_EVERY``). This is the
  route's way to end a fight with no play; it writes game state, not code.

The image is booted cold: no save state is loaded, so every byte of code
comes from CUE's own disc. Mednafen runs from the ``local/mednafen_pick``
home (silent, the route's key map), or from the home named by the
environment variable ``COLD_WALK_HOME`` (`EXP-0053`: a case home with the
key map's settings). ``OUT/sound.wav`` is the recording;
``OUT/steps.json`` records each step's frame and the WAV's length in
samples at its start, so that a sound can be cut from the moment it was
made. Screenshots go to ``OUT/shots/``. OUT is an ignored path.
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
from tools.mednafen.route import BINARY, CPU, pick_home, send, send_chord

SHOT_EVERY, SETTLE, STEP = 60, 30, 20
AWAIT_STEP, AWAIT_LIMIT = 30, 12.0
PRESS_WAIT = 60
VITALITY = 0x10


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


def wav_frames(path: Path) -> int:
    """Sample frames written so far (16-bit stereo; header 44 bytes)."""
    return max(0, (path.stat().st_size - 44) // 4) if path.exists() else 0


def main(cue: Path, out: Path, steps: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    (out / "shots").mkdir()
    home = (
        Path(os.environ["COLD_WALK_HOME"])
        if "COLD_WALK_HOME" in os.environ
        else pick_home()
    )
    agent_dir = (out / "agent").resolve()
    wav = (out / "sound.wav").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    record: list[dict[str, object]] = []
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), "-soundrecord", str(wav), str(cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
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

            def run(count: int, ko: bool = False) -> None:
                nonlocal frame
                while count > 0:
                    n = min(STEP if ko else SHOT_EVERY, count)
                    if ko:
                        for block in CPU:
                            agent.bus_write(block + VITALITY, bytes(2))
                    agent.frames(n)
                    agent.wait_halted(60.0)
                    frame += n
                    count -= n
                    if ko or frame % SHOT_EVERY < n:
                        shot = out / "shots" / f"f{frame:06d}.png"
                        agent.screenshot(shot.resolve())

            for step in steps:
                kind, _, value = step.partition(":")
                time.sleep(0.2)
                record.append({"step": step, "frame": frame, "wav": wav_frames(wav)})
                if kind == "wait":
                    run(int(value))
                elif kind == "ko":
                    run(int(value), ko=True)
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
                elif kind == "press":
                    key, _, rest = value.partition(":")
                    reference, _, tries = rest.rpartition(":")
                    wanted = thumbnail(Path(reference))
                    for _ in range(int(tries)):
                        agent.run()
                        send(process.pid, key)
                        agent.pause()
                        agent.frames(PRESS_WAIT)
                        agent.wait_halted(60.0)
                        frame += PRESS_WAIT
                        shot = (out / "shots" / f"f{frame:06d}.png").resolve()
                        agent.screenshot(shot)
                        if difference(thumbnail(shot), wanted) < AWAIT_LIMIT:
                            break
                    else:
                        raise RuntimeError(f"{reference} never matched")
                elif kind == "shot":
                    agent.screenshot((out / "shots" / f"{value}.png").resolve())
                elif kind == "chord":
                    agent.run()
                    send_chord(process.pid, value)
                    agent.pause()
                    agent.frames(SETTLE)
                    agent.wait_halted(60.0)
                    frame += SETTLE
                elif kind == "peek":
                    address, _, length = value.partition(":")
                    data = agent.bus_read(int(address, 16), int(length))
                    record[-1]["bytes"] = data.hex()
                elif kind == "save":
                    agent.run()
                    agent.savestate((out / f"{value}.mcs").resolve())
                    agent.pause()
                elif kind == "keys":
                    agent.run()
                    send(process.pid, value)
                    agent.pause()
                    agent.frames(SETTLE)
                    agent.wait_halted(60.0)
                    frame += SETTLE
                else:
                    raise ValueError(f"unknown step {step}")
            time.sleep(0.2)
            record.append({"step": "end", "frame": frame, "wav": wav_frames(wav)})
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
            (out / "steps.json").write_text(json.dumps(record, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]))

r"""EXP-0050: record the game's sound while stepping from a save state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/voice_record.py \
        CUE OUT STATE STEP [STEP ...]

Mednafen starts on CUE with ``-soundrecord OUT/sound.wav`` (its own WAV
recorder, `src/drivers/main.cpp`), in the route's pick home (silent:
volume 0), loads STATE and pauses. Each STEP is:

- ``wait:N``: run N frames;
- ``keys:MOVES``: press MOVES (`tools.mednafen.route.KEYS`) with
  Mednafen in front, then run ``SETTLE`` frames;
- ``shot:NAME``: a screenshot ``OUT/NAME.png``.

``OUT/steps.json`` records each step with the emulated frame count and the
WAV length (in samples) at that moment, so that sounds can be matched to
steps. The WAV also holds the audio from before STATE was loaded (the
boot until the agent answers); ``wav_start`` gives its length at the
first step. Outputs go to the ignored OUT.
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

SETTLE = 30


def wav_frames(path: Path) -> int:
    """Sample frames written so far (16-bit stereo assumed; header 44 bytes)."""
    return max(0, (path.stat().st_size - 44) // 4) if path.exists() else 0


def main(cue: Path, out: Path, state: Path, steps: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    wav = (out / "sound.wav").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
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
            time.sleep(2)
            agent.loadstate(state.resolve())
            agent.pause()
            frame = 0
            record.append({"step": "wav_start", "frame": 0, "wav": wav_frames(wav)})
            for step in steps:
                kind, _, value = step.partition(":")
                if kind == "wait":
                    agent.frames(int(value))
                    agent.wait_halted(120.0)
                    frame += int(value)
                elif kind == "keys":
                    agent.run()
                    send(process.pid, value)
                    agent.pause()
                    agent.frames(SETTLE)
                    agent.wait_halted(60.0)
                    frame += SETTLE
                elif kind == "shot":
                    agent.screenshot((out / f"{value}.png").resolve())
                else:
                    raise ValueError(f"unknown step {step}")
                time.sleep(0.2)
                record.append({"step": step, "frame": frame, "wav": wav_frames(wav)})
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    (out / "steps.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record[-1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4:])
    )

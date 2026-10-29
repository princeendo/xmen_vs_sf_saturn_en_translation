"""EXP-0018: find where an image's cold boot first differs from the original's.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0018/boot_ram_scan.py CUE OUT [STEPS]

Cold-boots CUE in the patched build (silent home, no input), pauses every 60
frames for STEPS steps (default 45), and saves the SHA-256 of WRAM-L and WRAM-H
at each step plus both regions at every step whose hash differs from the
previous run given by ``--compare``. With two runs on two images, the first
step whose hashes differ brackets the first divergence. Outputs go to the
ignored OUT.
"""

from __future__ import annotations

import argparse
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
REGIONS = {"workraml": 1 << 20, "workramh": 1 << 20}
STEP = 60


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--steps", type=int, default=45)
    parser.add_argument("--compare", type=Path, help="result.json of an earlier run")
    args = parser.parse_args(argv)
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    earlier = json.loads(args.compare.read_text())["steps"] if args.compare else None
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    steps: list[dict[str, object]] = []
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.pause()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.2)
            for index in range(args.steps):
                agent.frames(STEP)
                status = agent.wait_halted(60.0)
                entry: dict[str, object] = {"frame": status["frame"]}
                for space, size in REGIONS.items():
                    path = (out / f"{space}-{index:03d}.bin").resolve()
                    agent.command(f"read {space} 0 {size} {path}")
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    entry[space] = digest
                    same = earlier is not None and earlier[index][space] == digest
                    if earlier is None or same:
                        path.unlink()
                steps.append(entry)
        finally:
            process.send_signal(signal.SIGTERM)
            exit_code = process.wait(timeout=30)
    result = {"cue": str(args.cue), "exit_code": exit_code, "steps": steps}
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    if earlier is not None:
        marks = "".join(
            "="
            if all(e[s] == steps[i][s] for s in REGIONS)
            else ("L" if e["workraml"] != steps[i]["workraml"] else "H")
            for i, e in enumerate(earlier[: len(steps)])
        )
        print(marks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

r"""EXP-0053: cold-boot in a given home, then dump work RAM, with optional logs.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0053/boot_dump.py \
        CUE HOME OUT FRAMES [KIND:FIRST:LAST ...]

HOME is a case home made by ``census.py`` (``OUT/homes/<case>``), so the cart
and backup memory are the case's. Mednafen is booted cold on CUE with no
input. Each ``KIND:FIRST:LAST`` (``read``, ``write`` or ``pc``; hex bus
addresses, both ends included) is set as a log-mode breakpoint from the
first frame. After FRAMES frames the game is paused and OUT gets:

- ``screen.png``;
- ``wram_l.bin`` (``0x00200000``-``0x002FFFFF``) and ``wram_h.bin``
  (``0x06000000``-``0x060FFFFF``), read live over the agent;
- ``hits.txt``, every breakpoint hit line.

A copy of the home is used (``OUT/home``), so the case's backup memory is
not changed by the run. OUT is an ignored path.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.route import BINARY

WRAM_L, WRAM_H, SIZE = 0x00200000, 0x06000000, 0x100000


def main(cue: Path, home: Path, out: Path, frames: int, logs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    copy = out / "home"
    shutil.copytree(home, copy, ignore=shutil.ignore_patterns("agent", "*.lck"))
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(copy.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
                    time.sleep(0.2)
            agent.pause()
            kinds: dict[str, list[str]] = {}
            for spec in logs:
                kind, first, last = spec.split(":")
                span = f"{int(first, 16):08X}-{int(last, 16):08X}"
                kinds.setdefault(kind, []).append(span)
            if kinds:
                agent.bpmode("log")
            for kind, ranges in kinds.items():
                agent.breakpoints(kind, ranges)
            agent.frames(frames)
            agent.wait_halted(max(120.0, frames / 20))
            agent.screenshot((out / "screen.png").resolve())
            (out / "wram_l.bin").write_bytes(agent.bus_read(WRAM_L, SIZE))
            (out / "wram_h.bin").write_bytes(agent.bus_read(WRAM_H, SIZE))
            if logs:
                hits = [line for line in agent.events() if line.startswith("hit")]
                (out / "hits.txt").write_text("\n".join(hits) + "\n")
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    return 0


if __name__ == "__main__":
    a = sys.argv
    raise SystemExit(main(Path(a[1]), Path(a[2]), Path(a[3]), int(a[4]), a[5:]))

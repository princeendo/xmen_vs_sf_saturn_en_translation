r"""EXP-0066: log PC and write breakpoint hits around the continue hint.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0066/trace_run.py \
        CUE STATE OUT FROM TO [pc:ADDR ...] [write:FIRST-LAST ...] \
        [ADDR:OLD:NEW ...]

As `continue_run.py` (the player loses during frames ``LOSE`` from the
load; optional RAM patches checked and applied first), with no logging up to
frame FROM. From FROM to TO, log-mode breakpoints: ``pc:ADDR`` (hex) on
execution, ``write:FIRST-LAST`` (hex, inclusive) on writes. Every hit line
(frame, PC and all registers) goes to ``OUT/hits.log``; at TO, WRAM-L and
WRAM-H are dumped (``DUMPS``). OUT is an ignored path.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.mednafen.route import PLAYER, VITALITY

_SPEC = importlib.util.spec_from_file_location(
    "continue_run", "research/experiments/EXP-0066/continue_run.py"
)
assert _SPEC and _SPEC.loader
CONTINUE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(CONTINUE)
LOSE, STEP, DUMPS = CONTINUE.LOSE, CONTINUE.STEP, CONTINUE.DUMPS


def main(
    cue: Path, state: Path, out: Path, start: int, stop: int, args: list[str]
) -> int:
    pcs = [a[3:] for a in args if a.startswith("pc:")]
    writes = [a[6:] for a in args if a.startswith("write:")]
    patches = [a for a in args if a.count(":") == 2]
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = out / "agent"
    agent_dir.mkdir()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(quiet_home().resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
        MEDNAFEN_ALLOWMULTI="1",
    )
    hits: list[str] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            for patch in patches:
                address, old, new = patch.split(":")
                at = int(address, 16)
                if agent.bus_read(at, len(old) // 2) != bytes.fromhex(old):
                    raise SystemExit(f"{address}: not {old}")
                agent.bus_write(at, bytes.fromhex(new))
            frame = 0
            while frame < stop:
                if frame == start:
                    agent.bpmode("log")
                    if pcs:
                        agent.breakpoints("pc", pcs)
                    if writes:
                        agent.breakpoints("write", writes)
                if LOSE[0] <= frame < LOSE[1]:
                    for block in PLAYER:
                        agent.bus_write(block + VITALITY, bytes(2))
                agent.clear_events()
                count = STEP if frame >= start else min(STEP, start - frame)
                agent.frames(count)
                agent.wait_halted(60.0)
                frame += count
                hits += [line for line in agent.events() if line.startswith("hit")]
            agent.breakpoints("pc", [])
            agent.breakpoints("write", [])
            agent.bpmode("halt")
            for name, base, size in DUMPS:
                data = b"".join(
                    agent.bus_read(base + at, 0x10000) for at in range(0, size, 0x10000)
                )
                (out / name).write_bytes(data)
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "hits.log").write_text("".join(f"{line}\n" for line in hits))
    print(f"{len(hits)} hits")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]), int(a[4]), a[5:])
    )

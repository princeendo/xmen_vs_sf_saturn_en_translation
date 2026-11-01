r"""EXP-0066: lose a fight from a saved state and log the continue screen's text.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0066/continue_run.py \
        CUE STATE OUT [FRAMES] [ADDR:OLD:NEW ...]

Loads STATE (a fight in progress), applies each optional RAM patch (hex
address, original bytes, new bytes; the original is checked first), then for
frames ``LOSE`` (from the load) sets both player fighters' vitality
(`tools.mednafen.route` ``PLAYER`` blocks + ``VITALITY``) to 0 every ``STEP``
frames, so the CPU wins. Runs FRAMES frames in all (default ``FRAMES``) and
logs:

- every change of the quote pointer ``0x060F2490`` (`route.POINTER`), with
  the frame;
- every write to it, from a log-mode write breakpoint (PC and frame);
- a screenshot every ``SHOT_EVERY`` frames;
- at the end, WRAM-L and WRAM-H (``DUMPS``, stock debugger reads).

Writes ``OUT/result.json`` and ``OUT/shots/``. OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.mednafen.route import PLAYER, POINTER, VITALITY, parse_hit

FRAMES, LOSE, STEP, SHOT_EVERY = 4800, (1500, 3000), 10, 30
DUMPS = (("wram_l.bin", 0x00200000, 0x100000), ("wram_h.bin", 0x06000000, 0x100000))


def main(cue: Path, state: Path, out: Path, frames: int, patches: list[str]) -> int:
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "shots").mkdir()
    agent_dir = out / "agent"
    agent_dir.mkdir()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(quiet_home().resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
        MEDNAFEN_ALLOWMULTI="1",
    )
    changes: list[tuple[int, str]] = []
    writes: list[tuple[int, str]] = []
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
            agent.bpmode("log")
            agent.breakpoints("write", [f"{POINTER:08X}-{POINTER + 3:08X}"])
            last = None
            for frame in range(0, frames, STEP):
                if LOSE[0] <= frame < LOSE[1]:
                    for block in PLAYER:
                        agent.bus_write(block + VITALITY, bytes(2))
                agent.clear_events()
                agent.frames(STEP)
                agent.wait_halted(60.0)
                for line in agent.events():
                    if line.startswith("hit"):
                        writes.append((frame + STEP, parse_hit(line).get("PC", "?")))
                pointer = agent.bus_read(POINTER, 4).hex()
                if pointer != last:
                    changes.append((frame + STEP, pointer))
                    last = pointer
                if (frame + STEP) % SHOT_EVERY == 0:
                    agent.screenshot(out / "shots" / f"r{frame + STEP:05d}.png")
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
    result = {
        "cue": str(cue),
        "state": str(state),
        "patches": patches,
        "pointer_changes": changes,
        "pointer_writes": writes,
    }
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"pointer_changes": changes, "writes": writes[:40]}))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    rest = a[3:]
    count = int(rest.pop(0)) if rest and ":" not in rest[0] else FRAMES
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), count, rest))

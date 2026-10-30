r"""EXP-0049: show other cells in place of some, by rewriting FIX.PRS in RAM.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/cell_swap.py \
        CUE OUT STATE TARGET SOURCE COUNT FRAMES [--blank N ...] [--keys MOVES]

``FIX.PRS`` is loaded raw at WRAM-L ``PACK`` (``0x002C3EA0``; `EXP-0049`).
Cells TARGET..TARGET+COUNT-1 and SOURCE..SOURCE+COUNT-1 must lie in the same
16-cell block. The block is rebuilt with the SOURCE cells' encoded bytes and
size bytes in the TARGET slots; every other cell keeps its own, except the
``--blank`` cells, which become blank (size 0) to make room. The rebuilt
block must fit in the block's original span.

With ``--keys``, MOVES (`tools.mednafen.route.KEYS`) are sent after the
write, with Mednafen in front (the route's pick home), so that a screen
that decodes its cells on a cursor move shows them.

Two runs from STATE, each FRAMES frames then a screenshot:

- ``control.png``: no change;
- ``swap.png``: the block's bytes and the size bytes written into RAM
  first, after checking that RAM holds the untouched file's bytes there.

At the end of the swap run, the edited ranges are read back and printed
(``edits_survived_run``): a reload of ``FIX.PRS`` would undo them.
``OUT/changes.json`` lists every RAM range written, with old and new bytes
(AGENTS.md rule 12). Nothing on the disc changes.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from cells import SIZES, locate

from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.mednafen.route import BINARY, pick_home, send

FIX = Path("local/ref007/saturn_files/FIX.PRS")
PACK = 0x002C3EA0


def rebuild(
    fix: bytes, target: int, source: int, count: int, blank: list[int]
) -> list[tuple[int, bytes, bytes]]:
    block = target & ~15
    if source & ~15 != block or (target + count - 1) & ~15 != block:
        raise ValueError("cells must share one block")
    start = locate(fix, block)[0]
    end = 16 + struct.unpack_from(">I", fix, 16 + (block + 16) // 4)[0]
    data, sizes = bytearray(), bytearray()
    for index in range(block, block + 16):
        donor = source + index - target if target <= index < target + count else index
        if index in blank:
            sizes.append(0)
            continue
        at, _ = locate(fix, donor)
        size = fix[SIZES + donor]
        length = 128 if size >= 128 else size
        data += fix[at : at + length]
        sizes.append(size)
    if len(data) > end - start:
        raise ValueError(f"rebuilt block needs {len(data)} of {end - start} bytes")
    return [
        (start, fix[start : start + len(data)], bytes(data)),
        (SIZES + block, fix[SIZES + block : SIZES + block + 16], bytes(sizes)),
    ]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("state", type=Path)
    parser.add_argument("target", type=lambda v: int(v, 0))
    parser.add_argument("source", type=lambda v: int(v, 0))
    parser.add_argument("count", type=int)
    parser.add_argument("frames", type=int)
    parser.add_argument("--blank", type=lambda v: int(v, 0), nargs="*", default=[])
    parser.add_argument("--keys", default="")
    args = parser.parse_args(argv)
    fix = FIX.read_bytes()
    edits = rebuild(fix, args.target, args.source, args.count, args.blank)
    args.out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (args.out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str((pick_home() if args.keys else QUIET_HOME).resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    with (args.out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            time.sleep(3)
            for name in ("control", "swap"):
                agent.loadstate(args.state.resolve())
                agent.pause()
                if name == "swap":
                    for offset, old, new in edits:
                        found = agent.bus_read(PACK + offset, len(old))
                        if found != old:
                            raise RuntimeError(f"{PACK + offset:#x}: not FIX.PRS")
                        agent.bus_write(PACK + offset, new)
                if args.keys:
                    agent.run()
                    send(process.pid, args.keys)
                    agent.pause()
                agent.frames(args.frames)
                agent.wait_halted(120.0)
                agent.screenshot((args.out / f"{name}.png").resolve())
                if name == "swap":
                    # did the edit survive the run (a file reload would undo it)?
                    survived = [
                        agent.bus_read(PACK + offset, len(new)) == new
                        for offset, _, new in edits
                    ]
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    print(json.dumps({"edits_survived_run": survived}))
    (args.out / "changes.json").write_text(
        json.dumps(
            [
                {
                    "ram_address": f"{PACK + o:#010x}",
                    "fix_offset": f"{o:#x}",
                    "original": old.hex(),
                    "modified": new.hex(),
                }
                for o, old, new in edits
            ],
            indent=1,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

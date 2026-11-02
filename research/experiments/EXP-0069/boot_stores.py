r"""EXP-0069: where the toggle routine stores during a cold boot.

Run from the repository root:

    MEDNAFEN_HOME=HOME ./invenv.sh python research/experiments/EXP-0069/boot_stores.py \
        CUE OUT FRAMES [PC ...] [--watch LO-HI]

Boots CUE cold (no input) in the Mednafen home HOME, with log-mode PC
breakpoints on each PC (hex; default ``STORES``: the routine's site write
and its byte copy) and on the routine's entry ``ENTRY``. Runs FRAMES frames,
``STEP`` at a time, dumping WRAM-H at each step to ``OUT/fNNNNNN.bin``, and
writes every hit (frame, PC and registers) to ``OUT/hits.json``. OUT is an
ignored path. With ``--watch LO-HI`` (hex), log-mode read and write
breakpoints on that range are added; their hits are in ``hits.json`` too.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.name_toggle import CODE
from tools.mednafen.replay_state import BINARY, connect
from tools.mednafen.route import parse_hit

ENTRY = CODE  # the first build had it at 0x0601E138
STORES = (CODE + 0x3A, CODE + 0x96)
STEP = 300


def main(
    cue: Path, out: Path, frames: int, pcs: list[int], watch: str | None = None
) -> int:
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = out / "agent"
    agent_dir.mkdir()
    env = dict(os.environ, MEDNAFEN_AGENT_DIR=str(agent_dir), MEDNAFEN_ALLOWMULTI="1")
    hits: list[dict[str, str]] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.pause()
            agent.wait_halted()
            agent.bpmode("log")
            agent.breakpoints("pc", [f"{pc:08X}" for pc in (ENTRY, *pcs)])
            if watch:
                agent.breakpoints("read", [watch])
                agent.breakpoints("write", [watch])
            done = 0
            while done < frames:
                agent.clear_events()
                agent.frames(STEP)
                agent.wait_halted(120.0)
                done += STEP
                hits += [parse_hit(x) for x in agent.events() if x.startswith("hit")]
                ram = b"".join(
                    agent.bus_read(0x06000000 + at, 0x10000)
                    for at in range(0, 0x100000, 0x10000)
                )
                (out / f"f{done:06d}.bin").write_bytes(ram)
                agent.screenshot(out / f"f{done:06d}.png")
            agent.breakpoints("pc", [])
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "hits.json").write_text(json.dumps(hits, indent=1) + "\n")
    entries = [h for h in hits if h.get("PC") == f"{ENTRY:08X}"]
    print(
        len(entries),
        "entries; first at frame",
        entries[0]["frame"] if entries else None,
    )
    for h in hits:
        if h.get("PC") != f"{ENTRY:08X}":
            print(
                h.get("frame"),
                h.get("PC"),
                "R9",
                h.get("R9"),
                "R13",
                h.get("R13"),
                "R6",
                h.get("R6"),
            )
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    watched = None
    if "--watch" in a:
        at = a.index("--watch")
        watched = a[at + 1]
        del a[at : at + 2]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            int(a[2]),
            [int(x, 16) for x in a[3:]] or list(STORES),
            watched,
        )
    )

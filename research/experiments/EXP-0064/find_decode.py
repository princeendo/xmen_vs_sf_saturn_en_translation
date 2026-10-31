r"""EXP-0064: find when and where a caption's characters first appear in memory.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0064/find_decode.py \
        CUE STATE OUT PROBE FIRST:LAST STEP COUNT

PROBE is a raw VDP2 VRAM dump (from `EXP-0049/dump_screen.py`) and FIRST:LAST
(hex, VRAM offsets) the caption's character range in it; its 32-byte cells
with more than three distinct bytes are the probes. STATE is loaded into a
silent Mednafen on CUE; then COUNT times it advances STEP frames, halts, reads
WRAM-L, WRAM-H and VDP2 VRAM over the bus and counts the probes found in each,
with the lowest and highest address. The first step at which a region holds
probes is dumped to ``OUT/step<n>_<region>.bin``. ``OUT/steps.json`` lists
every step. OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home

REGIONS = {
    "wram_l": (0x00200000, 0x100000),
    "wram_h": (0x06000000, 0x100000),
}
VDP2_BASE, VDP2_SIZE = 0x25E00000, 0x80000  # read from the "vdp2vram" space


def main(
    cue: Path, state: Path, out: Path, probe: Path, span: str, step: int, count: int
) -> int:
    first, last = (int(x, 16) for x in span.split(":"))
    vram = probe.read_bytes()
    probes = [
        vram[i : i + 32]
        for i in range(first, last, 32)
        if len(set(vram[i : i + 32])) > 3
    ]
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
    steps: list[dict[str, object]] = []
    dumped: set[str] = set()
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            for n in range(count):
                agent.frames(step)
                agent.wait_halted(60.0)
                frame = int(agent.status()["frame"])
                record: dict[str, object] = {"step": n, "frame": frame}
                reads = {n: (b, agent.bus_read(b, s)) for n, (b, s) in REGIONS.items()}
                reads["vdp2"] = (VDP2_BASE, agent.read("vdp2vram", 0, VDP2_SIZE))
                for name, (base, data) in reads.items():
                    found = sorted(p for p in (data.find(x) for x in probes) if p >= 0)
                    record[name] = (
                        [
                            len(found),
                            f"{base + found[0]:#010x}",
                            f"{base + found[-1]:#010x}",
                        ]
                        if found
                        else [0]
                    )
                    if found and name not in dumped:
                        (out / f"step{n:03d}_{name}.bin").write_bytes(data)
                        dumped.add(name)
                steps.append(record)
                print(json.dumps(record), flush=True)
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "steps.json").write_text(json.dumps(steps, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), Path(a[3]), a[4], int(a[5]), int(a[6]))
    )

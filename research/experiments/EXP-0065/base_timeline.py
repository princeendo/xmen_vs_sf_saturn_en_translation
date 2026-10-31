r"""EXP-0065: NBG1's character base and its built map's characters, over time.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/base_timeline.py \
        CUE STATE OUT STEP COUNT

Loads STATE into a silent Mednafen on CUE, then COUNT times advances STEP
frames, halts and reads the base words at WRAM-H ``0x06020BB8`` (the second
is NBG1's: character = index x 4 + base, `0x0601F9E4`) and the built NBG1
map at ``0x0604C000``-``0x0604DFFF``. For each step it records the base and
the distinct character numbers in the map. Writes ``OUT/timeline.json``.
OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home

BASES, MAP, MAP_BYTES = 0x06020BB8, 0x0604C000, 0x2000


def main(cue: Path, state: Path, out: Path, step: int, count: int) -> int:
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
    records: list[dict[str, object]] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            for _ in range(count):
                agent.frames(step)
                agent.wait_halted(60.0)
                bases = struct.unpack(">II", agent.bus_read(BASES, 8))
                words = struct.unpack(
                    f">{MAP_BYTES // 2}H", agent.bus_read(MAP, MAP_BYTES)
                )
                chars = sorted({w & 0x7FFF for w in words[1::2]})
                records.append(
                    {
                        "frame": int(agent.status()["frame"]),
                        "base": f"{bases[1]:#x}",
                        "chars": chars,
                    }
                )
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "timeline.json").write_text(json.dumps(records) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]), int(a[4])))

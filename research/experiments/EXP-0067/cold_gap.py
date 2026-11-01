r"""EXP-0067: from a cold boot, compare RAM with a built MMPACK.PCA's first segment.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0067/cold_gap.py \
        CUE MMPACK OUT FRAME [FRAME ...]

Boots CUE (no input, the agent binary) and at each FRAME dumps WRAM-H to
``OUT/f<frame>.bin``, then compares RAM ``0x06014000`` onward with MMPACK's
decoded first segment (its header gives the address and size): the bytes
before the hint table, and the table itself (``continue_hints.TABLE`` to the
segment's end). A log-mode write breakpoint on the gap
(``continue_hints.TABLE``-``GAP_END``) records every write, with PC and frame.
Prints one line per frame; writes ``OUT/result.json``. OUT is an ignored
path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.continue_hints import GAP_END, TABLE
from tools.disc.prs import decompress_entries, split_header
from tools.mednafen.replay_state import BINARY, connect, quiet_home
from tools.mednafen.route import parse_hit

WRAM_H = 0x06000000


def main(cue: Path, mmpack: Path, out: Path, targets: list[int]) -> int:
    raw = mmpack.read_bytes()
    _, entries = split_header(raw)
    (first, size), _ = entries
    segment = decompress_entries(raw)[1][:size]
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
    results, writes = [], []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.pause()
            agent.wait_halted()
            agent.bpmode("log")
            agent.breakpoints("write", [f"{TABLE:08X}-{GAP_END - 1:08X}"])
            frame = int(agent.status()["frame"])
            for target in sorted(targets):
                agent.clear_events()
                agent.frames(target - frame)
                agent.wait_halted(max(60.0, (target - frame) / 20))
                frame = int(agent.status()["frame"])
                for line in agent.events():
                    if line.startswith("hit"):
                        hit = parse_hit(line)
                        writes.append((hit.get("frame"), hit.get("PC")))
                ram = b"".join(
                    agent.bus_read(WRAM_H + at, 0x10000)
                    for at in range(0, 0x100000, 0x10000)
                )
                (out / f"f{target:06d}.bin").write_bytes(ram)
                got = ram[first - WRAM_H : first - WRAM_H + size]
                split = TABLE - first
                row = {
                    "frame": target,
                    "before_table_equal": got[:split] == segment[:split],
                    "table_equal": got[split:] == segment[split:],
                    "table_zero": not any(got[split:]),
                }
                results.append(row)
                print(json.dumps(row))
            agent.breakpoints("write", [])
            agent.bpmode("halt")
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "result.json").write_text(
        json.dumps({"cue": str(cue), "rows": results, "gap_writes": writes}, indent=1)
        + "\n"
    )
    print(f"{len(writes)} gap writes")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), [int(x) for x in a[3:]]))

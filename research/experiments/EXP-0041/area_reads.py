"""EXP-0041: who reads Nash's quote table and ending area once both are English?

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0041/area_reads.py OUT AREA

From ``f00210163.mcs`` (`EXP-0034`, just before the pre-boss line), on the
untouched image with no input, RAM is first set up as the M7 build will
load it:

- version 4 for slots 0-17 with an English ending for slot 16
  (`tools.disc.english_mode.patches_v4`);
- Nash's ``MCED`` script switched to English
  (`tools.disc.english_mode.mced_english_scripts`). ``MCED`` is not yet loaded
  at this checkpoint (it is by ``f00216311``), so this edit is made at the
  first stop where its original bytes are present;
- ``MC10``'s quote table (WRAM-L ``0x0024FA00``) holding the roster build's
  800 English win-quote bytes, then the six arcade English ending records
  (600 bytes, quote table + 800).

AREA picks the read-breakpoint range (log mode, plus the cache-through
mirror). The agent's hit lines do not give the address read, so each area is
a separate run:

- ``quotes``: table + 0 to + 799;
- ``ending``: table + 800 to + 1,399 (the English ending records);
- ``rest``: table + 1,400 to + 0x687 (the old Japanese ending bytes left
  over).

The run stops at each frame in ``CHUNKS`` and counts the hits by PC in each
span. At ``SHOTS`` it saves a screenshot and the quote pointer. Outputs go
to the ignored OUT.
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
from tools.disc.build_english import read_file
from tools.disc.english_mode import as_bytes, mced_english_scripts, patches_v4
from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00210163.mcs")
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
BUILD_MC10 = Path("local/re010/b1/MC10.SHP")  # roster build (EXP-0032)
TABLE, TABLE_OFFSET = 0x0024FA00, 0x2A00
EN_ENDING, EN_SIZE, COUNT = 0x18D0AE, 100, 6
MCED_BASE = 0x060D2000
AREAS = {
    "quotes": (TABLE, TABLE + 800),
    "ending": (TABLE + 800, TABLE + 1400),
    "rest": (TABLE + 1400, TABLE + 0x688),
}
CHUNKS = {
    "pre-boss line": 211000,
    "Apocalypse fight": 216900,
    "post-boss quote": 217400,
    "partner fight": 220500,
    "ending": 222700,
}
SHOTS = [210250, 217150, 220700, 221100, 221500, 221900, 222300, 222650]
POINTER = 0x060F2490


def parse(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def main(out: Path, area: str) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    program = PROGRAM.read_bytes()
    win, _ = decompress_file(BUILD_MC10.read_bytes())
    english = (
        win[TABLE_OFFSET : TABLE_OFFSET + 800]
        + program[EN_ENDING : EN_ENDING + EN_SIZE * COUNT]
    )
    mced, _ = decompress_file(read_file("MCED.SHP;1"))
    low, high = AREAS[area]
    ranges = [
        f"{low:08X}-{high - 1:08X}",
        f"{low | 0x20000000:08X}-{(high - 1) | 0x20000000:08X}",
    ]
    start = int(STATE.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "area": area, "range": ranges}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
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
            agent.loadstate(STATE.resolve())
            agent.pause()
            edits = [
                (a, as_bytes(o), as_bytes(n))
                for a, o, n in patches_v4(list(range(18)), [16])
            ]
            pending = [
                (MCED_BASE + offset, old, new)
                for offset, old, new in mced_english_scripts(mced, [16])
            ]
            edits.append((TABLE, agent.bus_read(TABLE, len(english)), english))
            for address, old, new in edits:
                found = agent.bus_read(address, len(old))
                if found != old:
                    raise RuntimeError(f"{address:#x}: {found.hex()}")
                agent.bus_write(address, new)
            agent.bpmode("log")
            agent.breakpoints("read", ranges)
            stops = sorted({*CHUNKS.values(), *SHOTS})
            spans = {frame: name for name, frame in CHUNKS.items()}
            counts: dict[str, dict[str, int]] = {name: {} for name in CHUNKS}
            pointers: dict[str, str] = {}
            now, current = start, 0
            names = list(CHUNKS)
            for stop in stops:
                agent.clear_events()
                agent.frames(stop - now)
                agent.wait_halted(300.0)
                now = stop
                for address, old, new in list(pending):
                    if agent.bus_read(address, len(old)) == old:
                        agent.bus_write(address, new)
                        pending.remove((address, old, new))
                        result[f"mced_edit_at_{address:#010x}"] = stop
                span = names[current]
                for line in agent.events():
                    if line.startswith("hit"):
                        pc = parse(line).get("PC", "?")
                        counts[span][pc] = counts[span].get(pc, 0) + 1
                if stop in SHOTS:
                    agent.screenshot((out / f"f{stop:08d}.png").resolve())
                    pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                    pointers[str(stop)] = f"{pointer:#010x}"
                if stop in spans:
                    current = min(current + 1, len(names) - 1)
            agent.breakpoints("read", [])
            agent.bpmode("halt")
            result["edits"] = len(edits)
            result["mced_pending_at_end"] = len(pending)
            result["counts"] = counts
            result["pointers"] = pointers
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps({"counts": result.get("counts"), "pointers": result.get("pointers")})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2]))

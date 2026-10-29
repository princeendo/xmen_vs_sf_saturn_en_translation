"""EXP-0023: live-RAM trial of the English-mode patch for Ryu's win quotes.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/english_trial.py OUT [RUN ...]

From `pre_ko`, paused, a patched run does three things:

1. writes `english_patch.PATCHES` into WRAM-H (after checking the original
   bytes);
2. writes Ryu's 8 official arcade English records (US set ``xmvsfu``, slot 9
   records 0-7, 100 bytes each, read at run time from the ignored
   ``local/ref003/xmvsfu-68k.bin``) over the start of his WRAM-L quote table
   ``0x0024F5D8``;
3. optionally forces the index with an ``onhit`` write after the store at
   ``0x06066696`` (`EXP-0021`), or forces the speaker's slot x 2
   (``@(6,gbr)``, GBR = ``0x06001FC0``) with an ``onhit`` write after the PC
   ``0x06066662``, before the patched slot test.

It then plays 660 frames to the quote screen and saves a screenshot, VDP1
VRAM, the pointer, the task flag and the 50 codes shown. Runs: ``control`` (no
write), ``natural`` (patch and records, no forcing), ``K`` for a forced
index K, and ``slotN`` for a forced speaker slot N (another character's
Japanese quote, which must keep the Japanese grid). Outputs go to the ignored OUT.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from english_patch import FLAG, PATCHES, as_bytes

from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.reference.xvsf_text import long

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/dbg003/f00009769.mcs")  # pre_ko
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
EN_TABLE, SLOT = 0x17E1E8, 9
TABLE = 0x0024F5D8
TASK, INDEX, SETTER_PC, POINTER = 0x060F8AC0, 0x060F8AE6, 0x06066696, 0x060F2490
SLOT_WORD, SLOT_PC = 0x06001FC6, 0x06066662
TO_QUOTE = 660


def english_records() -> bytes:
    program = PROGRAM.read_bytes()
    base = long(program, EN_TABLE + 4 * SLOT)
    return program[base : base + 8 * 100]


def main(out: Path, runs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    records = english_records()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {}
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
            for run in runs:
                agent.loadstate(STATE.resolve())
                agent.pause()
                agent.onhit_clear()
                agent.clear_events()
                entry: dict[str, object] = {}
                if run != "control":
                    for address, old, new in PATCHES:
                        data = as_bytes(old)
                        found = agent.bus_read(address, len(data))
                        if found != data:
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, as_bytes(new))
                    entry["table_before"] = agent.bus_read(TABLE, 800).hex()
                    agent.bus_write(TABLE, records)
                if run.startswith("slot"):
                    agent.bpmode("log")
                    agent.breakpoints("pc", [f"{SLOT_PC:08X}"])
                    slot2 = 2 * int(run[4:])
                    agent.onhit_write(SLOT_PC, SLOT_WORD, slot2.to_bytes(2, "big"))
                elif run not in ("control", "natural"):
                    agent.bpmode("log")
                    agent.breakpoints("write", [f"{INDEX:08X}-{INDEX:08X}"])
                    agent.onhit_write(SETTER_PC, INDEX, bytes([int(run)]))
                agent.frames(TO_QUOTE)
                agent.wait_halted(60.0)
                agent.screenshot((out / f"{run}.png").resolve())
                (out / f"{run}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                entry.update(
                    {
                        "index": agent.bus_read(INDEX, 1)[0],
                        "slot2": int.from_bytes(agent.bus_read(SLOT_WORD, 2), "big"),
                        "flag": agent.bus_read(TASK + FLAG, 1)[0],
                        "pointer": f"{pointer:#010x}",
                        "codes_at_quote": agent.bus_read(pointer, 100).hex(),
                    }
                )
                result[run] = entry
                agent.breakpoints("write")
                agent.breakpoints("pc")
                agent.onhit_clear()
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: {
                    kk: vv
                    for kk, vv in v.items()
                    if kk in ("index", "slot2", "flag", "pointer")
                }
                for k, v in result.items()
                if isinstance(v, dict)
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    runs = sys.argv[2:] or ["control", "natural", "0", "3", "7", "slot3"]
    raise SystemExit(main(Path(sys.argv[1]), runs))

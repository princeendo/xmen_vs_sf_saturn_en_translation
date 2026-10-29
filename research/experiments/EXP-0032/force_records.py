"""EXP-0032: draw every roster character's English records through the English renderer.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0032/force_records.py \\
        BUILD OUT SLOT [SLOT ...]

Adapted from `research/experiments/EXP-0028/force_draws.py` (this repository,
commit ``1a6d268``). It uses only that script's ``ryu`` case: Ryu's `pre_ko`
state, paused at seed 8520, 660 frames to the quote, and the seeds for draws
0-7. Three changes:

- The code and slot bytes are `tools.disc.english_mode.patches_v3` for the
  whole roster (``SLOTS``, slots 0-17), taken from BUILD's decoded
  ``MMPACK.PCA`` after checking they equal the patch table.
- For each SLOT, the character's 800 English bytes are taken from BUILD's
  MC file at its table offset (`data/text/m5_roster.json`) and written over
  Ryu's table in RAM (``0x0024F5D8``). Ryu's slot is marked English, so the
  renderer draws them in the English grid. This checks each record's bytes
  through the renderer, not the character's own load or slot.
- The runs are ``<slot>-<draw>`` for draws 0-7, plus one ``control`` (nothing
  written) per process.

Each run saves a screenshot, VDP1 VRAM, the pointer, the 100 bytes shown and
the expected bytes, for `research/experiments/EXP-0023/cell_check_en.py`.
Outputs go to the ignored OUT.
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
from tools.disc.english_mode import as_bytes, patches_v3
from tools.disc.prs import decompress_entries, decompress_file, split_header
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
SLOTS = list(range(18))  # the M5 roster's English slots (RE-008)
SEED, POINTER, TABLE_SIZE = 0x060F545A, 0x060F2490, 800
ROSTER = Path("data/text/m5_roster.json")
# Ryu's case from EXP-0028 force_draws.py (EXP-0024 seed_scan.py, local/re003/scan1-4)
STATE = Path("local/checkpoints/dbg003/f00009769.mcs")
STATE_SEED, FRAMES, TABLE_RAM = 8520, 660, 0x0024F5D8
SEEDS = [2, 12, 15, 8, 21, 33, 17, 27029]  # draws 0-7


def built_sites(build: Path) -> list[tuple[int, bytes, bytes]]:
    raw = (build / "MMPACK.PCA").read_bytes()
    _, entries = split_header(raw)
    _, code, _ = decompress_entries(raw)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size
    sites = []
    for address, old, new in patches_v3(SLOTS):
        size = len(as_bytes(new))
        built = code[address - base : address - base + size]
        if built != as_bytes(new):
            raise SystemExit(f"{address:#x}: build differs from the patch table")
        sites.append((address, as_bytes(old), built))
    return sites


def built_english(build: Path, slot: int) -> bytes:
    member = next(
        m for m in json.loads(ROSTER.read_text())["roster"] if m["slot"] == slot
    )
    table, _ = decompress_file((build / member["mc_file"].split(";")[0]).read_bytes())
    start = int(member["table_offset"], 16)
    return table[start : start + TABLE_SIZE]


def main(build: Path, out: Path, slots: list[int]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    sites = built_sites(build)
    english = {slot: built_english(build, slot) for slot in slots}
    runs = ["control", *[f"{s}-{d}" for s in slots for d in range(8)]]
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
                for _ in range(20):
                    agent.loadstate(STATE.resolve())
                    agent.pause()
                    if int.from_bytes(agent.bus_read(SEED, 2), "big") == STATE_SEED:
                        break
                    agent.run()
                else:
                    raise RuntimeError(f"never paused at seed {STATE_SEED}")
                entry: dict[str, object] = {}
                if run != "control":
                    slot, draw = (int(x) for x in run.split("-"))
                    for address, original, data in sites:
                        found = agent.bus_read(address, len(data))
                        if found != original:
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, data)
                    agent.bus_write(TABLE_RAM, english[slot])
                    agent.bus_write(SEED, SEEDS[draw].to_bytes(2, "big"))
                    entry["slot"], entry["draw"], entry["seed"] = (
                        slot,
                        draw,
                        SEEDS[draw],
                    )
                    entry["expected"] = english[slot][
                        100 * draw : 100 * draw + 100
                    ].hex()
                    entry["expected_pointer"] = f"{TABLE_RAM + 100 * draw:#010x}"
                agent.frames(FRAMES)
                agent.wait_halted(120.0)
                agent.screenshot((out / f"{run}.png").resolve())
                (out / f"{run}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                entry["pointer"] = f"{pointer:#010x}"
                entry["codes_at_quote"] = agent.bus_read(pointer, 100).hex()
                result[run] = entry
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    bad = [
        k
        for k, v in result.items()
        if isinstance(v, dict)
        and k != "control"
        and (
            v["pointer"] != v["expected_pointer"]
            or v["codes_at_quote"] != v["expected"]
        )
    ]
    print(json.dumps({"runs": len(runs), "not_as_predicted": bad}))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), [int(s) for s in sys.argv[3:]])
    )

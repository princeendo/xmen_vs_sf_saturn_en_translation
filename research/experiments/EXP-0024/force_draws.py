"""EXP-0024: show every one of Ryu's 16 Saturn quote draws with the built files.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0024/force_draws.py BUILD OUT [RUN ...]

BUILD holds ``MMPACK.PCA`` and ``MC09.SHP`` from `tools.disc.build_english`.
From the `pre_ko` checkpoint, paused, a forced run first writes the code at
every `tools.disc.english_mode.PATCHES` site and the 800-byte English table
into RAM. Both are taken from the decoded BUILD files, after checking that
RAM held the original bytes. Then the run steers the draw ``r = RNG() & 0x0F``
to R by writing the RNG seed word (``0x060F545A``) with the seed that
``seed_scan.py`` found for R (``SEEDS``; two identical scans). The machine is
paused at the same RNG position each time. An ``onhit`` write right after the
draw's store does not work: the selector reads the value back two
instructions later from the SH-2 data cache, which a debugger write does not
update (`EXP-0024`). Each run plays to the
quote screen and saves a screenshot, VDP1 VRAM, the pointer and the 100 bytes
shown (``codes_at_quote``), and the record the compiler predicts for draw R
(``expected``, English record ``R & 7``). Runs: ``control`` (nothing written)
and ``0``-``15``. Outputs go to the ignored OUT.
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
from tools.disc.english_mode import PATCHES, as_bytes
from tools.disc.prs import decompress_entries, decompress_file, split_header
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/dbg003/f00009769.mcs")  # pre_ko
TABLE_RAM, TABLE_FILE, TABLE_SIZE = 0x0024F5D8, 0x25D8, 800
SEED, STATE_SEED = 0x060F545A, 8520  # seed word; its value when paused at pre_ko
POINTER, TO_QUOTE = 0x060F2490, 660
# draw -> seed giving it from pre_ko (seed_scan.py, local/re003/scan1-4)
SEEDS = {
    0: 2,
    1: 12,
    2: 15,
    3: 8,
    4: 21,
    5: 33,
    6: 17,
    7: 27029,
    8: 5,
    9: 26,
    10: 1,
    11: 13,
    12: 35,
    13: 19,
    14: 3,
    15: 6,
}


def built_parts(build: Path) -> tuple[list[tuple[int, bytes]], bytes]:
    raw = (build / "MMPACK.PCA").read_bytes()
    _, entries = split_header(raw)
    _, code, _ = decompress_entries(raw)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size
    sites = []
    for address, _, new in PATCHES:
        size = len(as_bytes(new))
        built = code[address - base : address - base + size]
        if built != as_bytes(new):
            raise SystemExit(f"{address:#x}: build differs from the patch table")
        sites.append((address, built))
    table, _ = decompress_file((build / "MC09.SHP").read_bytes())
    return sites, table[TABLE_FILE : TABLE_FILE + TABLE_SIZE]


def main(build: Path, out: Path, runs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    sites, english = built_parts(build)
    originals = {address: as_bytes(old) for address, old, _ in PATCHES}
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
                    for address, data in sites:
                        found = agent.bus_read(address, len(data))
                        if found != originals[address]:
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, data)
                    agent.bus_write(TABLE_RAM, english)
                    draw = int(run)
                    agent.bus_write(SEED, SEEDS[draw].to_bytes(2, "big"))
                    entry["seed"] = SEEDS[draw]
                    index = draw & 7
                    entry["expected"] = english[100 * index : 100 * index + 100].hex()
                    entry["expected_pointer"] = f"{TABLE_RAM + 100 * index:#010x}"
                agent.frames(TO_QUOTE)
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
    summary = {
        k: (
            v["pointer"],
            v.get("expected_pointer"),
            v.get("expected") in (None, v["codes_at_quote"]),
        )
        for k, v in result.items()
        if isinstance(v, dict)
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    runs = sys.argv[3:] or ["control", *[str(r) for r in range(16)]]
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), runs))

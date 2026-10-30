"""EXP-0047: show every one of a character's 16 Saturn quote draws with the M8 build.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0047/force_draws.py \\
        CASE BUILD OUT [RUN ...]

Copied from `research/experiments/EXP-0032/force_draws.py` (this repository,
commit ``7196075``) for `END-015`. The changes, so that the M8 build's
version-4 code and files are what is written:

- the sites are `tools.disc.english_mode.patches_v4` for ``SLOTS`` with
  the M8 ending slots ``ENDING_SLOTS``, not ``patches_v3``;
- the table written is the build's from the quote table to the end of its
  English ending records (800 + 100n bytes), so a read past English record
  7 sees the build's bytes.

`EXP-0032`'s copy was itself copied from `EXP-0028`'s, generalized from
`EXP-0024`'s.

CASE is ``ryu`` or ``ken`` (state, paused seed, frames to the
quote, table address and draw seeds below). BUILD holds ``MMPACK.PCA`` and the
MC files from `tools.disc.build_english`.

From the case's `pre_ko` state, paused at a fixed RNG position, a forced run
writes into RAM:

- the code and slot bytes at every `tools.disc.english_mode.patches_v4`
  site;
- the character's English table and ending records.

Both are taken from the decoded BUILD files, after checking that RAM held
the original bytes. The run then steers the draw by writing the RNG seed word
with the seed found for it (``seed_scan.py``). It plays to the quote screen
and saves a screenshot, VDP1 VRAM, the pointer, the 100 bytes shown, and the
compiler's record for that draw (English record ``R & 7``). Runs:
``control`` (nothing written) and ``0``-``15``. Outputs go to the ignored OUT.
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
from tools.disc.english_mode import as_bytes, patches_v4
from tools.disc.prs import decompress_entries, decompress_file, split_header
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
SLOTS = list(range(18))  # the M5 roster's English slots (RE-008)
ENDING_SLOTS = [*range(8), *range(9, 18)]  # the M8 roster (END-011)
SEED, POINTER, TABLE_SIZE = 0x060F545A, 0x060F2490, 800
CASES: dict[str, dict[str, object]] = {
    "ryu": {
        "state": "local/checkpoints/dbg003/f00009769.mcs",
        "state_seed": 8520,
        "frames": 660,
        "file": "MC09.SHP",
        "table_file": 0x25D8,
        "table_ram": 0x0024F5D8,
        "ending_records": 7,
        # EXP-0024 seed_scan.py, local/re003/scan1-4
        "seeds": [2, 12, 15, 8, 21, 33, 17, 27029, 5, 26, 1, 13, 35, 19, 3, 6],
    },
    "ken": {
        "state": "local/checkpoints/re004/f00007684.mcs",
        "state_seed": 9501,
        "frames": 700,
        "file": "MC0A.SHP",
        "table_file": 0x2A4C,
        "table_ram": 0x0024FA4C,
        "ending_records": 4,
        # EXP-0028 seed_scan.py, local/re007/scan1 (seeds 1-60) and scan2 (repeat)
        "seeds": [15, 20, 25, 2, 35, 24, 4, 9, 7, 12, 1, 3, 8, 13, 5, 10],
    },
}


def built_parts(
    build: Path, case: dict[str, object]
) -> tuple[list[tuple[int, bytes, bytes]], bytes]:
    raw = (build / "MMPACK.PCA").read_bytes()
    _, entries = split_header(raw)
    _, code, _ = decompress_entries(raw)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size
    sites = []
    for address, old, new in patches_v4(SLOTS, ENDING_SLOTS):
        size = len(as_bytes(new))
        built = code[address - base : address - base + size]
        if built != as_bytes(new):
            raise SystemExit(f"{address:#x}: build differs from the patch table")
        sites.append((address, as_bytes(old), built))
    table, _ = decompress_file((build / str(case["file"])).read_bytes())
    start = int(str(case["table_file"]))
    size = TABLE_SIZE + 100 * int(str(case["ending_records"]))
    return sites, table[start : start + size]


def main(case_name: str, build: Path, out: Path, runs: list[str]) -> int:
    case = CASES[case_name]
    seeds = case["seeds"]
    assert isinstance(seeds, list)
    if len(seeds) != 16:
        raise SystemExit(f"{case_name}: no seed for every draw yet")
    out.mkdir(parents=True, exist_ok=False)
    configure()
    sites, english = built_parts(build, case)
    table_ram = int(str(case["table_ram"]))
    state_seed = int(str(case["state_seed"]))
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
                    agent.loadstate(Path(str(case["state"])).resolve())
                    agent.pause()
                    if int.from_bytes(agent.bus_read(SEED, 2), "big") == state_seed:
                        break
                    agent.run()
                else:
                    raise RuntimeError(f"never paused at seed {state_seed}")
                entry: dict[str, object] = {}
                if run != "control":
                    for address, original, data in sites:
                        found = agent.bus_read(address, len(data))
                        if found != original:
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, data)
                    agent.bus_write(table_ram, english)
                    draw = int(run)
                    agent.bus_write(SEED, int(seeds[draw]).to_bytes(2, "big"))
                    entry["seed"] = seeds[draw]
                    index = draw & 7
                    entry["expected"] = english[100 * index : 100 * index + 100].hex()
                    entry["expected_pointer"] = f"{table_ram + 100 * index:#010x}"
                agent.frames(int(str(case["frames"])))
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
    runs = sys.argv[4:] or ["control", *[str(r) for r in range(16)]]
    raise SystemExit(main(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), runs))

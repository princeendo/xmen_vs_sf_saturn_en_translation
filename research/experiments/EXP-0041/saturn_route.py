"""EXP-0041: a no-play Saturn route from the select screen to Nash's ending.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0041/saturn_route.py CUE MC10 OUT \\
        [--area FIRST:LAST] [--frames N] [--mmpack BUILT_MMPACK]

The pick and its key sending come from `research/experiments/EXP-0036/pick_writer.py`
(this repository, commit ``752984c``): the select state
``local/checkpoints/re004/f00002973.mcs`` (cursor on Ken), ``u`` to Nash, then
button A. Here A is then pressed ``PRESSES`` more times, ``GAP`` seconds
apart, to pick the partner and pass the mode screen. Mednafen is brought to
the front to receive the keys, and the key home is ``local/mednafen_pick``.

The select state was saved on the untouched image after Start, so its RAM
already holds the original ``MMPACK.PCA`` code; only files loaded later (the
picked characters' MC files, ``MCED``) come from CUE. With ``--mmpack``, every
byte where BUILT_MMPACK's decoded streams differ from the untouched file's is
written into RAM right after the state loads. Each range is checked against
the original first. This gives the build's code in RAM, as a cold boot of
CUE would. (The first two runs, ``route_after`` and ``route_rest``, lacked
this and ran the original code; see the README.)

After the presses the emulator is paused, and Nash's buffer
(``0x0024D000``) is compared with MC10 (the file to expect, decoded) plus the
`EXP-0025` fix-ups. That is the load check. Then, for N frames (default
30,000), the run alternates:

- set the CPU side's vitality words ``0x060F4610`` and ``0x060F4E10`` to 0
  (the Saturn twins of the arcade route's ``0xFF4610``/``0xFF4E10``, found
  in `EXP-0041` RAM dumps);
- run ``STEP`` frames.

A screenshot is saved every ``SHOT_EVERY`` frames, and every change of the
quote pointer ``0x060F2490`` is logged with its frame.

With ``--area``, read breakpoints in log mode cover FIRST-LAST (hex, plus
the cache-through mirror). Hits are counted by PC, and by whether the quote
pointer was inside that area at the time. Outputs go to the ignored OUT.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0025"))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0032"))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0036"))
from analyze import fixups
from pick_roster import KEYS, pick_home
from pick_writer import send

from tools.disc.build_english import read_file
from tools.disc.prs import decompress_entries, decompress_file, split_header
from tools.mednafen.agent import Agent, AgentError

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
STATE = Path("local/checkpoints/re004/f00002973.mcs")
MOVES, PRESSES, GAP = "u", 6, 1.0
BASE = 0x0024D000
VITALITY = (0x060F4610, 0x060F4E10)
POINTER = 0x060F2490
STEP, SHOT_EVERY = 20, 120


def code_ranges(built: bytes) -> list[tuple[int, bytes, bytes]]:
    """(RAM address, original, built) for each run of differing decoded bytes."""
    raw = read_file("MMPACK.PCA;1")
    _, entries = split_header(raw)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size
    _, old, _ = decompress_entries(raw)
    _, new, _ = decompress_entries(built)
    if len(old) != len(new):
        raise ValueError("decoded MMPACK sizes differ")
    ranges, start = [], None
    for i in range(len(old) + 1):
        same = i == len(old) or old[i] == new[i]
        if not same and start is None:
            start = i
        if same and start is not None:
            ranges.append((base + start, old[start:i], new[start:i]))
            start = None
    return ranges


def write_code(agent: Agent, built: Path) -> int:
    ranges = code_ranges(built.read_bytes())
    for address, old, new in ranges:
        found = agent.bus_read(address, len(old))
        if found != old:
            raise RuntimeError(f"{address:#x}: {found.hex()}")
        agent.bus_write(address, new)
    return len(ranges)


def parse(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("mc10", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--area")
    parser.add_argument("--frames", type=int, default=30000)
    parser.add_argument("--mmpack", type=Path)
    args = parser.parse_args(argv)
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    (out / "shots").mkdir()
    decoded, _ = decompress_file(args.mc10.read_bytes())
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    ranges: list[str] = []
    area: tuple[int, int] | None = None
    if args.area:
        first, last = (int(v, 16) for v in args.area.split(":"))
        area = (first, last)
        ranges = [
            f"{first:08X}-{last:08X}",
            f"{first | 0x20000000:08X}-{last | 0x20000000:08X}",
        ]
    result: dict[str, object] = {
        "cue": str(args.cue),
        "mc10": str(args.mc10),
        "area": ranges,
    }
    pointer_log: list[tuple[int, str]] = []
    hits_in: dict[str, int] = {}
    hits_out: dict[str, list[int]] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            if args.mmpack is not None:
                agent.pause()
                result["mmpack_ranges"] = write_code(agent, args.mmpack)
                agent.run()
            time.sleep(0.5)
            send(process.pid, [(KEYS[m][0], 0.1) for m in MOVES])
            for _ in range(1 + PRESSES):
                send(process.pid, [("k", 0.2)])
                time.sleep(GAP)
            agent.pause()
            agent.screenshot((out / "after_pick.png").resolve())
            ram = agent.bus_read(BASE, len(decoded))
            total, unaligned, exact = fixups(decoded, ram, BASE + 0x40)
            result["load_check"] = {
                "fixups": total,
                "fixups_2_aligned": unaligned,
                "ram_equals_mc10_plus_fixups": exact,
            }
            if ranges:
                agent.bpmode("log")
                agent.breakpoints("read", ranges)
            frame, last_pointer = 0, None
            while frame < args.frames:
                for address in VITALITY:
                    agent.bus_write(address, bytes(2))
                agent.clear_events()
                agent.frames(STEP)
                agent.wait_halted(60.0)
                frame += STEP
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                if pointer != last_pointer:
                    pointer_log.append((frame, f"{pointer:#010x}"))
                    last_pointer = pointer
                if ranges:
                    inside = area is not None and area[0] <= pointer <= area[1]
                    for line in agent.events():
                        if line.startswith("hit"):
                            pc = parse(line).get("PC", "?")
                            if inside:
                                hits_in[pc] = hits_in.get(pc, 0) + 1
                            else:
                                hits_out.setdefault(pc, []).append(frame)
                if frame % SHOT_EVERY == 0:
                    agent.screenshot((out / "shots" / f"r{frame:06d}.png").resolve())
            if ranges:
                agent.breakpoints("read", [])
                agent.bpmode("halt")
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["pointer_changes"] = pointer_log
    result["hits_while_pointer_in_area"] = hits_in
    result["hits_while_pointer_elsewhere"] = {
        pc: {"count": len(f), "first": f[0], "last": f[-1]}
        for pc, f in hits_out.items()
    }
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "load_check",
                    "hits_while_pointer_in_area",
                    "hits_while_pointer_elsewhere",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

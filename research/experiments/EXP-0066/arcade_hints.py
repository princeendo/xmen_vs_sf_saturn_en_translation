"""EXP-0066: run the arcade continue-hint starter with a forced index.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0066/arcade_hints.py OUT RUN...

Each RUN is ``LANG:INDEX``: ``LANG`` is ``en`` (the US set's own language
word) or ``jp`` (language word ``0xFF547A`` and record-size word ``0xFF5478``
set to 0 at frame 6100, as in `EXP-0022`). ``INDEX`` (0-15) is forced into D0
at ``0x04F434``, right after the starter's ``andi.w #$f, D0`` (``0x04F430``),
or ``-`` to leave the game's own value.

Adapted from `research/experiments/EXP-0022/run_pair.py` (this repository,
the win-quote selector): the same `EXP-0009` route, NVRAM and configuration
copies, and headless MAME 0.289 with its debugger. Breakpoints print the
index before and after the starter's map and the table base it stores; reads
of ``0x180000``-``0x18E179`` are logged; snapshots at ``SNAPS`` show both
hint pages. Outputs go to the ignored ``OUT/<run>/``; a summary is printed.
The game data is never written; only D0 and the two language words are set.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ROMS = ROOT / "local/arcade_roms/xmvsf_mame0289"
STATE = ROOT / "local/ref004"  # EXP-0009 NVRAM and configuration
SCRIPT = ROOT / "tools/reference/mame_timeline.lua"
ROUTE = """1000 repeat 4 30 8 Coin 1
1200 repeat 10 60 8 1 Player Start
1900 repeat 40 30 8 P1 Button 1
"""
SIZES = {"jp": 76, "en": 100}
SNAPS = (6600, 7000)
RECORD_READER = "04f612"  # EXP-0009: reads the printed record's text


def timeline(lang: str, index: str, run_dir: Path) -> str:
    rand = 'printf "rand d0=%08x",d0'
    if index != "-":
        rand = f"d0=(d0&ffff0000)|{int(index):x};" + rand
    lines = [
        ROUTE,
        f"5000 debug bpset 4f434,1,{{{rand};g}}",
        '5000 debug bpset 4f44c,1,{printf "index d0=%08x lang=%04x",d0,w@ff547a;g}',
        '5000 debug bpset 4f464,1,{printf "base long=%08x",d@(a0+34)}',
        "5000 debug bpset 4f464,1,{g}",
        f"5000 logreads 0x180000 0x18E179 {run_dir / 'reads.txt'}",
    ]
    if lang == "jp":
        lines += ["6100 debug do w@ff547a=0", "6100 debug do w@ff5478=0"]
    lines += [f"{frame} snap" for frame in SNAPS]
    lines += [f"{SNAPS[-1] + 100} exit", ""]
    return "\n".join(lines)


def run(out: Path, spec: str) -> dict[str, object]:
    lang, index = spec.split(":")
    name = spec.replace(":", "_").replace("-", "x")
    run_dir = (out / name).resolve()
    run_dir.mkdir(parents=True)
    shutil.copytree(STATE / "nvram", run_dir / "nvram")
    shutil.copytree(STATE / "cfg", run_dir / "cfg")
    (run_dir / "timeline.txt").write_text(timeline(lang, index, run_dir))
    command = [
        "mame", "xmvsfu", "-rompath", str(ROMS), "-video", "none", "-sound", "none",
        "-nothrottle", "-skip_gameinfo", "-nomouse", "-cfg_directory", "cfg",
        "-nvram_directory", "nvram", "-homepath", ".", "-snapshot_directory", "snap",
        "-debug", "-debugger", "none", "-debuglog", "-autoboot_script", str(SCRIPT),
    ]  # fmt: skip
    env = {**os.environ, "MAME_TIMELINE": str(run_dir / "timeline.txt")}
    with (run_dir / "mame.log").open("wb") as log:
        subprocess.run(
            command, cwd=run_dir, env=env, stdout=log, stderr=log, check=True
        )
    debug = (run_dir / "debug.log").read_text()
    steps = [
        line for line in debug.splitlines() if re.match(r"(rand|index|base) ", line)
    ]
    reads = (run_dir / "reads.txt").read_text().split()
    texts = [
        (int(reads[i]), int(reads[i + 2], 16))
        for i in range(0, len(reads), 3)
        if reads[i + 1] == RECORD_READER
    ]
    result: dict[str, object] = {"run": spec, "steps": steps}
    base_text = re.search(r"base long=([0-9a-f]+)", debug)
    if base_text:
        base = int(base_text.group(1), 16)
        result["pages"] = [
            {
                "frame": frame,
                "address": f"{address:#x}",
                "record": (address - base) / SIZES[lang],
            }
            for frame, address in texts
            if address >= base
        ]
    return result


def main(out: Path, specs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    results = [run(out, spec) for spec in specs]
    (out / "summary.json").write_text(json.dumps(results, indent=1) + "\n")
    print(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))

"""EXP-0030: run the arcade win-quote selector with a forced draw, in either language.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0030/run_pair.py OUT RUN...

Copied from `research/experiments/EXP-0022/run_pair.py` (this repository,
commit ``890875d``). The one change: text reads are logged from ``READ_START``
(``0x17E000``) instead of ``0x180000``, so the Japanese records of slots 0-5
(``0x17E3FC`` up) are logged too. The original description follows.

Each RUN is ``LANG:SLOT:R``: ``LANG`` is ``en`` (the US set's own language
word, 2) or ``jp`` (language word ``0xFF547A`` and record-size word ``0xFF5478``
set to 0 at frame 6100). ``SLOT`` is the speaker's slot, or ``-`` to leave
it. ``R`` is the value forced into D0 after the random call at
``0x04F3B2``, or ``-`` to leave it.

Every run boots ``xmvsfu`` in MAME 0.289 on the `EXP-0009` route, with a copy
of `EXP-0009`'s NVRAM and configuration. Debugger breakpoints (printing, then
continuing) log each step of the selector at ``0x04F396``. Reads of the text
area are logged, and a snapshot is taken at frame 6280. Outputs go to the
ignored ``OUT/<run>/``, and a summary is printed. The game data is never
written; only registers and the two language words are set.
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
TABLES = {"jp": 0x17E19C, "en": 0x17E1E8}
READ_START = 0x17E000  # below the first Japanese record (0x17E3FC)
SIZES = {"jp": 76, "en": 100}


def timeline(lang: str, slot: str, draw: str, run_dir: Path) -> str:
    entry = 'printf "entry a0=%08x d1=%08x",a0,d1'
    if slot != "-":
        entry = f"d1={2 * int(slot):x};" + entry
    rand = 'printf "rand d0=%08x",d0'
    if draw != "-":
        rand = f"d0=(d0&ffff0000)|{int(draw):x};" + rand
    lines = [
        ROUTE,
        f"5000 debug bpset 4f396,1,{{{entry};g}}",
        f"5000 debug bpset 4f3b2,1,{{{rand};g}}",
        '5000 debug bpset 4f3c6,1,{printf "index d0=%08x",d0;g}',
        '5000 debug bpset 4f3d2,1,{printf "lang d0=%08x",d0;g}',
        '5000 debug bpset 4f3da,1,{printf "base long=%08x",d@(a1+d1);g}',
        f"5000 logreads {READ_START:#x} 0x18E179 {run_dir / 'reads.txt'}",
    ]
    if lang == "jp":
        lines += ["6100 debug do w@ff547a=0", "6100 debug do w@ff5478=0"]
    lines += ["6280 snap", "6400 exit", ""]
    return "\n".join(lines)


def run(out: Path, spec: str) -> dict[str, object]:
    lang, slot, draw = spec.split(":")
    name = spec.replace(":", "_").replace("-", "x")
    run_dir = (out / name).resolve()
    run_dir.mkdir(parents=True)
    shutil.copytree(STATE / "nvram", run_dir / "nvram")
    shutil.copytree(STATE / "cfg", run_dir / "cfg")
    (run_dir / "timeline.txt").write_text(timeline(lang, slot, draw, run_dir))
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
        line
        for line in debug.splitlines()
        if re.match(r"(entry|rand|index|lang|base) ", line)
    ]
    reads = (
        (run_dir / "reads.txt").read_text().split()
        if (run_dir / "reads.txt").exists()
        else []
    )
    first = next(
        (
            int(reads[i + 2], 16)
            for i in range(0, len(reads), 3)
            if reads[i + 1] == "04f612"
        ),
        None,
    )
    base_text = re.search(r"base long=([0-9a-f]+)", debug)
    result: dict[str, object] = {
        "run": spec,
        "steps": steps,
        "first_text_read": f"{first:#x}" if first else None,
    }
    if base_text and first is not None:
        base = int(base_text.group(1), 16)
        size = SIZES[lang]
        result["record"] = (first - base) / size
    return result


def main(out: Path, specs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    results = [run(out, spec) for spec in specs]
    (out / "summary.json").write_text(json.dumps(results, indent=1) + "\n")
    print(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))

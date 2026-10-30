"""EXP-0044: run one MAME timeline on the US arcade set, headless, with a debug log.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0044/run_mame.py OUT TIMELINE [SET]

Copied unchanged from `research/experiments/EXP-0037/run_mame.py` (this
repository, commit ``606467a``) except this paragraph, the first line and
the usage line.
The run setup is `research/experiments/EXP-0030/run_pair.py`'s (this
repository, commit ``473d107``): MAME 0.289, ``xmvsfu`` by default, a copy of
`EXP-0009`'s NVRAM and configuration, ``-debug -debugger none -debuglog``,
and `tools/reference/mame_timeline.lua`. TIMELINE is a timeline file in that
script's format. Inside it, ``{run}`` is replaced with the absolute run
directory, so dumps and logs land in OUT. Snapshots go to ``OUT/snap``. The
game data is never written. Outputs go to the ignored OUT.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ROMS = ROOT / "local/arcade_roms/xmvsf_mame0289"
STATE = ROOT / "local/ref004"  # EXP-0009 NVRAM and configuration
SCRIPT = ROOT / "tools/reference/mame_timeline.lua"


def run(out: Path, timeline: Path, game: str = "xmvsfu") -> int:
    run_dir = out.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    shutil.copytree(STATE / "nvram", run_dir / "nvram")
    shutil.copytree(STATE / "cfg", run_dir / "cfg")
    text = timeline.read_text().replace("{run}", str(run_dir))
    (run_dir / "timeline.txt").write_text(text)
    command = [
        "mame", game, "-rompath", str(ROMS), "-video", "none", "-sound", "none",
        "-nothrottle", "-skip_gameinfo", "-nomouse", "-cfg_directory", "cfg",
        "-nvram_directory", "nvram", "-homepath", ".", "-snapshot_directory", "snap",
        "-debug", "-debugger", "none", "-debuglog", "-autoboot_script", str(SCRIPT),
    ]  # fmt: skip
    env = {**os.environ, "MAME_TIMELINE": str(run_dir / "timeline.txt")}
    with (run_dir / "mame.log").open("wb") as log:
        result = subprocess.run(command, cwd=run_dir, env=env, stdout=log, stderr=log)
    return result.returncode


if __name__ == "__main__":
    game = sys.argv[3] if len(sys.argv) > 3 else "xmvsfu"
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2]), game))

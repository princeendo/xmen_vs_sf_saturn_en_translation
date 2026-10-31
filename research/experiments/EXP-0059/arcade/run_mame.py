r"""EXP-0059: run one MAME timeline on the US set, headless.

A copy of ``research/experiments/EXP-0044/run_mame.py`` (HEAD 03bca0c) with
SCRIPT pointed at this folder's ``mame_timeline_op.lua`` and MAME's full path.

Run from the repository root:

    python3 research/experiments/EXP-0059/arcade/run_mame.py OUT TIMELINE
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ROMS = ROOT / "local/arcade_roms/xmvsf_mame0289"
STATE = ROOT / "local/ref004"
SCRIPT = ROOT / "research/experiments/EXP-0059/arcade/mame_timeline_op.lua"


def run(out, timeline, game="xmvsfu"):
    run_dir = out.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    shutil.copytree(STATE / "nvram", run_dir / "nvram")
    shutil.copytree(STATE / "cfg", run_dir / "cfg")
    text = timeline.read_text().replace("{run}", str(run_dir))
    (run_dir / "timeline.txt").write_text(text)
    command = [
        "/opt/homebrew/bin/mame",
        game,
        "-rompath",
        str(ROMS),
        "-video",
        "none",
        "-sound",
        "none",
        "-nothrottle",
        "-skip_gameinfo",
        "-nomouse",
        "-cfg_directory",
        "cfg",
        "-nvram_directory",
        "nvram",
        "-homepath",
        ".",
        "-snapshot_directory",
        "snap",
        "-debug",
        "-debugger",
        "none",
        "-debuglog",
        "-autoboot_script",
        str(SCRIPT),
    ]
    env = {**os.environ, "MAME_TIMELINE": str(run_dir / "timeline.txt")}
    with (run_dir / "mame.log").open("wb") as log:
        return subprocess.run(
            command, cwd=run_dir, env=env, stdout=log, stderr=log
        ).returncode


if __name__ == "__main__":
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))

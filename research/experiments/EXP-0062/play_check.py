r"""EXP-0062: the user's cold-boot play check of the special cases.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0062/play_check.py OUT

Two boots, one after another (``BOOTS``): the American-names image
(`EXP-0061`: ``build/spec004_us``), then the Saturn-names image
(``build/spec004_saturn``), each with the 4 MB cart and a valid save.

Adapted from `EXP-0057/play_check.py` (its ``make_home`` and ``fixture`` are
loaded from that file): each boot gets a fresh copy of the interactive home
``local/mednafen`` (the user's pad settings and sound), ``OUT/homes/<boot>``,
and the user's own home is never written. Mednafen opens on the image with the
agent interface, and `tools.mednafen.session_recorder` keeps a screenshot every
``SHOT_INTERVAL`` seconds (a boss box is on screen about 2 seconds) and the
newest ``KEEP_STATES`` states, one a minute, in ``OUT/<boot>/``. When the user
closes the window, the recorder is stopped and the next boot opens.
``OUT/boots.json`` records each boot's image, fixture hash and times. OUT is an
ignored path.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY

_SPEC = importlib.util.spec_from_file_location(
    "exp0057", "research/experiments/EXP-0057/play_check.py"
)
assert _SPEC and _SPEC.loader
EXP0057 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(EXP0057)

CUE = EXP0057.CUE
BOOTS = [
    ("us", "build/spec004_us"),
    ("saturn", "build/spec004_saturn"),
]
SHOT_INTERVAL, KEEP_STATES = 0.5, 30


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    record = []
    data = EXP0057.fixture("valid")
    for name, image in BOOTS:
        home = (out / "homes" / name).resolve()
        EXP0057.make_home(home, "extram4", data)
        agent = (out / name / "agent").resolve()
        agent.mkdir(parents=True)
        env = {
            **os.environ,
            "MEDNAFEN_HOME": str(home),
            "MEDNAFEN_AGENT_DIR": str(agent),
        }
        print(f"opening {name}", flush=True)
        start = time.time()
        with (out / f"{name}.log").open("wb") as log:
            game = subprocess.Popen(
                [str(BINARY), str(Path(image) / CUE)], env=env, stdout=log, stderr=log
            )
            recorder = subprocess.Popen(
                [
                    *(sys.executable, "-m", "tools.mednafen.session_recorder"),
                    *(str(out / name), "--agent-dir", str(agent)),
                    *("--state-interval", "60", "--keep-states", str(KEEP_STATES)),
                    *("--shot-interval", str(SHOT_INTERVAL)),
                ],
                stdout=log,
                stderr=log,
            )
            game.wait()
            (out / name / "STOP").touch()
            recorder.wait(timeout=60)
        record.append(
            {
                "boot": name,
                "image": image,
                "cart": "extram4",
                "fixture": "valid",
                "fixture_sha256": hashlib.sha256(data).hexdigest(),
                "seconds": round(time.time() - start, 1),
            }
        )
        (out / "boots.json").write_text(json.dumps(record, indent=1) + "\n")
    print("all boots done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

r"""EXP-0057: the user's cold-boot play check of the English boot warnings.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0057/play_check.py OUT

Six boots, one after another, in this order (``BOOTS``): for each built image
(`EXP-0056`: ``build/boot004_us``, then ``build/boot004_saturn``) a no-cart
boot, a boot with a save-memory problem (a damaged save for the American
image, too little free space for the Saturn-names image), and a normal boot
with the 4 MB cart and a valid save.

Each boot gets a fresh copy of the interactive home ``local/mednafen`` (the
user's pad settings and sound), ``OUT/homes/<boot>``: ``ss.cart`` set, and the
backup memory replaced by the boot's fixture (`tools.mednafen.backup_ram`;
``valid`` is a copy of the silent home's save, as in `EXP-0053`). The user's
own home is never written. Mednafen opens on the image with the agent
interface, and `tools.mednafen.session_recorder` keeps screenshots every
second in ``OUT/<boot>/``. When the user closes the window, the recorder is
stopped and the next boot opens. ``OUT/boots.json`` records each boot's image,
cart, fixture hash and times. OUT is an ignored path.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.backup_ram import corrupt, with_free
from tools.mednafen.home import QUIET_HOME, apply_settings
from tools.mednafen.replay_state import BINARY

HOME = Path("local/mednafen")
SAVE_NAME = "X-Men vs. Street Fighter (Japan) (3M).cead02d9d3cc1b97c82dbf063fba19bf"
CUE = "X-Men vs. Street Fighter (Japan) (3M).cue"
BOOTS = [
    ("us_no_cart", "build/boot004_us", "none", "valid"),
    ("us_damaged_save", "build/boot004_us", "extram4", "corrupt"),
    ("us_normal", "build/boot004_us", "extram4", "valid"),
    ("saturn_no_cart", "build/boot004_saturn", "none", "valid"),
    ("saturn_no_space", "build/boot004_saturn", "extram4", "free18"),
    ("saturn_normal", "build/boot004_saturn", "extram4", "valid"),
]


def fixture(kind: str) -> bytes:
    valid = (QUIET_HOME / "sav" / f"{SAVE_NAME}.bkr").read_bytes()
    if kind == "valid":
        return valid
    if kind == "corrupt":
        return bytes(corrupt(valid))
    if kind.startswith("free"):
        return bytes(with_free(int(kind.removeprefix("free"))))
    raise ValueError(kind)


def make_home(home: Path, cart: str, data: bytes) -> None:
    shutil.copytree(
        HOME,
        home,
        symlinks=True,
        ignore=shutil.ignore_patterns("*.lck", "agent", "mcs", "snaps"),
    )
    for old in (home / "sav").glob(f"{SAVE_NAME}.b*"):
        old.unlink()
    (home / "sav" / f"{SAVE_NAME}.bkr").write_bytes(data)
    apply_settings(home / "mednafen.cfg", {"ss.cart": cart})


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    record = []
    for name, image, cart, kind in BOOTS:
        data = fixture(kind)
        home = (out / "homes" / name).resolve()
        make_home(home, cart, data)
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
                    *("--state-interval", "3600", "--keep-states", "1"),
                    *("--shot-interval", "1"),
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
                "cart": cart,
                "fixture": kind,
                "fixture_sha256": hashlib.sha256(data).hexdigest(),
                "seconds": round(time.time() - start, 1),
            }
        )
        (out / "boots.json").write_text(json.dumps(record, indent=1) + "\n")
    print("all boots done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

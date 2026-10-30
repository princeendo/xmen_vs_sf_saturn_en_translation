r"""EXP-0053: cold-boot an image under each cart and backup-memory condition.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0053/census.py CUE OUT \
        [CASE ...] [--first F] [--last L] [--step S] [--parallel N]

Each CASE (``CASES`` below, all by default) gets a fresh Mednafen home,
``OUT/homes/<case>``: the silent home's ``mednafen.cfg``, ``firmware/`` and
clock file (``.smpc``) copied, ``ss.cart`` set to the case's cart, and the
case's backup-RAM fixture written to ``sav/`` under the image's save name
(``SAVE_NAME``). The silent home itself is never changed. Then
`tools.mednafen.frame_capture` boots CUE cold with no input and takes
screenshots at F, F + S, ... L into ``OUT/<case>/``.

Fixtures (`tools.mednafen.backup_ram`; ``valid`` is a copy of the silent
home's own save, which holds this game's file):

- ``valid``: the game's save (the control);
- ``zero``: all zero (unformatted);
- ``corrupt``: ``valid`` with one byte inside the game's file inverted;
- ``freeN``: formatted, one dummy file, N blocks free, no save of this game.

``OUT/census.json`` records, per case, the cart, the fixture's SHA-256, the
save files in ``sav/`` after the run with their hashes (so that a renamed
save file or a rewrite by the game is seen), and the screenshots. OUT is an
ignored path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools.mednafen.backup_ram import corrupt, with_free
from tools.mednafen.home import QUIET_HOME, apply_settings

SAVE_NAME = "X-Men vs. Street Fighter (Japan) (3M).cead02d9d3cc1b97c82dbf063fba19bf"
CASES: dict[str, tuple[str, str]] = {
    "extram4_valid": ("extram4", "valid"),
    "none_valid": ("none", "valid"),
    "backup_valid": ("backup", "valid"),
    "extram1_valid": ("extram1", "valid"),
    "cs1ram16_valid": ("cs1ram16", "valid"),
    "extram4_zero": ("extram4", "zero"),
    "extram4_corrupt": ("extram4", "corrupt"),
    "extram4_free509": ("extram4", "free509"),
    "extram4_free19": ("extram4", "free19"),
    "extram4_free18": ("extram4", "free18"),
    "extram4_free17": ("extram4", "free17"),
    "extram4_free0": ("extram4", "free0"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixture(kind: str, valid: bytes) -> bytes:
    if kind == "valid":
        return valid
    if kind == "zero":
        return bytes(len(valid))
    if kind == "corrupt":
        return bytes(corrupt(valid))
    if kind.startswith("free"):
        return bytes(with_free(int(kind.removeprefix("free"))))
    raise ValueError(f"unknown fixture {kind}")


def make_home(home: Path, cart: str, data: bytes) -> None:
    home.mkdir(parents=True)
    shutil.copy(QUIET_HOME / "mednafen.cfg", home / "mednafen.cfg")
    shutil.copytree(QUIET_HOME / "firmware", home / "firmware")
    (home / "sav").mkdir()
    shutil.copy(QUIET_HOME / "sav" / f"{SAVE_NAME}.smpc", home / "sav")
    apply_settings(home / "mednafen.cfg", {"ss.cart": cart})
    (home / "sav" / f"{SAVE_NAME}.bkr").write_bytes(data)


def run(
    cue: Path, out: Path, case: str, frames: tuple[int, int, int]
) -> dict[str, object]:
    cart, kind = CASES[case]
    valid = (QUIET_HOME / "sav" / f"{SAVE_NAME}.bkr").read_bytes()
    data = fixture(kind, valid)
    home = out / "homes" / case
    make_home(home, cart, data)
    first, last, step = frames
    log = out / f"{case}.log"
    with log.open("wb") as handle:
        subprocess.run(
            [
                *("./invenv.sh", "python", "-m", "tools.mednafen.frame_capture"),
                *(str(cue), str(out / case), "--home", str(home)),
                *("--agent-dir", str(home / "agent")),
                *("--first", str(first), "--last", str(last), "--step", str(step)),
            ],
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=True,
        )
    saves = {p.name: sha256(p.read_bytes()) for p in sorted((home / "sav").iterdir())}
    shots = {
        p.name: sha256(p.read_bytes()) for p in sorted((out / case).glob("f*.png"))
    }
    return {
        "cart": cart,
        "fixture": kind,
        "fixture_sha256": sha256(data),
        "saves_after": saves,
        "shots": shots,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("cases", nargs="*", default=list(CASES))
    parser.add_argument("--first", type=int, default=300)
    parser.add_argument("--last", type=int, default=3600)
    parser.add_argument("--step", type=int, default=150)
    parser.add_argument("--parallel", type=int, default=3)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=False)
    frames = (args.first, args.last, args.step)
    with ThreadPoolExecutor(args.parallel) as pool:
        futures = {
            c: pool.submit(run, args.cue, args.out, c, frames) for c in args.cases
        }
        result = {c: f.result() for c, f in futures.items()}
    (args.out / "census.json").write_text(json.dumps(result, indent=1) + "\n")
    for case, entry in result.items():
        print(case, str(entry["fixture_sha256"])[:8], entry["saves_after"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

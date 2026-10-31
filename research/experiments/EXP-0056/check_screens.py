r"""EXP-0056: compare boot-warning screenshots with the built pictures.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0056/check_screens.py \
        FILES SCREEN:ERRn.BIN [SCREEN:ERRn.BIN ...]

FILES is the build's output directory (``tools.disc.build_english``
``--boot-warnings``). Each SCREEN (a PNG screenshot of a warning) is compared,
pixel for pixel, with ``FILES/ERRn.BIN`` as the game shows it
(`tools.disc.boot_warnings.shown`: picture row y at screen row y + 8, the
game's colour rule). Prints, per pair, the pixels that differ; exits 1 if any
pair differs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent.parent / "EXP-0054"))
from compare_screen import read_png  # type: ignore[import-not-found]

from tools.disc.boot_warnings import HEIGHT, WIDTH, shown


def main(argv: list[str]) -> int:
    files = Path(argv[0])
    failed = False
    for pair in argv[1:]:
        screen, name = pair.rsplit(":", 1)
        width, height, pixels = read_png(Path(screen))
        if (width, height) != (WIDTH, HEIGHT):
            raise SystemExit(f"{screen}: {width} x {height}")
        want = shown((files / name).read_bytes())
        differ = sum(
            pixels[i : i + 3] != want[i : i + 3] for i in range(0, len(want), 3)
        )
        failed |= differ > 0
        print(f"{name} {screen}: {differ} of {WIDTH * HEIGHT} pixels differ")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

r"""EXP-0066: force every continue-hint index and capture the hint.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0066/force_hints.py \
        CUE STATE OUT [INDEX ...]

For each INDEX (default 0-15), runs `continue_run.py` into ``OUT/iNN`` for
``FRAMES`` frames with one RAM change: the hint starter's ``and #0x0F,r0``
(``0x06066730``, ``C90F``) becomes ``mov #INDEX,r0`` (``E0nn``), so the
index is INDEX instead of the masked random value. Then copies the frame
``SHOT`` screenshot to ``OUT/iNN.png``. OUT is an ignored path.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_SPEC = importlib.util.spec_from_file_location(
    "continue_run", "research/experiments/EXP-0066/continue_run.py"
)
assert _SPEC and _SPEC.loader
CONTINUE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(CONTINUE)

MASK = 0x06066730
FRAMES, SHOT = 2400, 2370


def main(cue: Path, state: Path, out: Path, indexes: list[int]) -> int:
    out.mkdir(parents=True, exist_ok=True)
    for index in indexes:
        run = out / f"i{index:02d}"
        CONTINUE.main(cue, state, run, FRAMES, [f"{MASK:08X}:C90F:E0{index:02X}"])
        shutil.copy(run / "shots" / f"r{SHOT:05d}.png", out / f"i{index:02d}.png")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            [int(x) for x in a[3:]] or list(range(16)),
        )
    )

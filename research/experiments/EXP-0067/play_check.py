r"""EXP-0067: the user's cold-boot check of the English continue hints.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0067/play_check.py OUT [BOOT ...]

`EXP-0062/play_check.py` (loaded from that file) with its ``BOOTS`` replaced
by the ``--continue-hints`` builds: ``us`` (``build/hint002_us``), then
``saturn`` (``build/hint002_saturn``). Give BOOT names to open only those.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_SPEC = importlib.util.spec_from_file_location(
    "exp0062", "research/experiments/EXP-0062/play_check.py"
)
assert _SPEC and _SPEC.loader
EXP0062 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(EXP0062)

BOOTS = [("us", "build/hint002_us"), ("saturn", "build/hint002_saturn")]

if __name__ == "__main__":
    chosen = sys.argv[2:]
    boots = [b for b in BOOTS if not chosen or b[0] in chosen]
    EXP0062.BOOTS = boots  # type: ignore[attr-defined]
    raise SystemExit(EXP0062.main(Path(sys.argv[1])))

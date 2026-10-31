r"""EXP-0063: route one roster slot past the boss on a built image, for the sign.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0063/run_sign.py \
        CUE MMPACK OUT [SLOT ...]

`EXP-0061/run_boxes.py` (loaded from that file) with ``FRAMES`` raised to
``SIGN_FRAMES``, so that each run goes past the boss, through the post-boss
splash and quote, into the partner fight, where the sign shows. Screenshots
every 40 frames, as there. SLOT defaults to Ryu (9).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_SPEC = importlib.util.spec_from_file_location(
    "run_boxes", "research/experiments/EXP-0061/run_boxes.py"
)
assert _SPEC and _SPEC.loader
RUN_BOXES = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(RUN_BOXES)

SIGN_FRAMES = 13500
RYU = 9

if __name__ == "__main__":
    RUN_BOXES.FRAMES = SIGN_FRAMES
    raise SystemExit(
        RUN_BOXES.main(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            Path(sys.argv[3]),
            [int(s) for s in sys.argv[4:]] or [RYU],
        )
    )

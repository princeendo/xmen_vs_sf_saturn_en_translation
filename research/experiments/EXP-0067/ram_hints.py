r"""EXP-0067: the matched English continue hints, in RAM on the untouched image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0067/ram_hints.py \
        CUE STATE OUT [INDEX]

`EXP-0066/continue_run.py` for ``FRAMES`` frames with, at the load (each
original checked first):

- the English builds' renderer patches (`tools.disc.english_mode.PATCHES`,
  the entries from ``RENDERER_FROM`` on: the renderer reads the task byte
  instead of the global words, and the ending selector keeps reading 0);
- `tools.disc.continue_hints.patches()` (the starter, its base literal and
  the matched map);
- `tools.disc.continue_hints.table()` written at ``TABLE`` (zero before);
- with INDEX, the starter's mask forced to ``mov #INDEX,r0``
  (``0x06066730``, as `EXP-0066/force_hints.py`).

The arcade records come from ``local/ref003/xmvsfu-68k.bin``. OUT is an
ignored path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc import continue_hints
from tools.disc.english_mode import PATCHES

_SPEC = importlib.util.spec_from_file_location(
    "continue_run", "research/experiments/EXP-0066/continue_run.py"
)
assert _SPEC and _SPEC.loader
CONTINUE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(CONTINUE)

FRAMES = 3000
RENDERER_FROM = 0x06066948
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
MASK = 0x06066730


def hex_patch(address: int, old: str, new: str) -> str:
    return f"{address:08X}:{old.replace(' ', '')}:{new.replace(' ', '')}"


def main(cue: Path, state: Path, out: Path, index: int | None) -> int:
    renderer = [p for p in PATCHES if p[0] >= RENDERER_FROM or p[0] == 0x060668C4]
    table = continue_hints.table(PROGRAM.read_bytes())
    patches = [hex_patch(*p) for p in renderer + continue_hints.patches()]
    patches.append(
        hex_patch(continue_hints.TABLE, bytes(len(table)).hex(), table.hex())
    )
    if index is not None:
        patches.append(f"{MASK:08X}:C90F:E0{index:02X}")
    CONTINUE.main(cue, state, out, FRAMES, patches)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]) if len(a) > 3 else None)
    )

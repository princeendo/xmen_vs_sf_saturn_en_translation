r"""EXP-0066: show two arcade English hint records in the Saturn hint box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0066/fit_run.py \
        CUE STATE OUT FIRST SECOND [PROGRAM]

`continue_run.py` for ``FRAMES`` frames with the Saturn's own English path
switched on in RAM, all at the load (each original value checked first):

- the starter's index forced to 0 (``0x06066730`` ``C90F`` -> ``E000``);
- the English base long (``0x0606679C``) set to the Japanese table's
  address, ``0x06085544``, where the records are written;
- the record-size and language words ``0x060F5478`` and ``0x060F547A`` set
  to 2 (the US arcade's values, `EXP-0022`);
- the arcade's English area records FIRST and SECOND (270-293, 100 bytes
  each, from PROGRAM, default ``local/ref003/xmvsfu-68k.bin``) written over
  the first 200 bytes of the Japanese table (checked against the untouched
  ``MMPACK.PCA``, read from the source track).

The two pages show at about frames 2,370 and 2,760 (``OUT/shots``). OUT is
an ignored path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import decompress_entries
from tools.mednafen.route import SOURCE_TRACK, track_file

_SPEC = importlib.util.spec_from_file_location(
    "continue_run", "research/experiments/EXP-0066/continue_run.py"
)
assert _SPEC and _SPEC.loader
CONTINUE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(CONTINUE)

FRAMES = 3000
TABLE, SIZE = 0x06085544, 100
ENGLISH, FIRST_RECORD = 0x18D81A, 270
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
SEGMENT, SEGMENT_OFFSET = 0x0601F000, 0xA460  # MMPACK.PCA segment 2 (EXP-0066)


def main(cue: Path, state: Path, out: Path, records: list[int], program: Path) -> int:
    prog = program.read_bytes()
    _, mmpack, _ = decompress_entries(track_file(SOURCE_TRACK, "MMPACK.PCA;1"))
    at = TABLE - SEGMENT + SEGMENT_OFFSET
    original = mmpack[at : at + SIZE * len(records)]
    new = b"".join(
        prog[
            ENGLISH + SIZE * (r - FIRST_RECORD) : ENGLISH
            + SIZE * (r - FIRST_RECORD + 1)
        ]
        for r in records
    )
    patches = [
        "06066730:C90F:E000",
        "0606679C:06085B80:06085544",
        "060F5478:0000:0002",
        "060F547A:0000:0002",
        f"{TABLE:08X}:{original.hex().upper()}:{new.hex().upper()}",
    ]
    CONTINUE.main(cue, state, out, FRAMES, patches)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            [int(a[3]), int(a[4])],
            Path(a[5]) if len(a) > 5 else PROGRAM,
        )
    )

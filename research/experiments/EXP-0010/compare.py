"""EXP-0010: locate every arcade English record in a PS1 file (no game text output).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0010/compare.py \
        local/ref003/xmvsfu-68k.bin local/ref006/files/P/P4/SELECT.BIN

The first argument is the arcade program in 68000 order (as built by
``tools.reference.xvsf_text.build_program``). Each 100-byte arcade record
(`EXP-0008`) is byte-swapped (the PS1 is little-endian) and searched for. The
PS1 text run around the win quotes is then listed record by record as an
arcade record number or ``PS1`` for a record found nowhere in the arcade.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.xvsf_text import DECODE

AREA, RECORDS, SIZE = 0x186EA2, 294, 100


def swap(data: bytes) -> bytes:
    out = bytearray(len(data))
    out[0::2] = data[1::2]
    out[1::2] = data[0::2]
    return bytes(out)


def is_text(chunk: bytes) -> bool:
    codes = [int.from_bytes(chunk[i : i + 2], "little") for i in range(0, SIZE, 2)]
    known = all(c in DECODE or 0x0130 <= c <= 0x013F for c in codes)
    return known and any(c in DECODE and DECODE[c].isalpha() for c in codes)


def main(program: Path, ps1: Path) -> int:
    rom, data = program.read_bytes(), ps1.read_bytes()
    records = [
        swap(rom[AREA + SIZE * k : AREA + SIZE * (k + 1)]) for k in range(RECORDS)
    ]
    index = {record: k for k, record in enumerate(records)}
    offsets = [data.find(record) for record in records]
    groups: list[list[int]] = []
    for offset, k in sorted((o, k) for k, o in enumerate(offsets) if o >= 0):
        if groups and offset == groups[-1][1] + SIZE and k == groups[-1][3] + 1:
            groups[-1][1], groups[-1][3] = offset, k
        else:
            groups.append([offset, offset, k, k])
    start = min(o for o in offsets if o >= 0 and index[data[o : o + SIZE]] == 0)
    run: list[object] = []
    address = start
    while address + SIZE <= len(data) and is_text(data[address : address + SIZE]):
        run.append(index.get(data[address : address + SIZE], "PS1"))
        address += SIZE
    report = {
        "found": sum(o >= 0 for o in offsets),
        "missing": [k for k, o in enumerate(offsets) if o < 0],
        "groups": [
            {"ps1_offset": f"{g[0]:#07x}", "arcade_records": [g[2], g[3]]}
            for g in groups
        ],
        "run_from_record_0": {"ps1_offset": f"{start:#07x}", "records": run},
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))

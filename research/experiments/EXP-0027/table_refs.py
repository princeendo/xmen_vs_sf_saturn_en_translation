"""EXP-0027: find every static reference to an address range in work-RAM dumps.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0027/table_refs.py START END DUMP...

Each DUMP is ``PREFIX`` for ``PREFIX-workraml.bin`` and ``PREFIX-workramh.bin``
(``research/experiments/EXP-0025/dump_states.py``). The script reports, in
both regions:

- every 2-byte-aligned 32-bit value in [START, END) or its cache-through
  mirror (``+ 0x20000000``), which is how SH-2 code holds a table address;
- every word that, decoded as an SH-2 PC-relative load, would read inside
  the range: ``mov.w @(disp,pc)`` (``9nxx``), ``mov.l @(disp,pc)``
  (``Dnxx``) and ``mova`` (``C7xx``).

Data words also decode as instructions, so every hit is listed for review;
none is assumed to be code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REGIONS = (("workraml", 0x00200000), ("workramh", 0x06000000))


def scan(data: bytes, base: int, start: int, end: int) -> dict[str, list[str]]:
    literals, loads = [], []
    for offset in range(0, len(data) - 3, 2):
        value = int.from_bytes(data[offset : offset + 4], "big")
        if start <= value < end or start <= value - 0x20000000 < end:
            literals.append(f"{base + offset:#010x}={value:#010x}")
    for offset in range(0, len(data) - 1, 2):
        pc = base + offset
        word = int.from_bytes(data[offset : offset + 2], "big")
        disp = word & 0xFF
        if word >> 12 == 0x9:
            target = pc + 4 + 2 * disp
        elif word >> 12 == 0xD or word >> 8 == 0xC7:
            target = (pc & ~3) + 4 + 4 * disp
        else:
            continue
        if start <= target < end:
            loads.append(f"{pc:#010x}:{word:04X}->{target:#010x}")
    return {"literals": literals, "pc_relative": loads}


def main(start: int, end: int, prefixes: list[str]) -> int:
    report = {}
    for prefix in prefixes:
        for region, base in REGIONS:
            data = Path(f"{prefix}-{region}.bin").read_bytes()
            report[f"{Path(prefix).name}-{region}"] = scan(data, base, start, end)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1], 0), int(sys.argv[2], 0), sys.argv[3:]))

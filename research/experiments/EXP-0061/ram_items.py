r"""EXP-0061: the English boss boxes as RAM writes for `EXP-0049/patch_run.py`.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0061/ram_items.py DUMP [NAMES]

DUMP is a WRAM-H dump (``0x06000000``) taken at the state the writes start
from, before the box setup runs. Prints ``ADDRESS:OLD:NEW`` items: the code
and index-table changes of `tools.disc.boss_boxes.patches` (their original
bytes checked against DUMP), then every English record of
`tools.disc.boss_boxes.records` at ``MC08`` + its offset, with DUMP's bytes
as OLD. NAMES (``us``, the default, or ``saturn``) picks slots 14-16's
second box.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.boss_boxes import MC08, load, patches, records

WRAM_H = 0x06000000


def main(dump: Path, names: str) -> int:
    memory = dump.read_bytes()
    items = []
    for address, old, new in patches():
        found = memory[address - WRAM_H :][: len(bytes.fromhex(old))]
        if found != bytes.fromhex(old):
            raise SystemExit(f"{address:#010x}: dump holds {found.hex()}, not {old}")
        items.append(f"{address:08X}:{old.replace(' ', '')}:{new.replace(' ', '')}")
    for offset, record in records(load(), names).items():
        address = MC08 + offset
        old_bytes = memory[address - WRAM_H :][: len(record)]
        items.append(f"{address:08X}:{old_bytes.hex()}:{record.hex()}")
    print(" ".join(items))
    return 0


if __name__ == "__main__":
    names = sys.argv[2] if len(sys.argv) > 2 else "us"
    raise SystemExit(main(Path(sys.argv[1]), names))

r"""EXP-0068: WRAM-H ranges that are zero in every dump on hand.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0068/free_space.py MMPACK OUT [ROOT]

Walks ROOT (default ``local``) for 1 MB files and keeps those that are
WRAM-H dumps taken after `MMPACK.PCA` loaded: their bytes at
``0x06014000`` equal the first ``PROBE`` bytes of MMPACK's decoded first
segment (MMPACK is the untouched file). Then reports every run of at least
``MIN_RUN`` bytes that is zero in all of them, and marks whether it lies in
an MMPACK segment and whether its decoded bytes there are zero too. Writes
``OUT`` (JSON, ignored path): the dumps used (path, SHA-256) and the runs.
No game bytes are written.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import decompress_entries, split_header

WRAM_H, SIZE, PROBE, MIN_RUN = 0x06000000, 0x100000, 0x100, 64


def main(mmpack: Path, out: Path, root: Path) -> int:
    raw = mmpack.read_bytes()
    _, entries = split_header(raw)
    _, decoded, _ = decompress_entries(raw)
    segments, at = [], 0
    for dest, size in entries:
        segments.append((dest, decoded[at : at + size]))
        at += size
    probe = segments[0][1][:PROBE]
    first = segments[0][0] - WRAM_H
    used, nonzero = [], bytearray(SIZE)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.stat().st_size != SIZE:
            continue
        data = path.read_bytes()
        if data[first : first + PROBE] != probe:
            continue
        used.append([str(path), hashlib.sha256(data).hexdigest()])
        for i, byte in enumerate(data):
            if byte:
                nonzero[i] = 1
    runs, start = [], None
    for i in range(SIZE + 1):
        zero = i < SIZE and not nonzero[i]
        if zero and start is None:
            start = i
        if not zero and start is not None:
            if i - start >= MIN_RUN:
                address, length = WRAM_H + start, i - start
                where = None
                for dest, seg in segments:
                    if dest <= address and address + length <= dest + len(seg):
                        part = seg[address - dest : address - dest + length]
                        where = {"segment": f"{dest:#010x}", "file_zero": not any(part)}
                runs.append(
                    {"address": f"{address:#010x}", "length": length, "mmpack": where}
                )
            start = None
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"dumps": used, "runs": runs}, indent=1) + "\n")
    print(f"{len(used)} WRAM-H dumps; {len(runs)} zero runs of {MIN_RUN}+ bytes")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]) if len(a) > 2 else Path("local"))
    )

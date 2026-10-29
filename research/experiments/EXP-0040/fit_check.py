"""EXP-0040: do MMPACK.PCA and MCED.SHP still fit their sectors with version 4?

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0040/fit_check.py

Both files are read from the untouched source track
(`tools.disc.build_english.read_file`). ``MMPACK.PCA`` gets the version-4
code (`v4_trial.v4_code`) plus slot 16's English-ending bit, through
`tools.disc.build_english.build_mmpack`. ``MCED.SHP`` gets Nash's
script-header change at decoded ``0x2CF0`` (``0008`` → ``0038``), re-encoded
lazily to its own size, with the stream ending in the last sector (as
`build_mc` does). For each file it prints:

- the original size;
- the lazy stream's natural size;
- the margin;
- the rebuilt hash;
- whether the round trip decodes to the changed data.

Nothing is written.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0040"))
from v4_trial import ENDING_BIT, MCED_HEADER, SLOT, v4_code

from tools.disc.build_english import build_mmpack, last_sector_start, read_file
from tools.disc.english_mode import FIXED_TABLE
from tools.disc.prs import compress, compress_file, decompress_file

MCED_BASE = 0x060D2000  # MCED.SHP's decoded offset 0 in RAM (EXP-0038)


def main() -> int:
    report: dict[str, object] = {}
    raw = read_file("MMPACK.PCA;1")
    bit = (FIXED_TABLE + 2 * SLOT + 1, "00", f"{ENDING_BIT:02X}")
    rebuilt = build_mmpack(raw, [], [*v4_code(), bit])
    report["MMPACK.PCA"] = {
        "size": len(raw),
        "rebuilt_size": len(rebuilt),
        "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
    }
    raw = read_file("MCED.SHP;1")
    decoded, _ = decompress_file(raw)
    data = bytearray(decoded)
    address, old, new = MCED_HEADER
    offset = address - MCED_BASE
    if data[offset : offset + 2] != bytes.fromhex(old):
        raise ValueError("MCED header differs from the expected original")
    data[offset : offset + 2] = bytes.fromhex(new)
    natural = len(compress(bytes(data), lazy=True))
    rebuilt = compress_file(
        bytes(data), size=len(raw), min_end=last_sector_start(len(raw)), lazy=True
    )
    report["MCED.SHP"] = {
        "size": len(raw),
        "natural_lazy": natural,
        "margin": len(raw) - natural,
        "rebuilt_size": len(rebuilt),
        "round_trip": decompress_file(rebuilt)[0] == bytes(data),
        "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

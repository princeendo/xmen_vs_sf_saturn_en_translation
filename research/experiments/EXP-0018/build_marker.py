"""EXP-0018: build the M2 marker version of ``MC09.SHP``.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0018/build_marker.py OUT

Reads ``MC09.SHP`` from the untouched data track (checked against its
SHA-256 in `references/saturn_jp/iso_listing.json`), decompresses it, writes
あいう (``09E1 09E3 09E5``, `EXP-0016`) over line-1 cells 3-5 of each of Ryu's
16 win-quote records (table at decompressed offset ``0x25D8``, `EXP-0017`),
re-encodes it at the original size, and checks the round trip. Record 10
gets exactly the M1 change. Writes ``OUT/MC09.SHP`` and ``OUT/changes.json``
(every original and new code, rule 12) to the ignored OUT.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.iso9660 import RAW_SECTOR, USER_DATA
from tools.disc.patch_image import find_entry
from tools.disc.prs import compress_file, decompress_file

TRACK = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/"
    "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
)
LISTING = Path("references/saturn_jp/iso_listing.json")
NAME = "MC09.SHP;1"
TABLE, RECORD, RECORDS = 0x25D8, 76, 16
CELL = 3  # line 1, cells 3-5
MARKER = bytes.fromhex("09E109E309E5")  # あ い う: Unicode - 0x2661


def read_file(lsn: int, size: int) -> bytes:
    data = bytearray()
    with TRACK.open("rb") as stream:
        for index in range(lsn, lsn + (size + USER_DATA - 1) // USER_DATA):
            stream.seek(index * RAW_SECTOR + 16)
            data += stream.read(USER_DATA)
    return bytes(data[:size])


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    lsn, size = find_entry(TRACK, NAME)
    listed = next(
        f for f in json.loads(LISTING.read_text())["files"] if f["path"] == NAME
    )
    original = read_file(lsn, size)
    if hashlib.sha256(original).hexdigest() != listed["sha256"]:
        raise SystemExit("MC09.SHP does not match the listing")
    decoded, used = decompress_file(original)
    marked = bytearray(decoded)
    changes = []
    for record in range(RECORDS):
        offset = TABLE + record * RECORD + 2 * CELL
        changes.append(
            {
                "record": record,
                "decompressed_offset": f"{offset:#06x}",
                "ram_address": f"{0x0024D000 + offset:#010x}",
                "original": decoded[offset : offset + len(MARKER)].hex(),
                "modified": MARKER.hex(),
            }
        )
        marked[offset : offset + len(MARKER)] = MARKER
    # The loader asks for every sector and reads them on demand (EXP-0017), so
    # the stream must still end in the file's last sector.
    last_sector = (size - 1) // USER_DATA * USER_DATA + 1
    rebuilt = compress_file(bytes(marked), size=size, min_end=last_sector)
    check, rebuilt_used = decompress_file(rebuilt)
    if check != bytes(marked) or rebuilt_used < last_sector:
        raise SystemExit("round trip failed")
    (out / "MC09.SHP").write_bytes(rebuilt)
    result = {
        "file": NAME,
        "lsn": lsn,
        "size": size,
        "original_sha256": listed["sha256"],
        "original_stream_end": used,
        "decompressed_sha256": hashlib.sha256(decoded).hexdigest(),
        "repack_identical": compress_file(decoded) == original,
        "marked_decompressed_sha256": hashlib.sha256(marked).hexdigest(),
        "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
        "rebuilt_stream_end": rebuilt_used,
        "changed_decompressed_bytes": sum(
            a != b for a, b in zip(decoded, marked, strict=True)
        ),
        "changes": changes,
    }
    (out / "changes.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "changes"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

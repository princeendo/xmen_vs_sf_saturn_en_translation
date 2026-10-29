"""EXP-0023: build ``MMPACK.PCA`` and ``MC09.SHP`` for Ryu's English win quotes.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/build_english.py OUT

Both files are read from the untouched data track and checked against
`references/saturn_jp/iso_listing.json`.

* ``MMPACK.PCA`` (the main code, two entries): decode, apply
  `english_patch.PATCHES` at the entry 1 addresses (``0x0601F000`` onward),
  re-encode with lazy matching, and pad to the original size. The stream must
  still end in the file's last sector.
* ``MC09.SHP``: decode, then write Ryu's 8 official arcade English win-quote
  records over the start of his quote table (decompressed offset ``0x25D8``,
  100 bytes each). The records are the US set ``xmvsfu``, slot 9 records 0-7,
  read at run time from the ignored ``local/ref003/xmvsfu-68k.bin``. The
  pairing (`GATE-TRANSLATION`, `EXP-0022`) has Saturn draw ``r`` show English
  record ``r mod 8``, which the patched selector computes as ``r & 7``. Then
  re-encode lazily and pad the same way.

Writes ``OUT/MMPACK.PCA``, ``OUT/MC09.SHP`` and ``OUT/changes.json`` (every
changed range with original and new bytes, rule 12) to the ignored OUT.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from english_patch import PATCHES, as_bytes

from tools.disc.iso9660 import RAW_SECTOR, USER_DATA
from tools.disc.patch_image import find_entry
from tools.disc.prs import (
    compress_file,
    decompress_entries,
    decompress_file,
    split_header,
)
from tools.reference.xvsf_text import long

TRACK = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/"
    "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
)
LISTING = Path("references/saturn_jp/iso_listing.json")
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
EN_TABLE, SLOT, RECORDS, RECORD = 0x17E1E8, 9, 8, 100
QUOTE_TABLE = 0x25D8  # MC09.SHP decompressed offset of Ryu's quote table


def read_file(name: str) -> tuple[int, int, bytes]:
    lsn, size = find_entry(TRACK, name)
    data = bytearray()
    with TRACK.open("rb") as stream:
        for index in range(lsn, lsn + (size + USER_DATA - 1) // USER_DATA):
            stream.seek(index * RAW_SECTOR + 16)
            data += stream.read(USER_DATA)
    listed = next(
        f for f in json.loads(LISTING.read_text())["files"] if f["path"] == name
    )
    if hashlib.sha256(data[:size]).hexdigest() != listed["sha256"]:
        raise SystemExit(f"{name} does not match the listing")
    return lsn, size, bytes(data[:size])


def last_sector_start(size: int) -> int:
    return (size - 1) // USER_DATA * USER_DATA + 1


def build_mmpack(raw: bytes, changes: list[dict[str, object]]) -> bytes:
    header, entries = split_header(raw)
    _, decoded, _ = decompress_entries(raw)
    code = bytearray(decoded)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size  # address of decoded offset 0, for entry 1
    for address, old, new in PATCHES:
        offset = address - base
        original = bytes(code[offset : offset + len(as_bytes(old))])
        if original != as_bytes(old):
            raise SystemExit(f"{address:#x}: found {original.hex()}")
        code[offset : offset + len(original)] = as_bytes(new)
        changes.append(
            {
                "file": "MMPACK.PCA",
                "decompressed_offset": f"{offset:#x}",
                "ram_address": f"{address:#010x}",
                "original": original.hex(),
                "modified": as_bytes(new).hex(),
            }
        )
    rebuilt = compress_file(
        bytes(code),
        size=len(raw),
        min_end=last_sector_start(len(raw)),
        header=header,
        lazy=True,
    )
    if decompress_entries(rebuilt)[1] != bytes(code):
        raise SystemExit("MMPACK.PCA round trip failed")
    return rebuilt


def build_mc09(raw: bytes, changes: list[dict[str, object]]) -> bytes:
    program = PROGRAM.read_bytes()
    base = long(program, EN_TABLE + 4 * SLOT)
    english = program[base : base + RECORDS * RECORD]
    decoded, _ = decompress_file(raw)
    data = bytearray(decoded)
    end = QUOTE_TABLE + len(english)
    changes.append(
        {
            "file": "MC09.SHP",
            "decompressed_offset": f"{QUOTE_TABLE:#x}",
            "ram_address": f"{0x0024D000 + QUOTE_TABLE:#010x}",
            "length": len(english),
            "original": bytes(data[QUOTE_TABLE:end]).hex(),
            "modified": english.hex(),
            "source": (
                f"xmvsfu program {base:#x}-{base + len(english):#x}"
                " (slot 9, records 0-7)"
            ),
        }
    )
    data[QUOTE_TABLE:end] = english
    rebuilt = compress_file(
        bytes(data), size=len(raw), min_end=last_sector_start(len(raw)), lazy=True
    )
    if decompress_file(rebuilt)[0] != bytes(data):
        raise SystemExit("MC09.SHP round trip failed")
    return rebuilt


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    changes: list[dict[str, object]] = []
    summary = {}
    for name, builder in (("MMPACK.PCA;1", build_mmpack), ("MC09.SHP;1", build_mc09)):
        lsn, size, raw = read_file(name)
        rebuilt = builder(raw, changes)
        (out / name.split(";")[0]).write_bytes(rebuilt)
        summary[name] = {
            "lsn": lsn,
            "size": size,
            "original_sha256": hashlib.sha256(raw).hexdigest(),
            "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
        }
    (out / "changes.json").write_text(
        json.dumps({"files": summary, "changes": changes}, indent=1) + "\n"
    )
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

"""EXP-0019: build a ``FIX.PRS`` with one changed byte in glyph あ (``0x09E1``).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0019/build_font_probe.py OUT

Reads ``FIX.PRS`` (the quote font image, `EXP-0019`) from the untouched data
track and checks it against `references/saturn_jp/iso_listing.json`. It then
inverts the first pixel-value byte of glyph ``0x09E1``'s compressed stream
(after the 2-byte mask and its mask bytes), keeping the file size. Writes
``OUT/FIX.PRS`` and ``OUT/change.json`` (offset, original and new byte, and the
glyph cell before and after decoding, rule 12) to the ignored OUT.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.iso9660 import RAW_SECTOR, USER_DATA
from tools.disc.patch_image import find_entry
from tools.text.font import Font

TRACK = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/"
    "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
)
LISTING = Path("references/saturn_jp/iso_listing.json")
NAME = "FIX.PRS;1"
CODE = 0x09E1  # あ


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
    files = json.loads(LISTING.read_text())["files"]
    listed = next(f for f in files if f["path"] == NAME)
    original = read_file(lsn, size)
    if hashlib.sha256(original).hexdigest() != listed["sha256"]:
        raise SystemExit("FIX.PRS does not match the listing")
    font = Font(original, 0, 0)
    address, size_byte = font.locate(CODE)
    if size_byte & 0x80 or size_byte == 0:
        raise SystemExit("glyph is not compressed")
    mask = int.from_bytes(original[address : address + 2], "big")
    offset = address + 2 + bin(mask).count("1")
    modified = bytearray(original)
    modified[offset] ^= 0xFF
    before, _ = font.glyph(CODE)
    after, _ = Font(bytes(modified), 0, 0).glyph(CODE)
    (out / "FIX.PRS").write_bytes(modified)
    result = {
        "file": NAME,
        "lsn": lsn,
        "size": size,
        "original_sha256": listed["sha256"],
        "modified_sha256": hashlib.sha256(modified).hexdigest(),
        "code": f"{CODE:#06x}",
        "glyph_address": f"{address:#x}",
        "glyph_size": size_byte,
        "file_offset": f"{offset:#x}",
        "sector": lsn + offset // USER_DATA,
        "original_byte": f"{original[offset]:02x}",
        "modified_byte": f"{modified[offset]:02x}",
        "cell_before": before.hex(),
        "cell_after": after.hex(),
        "changed_cell_bytes": sum(a != b for a, b in zip(before, after, strict=True)),
    }
    (out / "change.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if "cell_" not in k}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

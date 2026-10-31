r"""EXP-0064: choose one literal byte of a stream block to change, and predict it.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0064/pick_literal.py \
        ST2 BLOCK FIRST:LAST VALUE OUT

Decodes stream block BLOCK (counting from 0) of ST2's ``MISS`` payload with
`tools.disc.st2_stream.lz_decode`, recording which payload byte each literal
came from. Among the literals whose output lies in FIRST:LAST (hex, offsets
in the decoded block), it picks the one whose change to VALUE (hex) alters
the fewest decoded bytes, all inside FIRST:LAST. Writes ``OUT/<ST2 name>``
(the file with that one byte changed), ``OUT/expected.bin`` (the decoded
block after the change) and ``OUT/change.json`` (file offset, original and
new byte, the decoded offsets that change). OUT is an ignored path.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.st2_stream import SECTOR, TAG, lz_decode, miss_sectors

PAYLOAD = SECTOR - len(TAG)


def block_start(payload: bytes, block: int) -> int:
    position, n = 0, 0
    while True:
        compressed, _ = struct.unpack_from(">II", payload, position)
        if compressed == 0:
            position += 4
            continue
        if n == block:
            return position
        _, end = lz_decode(payload, position)
        n += 1
        position = (end + 3) & ~3


def literal_sources(payload: bytes, start: int) -> dict[int, int]:
    """Decoded offset -> payload offset, for every literal of the block."""
    _, size = struct.unpack_from(">II", payload, start)
    position, produced, sources = start + 8, 0, {}
    while produced < size:
        flags = payload[position]
        position += 1
        for bit in range(8):
            if produced >= size:
                break
            if flags & (0x80 >> bit):
                word = (payload[position] << 8) | payload[position + 1]
                position += 2
                produced += (word & 0xF) + 3
            else:
                sources[produced] = position
                position += 1
                produced += 1
    return sources


def main(st2: Path, block: int, span: str, value: int, out: Path) -> int:
    first, last = (int(x, 16) for x in span.split(":"))
    data = st2.read_bytes()
    sectors = miss_sectors(data)
    payload = b"".join(data[o + len(TAG) : o + SECTOR] for o in sectors)
    start = block_start(payload, block)
    original, _ = lz_decode(payload, start)
    best = None
    for decoded, source in sorted(literal_sources(payload, start).items()):
        if not first <= decoded < last or payload[source] == value:
            continue
        changed = bytearray(payload)
        changed[source] = value
        result, _ = lz_decode(bytes(changed), start)
        diff = [i for i in range(len(original)) if result[i] != original[i]]
        if all(first <= i < last for i in diff) and (
            best is None or len(diff) < len(best[2])
        ):
            best = (source, result, diff)
            if len(diff) <= 2:
                break
    if best is None:
        raise SystemExit("no literal changes only bytes inside the span")
    source, result, diff = best
    offset = sectors[source // PAYLOAD] + len(TAG) + source % PAYLOAD
    new = bytearray(data)
    new[offset] = value
    out.mkdir(parents=True, exist_ok=False)
    (out / st2.name).write_bytes(bytes(new))
    (out / "expected.bin").write_bytes(result)
    record = {
        "file": st2.name,
        "file_offset": f"{offset:#x}",
        "original": f"{data[offset]:02X}",
        "new": f"{value:02X}",
        "payload_offset": f"{source:#x}",
        "decoded_changes": [f"{i:#x}" for i in diff],
    }
    (out / "change.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), int(a[1]), a[2], int(a[3], 16), Path(a[4])))

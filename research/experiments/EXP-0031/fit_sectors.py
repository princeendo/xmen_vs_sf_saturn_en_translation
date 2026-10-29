"""EXP-0031: check that every roster MC file, with its English records, fits its size.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0031/fit_sectors.py OUT_JSON

For each slot in `data/text/m5_roster.json`:

1. Read the MC file from the untouched track
   (`tools.disc.build_english.read_file`, checked against the ISO listing),
   and decode it.
2. Take the slot's English records 0-7 from the ignored US program
   ``local/ref003/xmvsfu-68k.bin`` (table ``0x17E1E8``). Recompile each
   with `tools.text.caption` and require identical bytes, as
   `tools.disc.build_english.compile_records` does.
3. Write the 800 bytes over the start of the census's table, and rebuild the
   file with `tools.disc.build_english.build_mc`, the build's own path. This
   re-encodes at the original size, with the stream ending in the last
   sector, and checks the round trip.

It records:

- the original size and sectors;
- the natural size of the English-edited file with the same encoder (no
  padding);
- the margin (original size minus that natural size);
- the natural size of the original content with the same encoder, as a
  reference for how close the encoder is to the original;
- whether the rebuilt file decodes to the original decoded file outside the
  800-byte English area.

Only sizes, offsets and hashes are written (AGENTS.md rule 21).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import build_mc, read_file
from tools.disc.prs import PrsError, compress_file, decompress_file
from tools.text.caption import compile_record, decode_record

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m5_roster.json")
EN_TABLE, RECORD, SHOWN, SECTOR = 0x17E1E8, 100, 8, 2048


def english(program: bytes, slot: int) -> bytes:
    base = int.from_bytes(program[EN_TABLE + 4 * slot : EN_TABLE + 4 * slot + 4])
    out = bytearray()
    for index in range(SHOWN):
        source = program[base + RECORD * index : base + RECORD * (index + 1)]
        if compile_record(decode_record(source)) != source:
            raise ValueError(f"slot {slot} record {index}: recompiled bytes differ")
        out += source
    return bytes(out)


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    roster = json.loads(ROSTER.read_text())["roster"]
    report = []
    failed = 0
    for member in roster:
        name = str(member["mc_file"])
        slot = int(member["slot"])
        table = int(str(member["table_offset"]), 16)
        raw = read_file(name)
        decoded, _ = decompress_file(raw)
        records = english(program, slot)
        edited = bytearray(decoded)
        edited[table : table + len(records)] = records
        entry: dict[str, object] = {
            "slot": slot,
            "character": member["name_list"],
            "file": name,
            "size": len(raw),
            "sectors": -(-len(raw) // SECTOR),
            "original_natural": len(compress_file(decoded, lazy=True)),
            "english_natural": len(compress_file(bytes(edited), lazy=True)),
            "english_sha256": hashlib.sha256(records).hexdigest(),
        }
        entry["margin"] = len(raw) - int(str(entry["english_natural"]))
        try:
            rebuilt = build_mc(raw, records, table, name, [])
        except (PrsError, ValueError) as error:
            failed += 1
            entry["fits"] = False
            entry["error"] = str(error)
            report.append(entry)
            continue
        back, used = decompress_file(rebuilt)
        outside = (
            back[:table] == decoded[:table]
            and back[table + len(records) :] == decoded[table + len(records) :]
        )
        entry.update(
            {
                "fits": True,
                "rebuilt_size": len(rebuilt),
                "stream_ends_in_last_sector": -(-used // SECTOR) == entry["sectors"],
                "english_in_place": back[table : table + len(records)] == records,
                "untouched_outside_english": outside,
                "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
            }
        )
        failed += not (
            entry["rebuilt_size"] == len(raw)
            and entry["stream_ends_in_last_sector"]
            and entry["english_in_place"]
            and outside
        )
        report.append(entry)
    out.write_text(json.dumps(report, indent=1) + "\n")
    for entry in report:
        print(
            f"slot {entry['slot']:2} {entry['file']:11} size {entry['size']:6} "
            f"english {entry['english_natural']:6} margin {entry['margin']:5} "
            f"orig-enc {entry['original_natural']:6} fits {entry['fits']} "
            f"outside-same {entry.get('untouched_outside_english')} "
            f"last-sector {entry.get('stream_ends_in_last_sector')}"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

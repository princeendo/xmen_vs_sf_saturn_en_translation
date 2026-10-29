"""EXP-0025: match MC files, arcade Japanese records and RAM dumps for `RE-004`.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/analyze.py DUMPS... > OUT.json

Each DUMPS argument is a prefix such as ``local/re004/dumps/f00007684``; the
files ``PREFIX-workraml.bin`` and ``PREFIX-workramh.bin`` come from
``dump_states.py``. For each listed character the script:

- decodes ``MCxx.SHP`` (xx = the arcade slot in hex, the hypothesis under
  test) from the untouched track and finds where the arcade's Japanese
  win-quote records 0-15 for that slot sit in it (table ``0x17E19C``);
- counts how many of the arcade's Japanese ending records for that slot
  (table ``0x17E2CC``) follow the 16 quotes;
- finds the 16 quote records in every dump and derives the file's load base;
- checks that RAM at that base equals the decoded file except for big-endian
  32-bit fields (2-byte aligned) holding file value + base + ``0x40``.

The arcade program is the ignored ``local/ref003/xmvsfu-68k.bin``. Only
offsets, counts and addresses are printed (no game text).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.disc.prs import decompress_file

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
QUOTES, ENDINGS, RECORD = 0x17E19C, 0x17E2CC, 76
SLOTS = {3: "Rogue", 9: "Ryu", 10: "Ken", 11: "Chun-Li", 15: "Gouki", 17: "Cammy"}
SPACES = (("workraml", 0x00200000), ("workramh", 0x06000000))


def long(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def fixups(decoded: bytes, ram: bytes, delta: int) -> tuple[int, int, bool]:
    """Fields explaining RAM as decoded + delta; returns (count, 2-aligned, exact)."""
    rebuilt = bytearray(decoded)
    count = unaligned = 0
    i = 0
    while i < len(decoded) - 3:
        if ram[i : i + 4] != decoded[i : i + 4]:
            value = (long(decoded, i) + delta) & 0xFFFFFFFF
            if value.to_bytes(4, "big") == ram[i : i + 4]:
                rebuilt[i : i + 4] = ram[i : i + 4]
                count += 1
                unaligned += i % 4 != 0
                i += 4
                continue
        i += 2
    return count, unaligned, bytes(rebuilt) == ram


def main(prefixes: list[str]) -> int:
    program = PROGRAM.read_bytes()
    dumps = {
        prefix: {
            space: Path(f"{prefix}-{space}.bin").read_bytes() for space, _ in SPACES
        }
        for prefix in prefixes
    }
    report: dict[str, object] = {}
    for slot, name in SLOTS.items():
        quotes = program[long(program, QUOTES + 4 * slot) :][: 16 * RECORD]
        endings = long(program, ENDINGS + 4 * slot)
        file_name = f"MC{slot:02X}.SHP;1"
        decoded, _ = decompress_file(read_file(file_name))
        offset = decoded.find(quotes)
        entry: dict[str, object] = {
            "file": file_name,
            "decoded_size": len(decoded),
            "quote_table_offset": f"{offset:#x}" if offset >= 0 else None,
        }
        if offset >= 0:
            start = offset + 16 * RECORD
            count = 0
            while (
                decoded[start + count * RECORD : start + (count + 1) * RECORD]
                == program[endings + count * RECORD : endings + (count + 1) * RECORD]
            ):
                count += 1
            entry["ending_records_after_quotes"] = count
        seen: dict[str, object] = {}
        for prefix, spaces in dumps.items():
            for space, base in SPACES:
                at = spaces[space].find(quotes)
                if at < 0 or offset < 0:
                    continue
                load = base + at - offset
                ram = spaces[space][at - offset : at - offset + len(decoded)]
                total, unaligned, exact = fixups(decoded, ram, load + 0x40)
                seen[Path(prefix).name] = {
                    "table": f"{base + at:#010x}",
                    "file_base": f"{load:#010x}",
                    "fixups": total,
                    "fixups_2_aligned": unaligned,
                    "ram_equals_file_plus_fixups": exact,
                }
        entry["in_dumps"] = seen
        report[name] = entry
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

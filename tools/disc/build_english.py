"""Build ``MMPACK.PCA`` and a character's MC file with English win quotes.

Run from the repository root:

    ./invenv.sh python -m tools.disc.build_english SPEC OUT [--program PATH]

SPEC is a translation record such as `data/translations/ryu_win_quotes.json`.
For each English record it names the source address in the US arcade program
and its SHA-256. The English text itself is not stored in the repository
(AGENTS.md rule 21); it is read from PATH, the ignored ``xmvsfu`` program
image (`EXP-0008`). The build has these steps:

1. Read every source record, check its hash, decode it to text, and recompile
   it with `tools.text.caption`. The recompiled bytes must equal the source
   bytes, unless the spec gives an opt-in ``grammar_fix`` and ``--fix-grammar``
   is set (none exist yet).
2. Write the compiled records over the start of the character's quote table
   in the MC file (100 bytes each, in English record order) and re-encode the
   file at its original size.
3. Apply `tools.disc.english_mode.PATCHES` to ``MMPACK.PCA`` and re-encode it
   at its original size.

Both files are read from the untouched data track and checked against
`references/saturn_jp/iso_listing.json`. Each stream must still end in its
file's last sector. ``OUT/changes.json`` records every changed range, with
original and new bytes (rule 12); OUT is an ignored path. Then
`tools.disc.patch_image` builds the image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.english_mode import PATCHES, as_bytes
from tools.disc.iso9660 import RAW_SECTOR, USER_DATA
from tools.disc.patch_image import find_entry
from tools.disc.prs import (
    compress_file,
    decompress_entries,
    decompress_file,
    split_header,
)
from tools.text.caption import compile_record, decode_record

TRACK = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/"
    "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
)
LISTING = Path("references/saturn_jp/iso_listing.json")
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
RECORD = 100


def read_file(name: str) -> bytes:
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
        raise ValueError(f"{name} does not match the listing")
    return bytes(data[:size])


def last_sector_start(size: int) -> int:
    return (size - 1) // USER_DATA * USER_DATA + 1


def compile_records(
    spec: dict[str, object], program: bytes, fix_grammar: bool
) -> bytes:
    out = bytearray()
    records = spec["records"]
    assert isinstance(records, list)
    for index, entry in enumerate(records):
        if entry["english_record"] != index:
            raise ValueError("records must be listed in English record order")
        address = int(entry["source_address"], 16)
        source = program[address : address + RECORD]
        if hashlib.sha256(source).hexdigest() != entry["sha256"]:
            raise ValueError(f"English record {index}: source hash differs")
        lines = decode_record(source)
        fix = entry.get("grammar_fix")
        if fix_grammar and fix:
            lines = list(fix)
        compiled = compile_record(lines)
        if compiled != source and not (fix_grammar and fix):
            raise ValueError(f"English record {index}: recompiled bytes differ")
        out += compiled
    return bytes(out)


def build_mc(
    raw: bytes, english: bytes, table: int, name: str, changes: list[dict[str, object]]
) -> bytes:
    decoded, _ = decompress_file(raw)
    data = bytearray(decoded)
    end = table + len(english)
    changes.append(
        {
            "file": name,
            "decompressed_offset": f"{table:#x}",
            "length": len(english),
            "original": bytes(data[table:end]).hex(),
            "modified": english.hex(),
        }
    )
    data[table:end] = english
    rebuilt = compress_file(
        bytes(data), size=len(raw), min_end=last_sector_start(len(raw)), lazy=True
    )
    if decompress_file(rebuilt)[0] != bytes(data):
        raise ValueError(f"{name} round trip failed")
    return rebuilt


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
            raise ValueError(f"{address:#x}: found {original.hex()}")
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
        raise ValueError("MMPACK.PCA round trip failed")
    return rebuilt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--program", type=Path, default=PROGRAM)
    parser.add_argument("--fix-grammar", action="store_true")
    args = parser.parse_args(argv)
    spec = json.loads(args.spec.read_text())
    args.out.mkdir(parents=True, exist_ok=False)
    english = compile_records(spec, args.program.read_bytes(), args.fix_grammar)
    changes: list[dict[str, object]] = []
    summary: dict[str, object] = {}
    mc_name = str(spec["mc_file"])
    table = int(str(spec["table_offset"]), 16)
    for name in (mc_name, "MMPACK.PCA;1"):
        raw = read_file(name)
        if name == mc_name:
            rebuilt = build_mc(raw, english, table, mc_name, changes)
        else:
            rebuilt = build_mmpack(raw, changes)
        (args.out / name.split(";")[0]).write_bytes(rebuilt)
        summary[name] = {
            "size": len(raw),
            "original_sha256": hashlib.sha256(raw).hexdigest(),
            "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
        }
    summary["english_sha256"] = hashlib.sha256(english).hexdigest()
    (args.out / "changes.json").write_text(
        json.dumps({"files": summary, "changes": changes}, indent=1) + "\n"
    )
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

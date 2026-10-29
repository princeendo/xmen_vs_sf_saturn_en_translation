"""Build ``MMPACK.PCA`` and characters' MC files with English win quotes.

Run from the repository root:

    ./invenv.sh python -m tools.disc.build_english SPEC [SPEC ...] OUT
        [--program PATH] [--fix-grammar] [--patch-version {2,3}] [--image DIR]

Each SPEC is a translation record such as
`data/translations/ryu_win_quotes.json`. For each English record it names the
source address in the US arcade program and its SHA-256. The English text
itself is not stored in the repository (AGENTS.md rule 21); it is read from
PATH, the ignored ``xmvsfu`` program image (`EXP-0008`). The build has these
steps:

1. Read every source record, check its hash, decode it to text, and recompile
   it with `tools.text.caption`. The recompiled bytes must equal the source
   bytes, unless the spec gives an opt-in ``grammar_fix`` and ``--fix-grammar``
   is set (none exist yet).
2. For each SPEC, write the compiled records over the start of the
   character's quote table in its MC file (100 bytes each, in English record
   order) and re-encode the file at its original size.
3. Patch ``MMPACK.PCA`` and re-encode it at its original size. Version 3
   (the default; `RE-006`, `EXP-0027`) is
   `tools.disc.english_mode.patches_v3` with every SPEC's ``arcade_slot``.
   Version 2 (`EXP-0023`) is the code-only Ryu patch; it takes exactly one
   SPEC, Ryu's, and reproduces `EXP-0024`'s files.

Both files are read from the untouched data track and checked against
`references/saturn_jp/iso_listing.json`. Each stream must still end in its
file's last sector. ``OUT/changes.json`` records every changed range, with
original and new bytes (rule 12); OUT is an ignored path. With ``--image
DIR`` (under ``build/``), `tools.disc.patch_image` then builds the image from
the untouched source with the files written to OUT; otherwise run it
separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from tools.disc.english_mode import ENGLISH_SLOT2, PATCHES, as_bytes, patches_v3
from tools.disc.iso9660 import RAW_SECTOR, USER_DATA
from tools.disc.patch_image import find_entry
from tools.disc.patch_image import main as patch_image
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
MANIFEST = Path("references/saturn_jp/README.md")
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


def mmpack_patches(
    specs: list[dict[str, object]], version: int
) -> list[tuple[int, str, str]]:
    slots = [int(str(spec["arcade_slot"])) for spec in specs]
    if len(set(slots)) != len(slots):
        raise ValueError(f"a slot appears twice: {slots}")
    files = [str(spec["mc_file"]) for spec in specs]
    if len(set(files)) != len(files):
        raise ValueError(f"an MC file appears twice: {files}")
    if version == 2:
        if slots != [ENGLISH_SLOT2 // 2]:
            raise ValueError("version 2 builds Ryu (slot 9) alone")
        return PATCHES
    if version == 3:
        return patches_v3(slots)
    raise ValueError(f"unknown patch version {version}")


def build_mmpack(
    raw: bytes,
    changes: list[dict[str, object]],
    patches: list[tuple[int, str, str]] = PATCHES,
) -> bytes:
    header, entries = split_header(raw)
    _, decoded, _ = decompress_entries(raw)
    code = bytearray(decoded)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size  # address of decoded offset 0, for entry 1
    for address, old, new in patches:
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


def file_summary(raw: bytes, rebuilt: bytes) -> dict[str, object]:
    return {
        "size": len(raw),
        "original_sha256": hashlib.sha256(raw).hexdigest(),
        "rebuilt_sha256": hashlib.sha256(rebuilt).hexdigest(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", type=Path, nargs="+", help="SPEC [SPEC ...] OUT")
    parser.add_argument("--program", type=Path, default=PROGRAM)
    parser.add_argument("--fix-grammar", action="store_true")
    parser.add_argument("--patch-version", type=int, choices=(2, 3), default=3)
    parser.add_argument("--image", type=Path, help="also build the image here")
    args = parser.parse_args(argv)
    if len(args.paths) < 2:
        parser.error("give at least one SPEC and OUT")
    *spec_paths, out = args.paths
    specs = [json.loads(path.read_text()) for path in spec_paths]
    patches = mmpack_patches(specs, args.patch_version)
    out.mkdir(parents=True, exist_ok=False)
    program = args.program.read_bytes()
    changes: list[dict[str, object]] = []
    summary: dict[str, object] = {"patch_version": args.patch_version}
    for spec in specs:
        english = compile_records(spec, program, args.fix_grammar)
        name = str(spec["mc_file"])
        raw = read_file(name)
        table = int(str(spec["table_offset"]), 16)
        rebuilt = build_mc(raw, english, table, name, changes)
        summary[name] = file_summary(raw, rebuilt)
        summary[f"{name} english_sha256"] = hashlib.sha256(english).hexdigest()
        (out / name.split(";")[0]).write_bytes(rebuilt)
    raw = read_file("MMPACK.PCA;1")
    rebuilt = build_mmpack(raw, changes, patches)
    summary["MMPACK.PCA;1"] = file_summary(raw, rebuilt)
    (out / "MMPACK.PCA").write_bytes(rebuilt)
    (out / "changes.json").write_text(
        json.dumps({"files": summary, "changes": changes}, indent=1) + "\n"
    )
    print(json.dumps(summary, indent=1))
    if args.image is None:
        return 0
    files = []
    for name in [*(str(spec["mc_file"]) for spec in specs), "MMPACK.PCA;1"]:
        files += ["--file", name, "--data", str(out / name.split(";")[0])]
    return patch_image(
        [
            *("--source-dir", str(TRACK.parent), "--manifest", str(MANIFEST)),
            *("--track", TRACK.name, *files, "--out-dir", str(args.image)),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())

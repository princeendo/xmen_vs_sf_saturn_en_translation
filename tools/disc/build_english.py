"""Build ``MMPACK.PCA`` and characters' MC files with English win quotes.

Run from the repository root:

    ./invenv.sh python -m tools.disc.build_english SPEC [SPEC ...] OUT
        [--program PATH] [--fix-grammar] [--patch-version {2,3,4}]
        [--names {us,none,saturn}] [--boot-warnings] [--image DIR]

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

An ending SPEC (``"kind": "ending"``, such as `data/translations/nash_ending.json`)
needs version 4 (`END-006`, `EXP-0040`) and a win-quote SPEC for the same slot
and file. Its records are compiled the same way and written right after
that slot's English win quotes, at quote table + 800
(`tools.disc.english_mode.ENDING_RECORDS`). ``MMPACK.PCA`` gets
`tools.disc.english_mode.patches_v4`, and ``MCED.SHP`` gets
`tools.disc.english_mode.mced_english_scripts` for the ending slots, re-encoded
at its original size. An ending SPEC's ``mced_shared_with`` lists the slots
whose script it shares and that switch with it (`END-014`: Ryu's lists 8,
Chun-Li's 18); a shared script is refused otherwise.

``--names`` picks the name variant (`LOC-004`): ``us`` (the default) adds
`tools.disc.names` patches to ``MMPACK.PCA``, so that every name surface
shows the American name; ``none`` leaves the Saturn's names, as every build
before `LOC-005` did. ``saturn`` (`LOC-006`) changes no code but makes the
name edits of `tools.disc.names.SATURN` to the official English: in the
records it lists (each recompiled after its edit, instead of being checked
against its source bytes) and, for ending slots, in ``MCED.SHP``'s English
scripts and label list. ``OUT/changes.json`` lists each edited record with
its source hash and the edit.

``--special`` (`SPEC-004`, `EXP-0061`) adds the special cases the user approved
in `SPEC-003`. It needs patch version 4 and Apocalypse's win-quote SPEC
(``MC08.SHP``):

- Apocalypse's boss-stage boxes in English (`tools.disc.boss_boxes`): the
  approved records written into ``MC08.SHP`` after its English quotes, and
  the box setup and index-table changes in ``MMPACK.PCA``; slots 14-16's
  second box follows ``--names`` (``saturn``, or the American names
  otherwise);
- slot 18 (Alpha Chun-Li) marked English, with the ending bit, so she shows
  Chun-Li's English quotes and ending as the arcade does (needs Chun-Li's
  ending SPEC, whose script slot 18 shares).

``--no-challengers`` (`NOCH-001`, `EXP-0063`) shows the arcade's own
``NO CHALLENGERS`` sign in place of ``⚠乱入禁止``, as the user chose: the one
region-word read that picks the sign (``0x0605F838``) is taken as US, as
``--names us`` does at its own sites. The game then draws the arcade's
English definition, art (``FIX.PRS`` ``0x480``-``0x487``) and position.

``--boot-warnings`` also writes the approved English boot-warning pictures,
``ERR1``-``ERR5.BIN`` (`tools.disc.boot_warnings`, `BOOT-004`), drawn from the
untouched files and ``FIX.PRS``; each keeps its size and header.

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
from itertools import pairwise
from pathlib import Path

from tools.disc import boss_boxes
from tools.disc.boot_warnings import NAMES as BOOT_WARNINGS
from tools.disc.boot_warnings import build as build_boot_warnings
from tools.disc.boot_warnings import load_layout
from tools.disc.english_mode import (
    ENDING_RECORDS,
    ENGLISH_SLOT2,
    PATCHES,
    as_bytes,
    ending_slot_patches,
    mced_english_scripts,
    patches_v3,
    patches_v4,
    slot_patches,
)
from tools.disc.iso9660 import RAW_SECTOR, USER_DATA
from tools.disc.names import (
    REGION_READ,
    US_REGION,
    VARIANTS,
    edit_lines,
    entry_edits,
    label_edits,
    load_saturn,
    text_edits,
)
from tools.disc.names import patches as name_patches
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
    spec: dict[str, object],
    program: bytes,
    fix_grammar: bool,
    edits: dict[int, list[tuple[int, str, str]]] | None = None,
    log: list[dict[str, object]] | None = None,
) -> bytes:
    """The spec's records, compiled; ``edits`` maps a record to its name edits."""
    out = bytearray()
    records = spec["records"]
    assert isinstance(records, list)
    named = {} if edits is None else edits
    if set(named) - set(range(len(records))):
        raise ValueError(f"name edits for missing records {sorted(named)}")
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
        if index in named:
            lines = edit_lines(lines, named[index])
        compiled = compile_record(lines)
        if compiled != source and not (fix_grammar and fix) and index not in named:
            raise ValueError(f"English record {index}: recompiled bytes differ")
        if index in named and log is not None:
            log.append(
                {
                    "mc_file": spec.get("mc_file"),
                    "english_record": index,
                    "source_address": entry["source_address"],
                    "source_sha256": entry["sha256"],
                    "edits": [list(e) for e in named[index]],
                    "compiled_sha256": hashlib.sha256(compiled).hexdigest(),
                }
            )
        out += compiled
    return bytes(out)


def build_mc(
    raw: bytes,
    english: bytes,
    table: int,
    name: str,
    changes: list[dict[str, object]],
    extra: dict[int, bytes] | None = None,
) -> bytes:
    """``raw`` with ``english`` at ``table``, and each ``extra`` offset's bytes."""
    decoded, _ = decompress_file(raw)
    data = bytearray(decoded)
    edits = {table: english, **(extra or {})}
    spans = sorted((offset, offset + len(new)) for offset, new in edits.items())
    for (_, end), (start, _) in pairwise(spans):
        if start < end:
            raise ValueError(f"{name}: edits overlap at {start:#x}")
    for offset, new in sorted(edits.items()):
        end = offset + len(new)
        if end > len(data):
            raise ValueError(f"{name}: edit at {offset:#x} runs past the file")
        changes.append(
            {
                "file": name,
                "decompressed_offset": f"{offset:#x}",
                "length": len(new),
                "original": bytes(data[offset:end]).hex(),
                "modified": new.hex(),
            }
        )
        data[offset:end] = new
    rebuilt = compress_file(
        bytes(data), size=len(raw), min_end=last_sector_start(len(raw)), lazy=True
    )
    if decompress_file(rebuilt)[0] != bytes(data):
        raise ValueError(f"{name} round trip failed")
    return rebuilt


def is_ending(spec: dict[str, object]) -> bool:
    return spec.get("kind") == "ending"


def mmpack_patches(
    specs: list[dict[str, object]], version: int
) -> list[tuple[int, str, str]]:
    wins = [spec for spec in specs if not is_ending(spec)]
    endings = [spec for spec in specs if is_ending(spec)]
    for group in (wins, endings):
        slots = [int(str(spec["arcade_slot"])) for spec in group]
        if len(set(slots)) != len(slots):
            raise ValueError(f"a slot appears twice: {slots}")
        files = [str(spec["mc_file"]) for spec in group]
        if len(set(files)) != len(files):
            raise ValueError(f"an MC file appears twice: {files}")
    slots = [int(str(spec["arcade_slot"])) for spec in wins]
    ending_slots = [int(str(spec["arcade_slot"])) for spec in endings]
    if endings and version != 4:
        raise ValueError("ending specs need patch version 4")
    for spec in endings:
        match = [w for w in wins if w["arcade_slot"] == spec["arcade_slot"]]
        if not match or match[0]["mc_file"] != spec["mc_file"]:
            raise ValueError(f"ending slot {spec['arcade_slot']} has no win-quote spec")
        if match[0]["table_offset"] != spec["table_offset"]:
            raise ValueError(f"ending slot {spec['arcade_slot']}: table offsets differ")
    if version == 4:
        return patches_v4(slots, ending_slots)
    if version == 2:
        if slots != [ENGLISH_SLOT2 // 2]:
            raise ValueError("version 2 builds Ryu (slot 9) alone")
        return PATCHES
    if version == 3:
        return patches_v3(slots)
    raise ValueError(f"unknown patch version {version}")


SPECIAL_FILE = "MC08.SHP;1"  # Apocalypse's file holds the boss boxes
ALPHA_CHUN_LI, CHUN_LI = 18, 11
NO_CHALLENGERS = 0x0605F838  # the region read that picks the sign (NOCH-001)


def shared_slots(spec: dict[str, object]) -> list[int]:
    value = spec.get("mced_shared_with", [])
    return [int(str(x)) for x in value] if isinstance(value, list) else []


def special_patches(
    specs: list[dict[str, object]], version: int
) -> list[tuple[int, str, str]]:
    """``--special``'s ``MMPACK.PCA`` changes: the boss boxes and slot 18."""
    if version != 4:
        raise ValueError("--special needs patch version 4")
    files = {str(s["mc_file"]) for s in specs if not is_ending(s)}
    if SPECIAL_FILE not in files:
        raise ValueError(f"--special needs the {SPECIAL_FILE} win-quote spec")
    shared = [s for s in specs if is_ending(s) and ALPHA_CHUN_LI in shared_slots(s)]
    if [int(str(s["arcade_slot"])) for s in shared] != [CHUN_LI]:
        raise ValueError("--special needs Chun-Li's ending spec, shared with slot 18")
    alpha = slot_patches([ALPHA_CHUN_LI]) + ending_slot_patches([ALPHA_CHUN_LI])
    return [*boss_boxes.patches(), *alpha]


def with_extra(
    patches: list[tuple[int, str, str]], extra: list[tuple[int, str, str]], what: str
) -> list[tuple[int, str, str]]:
    """``patches`` plus ``extra``; no two may touch the same bytes."""
    taken = {a + i for a, old, _ in patches for i in range(len(as_bytes(old)))}
    for address, old, _ in extra:
        if any(address + i in taken for i in range(len(as_bytes(old)))):
            raise ValueError(f"{address:#x}: a {what} patch overlaps another patch")
    return [*patches, *extra]


def with_names(
    patches: list[tuple[int, str, str]], names: str
) -> list[tuple[int, str, str]]:
    """``patches`` plus the name variant's; no two may touch the same bytes."""
    return with_extra(patches, name_patches(names), "name")


def no_challengers_patches() -> list[tuple[int, str, str]]:
    """``--no-challengers``: the sign's region read taken as US (`EXP-0063`)."""
    return [(NO_CHALLENGERS, REGION_READ, US_REGION)]


def build_mced(
    raw: bytes,
    slots: list[int],
    changes: list[dict[str, object]],
    shared: list[int] | None = None,
    saturn: dict[str, list[dict[str, object]]] | None = None,
) -> bytes:
    decoded, _ = decompress_file(raw)
    data = bytearray(decoded)
    edits = mced_english_scripts(decoded, slots, shared)
    if saturn is not None:
        edits += label_edits(decoded, saturn, slots) + entry_edits(decoded, saturn)
    for offset, old, new in edits:
        if data[offset : offset + len(old)] != old:
            raise ValueError(
                f"MCED.SHP {offset:#x}: found {data[offset : offset + len(old)].hex()}"
            )
        data[offset : offset + len(old)] = new
        changes.append(
            {
                "file": "MCED.SHP;1",
                "decompressed_offset": f"{offset:#x}",
                "length": len(old),
                "original": old.hex(),
                "modified": new.hex(),
            }
        )
    rebuilt = compress_file(
        bytes(data), size=len(raw), min_end=last_sector_start(len(raw)), lazy=True
    )
    if decompress_file(rebuilt)[0] != bytes(data):
        raise ValueError("MCED.SHP round trip failed")
    return rebuilt


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


def changed_range(name: str, raw: bytes, rebuilt: bytes) -> dict[str, object]:
    """The span from the first to the last changed byte of a raw file (rule 12)."""
    diff = [i for i in range(len(raw)) if raw[i] != rebuilt[i]]
    first, last = diff[0], diff[-1] + 1
    return {
        "file": name,
        "file_offset": f"{first:#x}",
        "length": last - first,
        "original": raw[first:last].hex(),
        "modified": rebuilt[first:last].hex(),
    }


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
    parser.add_argument("--patch-version", type=int, choices=(2, 3, 4), default=3)
    parser.add_argument("--names", choices=VARIANTS, default="us")
    parser.add_argument("--boot-warnings", action="store_true")
    parser.add_argument("--special", action="store_true")
    parser.add_argument("--no-challengers", action="store_true")
    parser.add_argument("--image", type=Path, help="also build the image here")
    args = parser.parse_args(argv)
    if len(args.paths) < 2:
        parser.error("give at least one SPEC and OUT")
    *spec_paths, out = args.paths
    specs = [json.loads(path.read_text()) for path in spec_paths]
    saturn = load_saturn() if args.names == "saturn" else None
    named = {
        str(spec["mc_file"]) + (" ending" if is_ending(spec) else ""): (
            {} if saturn is None else text_edits(saturn, str(path))
        )
        for path, spec in zip(spec_paths, specs, strict=True)
    }
    edited: list[dict[str, object]] = []
    patches = with_names(mmpack_patches(specs, args.patch_version), args.names)
    if args.special:
        patches += special_patches(specs, args.patch_version)
    if args.no_challengers:
        patches = with_extra(patches, no_challengers_patches(), "no-challengers")
    out.mkdir(parents=True, exist_ok=False)
    program = args.program.read_bytes()
    changes: list[dict[str, object]] = []
    summary: dict[str, object] = {
        "patch_version": args.patch_version,
        "names": args.names,
        "boot_warnings": args.boot_warnings,
        "special": args.special,
        "no_challengers": args.no_challengers,
    }
    endings = {str(s["mc_file"]): s for s in specs if is_ending(s)}
    for spec in (s for s in specs if not is_ending(s)):
        name = str(spec["mc_file"])
        english = compile_records(spec, program, args.fix_grammar, named[name], edited)
        if name in endings:
            if len(english) != ENDING_RECORDS:
                raise ValueError(f"{name}: win quotes are not {ENDING_RECORDS} bytes")
            ending = compile_records(
                endings[name],
                program,
                args.fix_grammar,
                named[f"{name} ending"],
                edited,
            )
            summary[f"{name} ending_sha256"] = hashlib.sha256(ending).hexdigest()
            english += ending
        raw = read_file(name)
        table = int(str(spec["table_offset"]), 16)
        extra = None
        if args.special and name == SPECIAL_FILE:
            extra = boss_boxes.records(boss_boxes.load(), args.names)
        rebuilt = build_mc(raw, english, table, name, changes, extra)
        summary[name] = file_summary(raw, rebuilt)
        summary[f"{name} english_sha256"] = hashlib.sha256(english).hexdigest()
        (out / name.split(";")[0]).write_bytes(rebuilt)
    built = [str(spec["mc_file"]) for spec in specs if not is_ending(spec)]
    if endings:
        raw = read_file("MCED.SHP;1")
        slots = [int(str(s["arcade_slot"])) for s in endings.values()]
        shared = [
            int(x) for s in endings.values() for x in s.get("mced_shared_with", [])
        ]
        rebuilt = build_mced(raw, slots, changes, shared, saturn)
        summary["MCED shared slots"] = shared
        summary["MCED.SHP;1"] = file_summary(raw, rebuilt)
        (out / "MCED.SHP").write_bytes(rebuilt)
        built.append("MCED.SHP;1")
    if args.boot_warnings:
        originals = {name: read_file(f"{name};1") for name in BOOT_WARNINGS}
        pictures = build_boot_warnings(read_file("FIX.PRS;1"), originals, load_layout())
        for name, picture in pictures.items():
            changes.append(changed_range(name, originals[name], picture))
            summary[f"{name};1"] = file_summary(originals[name], picture)
            (out / name).write_bytes(picture)
            built.append(f"{name};1")
    raw = read_file("MMPACK.PCA;1")
    rebuilt = build_mmpack(raw, changes, patches)
    summary["MMPACK.PCA;1"] = file_summary(raw, rebuilt)
    (out / "MMPACK.PCA").write_bytes(rebuilt)
    if saturn is not None:
        summary["saturn_name_records"] = edited
    (out / "changes.json").write_text(
        json.dumps({"files": summary, "changes": changes}, indent=1) + "\n"
    )
    print(json.dumps(summary, indent=1))
    if args.image is None:
        return 0
    files = []
    for name in [*built, "MMPACK.PCA;1"]:
        files += ["--file", name, "--data", str(out / name.split(";")[0])]
    return patch_image(
        [
            *("--source-dir", str(TRACK.parent), "--manifest", str(MANIFEST)),
            *("--track", TRACK.name, *files, "--out-dir", str(args.image)),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())

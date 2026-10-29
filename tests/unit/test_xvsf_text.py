from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from tools.reference.mame_audit import RomEntry, RomSet
from tools.reference.xvsf_text import (
    DECODE,
    LINE_CODES,
    RECORD_CODES,
    SLOTS,
    build_program,
    code_contexts,
    decode_codes,
    main,
    read_record,
    read_table,
    unmapped,
)

ENCODE = {char: code for code, char in DECODE.items()}


def encode_line(text: str) -> bytes:
    codes = [ENCODE[c] for c in text.ljust(LINE_CODES)]
    return b"".join(code.to_bytes(2, "big") for code in codes)


def record(line1: str, line2: str) -> bytes:
    return encode_line(line1) + encode_line(line2)


def test_map_layout_matches_the_tile_sheet() -> None:
    assert ENCODE["A"] == 0x0681 and ENCODE["O"] == 0x068F
    assert ENCODE["P"] == 0x06E0 and ENCODE["Z"] == 0x06EA
    assert ENCODE["a"] == 0x0691 and ENCODE["z"] == 0x06FA
    assert ENCODE["'"] == 0x0677 and ENCODE["."] == 0x067E and ENCODE["?"] == 0x06DF
    assert ENCODE[" "] == 0x0020
    assert decode_codes([0x0681, 0x0134]) == "A{0134}"


def test_read_record_and_table_with_aliases() -> None:
    start, table = 0x200, 0x100
    image = bytearray(0x200 + 5 * 2 * RECORD_CODES + 0x10)
    texts = [("I'm first.", ""), ("Second, ok?", "yes!"), ("Third", "")]
    texts += [("Fourth", ""), ("Fifth", "")]
    for i, (a, b) in enumerate(texts):
        address = start + i * 2 * RECORD_CODES
        image[address : address + 2 * RECORD_CODES] = record(a, b)
    end = start + 5 * 2 * RECORD_CODES
    pointers = [start, start + 2 * 2 * RECORD_CODES] + [start] * (SLOTS - 2)
    for i, pointer in enumerate(pointers):
        image[table + 4 * i : table + 4 * i + 4] = pointer.to_bytes(4, "big")
    assert read_record(bytes(image), start + 2 * RECORD_CODES) == [
        "Second, ok?",
        "yes!",
    ]
    slots = read_table(bytes(image), table, start, end)
    assert len(slots[0]["records"]) == 2  # type: ignore[arg-type]
    assert len(slots[1]["records"]) == 3  # type: ignore[arg-type]
    assert slots[2]["alias_of"] == 0
    assert unmapped([["A{0134}", "b"]]) == ["{0134}"]
    contexts = code_contexts(bytes(image), start, start + 2 * RECORD_CODES)
    assert contexts["0677 '"] == {"LL": 1}


def test_read_table_rejects_off_grid_pointer() -> None:
    image = bytearray(0x400)
    for i in range(SLOTS):
        image[4 * i : 4 * i + 4] = (0x102).to_bytes(4, "big")
    with pytest.raises(ValueError, match="outside the block grid"):
        read_table(bytes(image), 0, 0x100, 0x300)


def test_build_program_swaps_words_and_finds_relabelled_members(tmp_path: Path) -> None:
    data = bytes(range(8))
    clone = tmp_path / "clone.zip"
    with zipfile.ZipFile(clone, "w") as bundle:
        bundle.writestr("old.label", data)
    romset = RomSet(
        "clone",
        [
            RomEntry(
                "new.label",
                len(data),
                "00000000",
                hashlib.sha1(data).hexdigest(),
                "maincpu",
                0,
                "ROM_LOAD16_WORD_SWAP",
            )
        ],
    )
    assert build_program([clone], romset) == bytes([1, 0, 3, 2, 5, 4, 7, 6])


def test_program_out_writes_the_swapped_image(tmp_path: Path) -> None:
    data = bytes(range(8))
    with zipfile.ZipFile(tmp_path / "game.zip", "w") as bundle:
        bundle.writestr("prog.bin", data)
    sha1 = hashlib.sha1(data).hexdigest()
    driver = tmp_path / "cps2.cpp"
    driver.write_text(
        "ROM_START( game )\n"
        'ROM_REGION( 0x8, "maincpu", 0 )\n'
        f'ROM_LOAD16_WORD_SWAP( "prog.bin", 0x0, 0x8, CRC(00000000) SHA1({sha1}) )\n'
        "ROM_END\n"
    )
    out = tmp_path / "program.bin"
    args = ["--driver", str(driver), "--set", "game", "--rompath", str(tmp_path)]
    assert main([*args, "--program-out", str(out)]) == 0
    assert out.read_bytes() == bytes([1, 0, 3, 2, 5, 4, 7, 6])


def test_main_needs_an_output(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["--driver", "x", "--rompath", str(tmp_path)])

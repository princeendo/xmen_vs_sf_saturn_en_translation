from __future__ import annotations

import pytest

from tools.disc import name_toggle
from tools.disc.english_mode import as_bytes
from tools.disc.name_toggle import entry, menu_patches, patches, routine, runs, tables
from tools.sh2.asm import Assembler
from tools.sh2.disasm import decode


def test_every_form_decodes_back() -> None:
    a = Assembler(0x06000000)
    a.mov_l_label("lit", 3)
    a.mov_l_load(4, 5, post=True)
    a.mov_b_load(6, 7)
    a.mov_w_store(0, 1)
    a.mov_b_store(2, 13)
    a.tst(9, 9)
    a.or_(0, 11)
    a.cmp_eq(0, 1)
    a.cmp_hs(10, 12)
    a.extu_b(11, 11)
    a.shll8(13)
    a.dt(3)
    a.jsr(0)
    a.add(9, 13)
    a.add_imm(-1, 2)
    a.mov_imm(2, 0)
    a.label("back")
    a.branch("bf/s", "back")
    a.branch("bra", "back")
    a.rts()
    a.align4()
    a.label("lit")
    a.long(0x0601E370)
    code = a.assemble()
    text = [decode(code, 0x06000000, 0x06000000 + i)[1] for i in range(0, 38, 2)]
    assert text == [
        "mov.l @(0x06000028),r3   ! 0x0601E370",
        "mov.l @r4+,r5",
        "mov.b @r6,r7",
        "mov.w r0,@r1",
        "mov.b r2,@r13",
        "tst r9,r9",
        "or r0,r11",
        "cmp/eq r0,r1",
        "cmp/hs r10,r12",
        "extu.b r11,r11",
        "shll8 r13",
        "dt r3",
        "jsr @r0",
        "add r9,r13",
        "add #-1,r2",
        "mov #2,r0",
        "bf/s 0x06000020",
        "bra 0x06000020",
        "rts",
    ]


def test_out_of_reach_branches_are_refused() -> None:
    a = Assembler(0x06000000)
    a.branch("bt", "far")
    for _ in range(200):
        a.nop()
    a.label("far")
    with pytest.raises(ValueError, match="out of reach"):
        a.assemble()


def test_runs_join_close_differences() -> None:
    us = bytes(20)
    saturn = bytearray(us)
    saturn[2] = saturn[4] = saturn[15] = 1
    assert runs(us, bytes(saturn)) == [(2, b"\x01\x00\x01"), (15, b"\x01")]


def test_an_entry_holds_the_us_signature_and_the_saturn_bytes() -> None:
    us = bytes(range(32))
    saturn = bytearray(us)
    saturn[10:12] = b"\xaa\xbb"
    blob = entry(us, bytes(saturn))
    assert int.from_bytes(blob[:2], "big") == len(blob)
    assert blob[2:4] == (10).to_bytes(2, "big") and blob[4:8] == us[10:14]
    assert blob[8:] == (10).to_bytes(2, "big") + b"\x02\xaa\xbb"


BASE = 0x0601F000


def synthetic_second_segment() -> bytes:
    """The four row lists and the dispatch table at their real addresses,
    with made-up labels (no game text)."""
    seg = bytearray(0x0602B000 - BASE)
    labels = [f"ROW{k}".ljust(16).encode() + b"\0" for k in range(9)]
    combo = b"COMBO GAGE".ljust(16) + b"\0"
    strings_at = 0x0602A800
    where = {}
    for s in [*labels, combo]:
        where[s] = strings_at
        seg[strings_at - BASE : strings_at - BASE + len(s)] = s
        strings_at += len(s)
    for game, rows in (
        (0x0602A234, labels),
        (0x0602A248, [*labels, combo]),
        (0x0602A25E, labels),
        (0x0602A272, [*labels, combo]),
    ):
        for k, row in enumerate(rows):
            at = game - BASE + 2 * k
            seg[at : at + 2] = (where[row] - game).to_bytes(2, "big")
    for k in range(12):
        at = 0x06028128 - BASE + 4 * k
        seg[at : at + 4] = (0x06028000 + k).to_bytes(4, "big")
    return bytes(seg)


def read_list(blob: bytes, origin: int, at: int, count: int = 99) -> list[bytes]:
    rows = []
    for k in range(count):
        word = at - origin + 2 * k
        offset = int.from_bytes(blob[word : word + 2], "big")
        if not offset:
            break
        start = at + offset - origin
        rows.append(blob[start : blob.index(b"\0", start)])
    return rows


def test_the_menu_blob_adds_names_and_combo_gauge() -> None:
    origin = 0x002FF9D0
    blob, addresses = name_toggle.menu_blob(origin, synthetic_second_segment(), BASE)
    nine = read_list(blob, origin, addresses["list_6028560"])
    ten = read_list(blob, origin, addresses["list_6028568"])
    assert [r.strip() for r in nine][-1] == b"NAMES" and len(nine) == 10
    assert [r.strip() for r in ten][-2:] == [b"NAMES", b"COMBO GAUGE"]
    values = read_list(blob, origin, addresses["names_values"], 2)
    assert [v.strip() for v in values] == [b"U.S.", b"SATURN"]
    table = addresses["table"] - origin
    entries = [
        int.from_bytes(blob[table + 4 * k : table + 4 * k + 4], "big")
        for k in range(13)
    ]
    assert entries[:12] == [0x06028000 + k for k in range(12)]
    assert entries[12] == addresses["gauge_handler"]
    assert origin + len(blob) <= name_toggle.TAIL_END


def test_patches_keep_their_size() -> None:
    _, addresses = name_toggle.menu_blob(0x002FF9D0, synthetic_second_segment(), BASE)
    for _, old, new in patches(addresses):
        assert len(as_bytes(old)) == len(as_bytes(new))


def test_the_routine_fits_its_room_and_the_tables_hold_every_site() -> None:
    assert len(routine(name_toggle.CODE, 0x0601EDC0)) <= name_toggle.CODE_ROOM
    blob = tables(b"")
    assert len(blob) % 4 == 0
    assert blob[:4] == (0x0604FBDA).to_bytes(4, "big") and blob[4:6] == b"\x90\x9c"


def test_the_names_row_stores_the_setting_and_the_draw_block_calls_out() -> None:
    _, addresses = name_toggle.menu_blob(0x002FF9D0, synthetic_second_segment(), BASE)
    by_address = {a: n for a, _, n in menu_patches(addresses)}
    assert as_bytes(by_address[0x06028C64]) == name_toggle.SETTING.to_bytes(4, "big")
    assert as_bytes(by_address[0x06028C68]) == addresses["draw"].to_bytes(4, "big")
    block = as_bytes(by_address[0x06028BF8])
    code = [decode(block, 0x06028BF8, 0x06028BF8 + i)[1] for i in (0, 2)]
    assert code[0].startswith("mov.l @(0x06028C68),r0") and code[1] == "jsr @r0"


def test_the_routine_starts_with_the_handlers_increment() -> None:
    code = routine(name_toggle.CODE, 0x0601EDC0)
    first = [
        decode(code, name_toggle.CODE, name_toggle.CODE + i)[1] for i in range(2, 8, 2)
    ]
    assert first == ["mov.l @r0,r1", "add #1,r1", "mov.l r1,@r0"]
    assert decode(code, name_toggle.CODE, name_toggle.CODE)[1].endswith("! 0x060148C0")

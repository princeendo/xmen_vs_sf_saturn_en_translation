"""An Options row that switches the name convention at run time (`LOC-009`).

`LOC-008` (`EXP-0068`, D-060) measured what separates the two name variants:
the 10 art and voice sites in ``MMPACK.PCA`` and a few records, boxes and
labels in ``MC08``, ``MC0E``, ``MC10``, ``MC11`` and ``MCED.SHP``. The toggle
build starts from the American files with the sites unpatched, and adds:

* **The setting:** the byte ``SETTING`` (``0x0601E370``), inside the
  settings block the game saves with BACK UP: SAVE (`EXP-0069`); 0 is the
  American names (the default, and what existing saves hold), 1 the Saturn's.
  No code reads or writes it but the row (`EXP-0069` ``writes2``).
* **The rows** (`LOC-010`): NAMES is always the tenth Options row (menu
  state 11, the old COMBO GAGE row's handler, its value literal pointed at
  ``SETTING``); the hidden row returns as an eleventh, ``COMBO GAUGE`` (the
  user's spelling), still shown only when ``0x0601E36C`` is non-zero and
  still setting the gauge byte ``0x0601E359``. ``menu_blob`` builds, after
  the routine: the four row lists with their label strings (copied from the
  game's, NAMES and COMBO GAUGE added), the menu's dispatch table with a
  thirteenth entry (state 12, COMBO GAUGE's handler), that handler, and a
  routine that draws NAMES's value and, with the flag, COMBO GAUGE's.
  ``menu_patches`` points the game at them, raises the cursor's row count by
  one, and lets the exit line follow the last row (line 27 with eleven
  rows).
* **The routine** (``routine``, at ``CODE``), loaded as a third segment of
  ``MMPACK.PCA`` into the end of WRAM-L, after the last file loaded there
  (``VS00.PRS`` ends at ``0x002FF8C1``; zero in every WRAM-L dump,
  `EXP-0069`). It is called from the main V-blank-in handler
  (``0x060148CC``) in place of its frame-counter increment, which it does
  first. Then:

  - **art and voice:** each of the 10 name sites (``SITES``) gets
    ``mov #2,r0`` (American, as ``--names us`` builds) or the original read
    of the region word (Saturn), but only while the word before it is that
    site's own ``mov.w`` and the word after is ``tst r0,r0``, and it holds
    one of the two: other modules replace that code at times (the attract,
    part of the ending);
  - **text, for the Saturn names:** in each fighter buffer (``BASES``) a
    changed file is found by a 4-byte signature of its American bytes, and
    that file's Saturn bytes are copied over it (``entry``). A patched file
    no longer matches its signature.

  Its tables (``SITES``, then the entries) follow the continue hints in the
  gap after the first segment, where the build appends them.

Each patch is (WRAM-H address, original bytes, new bytes); the originals are
checked before any write.
"""

from __future__ import annotations

from tools.sh2.asm import Assembler

SETTING = 0x0601E370  # EXP-0068/EXP-0069: no other reader or writer
# 0x0601E138 is the interrupt-handler table (EXP-0069), not free room.
CODE, CODE_ROOM = 0x002FF900, 256  # EXP-0069: after VS00.PRS, zero in every dump
TAIL_END = 0x00300000  # the end of WRAM-L; the menu blob follows the routine
COUNTER = 0x060148C0  # the V-blank-in handler's frame counter
BASES = (0x0024D000, 0x060B0000, 0x060C1000, 0x060D2000)  # D-012, D-022, D-033
SIGNATURE = 4
JOIN = 3
US_OP, SATURN_OP, NEXT_OP = 0xE002, 0x00BD, 0x2008  # mov #2,r0; region read; tst
SITES = {  # name site (tools.disc.names.US_SITES) -> the mov.w before it
    0x0604FBDA: 0x909C,
    0x0604FC52: 0x9060,
    0x060639E6: 0x9010,
    0x0606E004: 0x9021,
    0x06073A28: 0x9082,
    0x0607FDA8: 0x905F,
    0x0607FE0E: 0x902C,
    0x0607FE94: 0x90C8,
    0x0607FEFA: 0x9095,
    0x0607FFA2: 0x9041,
}
HOOK_LITERAL = 0x06014958  # loaded only by 0x060148F8
HOOK_CODE = (0x060148FA, "6102 7101 2012", "400B 0009 0009")
VALUE_LITERAL = (0x06028C64, "0601 E359")  # state 11's byte (and its drawing)
NAMES_VALUES = ("U.S.", "SATURN")
FLAG, GAUGE = 0x0601E36C, 0x0601E359
GAUGE_VALUES = 0x0602A500  # the game's NORMAL / FULL list
ROWS_LABEL, GAUGE_LABEL = "NAMES", "COMBO GAUGE"
ROW_LISTS = {  # list literal -> the game's list (EXP-0068)
    0x06028560: 0x0602A234,  # nine rows
    0x06028568: 0x0602A248,  # ten (COMBO GAGE)
    0x06028524: 0x0602A25E,  # nine, BACK UP blank
    0x06028528: 0x0602A272,  # ten, BACK UP blank
}
DISPATCH = (0x06027F78, 0x06028128, 12)  # literal, table, entries (states 0-11)
CURSOR_LIMITS = {  # mov #max,r7 for the cursor: nine/ten rows -> ten/eleven
    0x060289EA: ("E70A", "E70B"),
    0x06028A02: ("E70B", "E70C"),
    0x06028A56: ("E70A", "E70B"),
    0x06028A6E: ("E70B", "E70C"),
    0x06028A9A: ("E70A", "E70B"),
    0x06028AB2: ("E70B", "E70C"),
}
EXIT_LINE = (0x0602856E, "E219", "0009")  # mov #25,r2: r2 is already the next line
DRAW_LITERAL = (0x06028C68, "0602 A500")
DRAW_BLOCK = (
    0x06028BF8,
    "D119 6010 2008 890B D118 6010 D118 6813 4000 001D 380C E115 E217 E305 C330 0032",
)
CALLS = {  # the routines a row handler calls (EXP-0069)
    "stepper": 0x06029CB4,
    "cursor": 0x060289E0,
    "labels": 0x060284C8,
    "values": 0x06028B28,
    "start": 0x06028AD0,
    "pad": 0x060AC2EC,
}


def _hex(blob: bytes) -> str:
    raw = blob.hex().upper()
    return " ".join(raw[i : i + 4] for i in range(0, len(raw), 4))


def _string(seg2: bytes, base: int, address: int) -> bytes:
    at = address - base
    return seg2[at : seg2.index(b"\0", at) + 1]


def menu_blob(
    origin: int, seg2: bytes, base: int = 0x0601F000
) -> tuple[bytes, dict[str, int]]:
    """The menu data and code at ``origin``; ``seg2`` is the game's decoded
    second segment, loaded at ``base``. Returns the bytes and their addresses."""
    names = ROWS_LABEL.ljust(16).encode("ascii") + b"\0"
    gauge = GAUGE_LABEL.ljust(16).encode("ascii") + b"\0"
    lists: dict[int, list[bytes]] = {}
    for literal, game in ROW_LISTS.items():
        rows, at = [], game - base
        while offset := int.from_bytes(seg2[at : at + 2], "big"):
            rows.append(_string(seg2, base, game + offset))
            at += 2
        combo = rows[-1].startswith(b"COMBO GAGE")
        rows = (rows[:-1] if combo else rows) + [names] + ([gauge] if combo else [])
        lists[literal] = rows
    strings = list(dict.fromkeys(s for rows in lists.values() for s in rows))
    a = Assembler(origin)
    addresses: dict[str, int] = {}
    for literal, rows in lists.items():
        a.label(f"list_{literal:x}")
        addresses[f"list_{literal:x}"] = a.pc
        for _row in rows:
            a.word(0)  # placeholder, fixed below
        a.word(0)
    a.label("names_values")
    addresses["names_values"] = a.pc
    a.word(0)
    a.word(0)
    value_strings = [v.ljust(6).encode("ascii") + b"\0" for v in NAMES_VALUES]
    string_at: dict[bytes, int] = {}
    for s in strings + value_strings:
        string_at[s] = a.pc
        a.data(s)
    a.data(bytes(-a.pc % 4))  # the strings end anywhere
    a.label("table")
    addresses["table"] = a.pc
    for k in range(DISPATCH[2]):
        at = DISPATCH[1] - base + 4 * k
        a.long(int.from_bytes(seg2[at : at + 4], "big"))
    a.long("gauge_handler")
    a.label("gauge_handler")  # state 12: as state 11's handler, for the gauge byte
    addresses["gauge_handler"] = a.pc
    a.mov_l_label("pad", 1)
    a.mov_l_label("gauge", 6)
    a.mov_imm(1, 7)
    a.mov_imm(1, 8)
    a.mov_imm(1, 9)
    for call in ("stepper", "cursor", "labels", "values", "start"):
        a.mov_l_label(call, 0)
        a.jsr(0)
        a.push_pr()  # the game's convention: the callee pops it
    a.pop_pr()
    a.rts()
    a.nop()
    a.label("draw")  # called from the old row-10 drawing (DRAW_BLOCK)
    addresses["draw"] = a.pc
    for byte, values, line, skip in (
        ("setting", "names_list", 23, None),
        ("gauge", "gauge_list", 25, "flag"),
    ):
        if skip:
            a.mov_l_label(skip, 1)
            a.mov_b_load(1, 0)
            a.tst(0, 0)
            a.branch("bt", "drawn")
        a.mov_l_label(byte, 1)
        a.mov_b_load(1, 0)
        a.mov_l_label(values, 1)
        a.mov(1, 8)
        a.shll(0)
        a.mov_w_index(1, 0)
        a.add(0, 8)
        a.mov_imm(21, 1)
        a.mov_imm(line, 2)
        a.mov_imm(5, 3)
        a.trapa(48)
        a.word(0x0032)
    a.label("drawn")
    a.rts()
    a.nop()
    a.align4()
    pool: list[tuple[str, int | str]] = [
        ("pad", CALLS["pad"]),
        ("gauge", GAUGE),
        ("setting", SETTING),
        ("flag", FLAG),
        ("names_list", "names_values"),
        ("gauge_list", GAUGE_VALUES),
    ]
    pool += [(c, CALLS[c]) for c in ("stepper", "cursor", "labels", "values", "start")]
    for name, value in pool:
        a.label(name)
        a.long(value)
    blob = bytearray(a.assemble())
    for literal, rows in lists.items():
        start = addresses[f"list_{literal:x}"]
        for k, row in enumerate(rows):
            at = start - origin + 2 * k
            blob[at : at + 2] = (string_at[row] - start).to_bytes(2, "big")
    start = addresses["names_values"]
    for k, s in enumerate(value_strings):
        at = start - origin + 2 * k
        blob[at : at + 2] = (string_at[s] - start).to_bytes(2, "big")
    return bytes(blob), addresses


def menu_patches(addresses: dict[str, int]) -> list[tuple[int, str, str]]:
    """Point the game's menu at ``menu_blob``'s rows, table and drawing."""
    out = [(*VALUE_LITERAL, _hex(SETTING.to_bytes(4, "big")))]
    for literal, game in ROW_LISTS.items():
        new = addresses[f"list_{literal:x}"]
        out.append(
            (literal, _hex(game.to_bytes(4, "big")), _hex(new.to_bytes(4, "big")))
        )
    out.append(
        (
            DISPATCH[0],
            _hex(DISPATCH[1].to_bytes(4, "big")),
            _hex(addresses["table"].to_bytes(4, "big")),
        )
    )
    out += [(at, old, new) for at, (old, new) in CURSOR_LIMITS.items()]
    out.append(EXIT_LINE)
    out.append((*DRAW_LITERAL, _hex(addresses["draw"].to_bytes(4, "big"))))
    call = "D01B 400B 0009" + " 0009" * 13
    out.append((DRAW_BLOCK[0], DRAW_BLOCK[1], call))
    return out


def runs(us: bytes, saturn: bytes, join: int = JOIN) -> list[tuple[int, bytes]]:
    """(offset, Saturn bytes) for each run of differing bytes; runs fewer than
    ``join`` equal bytes apart are joined (a run costs 3 header bytes)."""
    if len(us) != len(saturn):
        raise ValueError("the variants' decoded sizes differ")
    spans: list[list[int]] = []
    for i, (a, b) in enumerate(zip(us, saturn, strict=True)):
        if a == b:
            continue
        if spans and i - spans[-1][1] < join:
            spans[-1][1] = i + 1
        else:
            spans.append([i, i + 1])
    return [(start, saturn[start:end]) for start, end in spans]


def entry(us: bytes, saturn: bytes) -> bytes:
    """One file's entry: length, signature offset, the US signature, runs."""
    found = runs(us, saturn)
    if not found:
        raise ValueError("the variants do not differ")
    at = found[0][0]
    body = at.to_bytes(2, "big") + us[at : at + SIGNATURE]
    for offset, data in found:
        if len(data) > 0xFF:
            raise ValueError("run too long")
        body += offset.to_bytes(2, "big") + bytes([len(data)]) + data
    return (len(body) + 2).to_bytes(2, "big") + body


def tables(entries: bytes) -> bytes:
    """The site table (address, the word before, 2 spare) and the entries."""
    sites = b"".join(
        site.to_bytes(4, "big") + before.to_bytes(2, "big") + bytes(2)
        for site, before in SITES.items()
    )
    blob = sites + entries + bytes(2)
    return blob + bytes(-len(blob) % 4)


def read16(a: Assembler, ptr: int, n: int) -> None:
    """r{n} = the big-endian halfword at @r{ptr}+ (any alignment); uses r0."""
    a.mov_b_load(ptr, n, post=True)
    a.extu_b(n, n)
    a.shll8(n)
    a.mov_b_load(ptr, 0, post=True)
    a.extu_b(0, 0)
    a.or_(0, n)


def routine(origin: int, data: int) -> bytes:
    """The V-blank-in routine, assembled at ``origin``; ``tables`` at ``data``."""
    a = Assembler(origin)
    a.mov_l_label("counter", 0)  # the handler's own increment
    a.mov_l_load(0, 1)
    a.add_imm(1, 1)
    a.mov_l_store(1, 0)
    a.mov_l_label("setting", 1)
    a.mov_b_load(1, 2)  # r2: the setting (0 = American)
    a.mov_w_label("us_op", 6)  # r6: the sites' opcode, r7: the other one
    a.mov_w_label("saturn_op", 7)
    a.tst(2, 2)
    a.branch("bt", "sites")
    a.mov(6, 7)
    a.mov_w_label("saturn_op", 6)
    a.label("sites")
    a.mov_l_label("data", 8)
    a.mov_imm(len(SITES), 3)
    a.label("site")
    a.mov_l_load(8, 9, post=True)  # the site
    a.mov_w_load(8, 4)  # the word before it
    a.add_imm(4, 8)
    a.mov(9, 10)
    a.add_imm(-2, 10)
    a.mov_w_load(10, 0)
    a.cmp_eq(0, 4)
    a.branch("bf", "next_site")
    a.mov_w_r0_disp(4, 10)  # the word after it
    a.mov_w_label("next_op", 4)
    a.cmp_eq(0, 4)
    a.branch("bf", "next_site")
    a.mov_w_load(9, 0)
    a.cmp_eq(0, 7)
    a.branch("bf", "next_site")
    a.mov_w_store(6, 9)
    a.label("next_site")
    a.dt(3)
    a.branch("bf", "site")
    a.tst(2, 2)
    a.branch("bt", "done")  # American: the files are already American
    a.mov_l_label("bases", 11)
    a.label("base")
    a.mov_l_load(11, 9, post=True)
    a.tst(9, 9)
    a.branch("bt", "done")
    a.mov(8, 10)  # r8 still points at the entries
    a.label("entry")
    a.mov(10, 12)
    read16(a, 12, 13)  # length
    a.tst(13, 13)
    a.branch("bt", "base")
    a.add(13, 10)  # r10: the next entry
    read16(a, 12, 13)  # signature offset
    a.add(9, 13)
    a.mov_imm(SIGNATURE, 3)
    a.label("compare")
    a.mov_b_load(13, 0, post=True)
    a.mov_b_load(12, 1, post=True)
    a.cmp_eq(0, 1)
    a.branch("bf", "entry")
    a.dt(3)
    a.branch("bf", "compare")
    a.label("run")
    a.cmp_hs(10, 12)
    a.branch("bt", "entry")
    read16(a, 12, 13)  # run offset
    a.add(9, 13)
    a.mov_b_load(12, 3, post=True)  # run length
    a.extu_b(3, 3)
    a.label("copy")
    a.mov_b_load(12, 0, post=True)
    a.mov_b_store(0, 13)
    a.dt(3)
    a.branch("bf/s", "copy")
    a.add_imm(1, 13)
    a.branch("bra", "run")
    a.nop()
    a.label("done")
    a.rts()
    a.nop()
    for name, value in (
        ("us_op", US_OP),
        ("saturn_op", SATURN_OP),
        ("next_op", NEXT_OP),
    ):
        a.label(name)
        a.word(value)
    a.align4()
    for name, long_value in (
        ("counter", COUNTER),
        ("setting", SETTING),
        ("data", data),
        ("bases", "base_list"),
    ):
        a.label(name)
        a.long(long_value)
    a.label("base_list")
    for base in (*BASES, 0):
        a.long(base)
    code = a.assemble()
    if len(code) > CODE_ROOM:
        raise ValueError(f"the routine is {len(code)} bytes; the room is {CODE_ROOM}")
    return code


def patches(addresses: dict[str, int]) -> list[tuple[int, str, str]]:
    """Every in-place patch: the hook and the rows (the routine and
    ``menu_blob`` are the third segment)."""
    out = [(HOOK_LITERAL, "0601 48C0", _hex(CODE.to_bytes(4, "big"))), HOOK_CODE]
    return out + menu_patches(addresses)

"""Build the arcade's English attract captions into ``OPENING*.ST2`` (`CAP-002`).

The user chose the US arcade's own caption art, layout and colours, with the
banner respelled UNCANNY from the arcade's letters (`EXP-0065`,
``docs/localization_policy.md``). The art is game-derived and read at build
time from ART (``c1.png``-``c3.png``, 352 x 200 crops of the arcade captions;
``banner.png``, the stitched banner): `EXP-0065/caption_art.py` makes it from
MAME snapshots.

How the attract draws a caption (`EXP-0064`, `EXP-0065`): NBG1 tiles. Section
A's script writes NBG1's index and attribute arrays (map updates, frame bit
6); the builder ``0x0601F9E4`` turns them into pattern names, character =
NBG1's base + 4 x index, palette and flips from the attribute. The base is
the VRAM character of the current graphics block's part 1 (section C's for
caption 1). The script's palette records set the source palette; NBG1
palette 0 entry e is source index ``0x3FF`` + e.

Per file, using ``data/attract/caption_room.json`` (the indices each caption
may use, by block):

- **Glyphs:** each caption's art is placed on the plane at its scroll
  (captions 1-3) or along the banner's path (caption 4), each line aligned
  to the 16-pixel grid to need the fewest distinct characters, and cut into
  2 x 2-cell characters; colours become palette entries 1-9 (``ENTRIES``).
- **Blocks:** each glyph's 128 bytes go to its index in the block (part 1
  + 128 x index; caption 1's extra slots in section C's part 2, at 0x20 +
  their VRAM address).
- **Script:** the Japanese caption's map updates are replaced (captions 1-3)
  or, for the banner, its rows are cleared from the window's updates and
  written column by column as it scrolls, switching to the second block's
  indices at the script's re-index frame (files 0-4); the four caption
  palette loads get the arcade colours; the banner's scroll step becomes 9
  pixels a frame (``BANNER_STEP``), so the 1,098-pixel banner crosses the
  screen in the script's frames.
- **Encoding:** section A with `tools.disc.st2_encode.script_encode`, the
  changed graphics blocks with ``lz_encode``; each must fit the original's
  room (the compressed-size field and every later offset stay unchanged; the
  rest is zero padding).

Before returning, the build decodes what it wrote and renders every caption
frame from it (``check``): each must equal the intended English pixel for
pixel. The output is game-derived: write it under ``local/`` only.
"""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.disc.st2_encode import lz_encode, map_encode, script_encode
from tools.disc.st2_stream import (
    SECTOR,
    TAG,
    _objects_end,
    _palette_end,
    blocks,
    lz_decode,
    map_decode,
    miss_payload,
    miss_sectors,
    script_decode,
    sections,
)

ROOM = Path("data/attract/caption_room.json")
SCREEN_W, SCREEN_H = 352, 240
ART_TOP = 12  # screen y of the arcade crops' row 0
ENTRIES = {  # arcade colour -> NBG1 palette 0 entry, and its 4-bit source colour
    "111111": (1, 0xF111),
    "000000": (2, 0xF000),
    "ffffff": (3, 0xFFFF),
    "ffff99": (4, 0xFFF9),
    "ffee00": (5, 0xFFE0),
    "ffcc00": (6, 0xFFC0),
    "ffaa00": (7, 0xFFA0),
    "ff8811": (8, 0xF881),
    "dd6622": (9, 0xFD62),
}
BACKGROUND = 1
PALETTE_ZERO = 0x3FF  # source index of NBG1 palette 0 entry 0
MAP_BIT, PALETTE_BIT, SCROLL_BIT = 6, 4, 2
ARRAY = 0x1000  # index words, then attribute words
TAIL = -1  # Frame.parts key for the bytes after the end word


@dataclass(frozen=True)
class Still:
    """A caption shown whole (captions 1-3)."""

    art: str
    build: int  # script frame of the Japanese caption's map update
    palette: int  # script frame of its palette load
    scroll: tuple[int, int]


STILLS = {
    "caption1": Still("c1.png", 126, 127, (19, 16)),
    "caption2": Still("c2.png", 478, 479, (12, 16)),
    "caption3": Still("c3.png", 724, 724, (16, 272)),
}
BANNER_ART = "banner.png"
BANNER_FIRST, BANNER_CLEAR = 951, 1118  # window: blank fill .. the clear
BANNER_PALETTE = 952
BANNER_X0, BANNER_MOVES = 144, (953, 1115)  # NBG1 x at frame 952; moving frames
BANNER_OLD_STEP, BANNER_STEP = 8, 9
BANNER_TOP = 88  # screen y of the banner's row 0
BANNER_ROWS = range(4, 11)  # plane rows whose words the window's updates lose


# --- script frames, with the bit of each section ------------------------------


@dataclass
class Frame:
    word: int
    parts: dict[int, bytes] = field(default_factory=dict)  # bit -> section bytes


def parse_frames(script: bytes) -> list[Frame]:
    """Section A's frames (`tools.disc.st2_stream.script_frames`), keeping bits."""
    frames, p = [], 0
    while True:
        word = int.from_bytes(script[p : p + 2], "big")
        p += 2
        frame = Frame(word)
        frames.append(frame)
        if word == 0xFFFF:
            frame.parts[TAIL] = script[p:]  # four scripts end with a pad byte
            return frames
        for bit in range(11):
            if not word >> bit & 1 or bit == 10:
                continue
            begin = p
            if bit == 0:
                p += 1 + 2 * bin(script[p] & 0xF).count("1")
            elif bit in (1, 3):
                p += 4
            elif bit == 2:
                mask = script[p]
                p += 1
                for k in range(6):
                    if mask >> k & 1:
                        p += 3 if script[p] == 0 else 1
            elif bit == 9:
                p += 1 + 2 * bin(script[p] & 0x3F).count("1")
            elif bit == 4:
                p = _palette_end(script, p)
            elif bit in (5, 6, 7):
                p = map_decode(script, p)[1]
            else:
                p = _objects_end(script, p)
            frame.parts[bit] = script[begin:p]


def join_frames(frames: Sequence[Frame]) -> bytes:
    out = bytearray()
    for frame in frames:
        if frame.word == 0xFFFF:
            out += b"\xff\xff" + frame.parts.get(TAIL, b"")
            continue
        word = (frame.word & ~0x3FF) | sum(1 << bit for bit in frame.parts)
        out += word.to_bytes(2, "big")
        for bit in sorted(frame.parts):
            out += frame.parts[bit]
    return bytes(out)


def map_words(frame: Frame) -> list[int]:
    if MAP_BIT not in frame.parts:
        return [0xFFFF] * 0x2000
    return map_decode(frame.parts[MAP_BIT], 0)[0]


def set_map(frame: Frame, words: Sequence[int]) -> None:
    if all(w == 0xFFFF for w in words):
        frame.parts.pop(MAP_BIT, None)
    else:
        frame.parts[MAP_BIT] = map_encode(list(words))


def recolour(frame: Frame) -> None:
    """Put the arcade colours in the frame's palette record over palette 0."""
    part = bytearray(frame.parts[PALETTE_BIT])
    flags, p = part[0], 1
    for bit in (0, 2, 4):
        if flags >> bit & 1:
            while part[p] != 0xFF:
                p += 3
            p += 1
    if not flags >> 5 & 1:
        raise ValueError("no palette set records")
    cursor, done = 0, False
    while part[p] != 0xFF:
        delta, count = struct.unpack_from(">HH", part, p)
        cursor += delta
        for entry, colour in (v for v in ENTRIES.values()):
            index = PALETTE_ZERO + entry
            if cursor <= index < cursor + count:
                struct.pack_into(">H", part, p + 4 + 2 * (index - cursor), colour)
                done = True
        cursor += count
        p += 4 + 2 * count
    if not done:
        raise ValueError("palette 0 is not in the record")
    frame.parts[PALETTE_BIT] = bytes(part)


# --- art and glyphs ------------------------------------------------------------


def read_png(path: Path) -> tuple[int, int, list[list[int]]]:
    """(width, height, rows of palette entries) of an arcade-coloured PNG."""
    probe = subprocess.run(
        [
            *("ffprobe", "-v", "error", "-show_entries", "stream=width,height"),
            *("-of", "csv=p=0", str(path)),
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    width, height = (int(v) for v in probe.split(","))
    raw = subprocess.run(
        [
            *("ffmpeg", "-loglevel", "error", "-i", str(path)),
            *("-f", "rawvideo", "-pix_fmt", "rgb24", "-"),
        ],
        capture_output=True,
        check=True,
    ).stdout
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            key = raw[(y * width + x) * 3 : (y * width + x) * 3 + 3].hex()
            if key not in ENTRIES:
                raise ValueError(f"{path.name}: colour {key} at ({x}, {y})")
            row.append(ENTRIES[key][0])
        rows.append(row)
    return width, height, rows


Cell = tuple[int, ...]  # 256 palette entries, row by row
BLANK: Cell = (BACKGROUND,) * 256


def lines(rows: list[list[int]]) -> list[tuple[int, int]]:
    inked = [any(v != BACKGROUND for v in row) for row in rows]
    spans, y = [], 0
    while y < len(rows):
        if inked[y]:
            start = y
            while y < len(rows) and inked[y]:
                y += 1
            spans.append((start, y))
        else:
            y += 1
    return spans


def place(
    rows: list[list[int]], x0: int, y0: int, shifts: Sequence[tuple[int, int]]
) -> dict[tuple[int, int], Cell]:
    """Plane cells (column, row) of the art at plane (x0, y0), each line moved by
    its shift; blank cells are left out."""
    width = len(rows[0])
    pixels: dict[tuple[int, int], int] = {}
    for (top, bottom), (dx, dy) in zip(lines(rows), shifts, strict=True):
        for y in range(top, bottom):
            for x in range(width):
                if rows[y][x] != BACKGROUND:
                    pixels[(x0 + x + dx, y0 + y + dy)] = rows[y][x]
    cells: dict[tuple[int, int], list[int]] = {}
    for (x, y), value in pixels.items():
        cell = cells.setdefault((x // 16, y // 16), [BACKGROUND] * 256)
        cell[(y % 16) * 16 + x % 16] = value
    return {k: tuple(v) for k, v in cells.items()}


def best_shifts(rows: list[list[int]], x0: int, y0: int) -> list[tuple[int, int]]:
    """Per-line shifts (-8..7 pixels) that need the fewest distinct cells
    (coordinate descent from no shift; each line's pixels placed once per
    shift, then combined)."""
    spans = lines(rows)
    options = [(dx, dy) for dx in range(-8, 8) for dy in range(-8, 8)]
    shifts = [(0, 0)] * len(spans)
    alone: list[dict[tuple[int, int], dict[tuple[int, int], int]]] = []
    for top, bottom in spans:
        only = [
            row if top <= y < bottom else [BACKGROUND] * len(row)
            for y, row in enumerate(rows)
        ]
        per: dict[tuple[int, int], dict[tuple[int, int], int]] = {}
        for dx, dy in options:
            pixels: dict[tuple[int, int], int] = {}
            for y in range(top, bottom):
                for x, value in enumerate(only[y]):
                    if value != BACKGROUND:
                        pixels[(x0 + x + dx, y0 + y + dy)] = value
            per[(dx, dy)] = pixels
        alone.append(per)

    def count(trial: list[tuple[int, int]]) -> int:
        cells: dict[tuple[int, int], list[int]] = {}
        for i, shift in enumerate(trial):
            for (x, y), value in alone[i][shift].items():
                cell = cells.setdefault((x // 16, y // 16), [BACKGROUND] * 256)
                cell[(y % 16) * 16 + x % 16] = value
        return len({tuple(c) for c in cells.values()})

    best = count(shifts)
    improved = True
    while improved:
        improved = False
        for i in range(len(spans)):
            for option in options:
                trial = shifts[:]
                trial[i] = option
                value = count(trial)
                if value < best:
                    best, shifts, improved = value, trial, True
    return shifts


def char_bytes(cell: Cell) -> bytes:
    """A 2 x 2-cell character: four 8 x 8 4 bpp cells, left pixel high."""
    out = bytearray()
    for sy, sx in ((0, 0), (0, 8), (8, 0), (8, 8)):
        for y in range(8):
            for x in range(0, 8, 2):
                left = cell[(sy + y) * 16 + sx + x]
                right = cell[(sy + y) * 16 + sx + x + 1]
                out.append(left << 4 | right)
    return bytes(out)


def word_index(column: int, row: int) -> int:
    """Index-array position of plane cell (column 0-63, row 0-31)."""
    quarter = (column // 32) + 2 * (row // 16)
    return quarter * 512 + (column % 32) * 16 + row % 16


# --- blocks --------------------------------------------------------------------


@dataclass
class Block:
    data: bytearray

    def part1(self) -> tuple[int, int]:
        first, second = struct.unpack_from(">II", self.data, 4)
        return int(first), int(second)

    def chars(self) -> int:
        first, second = self.part1()
        return (second - first) // 128

    def offset(self, index: int, base: int, section_c: bool) -> int:
        first, _ = self.part1()
        if index < self.chars():
            return first + 128 * index
        if section_c:  # parts 0-2 sit from VRAM 0 (EXP-0065)
            offset = 0x20 + (base // 4 + index) * 128
            if offset + 128 > struct.unpack_from(">I", self.data, 12)[0]:
                raise ValueError(f"index {index} lies past section C's part 2")
            return offset
        raise ValueError(f"index {index} lies past the block's part 1")

    def glyph(self, index: int, base: int, section_c: bool = False) -> bytes:
        at = self.offset(index, base, section_c)
        return bytes(self.data[at : at + 128])

    def put(self, index: int, base: int, cell: Cell, section_c: bool = False) -> None:
        at = self.offset(index, base, section_c)
        self.data[at : at + 128] = char_bytes(cell)

    def blank(self, prefer: Sequence[int] = ()) -> int:
        solid = bytes([BACKGROUND << 4 | BACKGROUND]) * 128
        for index in [*prefer, *range(self.chars())]:
            if 0 <= index < self.chars() and self.glyph(index, 0) == solid:
                return int(index)
        raise ValueError("the block has no blank character")


def assign(
    cells: dict[tuple[int, int], Cell], free: Sequence[int], blank: int
) -> tuple[dict[Cell, int], list[tuple[int, Cell]]]:
    """Index per distinct cell, from ``free``; (index, cell) pairs to write."""
    distinct = list(dict.fromkeys(cells.values()))
    usable = [i for i in free if i != blank]
    if len(distinct) > len(usable):
        raise ValueError(f"{len(distinct)} characters, room for {len(usable)}")
    index = dict(zip(distinct, usable, strict=False))
    return index, [(i, c) for c, i in index.items()]


# --- the build -----------------------------------------------------------------


@dataclass
class Plan:
    """What the build intends to show, for the check."""

    stills: dict[str, tuple[Still, dict[tuple[int, int], Cell]]] = field(
        default_factory=dict
    )
    banner: dict[tuple[int, int], Cell] = field(default_factory=dict)


def banner_x(frame: int) -> int:
    first, last = BANNER_MOVES
    return BANNER_X0 + BANNER_STEP * max(0, min(frame, last) - first + 1)


def build(
    name: str, data: bytes, art: Path, room: dict[str, Any]
) -> tuple[bytes, Plan]:
    """The rebuilt ``OPENING*.ST2`` and what it should show."""
    found = sections(data)
    (a_offset, a_size), _, (c_offset, c_size) = found[:3]
    script, _ = script_decode(data, a_offset)
    frames = parse_frames(script)
    section_c = Block(bytearray(lz_decode(data, c_offset)[0]))
    payload = miss_payload(data)
    stream = [(offset, Block(bytearray(out))) for offset, out in blocks(payload)]
    changed: set[int] = set()  # stream blocks rewritten
    plan = Plan()

    for key, still in STILLS.items():
        info = room[key]
        _, _, rows = read_png(art / still.art)
        x0, y0 = still.scroll[0], still.scroll[1] + ART_TOP
        cells = place(rows, x0, y0, best_shifts(rows, x0, y0))
        old = map_words(frames[still.build])
        if key == "caption1":
            block, base, section = section_c, info["base"], True
            own = sorted({w for w in old[:ARRAY] if w != 0xFFFF})
            blank = 1
            free = [i for i in own if i != blank] + list(info["extra"])
        else:
            number = info["block"]
            block, section = stream[number][1], False
            first, _ = block.part1()
            base = info.get("base", 0)
            own = sorted({w for w in old[:ARRAY] if w != 0xFFFF})
            blank = block.blank(own if key == "caption2" else ())
            free = [i for i in own if i != blank]
            changed.add(number)
        index, writes = assign(cells, free, blank)
        for i, cell in writes:
            block.put(i, base, cell, section)
        words = [0xFFFF] * 0x2000
        visible_cols = range(x0 // 16, (x0 + SCREEN_W - 1) // 16 + 1)
        visible_rows = range(
            still.scroll[1] // 16, (still.scroll[1] + SCREEN_H - 1) // 16 + 1
        )
        for column in visible_cols:
            for row in visible_rows:
                k = word_index(column % 64, row % 32)
                placed = cells.get((column, row))
                words[k] = blank if placed is None or placed == BLANK else index[placed]
                words[ARRAY + k] = 0
        set_map(frames[still.build], words)
        recolour(frames[still.palette])
        plan.stills[key] = (still, cells)

    banner_cells = schedule_banner(frames, stream, room["caption4"], art, changed, plan)
    plan.banner = banner_cells
    recolour(frames[BANNER_PALETTE])
    first, last = BANNER_MOVES
    for n in range(first, last + 1):
        part = frames[n].parts.get(SCROLL_BIT)
        if part != bytes([0x04, BANNER_OLD_STEP]):
            raise ValueError(f"frame {n}: unexpected scroll section {part!r}")
        frames[n].parts[SCROLL_BIT] = bytes([0x04, BANNER_STEP])

    new_script = join_frames(frames)
    encoded_a = script_encode(new_script)
    if len(encoded_a) > a_size:
        raise ValueError(f"{name}: section A needs {len(encoded_a):#x} of {a_size:#x}")
    out = bytearray(data)
    out[a_offset : a_offset + a_size] = encoded_a + bytes(a_size - len(encoded_a))
    fit_block(out, c_offset, bytes(section_c.data), f"{name} section C", c_size)
    sectors = miss_sectors(data)
    for number in sorted(changed):
        offset, block = stream[number]
        old_compressed = struct.unpack_from(">I", payload, offset)[0]
        new = lz_encode(bytes(block.data))
        if len(new) - 8 > old_compressed:
            raise ValueError(
                f"{name} block {number}: {len(new) - 8:#x} > {old_compressed:#x}"
            )
        image = struct.pack(">II", old_compressed, len(block.data)) + new[8:]
        image += bytes(old_compressed + 8 - len(image))
        for k, byte in enumerate(image):
            at = offset + k
            sector = sectors[at // (SECTOR - len(TAG))]
            out[sector + len(TAG) + at % (SECTOR - len(TAG))] = byte
    return bytes(out), plan


def fit_block(
    out: bytearray, offset: int, decoded: bytes, what: str, room: int
) -> None:
    old_compressed = struct.unpack_from(">I", out, offset)[0]
    new = lz_encode(decoded)
    if len(new) - 8 > old_compressed or old_compressed + 8 > room:
        raise ValueError(f"{what}: {len(new) - 8:#x} > {old_compressed:#x}")
    image = struct.pack(">II", old_compressed, len(decoded)) + new[8:]
    out[offset : offset + 8 + old_compressed] = image + bytes(
        old_compressed + 8 - len(image)
    )


def schedule_banner(
    frames: list[Frame],
    stream: list[tuple[int, Block]],
    info: dict[str, Any],
    art: Path,
    changed: set[int],
    plan: Plan,
) -> dict[tuple[int, int], Cell]:
    """Write the banner column by column along its scroll; return its plane
    cells by unwrapped column."""
    _, _, rows = read_png(art / BANNER_ART)
    start_x = banner_x(BANNER_MOVES[0]) + SCREEN_W
    y0 = 16 + BANNER_TOP
    cells = place(rows, start_x, y0, best_shifts(rows, start_x, y0))
    columns = sorted({c for c, _ in cells})
    band = sorted({r for _, r in cells})
    if not set(band) <= set(BANNER_ROWS):
        raise ValueError(f"banner rows {band} outside {list(BANNER_ROWS)}")
    reindex = info["reindex"]
    parts = info["blocks"]
    blocks_used = [stream[p["block"]][1] for p in parts]
    blanks = [b.blank() for b in blocks_used]

    def write_frame(column: int) -> int:
        """The last frame before the column shows (just in time), and not
        before the column 1,024 pixels behind it has left the screen."""
        leave = 16 * (column - 64) + 16
        enter = 16 * column - SCREEN_W  # NBG1 x at which the column shows
        n = BANNER_FIRST
        while banner_x(n + 1) <= enter and n + 1 < BANNER_CLEAR:
            n += 1
        if banner_x(n) < leave or banner_x(n) > enter:
            raise ValueError(f"banner column {column} cannot be written in time")
        if reindex is not None and n == reindex - 1:
            n -= 1  # keep the frame before the re-index free of rebuilds
        return n

    last_col = (banner_x(BANNER_CLEAR) + SCREEN_W) // 16 + 1
    todo = {c: write_frame(c) for c in range(columns[0], last_col + 1)}
    for c in range(columns[0], last_col + 1):
        todo[c] = max(todo[c], BANNER_FIRST)

    def phase(n: int) -> int:
        return 1 if reindex is not None and n >= reindex else 0

    # glyphs per block: cells in columns written (or live at the re-index) in it
    need: list[dict[Cell, None]] = [{}, {}]
    for c in range(columns[0], last_col + 1):
        for r in band:
            cell = cells.get((c, r))
            if cell is None:
                continue
            need[phase(todo[c])][cell] = None
            live_at_reindex = (
                reindex is not None
                and todo[c] < reindex
                and (16 * c + 16 > banner_x(reindex))
            )
            if live_at_reindex:
                need[1][cell] = None
    index: list[dict[Cell, int]] = []
    for k, part in enumerate(parts):
        wanted = (
            list(need[k]) if len(parts) > 1 else list(dict.fromkeys(cells.values()))
        )
        free = [i for i in part["indices"] if i != blanks[k]]
        if len(wanted) > len(free):
            raise ValueError(
                f"banner block {part['block']}: {len(wanted)} glyphs, room {len(free)}"
            )
        index.append(dict(zip(wanted, free, strict=False)))
        for cell, i in index[k].items():
            blocks_used[k].put(i, part["base"], cell)
        changed.add(part["block"])

    # the window's updates lose the banner rows; ours replace them
    updates: dict[int, list[int]] = {}
    for n in range(BANNER_FIRST, BANNER_CLEAR):
        words = map_words(frames[n])
        for column in range(64):
            for row in BANNER_ROWS:
                k = word_index(column, row)
                words[k] = words[ARRAY + k] = 0xFFFF
        updates[n] = words

    def put(n: int, column: int, k_block: int) -> None:
        for row in BANNER_ROWS:
            k = word_index(column % 64, row)
            cell = cells.get((column, row)) if row in band else None
            if cell is None or cell == BLANK:
                updates[n][k] = blanks[k_block]
            else:
                updates[n][k] = index[k_block][cell]
            updates[n][ARRAY + k] = 0

    for column in range(64):  # blank fill of the banner rows
        for row in BANNER_ROWS:
            k = word_index(column, row)
            updates[BANNER_FIRST][k] = blanks[0]
            updates[BANNER_FIRST][ARRAY + k] = 0
    for c, n in todo.items():
        put(n, c, phase(n))
    if reindex is not None:
        # every plane column of the banner rows, under the second block: the
        # banner column it holds if that is still on screen or to come, else
        # the blank
        for plane in range(64):
            held = [c for c, n in todo.items() if n <= reindex and c % 64 == plane]
            if held and 16 * held[-1] + 16 > banner_x(reindex):
                put(reindex, held[-1], 1)
            else:
                for row in BANNER_ROWS:
                    k = word_index(plane, row)
                    updates[reindex][k] = blanks[1]
                    updates[reindex][ARRAY + k] = 0
    for n, words in updates.items():
        set_map(frames[n], words)
    return cells


# --- the check -----------------------------------------------------------------


def check(name: str, data: bytes, room: dict[str, Any], plan: Plan) -> None:
    """Render every caption frame from the rebuilt file and compare with the plan."""
    found = sections(data)
    script, _ = script_decode(data, found[0][0])
    frames = parse_frames(script)
    section_c = Block(bytearray(lz_decode(data, found[2][0])[0]))
    stream = [Block(bytearray(out)) for _, out in blocks(miss_payload(data))]
    arrays = [0] * 0x2000
    states: dict[int, list[int]] = {}
    for n, frame in enumerate(frames):
        for k, w in enumerate(map_words(frame)):
            if w != 0xFFFF:
                arrays[k] = w
        states[n] = arrays[:]

    def shown(
        state: list[int], block: Block, base: int, column: int, row: int, section: bool
    ) -> Cell:
        k = word_index(column % 64, row % 32)
        if state[ARRAY + k] != 0:
            raise ValueError(
                f"{name}: attribute {state[ARRAY + k]:#x} at {column},{row}"
            )
        raw = block.glyph(state[k], base, section)
        pixels: list[int] = [0] * 256
        for sub, (sy, sx) in enumerate(((0, 0), (0, 8), (8, 0), (8, 8))):
            for y in range(8):
                for x in range(0, 8, 2):
                    byte = raw[sub * 32 + y * 4 + x // 2]
                    pixels[(sy + y) * 16 + sx + x] = byte >> 4
                    pixels[(sy + y) * 16 + sx + x + 1] = byte & 15
        return tuple(pixels)

    for key, (still, cells) in plan.stills.items():
        info = room[key]
        block = section_c if key == "caption1" else stream[info["block"]]
        base = info.get("base", 0)
        state = states[still.build]
        x0, y0 = still.scroll
        for column in range(x0 // 16, (x0 + SCREEN_W - 1) // 16 + 1):
            for row in range(y0 // 16, (y0 + SCREEN_H - 1) // 16 + 1):
                want = cells.get((column, row), BLANK)
                if shown(state, block, base, column, row, key == "caption1") != want:
                    raise ValueError(f"{name} {key}: cell {column},{row} differs")
    info = room["caption4"]
    parts = info["blocks"]
    for n in range(BANNER_MOVES[0], BANNER_CLEAR):
        k_block = 1 if info["reindex"] is not None and n >= info["reindex"] else 0
        block, base = stream[parts[k_block]["block"]], parts[k_block]["base"]
        x = banner_x(n)
        for column in range(x // 16, (x + SCREEN_W - 1) // 16 + 1):
            for row in BANNER_ROWS:
                want = plan.banner.get((column, row), BLANK)
                if shown(states[n], block, base, column, row, False) != want:
                    raise ValueError(
                        f"{name} banner frame {n}: cell {column},{row} differs"
                    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("st2_dir", type=Path, help="the untouched OPENING*.ST2")
    parser.add_argument(
        "art", type=Path, help="c1-c3.png and banner.png (ignored path)"
    )
    parser.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    parser.add_argument("--room", type=Path, default=ROOM)
    args = parser.parse_args(argv)
    room = json.loads(args.room.read_text())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for k in range(8):
        name = f"OPENING{k}.ST2"
        data = (args.st2_dir / name).read_bytes()
        rebuilt, plan = build(name, data, args.art, room[f"OPENING{k}"])
        if len(rebuilt) != len(data):
            raise ValueError(f"{name}: size changed")
        check(name, rebuilt, room[f"OPENING{k}"], plan)
        (args.out_dir / name).write_bytes(rebuilt)
        print(f"{name}: built and checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

r"""EXP-0065: VDP2 character slots written, and slots visible, over time.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/vram_visible.py \
        CUE STATE OUT STEP COUNT [SKIP [ADDRESS:OLD:NEW]]

As `vram_timeline.py`, but a slot counts as used only if a cell inside the
352 x 224 screen references it. Each step reads, besides VDP2 VRAM, the RAM
the game copies into the scroll and map registers every frame (`0x06020EC6`):

- ``0x06020C5C``: NBG0 x, NBG0 y, NBG1 x, NBG1 y (words), then NBG2 x and y
  (one long);
- ``0x06020C5A``: NBG3 x (its y stays ``0x200`` from the setup list);
- ``0x06020C28``: NBG2's map registers (MPABN2, MPCDN2).

Layer settings (all saved states from the first caption on): NBG0 and NBG3
1 x 1 cells, one page each (``0x64000``, ``0x68000``), wrapping every 512
pixels; NBG1 2 x 2-cell characters, one plane of 2 x 2 pages at ``0x6C000``,
wrapping every 1,024 pixels; NBG2 2 x 2, four planes from MPABN2/MPCDN2
(offset 1), wrapping every 2,048 pixels. NBG1 has a line-scroll table (RAM
``0x060234D4``, copied to VRAM ``0x63C00`` every frame): when it is all
zero, NBG1 counts its scroll window like the others; otherwise every cell
of a visible row counts (conservative). SKIP frames are run
before the first step, after the optional RAM patch (hex, work RAM, checked
against OLD), for example the attract file digit at ``0x06020290``. Each step
also records NBG1's character base (``0x06020BBC``). Writes
``OUT/timeline.json``. OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home

SLOT, VRAM = 128, 0x80000
SCREEN_W, SCREEN_H = 352, 224
LINE_SCROLL, LINE_BYTES = 0x060234D4, 0x380  # copied to VRAM 0x63C00 every frame


def entry(vram: bytes, page: int, col: int, row: int, cells: int) -> int:
    return struct.unpack_from(">I", vram, page + 4 * (row * cells + col))[0]


def add(slots: set[int], char: int, size: int) -> None:
    start = (char * 32) % VRAM
    slots.update(range(start // SLOT, (start + size - 1) // SLOT + 1))


def small_layer(vram: bytes, page: int, sx: int, sy: int) -> set[int]:
    """One 64 x 64-cell page of 8 x 8 cells, wrapping."""
    slots: set[int] = set()
    for y in range(sy, sy + SCREEN_H, 8):
        for x in range(sx, sx + SCREEN_W + 8, 8):
            e = entry(vram, page, (x // 8) % 64, (y // 8) % 64, 64)
            add(slots, e & 0x7FFF, 32)
    return slots


def big_layer(
    vram: bytes, planes: list[int], sy: int, sx: int | None, wrap: int
) -> set[int]:
    """2 x 2-cell characters; ``planes`` are the first pages of 2 x 2-page
    planes, laid out 1 x 1 or 2 x 2. ``sx`` None means every column."""
    slots: set[int] = set()
    per_side = 2 if len(planes) == 4 else 1
    xs = range(0, wrap, 16) if sx is None else range(sx, sx + SCREEN_W + 16, 16)
    for y in range(sy, sy + SCREEN_H + 16, 16):
        for x in xs:
            px, py = x % wrap, y % wrap
            plane = (
                planes[(py // 1024) * per_side + (px // 1024)]
                if per_side == 2
                else planes[0]
            )
            qx, qy = px % 1024, py % 1024
            page = plane + 0x1000 * ((qy // 512) * 2 + (qx // 512))
            e = entry(vram, page, (qx % 512) // 16, (qy % 512) // 16, 32)
            add(slots, e & 0x7FFF, 128)
    return slots


def main(
    cue: Path,
    state: Path,
    out: Path,
    step: int,
    count: int,
    skip: int = 0,
    patch: str = "",
) -> int:
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = out / "agent"
    agent_dir.mkdir()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(quiet_home().resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
        MEDNAFEN_ALLOWMULTI="1",
    )
    records: list[dict[str, object]] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            if patch:
                address, old, new = patch.split(":")
                where = int(address, 16)
                found = agent.bus_read(where, len(bytes.fromhex(old)))
                if found != bytes.fromhex(old):
                    raise SystemExit(f"{address}: RAM holds {found.hex()}, not {old}")
                agent.bus_write(where, bytes.fromhex(new))
            if skip:
                agent.frames(skip)
                agent.wait_halted(max(60.0, skip / 30))
            previous: list[int] = []
            for _ in range(count):
                agent.frames(step)
                agent.wait_halted(60.0)
                vram = agent.read("vdp2vram", 0, VRAM)
                ram = agent.bus_read(0x06020C28, 0x48)
                lines = agent.bus_read(LINE_SCROLL, LINE_BYTES)
                flat = not any(lines)
                x0, y0, x1, y1 = struct.unpack_from(">4H", ram, 0x34)
                x2, y2 = struct.unpack_from(">2H", ram, 0x3C)
                (x3,) = struct.unpack_from(">H", ram, 0x32)
                ab, cd = struct.unpack_from(">2H", ram, 0)
                # page number = MPOFN offset (1) << 6 | the 6-bit map register
                planes2 = [
                    ((m & 0x3F) | 0x40) * 0x1000 for m in (ab, ab >> 8, cd, cd >> 8)
                ]
                used = {
                    "NBG0": small_layer(vram, 0x64000, x0 & 0x7FF, y0 & 0x7FF),
                    "NBG3": small_layer(vram, 0x68000, x3 & 0x7FF, 0x200),
                    "NBG1": big_layer(
                        vram, [0x6C000], y1 & 0x7FF, x1 & 0x7FF if flat else None, 1024
                    ),
                    "NBG2": big_layer(vram, planes2, y2 & 0x7FF, x2 & 0x7FF, 2048),
                }
                hashes = [zlib.crc32(vram[i : i + SLOT]) for i in range(0, VRAM, SLOT)]
                changed = [
                    i for i, h in enumerate(hashes) if previous and h != previous[i]
                ]
                previous = hashes
                records.append(
                    {
                        "frame": int(agent.status()["frame"]),
                        "scroll": [x0, y0, x1, y1, x2, y2, x3],
                        "line_scroll_flat": flat,
                        "base": struct.unpack(">I", agent.bus_read(0x06020BBC, 4))[0],
                        "nbg2_maps": [f"{ab:04x}", f"{cd:04x}"],
                        "changed": changed,
                        "used": {k: sorted(v) for k, v in used.items()},
                    }
                )
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "timeline.json").write_text(json.dumps(records) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            int(a[3]),
            int(a[4]),
            int(a[5]) if len(a) > 5 else 0,
            a[6] if len(a) > 6 else "",
        )
    )

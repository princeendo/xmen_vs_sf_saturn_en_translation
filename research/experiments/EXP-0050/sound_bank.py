r"""EXP-0050: the XvSF sound bank in sound RAM; decoder check; WAV export.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/sound_bank.py check DUMP_DIR
    ./invenv.sh python research/experiments/EXP-0050/sound_bank.py export \
        DUMP_DIR OUT_DIR [INDEX ...]

DUMP_DIR is a ``sound_dump.py`` dump (``scspram.bin``, ``wram_h.bin``).

**Bank** (observed in sound RAM at ``BANK`` = ``0x5C00``, loaded from
``INITDATA.PCA`` part 5): a u32 clip count, then one 8-byte entry per clip
(u16 ID, u16 length, u32 offset), then the clip data. Each offset counts
from the end of the table and is the sum of the lengths before it.

**Decoder:** ``decode_state`` is copied from the MSHvSF repository,
`tools/audio/sound_bank.py` at commit ``6161166``
(``decode_state``/``nibbles``, the routine at MSHvSF ``0x0600D420``). In
XvSF the same 16.16 multiplier table is at ``0x060168F4``. That the
algorithm is the same for XvSF's clips is what ``check`` tests:

- **The check:** the mixer's 16 channel records (``CHANNELS`` =
  ``0x0601776C``, 28 bytes each) hold the current pointer, the start, the
  end, the step and the predictor. For every active channel, the clip is
  decoded from its start up to the current pointer, and the step and
  predictor must equal the stored ones.

**Export:** writes ``OUT_DIR/c<index>_id<id>.wav`` (16-bit mono,
``RATE`` Hz, normalized). ``RATE`` is a HYPOTHESIS until a clip is
heard at the right pitch. The WAVs are game-derived: write them under
``local/`` only (rule 21).
"""

from __future__ import annotations

import json
import struct
import sys
import wave
from collections.abc import Iterator
from pathlib import Path

BANK = 0x5C00
CHANNELS = 0x0601776C - 0x06000000  # offset in the WRAM-H dump
RECORD = 28
STEP_INIT, STEP_MIN, STEP_MAX = 0x80, 0x80, 0x6000
MULTIPLIERS = (0xE666, 0xE666, 0xE666, 0xE666, 0x13333, 0x1999A, 0x20000, 0x26666)
RATE = 12016
SOUND_RAM = 0x25A00000


def nibbles(data: bytes) -> Iterator[int]:
    for byte in data:
        yield byte >> 4
        yield byte & 0x0F


def decode_state(
    data: bytes, predictor: int = 0, step: int = STEP_INIT
) -> tuple[list[int], int, int]:
    samples: list[int] = []
    for nibble in nibbles(data):
        magnitude = nibble & 7
        difference = (step * magnitude) >> 2
        predictor += -difference if nibble & 8 else difference
        step = min(STEP_MAX, max(STEP_MIN, (step * MULTIPLIERS[magnitude]) >> 16))
        samples.append(predictor)
    return samples, predictor, step


def clips(ram: bytes) -> list[tuple[int, int, int, int]]:
    """(index, ID, length, sound-RAM offset) of each clip."""
    count = struct.unpack_from(">I", ram, BANK)[0]
    data = BANK + 4 + 8 * count
    out = []
    for index in range(count):
        clip_id, length, offset = struct.unpack_from(">HHI", ram, BANK + 4 + 8 * index)
        out.append((index, clip_id, length, data + offset))
    return out


def check(dump: Path) -> list[dict[str, object]]:
    ram = (dump / "scspram.bin").read_bytes()
    wram = (dump / "wram_h.bin").read_bytes()
    rows = []
    for channel in range(16):
        cur, start, _end, step, pred = struct.unpack_from(
            ">IIIIi", wram, CHANNELS + RECORD * channel
        )
        if not start or not SOUND_RAM <= start < SOUND_RAM + 0x80000:
            continue  # idle, or a clip played from the cart (not in this dump)
        a, b = start - SOUND_RAM, cur - SOUND_RAM
        _, p, s = decode_state(ram[a:b])
        rows.append(
            {
                "channel": channel,
                "start": f"{start:#x}",
                "current": f"{cur:#x}",
                "stored": [f"{step:#x}", pred],
                "decoded": [f"{s:#x}", p],
                "match": (s, p) == (step, pred),
            }
        )
    return rows


def export(dump: Path, out: Path, wanted: list[int]) -> None:
    ram = (dump / "scspram.bin").read_bytes()
    out.mkdir(parents=True, exist_ok=True)
    for index, clip_id, length, offset in clips(ram):
        if wanted and index not in wanted:
            continue
        samples = decode_state(ram[offset : offset + length])[0]
        loudest = max((abs(s) for s in samples), default=0) or 1
        gain = 0.9 * 32767 / loudest
        pcm = b"".join(
            struct.pack("<h", max(-32768, min(32767, round(s * gain)))) for s in samples
        )
        with wave.open(str(out / f"c{index:03d}_id{clip_id:03x}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm)


def main(argv: list[str]) -> int:
    if argv[0] == "check":
        rows = check(Path(argv[1]))
        print(json.dumps(rows, indent=1))
        return 0 if rows and all(r["match"] for r in rows) else 1
    if argv[0] == "export":
        export(Path(argv[1]), Path(argv[2]), [int(a) for a in argv[3:]])
        return 0
    raise SystemExit("usage: check DUMP | export DUMP OUT [INDEX ...]")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

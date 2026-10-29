"""Compile English caption lines into Saturn quote-record codes, and back.

A record is a fixed number of lines (2) of a fixed number of cells: 25 in the
English mode (100-byte records, `EXP-0023`) or 19 in the Japanese mode
(76 bytes). Each cell is one big-endian 16-bit code. Characters use the
arcade's English map, which the Saturn quote font draws unchanged (`EXP-0020`):
``tools.reference.xvsf_text.DECODE``, space ``0x0020``. Lines are left-aligned
and padded with spaces, as the arcade records are (every arcade English
win-quote record of Ryu decodes and re-encodes to its exact bytes, `RE-003`).

The compiler rejects, rather than shortens or wraps, any line that does not fit
and any character outside the map (``CaptionError``).
"""

from __future__ import annotations

from collections.abc import Sequence

from tools.reference.xvsf_text import DECODE, SPACE

ENCODE = {char: code for code, char in DECODE.items()}
ENGLISH_CELLS = 25
LINES = 2


class CaptionError(ValueError):
    """Raised when text cannot be represented in a record."""


def encode_line(text: str, cells: int = ENGLISH_CELLS) -> list[int]:
    """Return ``cells`` codes for ``text``, left-aligned and space-padded."""
    if len(text) > cells:
        raise CaptionError(f"line is {len(text)} characters; the limit is {cells}")
    codes = []
    for char in text:
        if char not in ENCODE:
            raise CaptionError(f"character {char!r} has no code")
        codes.append(ENCODE[char])
    return codes + [SPACE] * (cells - len(codes))


def compile_record(lines: Sequence[str], cells: int = ENGLISH_CELLS) -> bytes:
    """Return the record bytes for exactly ``LINES`` lines of text."""
    if len(lines) != LINES:
        raise CaptionError(f"a record has {LINES} lines, not {len(lines)}")
    codes = [code for line in lines for code in encode_line(line, cells)]
    return b"".join(code.to_bytes(2, "big") for code in codes)


def decode_record(data: bytes, cells: int = ENGLISH_CELLS) -> list[str]:
    """Return the lines of a record, trailing spaces removed."""
    if len(data) != 2 * LINES * cells:
        raise CaptionError(f"a record is {2 * LINES * cells} bytes, not {len(data)}")
    codes = [int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)]
    lines = []
    for row in range(LINES):
        chars = []
        for code in codes[row * cells : (row + 1) * cells]:
            if code not in DECODE:
                raise CaptionError(f"code {code:#06x} has no character")
            chars.append(DECODE[code])
        lines.append("".join(chars).rstrip())
    return lines

"""The name variants: American art and voice, or Saturn names in the English.

**American** (``us``; `LOC-005`, `EXP-0051`): patches to ``MMPACK.PCA``.

The Saturn code keeps the US arcade's name choice. Each name surface reads the
word at R11 + ``0xD478`` (``0x060F5478``; the arcade's ``0xFF5478``, called
the size word in D-018). When it is non-zero, the surface takes the American
entry of a list that sits right after the Japanese one, 19 words (38 bytes)
later. The Saturn keeps the word at 0. Setting it in RAM turned every art
surface American, but it also switches the quote and ending layout (D-018),
so it cannot be set globally.

The American variant instead changes each name surface's read of that word,
``mov.w @(r0,r11),r0`` (``00BD``), to ``mov #2,r0`` (``E002``): the US
region's value, for that read only. The 10 sites are every reader of the word
in ``MMPACK.PCA`` that chooses a per-character list (a static scan found 45
readers; the others are region jump tables and constants). Each surface was
shown American, with only these patches, in `EXP-0051`.

The voice sites pick a sound request ``0xA0`` + slot, or ``0xB2``-``0xB4``
for slots 14-16 in the American list. Those requests play table A entries
18-20, the "Bison", "Akuma" and "Charlie" calls (`EXP-0050`).

**Saturn names** (``saturn``; `LOC-006`, `EXP-0052`): no code change, so the
art and voice keep the Saturn's names. The official English gets the name
edits in ``SATURN`` (`GATE-TRANSLATION`, Saturn-names extension):

- **Text:** in a compiled record's line, the one occurrence of a name is
  replaced (``edit_lines``); the line must still fit 25 cells.
- **Labels:** in a slot's English ending script in ``MCED.SHP``, a label
  byte is replaced on every page that has it (``label_edits``). A script is
  scenes of (page length, record x 256 + label) words, each scene ended by
  ``FFFF`` and a word repeating its last page's (`EXP-0038`, `EXP-0043`);
  that word is edited too.
- **Label entries:** a 16-cell, 16-bit ASCII entry of the label list is
  rewritten (``entry_edits``), at an index that no script uses.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.disc.english_mode import MCED_RELOCATION, MCED_SCRIPTS, SLOTS

REGION_READ = "00BD"  # mov.w @(r0,r11),r0, with r0 = 0xD478
US_REGION = "E002"  # mov #2,r0

US_SITES: dict[int, str] = {
    0x060639E6: "select label",
    0x06073A28: "VS-screen name",
    0x0607FDA8: "life bar",
    0x0607FE0E: "life bar",
    0x0607FE94: "life bar",
    0x0607FEFA: "life bar",
    0x0607FFA2: "life bar (AKUMA's position)",
    0x0606E004: "win-banner name",
    0x0604FBDA: "name call",
    0x0604FC52: "name call",
}

VARIANTS = ("us", "none", "saturn")

SATURN = Path("data/translations/saturn_names.json")
LABELS, LABEL_CELLS = 0x3DA8, 16  # MCED's label list (decoded), 40 entries
ENGLISH_HEADER = 1  # header words: languages 0, 2, 4, 6
END_OF_SCENE = 0xFFFF


def patches(names: str) -> list[tuple[int, str, str]]:
    """The ``MMPACK.PCA`` patches for a name variant.

    ``none`` is the Saturn's own art and voice with no name change, as built
    before `LOC-005`; ``saturn`` changes no code either.
    """
    if names == "us":
        return [(address, REGION_READ, US_REGION) for address in sorted(US_SITES)]
    if names in ("none", "saturn"):
        return []
    raise ValueError(f"unknown name variant {names}")


def load_saturn(path: Path = SATURN) -> dict[str, list[dict[str, object]]]:
    data: dict[str, list[dict[str, object]]] = json.loads(path.read_text())
    return data


def text_edits(
    saturn: dict[str, list[dict[str, object]]], spec: str
) -> dict[int, list[tuple[int, str, str]]]:
    """The (line, old, new) edits for each English record of the spec at ``spec``."""
    edits: dict[int, list[tuple[int, str, str]]] = {}
    for edit in saturn["text"]:
        if Path(str(edit["spec"])) == Path(spec):
            record = int(str(edit["english_record"]))
            line = (int(str(edit["line"])), str(edit["old"]), str(edit["new"]))
            edits.setdefault(record, []).append(line)
    return edits


def edit_lines(lines: list[str], edits: list[tuple[int, str, str]]) -> list[str]:
    out = list(lines)
    for line, old, new in edits:
        if out[line].count(old) != 1:
            raise ValueError(f"line {line} holds {old!r} {out[line].count(old)} times")
        out[line] = out[line].replace(old, new)
    return out


def _word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def english_script(decoded: bytes, slot: int) -> int:
    """Decoded offset of ``slot``'s English ending script in ``MCED.SHP``."""
    if not 0 <= slot < SLOTS:
        raise ValueError(f"slot {slot} is outside 0-{SLOTS - 1}")
    entry = MCED_SCRIPTS + 4 * slot
    value = int.from_bytes(decoded[entry : entry + 4], "big")
    base = value + MCED_RELOCATION
    headers = [_word(decoded, base + 2 * i) for i in range(4)]
    if len(set(headers[ENGLISH_HEADER:])) != 1:
        raise ValueError(f"slot {slot}: languages 2, 4 and 6 have different scripts")
    return base + headers[ENGLISH_HEADER]


def label_edits(
    decoded: bytes, saturn: dict[str, list[dict[str, object]]], slots: list[int]
) -> list[tuple[int, bytes, bytes]]:
    """Edits that switch each listed label of ``slots``' English scripts.

    The pages found must be the pages listed; the trailing word of a scene
    whose last page is switched is switched too.
    """
    edits = []
    for edit in saturn["labels"]:
        slot = int(str(edit["slot"]))
        if slot not in slots:
            continue
        old, new = int(str(edit["old"])), int(str(edit["new"]))
        start = english_script(decoded, slot)
        found, page = [], 0
        for scene in range(_word(decoded, start) // 2):
            at = start + _word(decoded, start + 2 * scene)
            while _word(decoded, at) != END_OF_SCENE:
                page += 1
                if decoded[at + 3] == old:
                    found.append(page)
                    edits.append((at + 3, bytes([old]), bytes([new])))
                last = at + 3
                at += 4
            if decoded[at + 3] == old and decoded[at + 2] == decoded[last - 1]:
                edits.append((at + 3, bytes([old]), bytes([new])))
        if found != edit["pages"]:
            raise ValueError(f"slot {slot}: label {old} is on pages {found}")
    return edits


def label_cells(text: str) -> bytes:
    if len(text) > LABEL_CELLS or not text.isascii():
        raise ValueError(f"label {text!r} does not fit {LABEL_CELLS} ASCII cells")
    return b"".join(b"\0" + c.encode() for c in text.ljust(LABEL_CELLS))


def entry_edits(
    decoded: bytes, saturn: dict[str, list[dict[str, object]]]
) -> list[tuple[int, bytes, bytes]]:
    """Edits that rewrite label list entries; each must hold its ``old`` text."""
    edits = []
    for edit in saturn["label_entries"]:
        at = LABELS + 2 * LABEL_CELLS * int(str(edit["index"]))
        old, new = label_cells(str(edit["old"])), label_cells(str(edit["new"]))
        if decoded[at : at + len(old)] != old:
            raise ValueError(f"label entry {edit['index']} is not {edit['old']!r}")
        edits.append((at, old, new))
    return edits

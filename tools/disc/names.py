"""The name-variant patches for ``MMPACK.PCA`` (`LOC-005`, `EXP-0051`).

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
"""

from __future__ import annotations

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


def patches(names: str) -> list[tuple[int, str, str]]:
    """The ``MMPACK.PCA`` patches for a name variant.

    ``none`` is the Saturn's own art and voice with no name change, as built
    before `LOC-005`. ``saturn`` is `LOC-006`'s and not yet built.
    """
    if names == "us":
        return [(address, REGION_READ, US_REGION) for address in sorted(US_SITES)]
    if names == "none":
        return []
    if names == "saturn":
        raise ValueError("the Saturn-names variant is not built yet (LOC-006)")
    raise ValueError(f"unknown name variant {names}")

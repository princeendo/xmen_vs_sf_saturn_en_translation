"""The continue hints in the arcade's English, matched to each Saturn hint (`HINT-002`).

The hint starter (``0x06066728``-``0x0606678C``, in ``MMPACK.PCA``) is the
arcade's (`EXP-0066`, D-058): index = ``rand & 0x0F``; with the global
language word set, it maps the index through the bytes at ``MAP`` and takes the
English base; the renderer then reads two 100-byte pages, records ``map[i]``
and ``map[i] + 1``. The Saturn keeps that path but not the English records.

The user chose (`HINT-002`, `docs/localization_policy.md`) to show each Saturn
hint's own English, as written, rather than the arcade's map (which falls out
of step from index 8). So:

* **Table** (``TABLE`` records, 100 bytes each, in this order): the arcade's
  English area records 270-283, record 284 twice (the super-jump hint has one
  page, shown on both), then 285-292. ``ORDER`` lists them; the record bytes
  come from the arcade program at build time.
* **Map** (``MAP``): Saturn index i -> the table's first page for hint i.
  Indices 12-15 repeat the Saturn's own hints 4, 2, 9 and 3.
* **Starter** (``STARTER``): always maps the index; sets the task's English
  byte (+ ``english_mode.FLAG``, which the English builds' renderer reads) to
  2; stores the base ``TABLE``. It leaves r14 = -1, T = 1 and ``@(6,gbr)`` = 0,
  as the original Japanese path did.
* **Page step** (``PAGE_STEP``): the hint task's state-0 handler (task type
  byte + 39 = 2 only, through the dispatch at ``0x06066486``) shows the
  second page after task + 78 counts down, but only when the global language
  word is set. It now reads the task's English byte instead, as the
  renderer does in the English builds.
* **Storage:** ``TABLE`` is in the gap between ``MMPACK.PCA``'s two segments
  (``0x0601E460``-``0x0601EFFF``), zero in every gameplay dump. The build
  extends the first segment over it (`tools.disc.build_english`).

Each patch is (WRAM-H address, original bytes, new bytes); the originals are
checked before any write.
"""

from __future__ import annotations

from tools.disc.english_mode import FLAG

FIRST_RECORD, ENGLISH_AREA, SIZE = 270, 0x18D81A, 100  # EXP-0008, EXP-0066
ORDER = [*range(270, 284), 284, 284, *range(285, 293)]
TABLE = 0x0601E460  # end of MMPACK.PCA's first segment
GAP_END = 0x0601F000  # its second segment
MAP = 0x060667A8
HINT_PAGES = {  # Saturn hint index -> its English records (EXP-0066)
    0: (270, 271),
    1: (272, 273),
    2: (274, 275),
    3: (276, 277),
    4: (278, 279),
    5: (280, 281),
    6: (282, 283),
    7: (284, 284),
    8: (285, 286),
    9: (287, 288),
    10: (289, 290),
    11: (291, 292),
    12: (278, 279),  # the Saturn's record 12 repeats hint 4
    13: (274, 275),  # 13 repeats 2
    14: (287, 288),  # 14 repeats 9
    15: (276, 277),  # 15 repeats 3
}
MAP_ORIGINAL = "00 02 04 06 08 0A 0C 0E 10 12 14 16 00 02 04 06"

#   06066746 D112  mov.l @(0x06066790),r1   ; MAP
#   06066748 C501  mov.w @(2,gbr),r0       ; index (rand & 0x0F)
#   0606674A 001C  mov.b @(r0,r1),r0       ; first page
#   0606674C E126  mov #38,r1
#   0606674E 316C  add r6,r1               ; r6 = task
#   06066750 2100  mov.b r0,@r1            ; task + 38 = page
#   06066752 E027  mov #39,r0
#   06066754 E102  mov #2,r1
#   06066756 0614  mov.b r1,@(r0,r6)       ; task + 39 = 2, as before
#   06066758 E05C  mov #FLAG,r0
#   0606675A 0614  mov.b r1,@(r0,r6)       ; task + FLAG = 2: English
#   0606675C E04E  mov #78,r0
#   0606675E 9116  mov.w @(0x0606678E),r1  ; 0x0180
#   06066760 0615  mov.w r1,@(r0,r6)       ; task + 78, as before
#   06066762 D00D  mov.l @(0x06066798),r0  ; TABLE
#   06066764 E136  mov #54,r1
#   06066766 316C  add r6,r1
#   06066768 2101  mov.w r0,@r1
#   0606676A 4029  shlr16 r0
#   0606676C 2105  mov.w r0,@-r1           ; task + 52 = TABLE, as before
#   0606676E EEFF  mov #-1,r14
#   06066770 E000  mov #0,r0
#   06066772 C103  mov.w r0,@(6,gbr)
#   06066774 0018  sett
#   06066776 0009  nop (x 11, to the original trapa #63 at 0x0606678C)
STARTER = (
    0x06066746,
    "9073 00BD 2008 3EEA C103 8903 D10F C501 001C C003 C403 E126 316C 2100 E027"
    " E102 0614 E04E 9110 0615 C503 300C C103 D107 C503 021D 70FE 011D 6029 201D"
    " E136 316C 2101 4029 2105",
    f"D112 C501 001C E126 316C 2100 E027 E102 0614 E0{FLAG:02X} 0614 E04E 9116"
    " 0615 D00D E136 316C 2101 4029 2105 EEFF E000 C103 0018" + " 0009" * 11,
)
#   06066504 E05C  mov #FLAG,r0            ; was mov.w @(0x06066536),r0 (0xD47A)
#   06066506 00CC  mov.b @(r0,r12),r0      ; was mov.w @(r0,r11),r0 (global word)
PAGE_STEP = (0x06066504, "9017 00BD", f"E0{FLAG:02X} 00CC")
BASE_LITERAL = (0x06066798, "0608 5544", f"{TABLE >> 16:04X} {TABLE & 0xFFFF:04X}")


def map_bytes() -> bytes:
    first = {pair: ORDER.index(pair[0]) for pair in HINT_PAGES.values()}
    for pair, page in first.items():
        if ORDER[page + 1] != pair[1]:
            raise ValueError(f"records {pair} are not adjacent in ORDER")
    return bytes(first[HINT_PAGES[i]] for i in range(16))


def patches() -> list[tuple[int, str, str]]:
    """The ``MMPACK.PCA`` code and table changes."""
    return [
        STARTER,
        BASE_LITERAL,
        (MAP, MAP_ORIGINAL, map_bytes().hex(" ").upper()),
        PAGE_STEP,
    ]


def table(program: bytes) -> bytes:
    """The English hint records, in ``ORDER``, from the arcade program."""
    data = b"".join(
        program[
            ENGLISH_AREA + SIZE * (r - FIRST_RECORD) : ENGLISH_AREA
            + SIZE * (r - FIRST_RECORD + 1)
        ]
        for r in ORDER
    )
    if TABLE + len(data) > GAP_END:
        raise ValueError("the hint table does not fit the gap")
    return data

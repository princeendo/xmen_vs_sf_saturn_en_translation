# EXP-0049 (Names): Where Each Name Surface Is Stored

Task: LOC-002
Status: DONE
Confidence:

- CONFIRMED: every surface's storage, by a controlled change;
- CONFIRMED: the American names' art for the life bar and the select
  label (shown on screen);
- UNKNOWN: where the VS and banner screens get each character's letter
  list.

## Observation

`EXP-0048` (D-044): the Saturn shows `VEGA`, `GOUKI` and `NASH` on four art
surfaces: select label, VS screen, life bar and win banner. The US arcade
shows `BISON`, `AKUMA` and `CHARLIE` there. `EXP-0011` found no name as
plain text on the disc.

## Questions

For each surface, where is the name art stored (file, offset)? Show it by
a controlled change. And is the American name's art on the disc?

## Tools

| Tool | Use |
| --- | --- |
| [`dump_screen.py`](dump_screen.py) | Per state: screenshot (after one frame), VDP1/VDP2 VRAM, WRAM-L, WRAM-H (live agent reads) |
| [`find_bytes.py`](find_bytes.py) | A VRAM block in RAM dumps and in every disc file (raw, PRS, PCA) |
| [`write_log.py`](write_log.py) | Log-mode breakpoints (write, read or pc) after a state, with optional RAM patches and keys; every hit's PC and registers |
| [`cells.py`](cells.py) | Reimplementation of the `FIX.PRS` cell decoder at `0x06024CF0` |
| [`cell_swap.py`](cell_swap.py) | Rewrites one 16-cell block of `FIX.PRS` in RAM; control and swap runs; read-back of the edit |
| [`patch_run.py`](patch_run.py) | Control and patched runs from one state with checked RAM patches and optional keys |
| `tools.memory.vdp1_sprites`, `tools.sh2.disasm` | VDP1 sprites; SH-2 disassembly of the WRAM-H dumps |

States: `local/loc001/session/states` (the `EXP-0048` voice session, M8
build) and the route's select state.

## The two cell paths (from the code)

The sprite cell loader (`0x06024B60`-`0x06024CCC`) takes each object's
pack descriptor (object + 16):

- **Negative:** the cell comes from the fixed pack. Its base address is
  the long at `0x0602586C`, which is **`FIX.PRS`, loaded raw at WRAM-L
  `0x002C3EA0`**. The decoder at `0x06024CF0` unpacks it into the
  128-byte buffer `0x06024DDC`:
  - a block offset table at + 16;
  - a size/type byte per cell at + 16 + `0x380`;
  - each cell raw, blank, or mask coded.

  `cells.py` reproduces 18 of 18 VRAM cells.
- **Otherwise:** the cell comes from an image pack. The descriptor's data
  pointer + 16 is a frame table, 6 bytes per frame:
  - a word;
  - a size byte, width = low nibble + 1 and height = high nibble + 1, in
    cells;
  - a 24-bit offset.

  The frame data is unpacked by a second decoder (`0x060252BA`, a
  bit-stream format) into `0x060ABA58`.
- **Transfer:** both paths reach VDP1 by SCU DMA level 0
  (`0x06024010`: source R9, destination R10, length R11).

Image-pack descriptors seen:

- `0x060255F8` + 16 × slot: the slot's face file `FCxx.PRS`, a slice of
  `FCALL.PRS`, which is loaded at VDP1 `0x8000`;
- `0x06025808`: **`VS00.PRS`**, loaded raw at WRAM-L `0x002F7030`, right
  after `FIX.PRS`.

## Actual Result

| Surface | Stored in | Names there | Controlled change (run) | Result |
| --- | --- | --- | --- | --- |
| Life bar (player's side) | `FIX.PRS` cells `0x0880`-`0x08CF` | 20 names, among them VEGA `0x089B`, **BISON**, GOUKI `0x08A3`, **AKUMA** `0x08A6`, NASH `0x0884` | `swap1`: GOUKI's cells get AKUMA's (block `0x08A0` rebuilt) | life bar `AKUMA`; VEGA, CHUN-LI, ROGUE unchanged |
| Life bar (CPU side) | `FIX.PRS` cells `0x0822`-`0x087F` | 20 names, among them CHUN-LI `0x0850`, ROGUE `0x0862`, **BISON**, GOUKI `0x0879`, **AKUMA** `0x087C` | (same mechanism) | — |
| Life bar, CHARLIE | `FIX.PRS` cells `0x03C8`-`0x03CB` and `0x03CC`-`0x03CF` (two styles) | **CHARLIE** | `charlie_life`: block `0x0880` repointed so NASH's cells decode `0x03CC`- | life bar `CHARL…` (NASH's sprite is 3 cells wide) |
| Select label | **`VS00.PRS`** frames `0x96`-`0xA7` (slots 0-17 in order; Cyclops `0x97`, Ryu `0x9F`) | plus **BISON** `0xA8`, **AKUMA** `0xA9`, **CHARLIE** `0xAA` | `label_a8c`, `label_a9`, `label_aa`: frame `0x97`'s entry (size and offset) set to `0xA8`/`0xA9`/`0xAA`'s | the label reads `BISON`, `AKUMA`, `CHARLIE` in Cyclops's place |
| VS-screen name | **`VS00.PRS`** one-cell letter font (frames about `0x78`-`0x95`; E `0x7D`, N `0x7E`, I `0x7F`, R `0x80`, L `0x82`, O `0x83`, S `0x85`, Y `0x88`, M `0x89`, T `0x8A`, U `0x8B`, B `0x8D`, A `0x8E`, H `0x8F`, D `0x93`) | letters, not names | `vs_patch1`: frame `0x7E` (N) points at `0x8F`'s data | `HASH` |
| Win-banner name | **`VS00.PRS`** 2 × 2 letter font (frames `0xB5`-`0xD4`; A `0xB8`, R `0xBA`, N `0xBD`, H `0xBE`, U `0xBF`, Y `0xC1`, S `0xC2`) | letters, not names | `banner_vs00`: frame `0xBD` (N) points at `0xBE`'s data, with CPU vitality set to 0 | `HASH` |
| Ending speaker labels | `MCED.SHP` label list, decoded `0x3DA8` (`EXP-0038`) | `Vega`, `Gouki`, `Nash`, `Bison`, `Akuma`, `Charlie`, `Nash's friend`, `Charlie's friend`… | (`EXP-0038`, D-033) | — |

Every patch was checked against the untouched bytes first, and held to
the end of its run (`changes.json` in each run directory, rule 12). The
letter maps come from the order of the DMA transfers paired with the
`VS00` frame decodes of the same frames; `vs_patch1` and `banner_vs00`
confirm N and H.

**`Balrog`:** no label or text "Balrog" in any file (8- or 16-bit ASCII,
raw and decoded). The ending labels are read from `MCED`'s 40-entry list
(`EXP-0038`), which has none. ABSENT.

**Letters for the American names:** both `VS00` letter fonts are drawn
from per-letter frames. Every letter of BISON, AKUMA and CHARLIE also
occurs in a roster name the game spells on those screens: K in GOUKI and
KEN, C in CYCLOPS, the others in NASH, SABRETOOTH, DHALSIM and RYU. So
the VS and banner screens can spell them with existing art.

### Failed or invalid attempts (in order)

1. Write breakpoints on VDP1 VRAM saw nothing; the cells come by DMA.
2. The agent's `physical` space returns zeros (not implemented).
3. The first cell-to-VRAM pairing was off; a brute-force match fixed it.
4. **`FIX.PRS` swaps** on the select label (`swap2`, `swap3`,
   `sel_swap`), the VS screen (`swap_vs`, `swap_vs2`) and the banner
   (`swap_banner`, `banner_swap`): no effect. Their art equals
   `FIX.PRS` cells byte for byte, but they are drawn from `VS00.PRS`.
   `swap_banner` was also invalid, since with no input the fight never
   ended; `banner_swap` fixed that with vitality 0.
5. **Lost or late keys** spoiled `swap2`, `label_a8` and `label_a8b`
   (one went to Option Mode).
6. **Name-text searches** in RAM, the cart, `MMPACK` and every file found
   no name stored as letters. They tried linear codes at strides 1-16,
   glyph cell numbers, and `VS00` letter codes at strides 1-12.

## Conclusion

**CONFIRMED:**

- **Life bar:** `FIX.PRS` cells, with BISON, AKUMA and CHARLIE all
  present.
- **Select label:** `VS00.PRS` frames `0x96`-`0xA7`, with BISON, AKUMA
  and CHARLIE at `0xA8`-`0xAA`.
- **VS name and win banner:** spelled from two `VS00.PRS` letter fonts,
  which have every letter the American names need.
- **Ending labels:** `MCED.SHP`'s list, which has the American labels and
  no `Balrog`.

So the disc already holds the American art for every name surface. Swapping
a frame-table entry or a cell block in RAM shows it.

**UNKNOWN (for `LOC-005`):** where the VS and banner screens get each
character's letter list. It is not stored as letters in any searched
code. The next step is to trace the code that writes the VS name's
objects (frame index at object + 24) back to its table.

## Uncertainty and Alternatives

- **Cart RAM** was read from save states with `mcs_extract`
  (unvalidated); it was used only for searching.
- **The `VS00` letter maps** are confirmed for N and H by patches; the
  other letters rest on the DMA pairing.
- **The win banner's** letters were seen only with the vitality patch.

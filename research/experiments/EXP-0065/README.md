# EXP-0065 (UI): English Attract Captions: the Map Path and the User's Options

Task: CAP-002
Status: IN_PROGRESS (map and palette paths confirmed; the user chose option
A; the build to come)
Confidence: CONFIRMED for the map and palette paths (offline replays equal
RAM); the build is not yet done

## Observation

`EXP-0064` (D-056): the four captions are NBG1 tiles from `OPENING*.ST2`;
where NBG1's caption maps come from was not traced. The official English is
the US arcade's (and US PS1's) four captions; the fourth is misspelled
"UNCCANY" in both.

User decisions (2026-10-31, verbatim): "Let's start CAP-002. But I want to
use "Uncanny" instead of "Unccany" if possible." and ""Decide it" can be
left out if you don't find a useful/meaningful place to put it."

## The Map Path

From `local/cap001/states1/t00002980.mcs` (caption 2 about 260 frames on):

- `EXP-0064/find_decode.py` with caption 2's map rows (VDP2 `0x6C000`-
  `0x6C3FF`) as probes: the entries appear in WRAM-H `0x0604C180`-
  `0x0604C340` and in VDP2 VRAM at the same step. WRAM-H `0x0604C000` is a
  staging copy of map page `0x6C000`.
- Write log on `0x0604C180`-`0x0604C1FF` (`EXP-0049/write_log.py`): every
  write is `0x0601FA4C`/`0x0601FA50`, called from the builder
  **`0x0601F9E4`**:
  - it reads an index array (WRAM-H **`0x06033020`**) and an attribute
    array (**`0x06035020`**), one word per 16 × 16 character;
  - pattern name = palette (attribute bits 0-4) and flips (bits 5-6), and
    character = index × 4 + a base (`0x1844` for caption 2, from
    `0x06020BB8` + 4);
  - it fills four quarter-pages, `0x0604C000`, `0x0604D000`, `0x0604C800`
    and `0x0604D800`; blank cells are cleared with `0x020C`.
- Write log on the index array (`0x06033020`-`0x0603305F`): written by a
  word-LZ at `0x06022F48`-`0x06023042` through a buffer at `0x0602A020`.
- **Section A, confirmed:** MSHvSF's section A decoders, copied unchanged
  into [`msh_script.py`](msh_script.py) (`script_decode`, `script_frames`,
  `map_decode`), decode all eight `OPENING` scripts to a clean end (1,752
  frames each, 221-279 map updates). Replaying `OPENING6`'s and `OPENING7`'s
  map updates, the 0x2000-word target array at `0x06033020` (index array,
  then the attribute array at `0x06035020`) equals RAM at caption 2 (state
  `t00003240`) in all 8,192 words at script frame 478.

**Maps must change.** In each caption's map, blank cells share one
character and repeated shapes share characters (caption 1: 240 cells in its
box, 106 distinct, 103 blank), so English of another shape cannot be drawn
by changing tile pixels alone.

## The Arcade Art

- **Captions 1-3:** MAME `xmvsfu` snapshots at frames 1,440, 1,800 and 2,055
  (equal to `EXP-0064`'s; rerun every frame around each caption in
  `local/cap002/mame_scroll`).
- **The banner:** it scrolls 8 pixels a frame (every shifted frame equal,
  frames 2,251-2,414). [`stitch_banner.py`](stitch_banner.py) joins it:
  1,098 × 48 (`local/cap002/banner.png`, `9dbc8ad2…`).
- **UNCANNY:** the letters sit at a 28-pixel pitch from x = 428 and share
  their 3-pixel outlines. [`respell.py`](respell.py) copies the arcade's
  own letters into the slots U, N, C, A, N, N, Y (source letters 0, 1, 2,
  4, 5, 5, 6): `banner_uncanny.png` `0e68b9fb…`. No new lettering.
- **Colours:** every caption and the banner use the same nine colours:
  background `111111`, outline `000000`, and seven shades `ffffff`,
  `ffff99`, `ffee00`, `ffcc00`, `ffaa00`, `ff8811`, `dd6622`. One 16-colour
  palette holds them.
- **The Saturn's caption palette** (NBG1 palette 0, colour-RAM offset 4):
  index 0 transparent, then a grey ramp `101010` … `f8f8f8`.

## The Palette Path

- Colour RAM `0x400`-`0x40F` (NBG1 palette 0) is not written by the CPU in
  700 frames from frame 2,600 (`cram_write`): it arrives by DMA from a
  buffer at WRAM-H **`0x06046000`** (the ramp at `0x06046802`).
- The buffer is rewritten every frame by `0x0601FAD0`: buffer[i + 1] =
  table[source[i]], source WRAM-H **`0x0602E020`**, table `0x06060000`
  (brightness).
- **Confirmed:** replaying the script's palette records (frame bit 4, flag
  bit 5: `[u16 delta][u16 count][count words]`, a cursor advanced by delta,
  then by count) gives the source array exactly (all 2,048 words) at script
  frame 479. The caption source colours are 4 bits per channel, `0xFRGB`
  (`F111` … `FFFF`).
- So the arcade's nine colours carry over exactly: `F111`, `F000`, `FFFF`,
  `FFF9`, `FFE0`, `FFC0`, `FFA0`, `F881`, `FD62`, written by the script's own
  palette records during each caption.

## Character Budget

With the arcade art on the 16-pixel grid (best of 16 alignments):

| Caption | Japanese characters (distinct, in its box) | English (distinct) |
| --- | --- | --- |
| 1 | 106 (blank included) | 130 |
| 2 | 139 | 57 |
| 3 | 96 | 84 |
| 4 (banner) | 54 + 44 | 106 |

Captions 1 and 4 need more characters than their Japanese slots hold.

## Options Put to the User

[`samples.py`](samples.py) pastes each arcade caption onto a Saturn caption
screen (352 × 240, the Saturn's `PRESS START BUTTON` kept):
`local/cap002/cap_samples.png` (`1a8e3069…`).

- **A. Arcade art, arcade colours:** Capcom's lettering, layout and
  yellow-to-orange shades; needs a palette change besides new maps and
  tiles.
- **B. Arcade art, Saturn colours:** the same lettering and layout, the
  seven shades mapped to the Saturn's greys (`f8f8f8` … `989898`); the
  palette is unchanged.

In both, the fourth caption reads UNCANNY, and 決めろ! is left out (it is
never shown).

**The user's choice** (verbatim): "Use option A: the arcade's art in the
arcade's own yellow-to-orange colours, with UNCANNY. I approve the arcade's
English wording as shown." Recorded in `docs/localization_policy.md` as a
`GATE-TRANSLATION` extension.

## Build Design

1. Per caption window, rewrite the section A map updates so each English
   cell has its own character (MSHvSF `EXP-0073`'s approach), and the
   palette records so palette 0 holds the arcade colours.
2. Paint the English characters into the caption's character slots in its
   graphics block; captions 1 and 4 need room beyond them (more slots, or a
   larger block), still to be designed.
3. Re-encode: MSHvSF's `map_encode` and `script_encode`/`script_splice` for
   section A (formats confirmed equal); a new ring-buffer encoder for the
   graphics blocks (MSHvSF's `lz_encode` targets the other LZ).
4. Check offline (every caption frame renders as planned; maps elsewhere
   unchanged), then from a cold boot, then the user's attract check.

## Uncertainty

- Room for captions 1 and 4's extra characters is not yet found.
- The table at `0x06060000` and the one-entry shift between source and
  buffer are observed, not traced.

# EXP-0049 (Names): Where Each Name Surface Is Stored

Task: LOC-002
Status: IN_PROGRESS
Confidence:

- CONFIRMED: life-bar names (storage, US names present, controlled
  change);
- SUPPORTED: select label (byte match, no controlled change yet);
- PARTLY UNKNOWN: win banner and VS screen (font found, name source not
  found).

## Observation

`EXP-0048` (D-044): the Saturn shows `VEGA`, `GOUKI` and `NASH` on four art
surfaces: select label, VS screen, life bar and win banner. The US arcade
shows `BISON`, `AKUMA` and `CHARLIE` there. `EXP-0011` found no name as
plain text on the disc.

## Questions

For each surface:

- where the name art is stored (file, offset), shown by a controlled
  change;
- whether the American name's art is on the disc.

## Tools

| Tool | Use |
| --- | --- |
| [`dump_screen.py`](dump_screen.py) | Per state: screenshot (after one frame), VDP1/VDP2 VRAM, WRAM-L, WRAM-H (live agent reads) |
| [`find_bytes.py`](find_bytes.py) | A VRAM block in RAM dumps and in every disc file (raw, PRS, PCA) |
| [`write_log.py`](write_log.py) | Log-mode breakpoints (write, read or pc) on a range after a state: every hit's PC and registers |
| [`cells.py`](cells.py) | Reimplementation of the cell decoder at `0x06024CF0`; sheets of decoded cells |
| [`cell_swap.py`](cell_swap.py) | Rewrites one 16-cell block of `FIX.PRS` in RAM so that some cells show others; control and swap runs; read-back of the edit |
| `tools.memory.vdp1_sprites` | VDP1 command list and sprite renders |
| `tools.sh2.disasm` | SH-2 disassembly of the WRAM-H dumps |

States: `local/loc001/session/states` (the `EXP-0048` voice session, M8
build) and the route's select state `local/checkpoints/re004/f00002973.mcs`.

## Actual Result

### The path from file to screen (life bar), traced

1. **Sprites:** at `f00007694` (Gouki + Vega against Chun-Li + Rogue), the
   life-bar names are VDP1 sprites. The colour word is `0x7040`, each cell
   16 × 16 at 4 bpp. GOUKI and VEGA's data is at VDP1 `0x17100`–`0x17380`,
   CHUN-LI and ROGUE's at `0x19700`–`0x19A80`.
2. **No stored copy:** those bytes are not in WRAM-L, WRAM-H or the cart
   (extracted, unvalidated), nor in any file, raw or decoded.
3. **No CPU write:** write breakpoints on VDP1 (`0x25C…` and `0x05C…`) saw
   none, so the cells arrive by DMA.
4. **The DMA:** a log on the SCU registers shows a level-0 DMA routine at
   `0x06024010`, with the source in R9, destination in R10 and length in
   R11. Each 128-byte cell comes from one composition buffer,
   `0x06024DDC`.
5. **The decoder:** the code that writes that buffer is at `0x06024CF0`
   (disassembled):
   - the cell index is in R3;
   - the pack's base address is the long at `0x0602586C`;
   - a block offset table sits at pack + 16 (indexed by cell / 16);
   - a size/type byte per cell sits at pack + 16 + `0x380` (negative:
     128 raw bytes; zero: blank; positive: a 16-bit mask and per-column
     run coding).

   `cells.py` reimplements it. Its output equals the VRAM cells byte for
   byte (18 of 18 cells checked).
6. **The pack:** the base address is `0x002C3EA0` in WRAM-L, where
   **`FIX.PRS` is loaded raw**. The file's bytes equal the RAM copy, and
   there is only one copy in RAM.

### Name art in `FIX.PRS` (decoded with `cells.py`, read by the agent)

| Cells | Style | Names |
| --- | --- | --- |
| `0x0822`-`0x087F` | the CPU side's life bar; also the select label | WOLVERINE, CYCLOPS, STORM, RYU, MAGNETO, JUGGERNAUT, GAMBIT, CHUN-LI (`0x0850`-`0x0853`), SABRETOOTH, APOCALYPSE, KEN, ROGUE (`0x0862`-`0x0864`), NASH, CAMMY, DHALSIM, ZANGIEF, VEGA, **BISON**, GOUKI (`0x0879`-`0x087B`), **AKUMA** (`0x087C`-`0x087E`) |
| `0x0880`-`0x08CF` | the player's life bar | MAGNETO, NASH (`0x0884`-`0x0886`), CHUN-LI, APOCALYPSE, CAMMY, DHALSIM, ZANGIEF, VEGA (`0x089B`-`0x089D`), RYU, **BISON**, GOUKI (`0x08A3`-`0x08A5`), **AKUMA** (`0x08A6`-`0x08A8`), WOLVERINE, KEN, CYCLOPS, STORM, GAMBIT, JUGGERNAUT, SABRETOOTH, ROGUE |
| near `0x03C8` | the same two styles | **CHARLIE**, twice (`local/loc002/fix_0300_x3.png`) |
| `0x0300`-`0x037F` | win-banner font, 2 × 2 cells a glyph | 0-9, A-Z, `?`, `.`, `&`, a heart |
| `0x01DA`-`0x01F3` | VS-screen-style letters, one cell each | A-Z in order (matched to the VS screen; see below) |

### Controlled changes

| Run | State | Change in RAM (`FIX.PRS` copy) | Control | Swap | Verdict |
| --- | --- | --- | --- | --- | --- |
| `swap1` | `f00007350` (before the fight), 344 frames | cells `0x08A3`-`0x08A5` (GOUKI, player's style) get `0x08A6`-`0x08A8` (AKUMA); `0x08AF` blanked to fit | life bar `GOUKI`, `VEGA`, `CHUN-LI`, `ROGUE` | **`AKUMA`**, `VEGA`, `CHUN-LI`, `ROGUE` | CONFIRMED |
| `swap2`, `swap3` | route select state, keys `uuullu` | cells `0x0879`-`0x087B` (GOUKI, select style) get `0x087C`-`0x087E` (AKUMA); `0x0870` blanked | keys lost (Ken) | `GOUKI` | no effect: the select screen decodes its labels before this state |
| `swap_vs`, `swap_vs2` | `f00030578` (before the VS screen), 340 frames | cell `0x01E7` (N) gets `0x01E1` (H) | `NASH` | `NASH`; the edit survived the run | no effect: the VS screen does not use these cells |
| `swap_banner` | `f00029551`, 345 frames | `0x034E`-`0x034F` (N's top) get `0x0342`-`0x0343` (H's top) | — | — | invalid: with no input the fight did not end, so no banner |

Every write was checked against the untouched file's bytes first.
`OUT/changes.json` in each run lists the bytes (rule 12).

### Select label

At `f00006139` and `f00006484`, the label's VDP1 cells equal `FIX.PRS`
cells:

- NASH: `0x0865`, `0x0866`, `0x0859`;
- GOUKI: `0x0879`-`0x087B`.

These are the CPU-side life-bar set. SUPPORTED, by byte equality. A
controlled change needs a state from before the select screen decodes its
labels.

### Win banner

At `f00029896` ("NASH / RYU"), the banner's sprites (colour word
`0x7010`) equal cells of the 2 × 2 letter font (`0x0324` A, `0x0342`/`0x0343`
H, `0x0368` S, …). Draw-list entries at `0x060E3500` hold
(x, y, id, attribute), with sprite ids `0x00B8`-`0x00C2` that are not
alphabetical.

### VS screen

At `f00030918`, the names (colour word `0x6010`) equal the one-cell letters
`0x01DA` + (letter − A): N `0x01E7`, A `0x01DA`, S `0x01EC`, H `0x01E1`,
R `0x01EB`, Y `0x01F2`, U `0x01EE`. Each letter matches exactly one
`FIX.PRS` cell.

But the RAM edit of `0x01E7` does not change the VS screen, and the
decoder at `0x06024CF0` is not called for these cells. Instead:

- **The transfer:** the VS cells reach VDP1 by the same DMA from a staging
  buffer (`0x060ABA58`…). The buffer is filled by a second decoder at
  `0x060252BA`, a bit-stream format.
- **Its input:** the input pointer at `0x060251EC` + 16 (`0x25C2B76F`) is
  in VDP1 VRAM. The data there is **`FC0C.PRS`**, loaded at VDP1
  `0x2A770`, and also part of `FCALL.PRS`, loaded at VDP1 `0x8000`.
- **Face files:** there are 19 face files, `FC00`-`FC12` (slots 0-18), and
  `FCALL.PRS` (218,112 bytes).
- **HYPOTHESIS:** the VS names are drawn from each character's face file
  (same letter art as `FIX.PRS`), not composed at run time from a string.

### Name text

For the banner and the VS screen, no name is stored as letters under any
linear code (bytes or words, scales 1, 2 and 4, strides 1-16). The search
covered WRAM-L, WRAM-H, `MMPACK.PCA` and the cart, plus every file at
stride 1. Searches by glyph cell numbers (top-left, top row, all four)
also found nothing.

## Conclusion (so far)

**CONFIRMED:**

- The life-bar names are compressed 16 × 16 cells in **`FIX.PRS`**,
  decoded by `0x06024CF0` and sent to VDP1 by SCU DMA.
- `FIX.PRS` holds both conventions for the life bar, in both styles:
  BISON and AKUMA beside VEGA and GOUKI, and CHARLIE as separate cells.
- Swapping GOUKI's cells for AKUMA's in RAM makes the life bar read
  AKUMA. Nothing else changes.

**SUPPORTED:** the select label uses the CPU-side life-bar cells.

**Open (LOC-002 not done):**

- the select-label controlled change, from a state before the labels are
  decoded;
- the win banner: which code picks the letters, where the names' text or
  layout is, and a controlled change in a run that reaches a win;
- the VS screen: the face-file format (second decoder `0x060252BA`),
  whether the name is part of each `FCxx.PRS`, and whether any American
  name exists there;
- CHARLIE's life-bar cells shown on screen.

## Uncertainty and Alternatives

- **Cart RAM:** read from save states with `mcs_extract`, which is
  unvalidated for that region. It was used only for searching.
- **The live `physical` address space** returns zeros (unimplemented in
  the agent build), so it was not used.
- **Lost keys** (`EXP-0046`) spoiled one select-screen run (`swap2`).

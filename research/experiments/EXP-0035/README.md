# EXP-0035 (M6): How Nash's Ending Text Is Drawn

Task: END-002
Status: DONE
Confidence: CONFIRMED (code, font, grid, patch regression, English grid
reachable); the English data path is UNKNOWN

## Observation

Nash's ending (`EXP-0034`, D-029) shows six timed pages of Japanese in a
purple box. Before M6, the type-4 selector `0x060668A2` was only a twin of
the arcade's ending selector that shares the quote renderer `0x06066948`
(`EXP-0023`); whether it draws the endings was a HYPOTHESIS.

## Hypotheses

1. The type-4 selector and the shared renderer draw the ending pages, with
   the quote font from `FIX.PRS` in the Japanese 2 × 19 grid.
2. The version-3 patch leaves the ending unchanged.
3. The arcade English grid (2 × 25 at 12 px) is reachable for the ending.

## Controlled Changes

All on `EXP-0034`'s checkpoints of the untouched image, in RAM only, one
change per run, no input:

| Run | Change |
| --- | --- |
| `trace_pages.py` | None. PC breakpoints in log mode on the four selectors and the renderer |
| `zero_cell.py` zeroed | 128 zero bytes over one glyph cell in VDP1 VRAM (page 3) |
| `ending_modes.py` v3 | The version-3 roster patch (`patches_v3`, slots 0-17) written over the code |
| `ending_modes.py` english | Size and language words `0x060F5478`/`0x060F547A` set to 2 (the `EXP-0023` method) |

## Predictions

1. The type-4 selector and the renderer hit during the ending. Every drawn
   cell equals `FIX.PRS`'s glyph for its code. Zeroing one cell removes
   exactly one glyph.
2. v3 screenshots equal control at all six pages.
3. With the words set, the box draws 2 × 25 sprites at a 12 px pitch.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Checkpoints | `local/checkpoints/end001/f00220064.mcs` (`7c5a7257…`), `f00221258.mcs` (`dbad90c0…`) (`EXP-0034`) |
| Source image | `local/disc_images/xmvsf_saturn_jp_3m`, Track 01 `c904a386…` |
| Source files | `local/ref007/saturn_files/FIX.PRS`, `MMPACK.PCA`, `MC10.SHP` (extracted from the source image in `EXP-0011`) |
| Emulator | agent build, home `local/mednafen_quiet` |

## Tools

| Tool | Use |
| --- | --- |
| [`trace_pages.py`](trace_pages.py) | Selector and renderer hits per page interval; screenshot, VDP1, VDP2, quote pointer and record per page |
| `research/experiments/EXP-0023/cell_check_en.py` | Drawn cells against `FIX.PRS` glyphs (its input built from `trace2`) |
| [`zero_cell.py`](zero_cell.py) | One-cell zero test with pixel diff |
| [`ending_modes.py`](ending_modes.py) | control, v3 and english runs; the selector's two lists at run time |
| `tools.sh2.disasm` | The original selector, from decoded `MMPACK.PCA` (base `0x06014BA0`) |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0035/trace_pages.py local/end002/trace2
# cell check: local/end002/cells/result.json = trace2's pages 1-6 (pointer, codes), plus their VDP1 dumps
./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/end002/cells local/ref007/saturn_files/FIX.PRS
./invenv.sh python research/experiments/EXP-0035/zero_cell.py local/end002/zero1
./invenv.sh python research/experiments/EXP-0035/ending_modes.py local/end002/modes2
./invenv.sh python -m tools.sh2.disasm local/end002/mmpack_code.bin --base 0x06014BA0 \
  --start 0x060668A2 --end 0x06066948
```

`local/end002/mmpack_code.bin` is the decoded `MMPACK.PCA`
(`tools.disc.prs.decompress_entries`), starting at `0x06014BA0`.

## Actual Result

### Code

| Interval ending at (page) | Type-4 selector `0x060668A2` | Renderer `0x06066948` | Others |
| --- | --- | --- | --- |
| 220,654 (1) | 1 | 1 | 0 |
| 220,887 (2) | — | 1 | 0 |
| 221,112 (3) | 1 | 1 | 0 |
| 221,342 (4) | — | 1 | 0 |
| 221,690 (5) | 1 | 1 | 0 |
| 222,037 (6) | 1 | 1 | 0 |
| 223,044 (credits) | — | — | 0 |

The win (`0x0606663C`), hint (`0x06066728`) and type-6 (`0x060667B8`)
selectors never hit. The renderer starts once per page; the type-4
selector runs once per scene, at the pages where the picture changes
(1, 3, 5, 6).

**The selector, unpatched** (disassembly):

- It reads the language word (literal `0xD47A`, `mov.w @(r0,r11)` at
  `0x060668C4`) and doubles it.
- It reads a list pointer through the table at `0x06066910`. Language 0
  gives `0x060854F8`; language 2 (also 4 and 6) gives `0x06085544`.
- It takes the long for the speaker's slot (`@(6,gbr)` × 2) from that list,
  stores it at task + `0x34`, and stores the task's address at
  R11 + `0xA48C`.

**The lists at run time** (at `f00220064`):

- **Language 0:** filled only for the three loaded characters:
  - slot 16 (Nash) `0x0024FEC0` (first member, WRAM-L);
  - slot 9 (Ryu) `0x060B2A98` (second member, WRAM-H);
  - slot 8 (Apocalypse) `0x060C1F60` (opponent).

  Every other slot holds a placeholder (`0x99xx0099` pattern).
- **Language 2:** 19 longs that are not addresses (for example
  `0x0A3A0A7C`). They read like pairs of character codes. The Saturn does
  not fill this list.

**The records shown.** The quote pointer `0x060F2490` was:

- `0x0024FEC0` at page 1;
- then 76 more at each page, up to `0x0025003C` at page 6.

All six 76-byte records equal decoded `MC10.SHP` at `0x2EC0` + 76k. That is
records 16-21, right after the 16 win quotes (table `0x2A00` + `0x4C0`).

### Font and grid

| Page | Quote sprites | Rows (VDP1 y) | Pitch | x range | Match to `FIX.PRS` glyph |
| --- | --- | --- | --- | --- | --- |
| 1, 2, 5 | 38 | 178, 194 | 16 px | 26-314 | 38/38 |
| 3, 4, 6 | 76 | 178, 194 | 16 px | 26-314 | 76/76 |

- **Grid:** 19 cells × 2 lines at a 16 px pitch, colour word `0x7020`. This
  is the same grid as the Japanese win quotes (`EXP-0020`).
- **Spaces:** they are drawn too; every one of the 38 codes has a sprite.
- **Pages 3, 4 and 6:** every cell has two identical sprite commands (same
  position, same character data).
- **On screen:** the glyphs appear about 9 px lower than the VDP1 y. For
  example, the zeroed cell at VDP1 (26, 178) changed screenshot pixels x
  27-40, y 187-200.

**Zero test (page 3, `f00221258`).** 128 zero bytes were written at VDP1
`0x1A000`, the first glyph of the top row (shared by both of its sprite
commands).

- Two frames later, 139 pixels differed from control, all inside x 27-40,
  y 187-200.
- At 4× zoom, the first glyph (何) was gone, and the rest of the line, the
  box and the label were unchanged.

### Patch regression (v3 against control)

- `patches_v3(0-17)`: every site held its original bytes before the write.
- All six page screenshots were byte-identical to control. Control itself
  equals `EXP-0034`'s session screenshots (`9d66b488…`, `361438a2…`,
  `4c3ef8e4…`, `388c0716…`, `78a2207a…`, `ab2f6006…`).
- The pointers and records were identical too.
- The words were 0 throughout, so the patched selector's constant 0 equals
  the value it replaced.

### Global words set to 2 (english)

- **Grid:** the box is drawn as 25 cells × 2 lines at a 12 px pitch:
  VDP1 x 24-312, rows 176 and 192, colour word `0x7000`, 50 (or 100)
  sprites. This is the arcade English grid.
- **Pointer:** `0x09EC0B8E`, the language-2 list's slot-16 value, which is
  not work RAM. It advanced by 100 bytes, not 76, at pages 3, 4 and 6 of
  the target frames. So the page timing differs from control.
- **Text:** pages 1-3 and 6 drew blank boxes. Pages 4 and 5 drew
  repeated, meaningless katakana from whatever that bus address returns.
- **Labels and pictures changed too.** At frame 222,037 the label reads
  **`Charlie`** (6× zoom) and the picture window is black, where control
  shows `Nash's friend` and Guile. No other English-mode page showed a
  label.

## Conclusion

**CONFIRMED:**

1. Nash's ending is drawn by the type-4 selector (once per scene) and the
   shared quote renderer (once per page). They use the quote font from
   `FIX.PRS` in the Japanese 2 × 19 grid at 16 px.
2. The six pages are `MC10` records 16-21, read in order from the WRAM-L
   copy of the first member's file. The selector's language-0 list holds
   one ending base per loaded slot.
3. The version-3 patch leaves Nash's ending pixel-identical (the open
   patch question, for this ending).
4. The renderer's English grid (2 × 25 at 12 px) is reachable for ending
   pages from a RAM trial, and the selector has an English branch in code.

**Not usable as is:** the English branch's list (`0x06085544`) is not
filled on the Saturn. English ending records would need their own pointer,
for example a per-slot test like version 3's, and records placed where it
points. The global words also change the page timing, the pictures and the
speaker labels. A Latin `Charlie` label exists in the game and is chosen by
the language word. So the ending's English mode has more parts than the
win quotes' (labels, scene script), and these must be mapped before M7.

## Uncertainty and Alternatives

- **One ending:** all of this is Nash's ending, one team (Nash first). The
  other characters and second-member endings are untested.
- **Where `Charlie` comes from:** not traced. The labels may be a table
  indexed by language, or English-mode script data (`END-003`,
  `docs/known_unknowns.md`).
- **The global words have side effects:** the size word is compared at 45
  sites every frame (`EXP-0023`). The English run's timing and picture
  changes may come from them, not from the ending's own English mode. A
  per-task flag trial would separate the two.
- **Disc origin:** the RAM records match decoded `MC10` byte for byte, but
  no writer breakpoint or disc marker test has been run. That is `END-003`.
- **Duplicate sprite commands** on pages 3, 4 and 6 are unexplained (two
  renderer tasks, `0x060F9D80` and `0x060F9FC0`, alternate). They do not
  change what is drawn.

## Reproduction

Run the procedure. Expect:

- the hit table above;
- 38/38 or 76/76 cell matches;
- a 139-pixel diff confined to x 27-40, y 187-200;
- v3 screenshots equal to control;
- the English grid with pointer `0x09EC0B8E`.

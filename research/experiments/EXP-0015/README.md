# EXP-0015: Find the Win-Quote Renderer and Its RAM Text

Task: DBG-005
Status: DONE
Confidence: CONFIRMED

## Observation

The M1 quote has reproducible checkpoints (`EXP-0014`). The extractor is valid
for WRAM-L, WRAM-H and VDP1/VDP2 VRAM; cart RAM is not validated (`EXP-0005`).
MSHvSF's quote was VDP1 sprites over a WRAM-L table of 16-bit codes, found by
an equality pattern (MSHvSF `EXP-0012`, `EXP-0013`); for XvSF that is a
hypothesis.

## Hypothesis

The quote is drawn by VDP1 sprites, one cell per distinct glyph. Its text is a
table of codes in RAM, findable by the cell-equality pattern without knowing
the encoding.

## Controlled Change

Renderer: from `quote_visible`, paused, 128 zero bytes written over one VDP1
VRAM glyph cell (trial) versus no write (control). Table search: none
(read-only).

## Prediction

The trial removes exactly one glyph; the control is unchanged. The equality
pattern matches one place.

## Inputs and Provenance

Checkpoints `local/checkpoints/dbg003/` (`EXP-0014`). Regions extracted with
`tools/memory/mcs_extract.py` to the ignored `research/memory_dumps/dbg005/`.
Arcade program `xmvsfu`/`xmvsfjr2` in 68000 order (`EXP-0008`).

## Tools and Environment

`tools/memory/vdp1_sprites.py`, `tools/text/search.py`,
`tools/text/pattern_search.py`, [`two_line_search.py`](two_line_search.py),
[`renderer_test.py`](renderer_test.py).

## Procedure

```bash
./invenv.sh python -m tools.memory.mcs_extract local/checkpoints/dbg003/f00010336.mcs \
  --out-dir research/memory_dumps/dbg005/quote_visible
./invenv.sh python -m tools.memory.vdp1_sprites \
  research/memory_dumps/dbg005/quote_visible/vdp1_vram.bin --json
./invenv.sh python -m tools.text.pattern_search \
  research/memory_dumps/dbg005/quote_visible/wram_l.bin \
  "b b b A B C D E F G H I J K L b b b b b b b M N O P Q R S T B U b b b b b b" \
  --width 2 --base 0x00200000
./invenv.sh python research/experiments/EXP-0015/renderer_test.py local/dbg005/renderer
```

## Actual Result

**VDP1 layout.** At `quote_visible`, 391 VDP1 commands, all 16×16 4 bpp
normal sprites. The text is two rows of 19 sprites with color word `0x7020`,
at y = 178 and y = 194, x = 26 to 314 in steps of 16. Each distinct glyph has
one 128-byte cell from `0x4A800` upward; the blank cell is `0x4A780`. Line 2's
う reuses line 1's cell (`0x4A880`). The bubble body is other sprites
(`0x7070`).

**Renderer, controlled change.** The trial cell read back as zeros after the
write. Two frames later only line 1's first glyph (も) was gone (agent-reviewed
crop); the control screenshot is byte-identical to the live session's
(`e006ebd8…7cc0`). The quote is drawn by VDP1 from these cells.

**Text search.**

- Plain encodings (Shift-JIS, EUC-JP, UTF-16BE) of `もう一度` and `その時に`:
  0 matches in WRAM-L, WRAM-H and cart RAM.
- A looser two-line structure (`two_line_search.py`): thousands of hits;
  rejected as non-discriminating.
- The full 38-cell equality pattern (blanks included): **1 hit**, WRAM-L
  `0x0024F8D0`, 16-bit big-endian, blank `0x0020`. No hit at 8-bit width or
  in WRAM-H or cart RAM.

**The table.** 22 consecutive 76-byte records (38 codes, 2 lines × 19 cells)
at `0x0024F5D8`-`0x0024FC60` (1,672 bytes,
`31d77550…f950` at `quote_visible`); the M1 quote is record 10. The bytes are
identical at `pre_ko`, `win_banner`, `pre_quote`, `quote_visible` and
`after_quote`.

**Codes.** The 13 hiragana in the record all equal Unicode − `0x2661` (い
`0x09E3` … も `0x0A21`): 13 of 13 fit one offset. Kanji are other codes in
`0x0A8A`-`0x0CAD`; `。` is `0x0A8A` and `！` is `0x0A92`.

**Arcade identity.**
- Saturn records 0-15 are byte-identical to the arcade's Japanese win-quote
  slot 9, records 0-15 (table `0x17E19C`, slot 9 at `0x180EBC`, 16 × 76
  bytes; the same in the US and JP sets). The M1 quote is arcade slot 9
  record 10 (`0x1811B4`).
- Saturn records 16-21 equal six arcade records from `0x184DF8`, the arcade
  Japanese endings table's slot 9 (`0x17E2F0`).

## Conclusion

**CONFIRMED:**
- The win quote is drawn by VDP1 from per-glyph cells.
- Its text is a WRAM-L table of 16-bit codes at `0x0024F5D8`: Ryu's 16
  arcade Japanese win quotes followed by six records of his arcade Japanese
  ending, copied unchanged.
- The M1 quote is record 10.
- Arcade slot 9 is Ryu: the slot-order hypothesis is now supported by the
  Saturn's own data.

## Uncertainty and Alternatives

- What selects record 10 (and when) is not traced; the table is resident
  before the K.O.
- Whether writing new codes into the table changes the drawn text is M1
  (`RE-001`), gated by `GATE-M0`.
- The meaning of records 16-21 on the Saturn (ending text resident with the
  quotes) is not tested.

## Reproduction

Run the procedure; expect one equality-pattern hit at `0x0024F8D0` and the
trial screenshot with one missing glyph.

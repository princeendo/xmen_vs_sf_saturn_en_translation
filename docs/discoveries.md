# Confirmed Discoveries

Only durable `CONFIRMED` findings about XvSF belong here, each with its evidence
(experiment, task) and reproduction instructions. Hypotheses and failures go in
`research_log.md`; open questions go in `docs/known_unknowns.md`.

MSHvSF findings are never recorded here. An MSHvSF finding enters this file only
after an XvSF experiment confirms the XvSF equivalent.

## D-001: Stock Mednafen cold-boots XvSF to the title screen (`EMU-003`, `EXP-0001`)

Stock Mednafen 1.32.1 (`892bb60a…29dd`) with the Japanese BIOS `sega_101.bin`
(`dcfef4b9…deac`) and the silent home `local/mednafen_quiet/` cold-boots the
untouched source image with no input. The log reports `SGID: T-1226G`,
`SGAREA: J` and `Cart: 4MiB Extended RAM` (`ss.cart auto`). The title logo with
`PRESS START BUTTON` shows from about 68 s to 75 s after launch. Three boots
gave byte-identical frames at one-second sampling; title frame 070 hashes
`ebfbb7da…e662`. (Note, `EXP-0018`: the frames from about 43 s depend on when
the boot runs. Original boots about five hours apart diverge there, and boots
minutes apart match, so these hashes reproduce only for boots close in time.) Source hashes were unchanged.

Reproduce: `research/experiments/EXP-0001/README.md`, "Procedure".

## D-002: XvSF needs the 4 MiB extended-RAM cart (`EMU-004`, `EXP-0002`)

With `-ss.cart extram4` three boots log `Cart: 4MiB Extended RAM` and give
frames byte-identical to D-001's `ss.cart auto` boots (89 of 89). With
`-ss.cart none` the log shows `Cart: None` and, from about 14 s, the game shows
only a Japanese warning that the 4MB extended RAM cartridge is not inserted
(frame `5af68833…f2c7`), and never reaches the title. `ss.cart auto` is the
project setting.

Reproduce: `research/experiments/EXP-0002/README.md`, "Procedure".

## D-003: Screenshots and save/load states work by hotkey (`EMU-006`, `EXP-0003`)

In stock 1.32.1, F9 writes a 352x240 PNG to the home's `snaps/` and F5 writes
`mcs/<image>.<md5>.mc0` (3,508,722 bytes at the title). F7 restores the saved
title screen later in the same session and in a fresh cold boot, about 45 s
before a normal boot reaches the title. The state file is unchanged by
loading. Both paths are git-ignored.

Reproduce: `research/experiments/EXP-0003/README.md`, "Procedure".

## D-004: Stock debugger dumps, writes and write breakpoints work unattended (`EMU-007`, `EXP-0004`)

Driven by `tools/mednafen/hotkeys.py` (Option chords posted as left-Option
events), the stock 1.32.1 memory editor dumps "Low Work RAM" and "High Work
RAM" (`00000000 000fffff FILE`, 1,048,576 bytes each), byte-identical when
repeated during one frame-advance freeze; `l` writes a file into WRAM-H and a
following dump reads it back exactly, and loading the saved original restores
it. A CPU-view write breakpoint on `06000000-060fffff 26000000-260fffff` halts
the game at a byte store into WRAM-H (`mov.b r0,@r9`, R9 `060C9047`).

Reproduce: `research/experiments/EXP-0004/README.md`, "Procedure".

## D-005: The save-state extractor is valid for WRAM and VDP VRAM on XvSF (`DBG-001`, `EXP-0005`)

`tools/memory/mcs_extract.py` (default `saturn` byte order) reproduces stock
debugger dumps of the same frame-advance freeze byte for byte: WRAM-L and
WRAM-H at two instants, VDP1 VRAM and VDP2 VRAM at one. The state stores each
16-bit element byte-swapped; the extractor undoes it. These four regions
from states are usable evidence. Cart RAM (4 MiB) is extracted but has no
debugger space to compare against, so it stays **HYPOTHESIS**.

Reproduce: `research/experiments/EXP-0005/README.md`, "Procedure".

## D-006: The reused agent interface is valid on XvSF (`EMU-021`, `EXP-0006`)

The MSHvSF frontend patch (`c30146ef…5244`) builds unchanged on 1.32.1. With
`MEDNAFEN_AGENT_DIR` unset the binary boots XvSF frame-identically to stock.
With it set: `read` of WRAM-L, WRAM-H, VDP1 and VDP2 VRAM equals validated
extraction of a state saved in the same poll; writes round-trip; `pause`,
`step`, `run` and `frames N` work; a log-mode write breakpoint on
`060C9047` logs hits at `06021B26` (the store the stock debugger halted on in
`EXP-0004`) and `06021B6A` without halting.

Reproduce: `research/experiments/EXP-0006/README.md`, "Procedure".

## D-007: The arcade English text is fixed records in the shared program ROM (`REF-003`, `EXP-0008`)

In every held CPS-II set, the English win quotes, endings and continue-screen
hints are 294 records of two 25-code lines at `0x186EA2`-`0x18E17A` (shared
ROM `xvs.06a`; `0x4C` earlier in Japan 960909). Pointer tables: win quotes
`0x17E1E8`, endings `0x17E318` (19 slots each). Codes are ASCII laid out as a
tile sheet (row bases `0x0670`/`0x06D0`/`0x0680`/`0x06E0`/`0x0690`/`0x06F0`
for ASCII rows 2-7; space `0x0020`). `tools/reference/xvsf_text.py` decodes
them with no leftover codes outside the hints; punctuation falls in its
expected context 88-100% of the time. MSHvSF's arcade map does not apply.

Reproduce: `research/experiments/EXP-0008/README.md`, "Procedure".

## D-008: The arcade draws the decoded records; `0xFF8BB4` selects the slot (`REF-004`, `EXP-0009`)

On the US set (MAME 0.289, scripted route, no human input), the CPU's win
quote reads record 109 (`0x189936`) and the speech bubble shows exactly the
decoder's two lines; the continue screen then shows hint records 270 and 271
as two pages, with code `0x0134` drawn as ↑. Work RAM `0xFF8BB4` holds the
win-quote slot base (written at PC `0x04F3DA`). Forcing it to slot 0's base
made the game read and draw slot 0's record at the same index, as predicted.
`0xFF2490` only copies the printed record's address.

Reproduce: `research/experiments/EXP-0009/README.md`, "Procedure".

## D-009: The US PS1 stores the arcade English byte-identically (`REF-006`, `EXP-0010`)

`P/P4/SELECT.BIN` on the US PS1 disc holds 293 of the arcade's 294 English
records, little-endian and byte-identical. Win quotes (161) and endings (109)
are complete and in arcade order. The arcade hints appear twice: verbatim
less one record, and a PS1 variant with 7 rewritten records. The arcade's
"coming soon" line is absent. No Spanish, Portuguese or Japanese tables are
on the disc.

Reproduce: `research/experiments/EXP-0010/README.md`, "Procedure".

## D-010: The Saturn win quote is VDP1 glyph cells over a WRAM-L code table (`DBG-005`, `EXP-0015`)

The quote is two rows of 19 VDP1 16×16 4 bpp sprites (color word `0x7020`),
one 128-byte VRAM cell per distinct glyph; blanking one cell removed exactly
that glyph (control unchanged). The text is a WRAM-L table at `0x0024F5D8`: 22
records of 38 big-endian 16-bit codes (2 lines × 19 cells, blank `0x0020`),
found by a 38-cell equality pattern (one hit). Records 0-15 are byte-identical
to the arcade's Japanese win quotes for slot 9 (Ryu); 16-21 are his Japanese
ending's first records. Hiragana codes are Unicode − `0x2661`. The table is
resident from before the K.O. The M1 quote is record 10.

Reproduce: `research/experiments/EXP-0015/README.md`, "Procedure".

## D-011 (M1): Writing codes into the WRAM-L record changes the quote (`RE-001`, `EXP-0016`)

At the `pre_ko` checkpoint, writing `09E1 09E3 09E5` over `0A21 09E5 0AC8` at
WRAM-L `0x0024F8D6` (record 10, line 1, cells 3-5) made Ryu's quote read
あいう度鍛え直してこい。; only those three cells changed on screen. The no-write
control showed the original quote, byte-identical to the live capture.

Reproduce: `research/experiments/EXP-0016/README.md`, "Procedure".

## D-012 (M2): Ryu's quote table comes from `MC09.SHP`, LZ77-compressed (`DISC-001`, `EXP-0017`)

When Ryu is picked, the game loads `MC09.SHP` (Track 01 LSN 53,719, 20,686
bytes, SHA-256 `e9a5605b333c0cc311458fe225a7812b30c3223237a6f4c69e1e65397de1641a`)
to WRAM-L `0x0024D000`. The loader decompresses it through the streaming
routine at WRAM-H `0x0601077C`.

**File format.** A big-endian 32-bit entry count (0 = one stream), then an
LZ77 stream:

- Control bits are read LSB first; 1 is a literal.
- 0,0 then two bits n (first high) and an offset byte: copy n + 2 bytes from
  byte − `0x100`.
- 0,1 then a big-endian word v: copy (v & 7) + 2 bytes from (v >> 3) −
  `0x2000`. When v & 7 is 0, a count byte gives n + 1 bytes, and 0 ends the
  stream.

**Result.** `tools/disc/prs.py` decodes the file to 43,064 bytes. The quote
table is at decompressed offset `0x25D8`, byte-identical; record 10 (M1) is at
`0x28D0`. The rest equals RAM after the load except 259 32-bit fields, each
relocated by `+0x0024D040`, none in the table.

**Evidence.** With a write breakpoint on the table, the control (no input)
has no hit. Two picks halted identically at `0x0600D124`. The same decoder
fully consumes 50 files: `MC*.SHP`, `MS*.SHP` and `*.PCA`.

Reproduce: `research/experiments/EXP-0017/README.md`, "Procedure".

## D-013 (M2): A rebuilt image shows the quote change after a cold boot (`DISC-002`, `EXP-0018`)

The image is built from the untouched source with only `MC09.SHP`
re-encoded (`tools/disc/prs.py` `compress_file`):

- **Content:** あいう (`09E1 09E3 09E5`) in line-1 cells 3-5 of all 16 Ryu
  win-quote records. Record 10 gets exactly the M1 bytes.
- **Size:** the original 20,686 bytes, with the stream ending in the last
  sector.
- **Sectors:** only LSN 53,722-53,729 change. Every sector passes EDC/ECC;
  `tools/disc/sector.py` reproduces all 71,908 source sectors' EDC/ECC first.

**Result.**

- From power-on, two user Ryu wins showed あいう in records 1 and 8, with the
  rest of each quote and the game normal.
- Picking Ryu from a saved state with the rebuilt image mounted loads the
  marked table. The original image loads the original table.
- Re-encoding the original decoded file reproduces `MC09.SHP` byte for byte.

Reproduce: `research/experiments/EXP-0018/README.md`, "Procedure".

## D-014 (M2): The quote font is `FIX.PRS`, and its format is proven (`FONT-001`, `EXP-0019`)

The win-quote font is the data-track file `FIX.PRS` (LSN 46,715, 209,285
bytes, SHA-256 `68032831c08fb1304d1becd5d5a68fc904b2adeedfb70d76cb2b0e42c8b90bab`),
stored uncompressed.

**In RAM.** It is loaded unchanged to WRAM-L `0x002C3EA0` (the pointer is at
WRAM-H `0x0602586C`). The routine at `0x06024CF0` (code in R3) builds each
glyph into the staging cell `0x06024DDC`.

**Layout.**

| Offset | Content |
| --- | --- |
| 0x000 | 16-byte header; the last word is the code count `0x0E00` |
| 0x010 | block table: one long per 16 codes |
| 0x390 | size table: one byte per code (0 empty, negative raw 128 bytes, else compressed length) |
| after | glyph data |

Compressed glyphs are a mask-selected column-run fill (`tools/text/font.py`).

**Evidence.**

- `tools/text/font_pack.py` repacks `FIX.PRS` byte for byte.
- Decoding reproduces all 22 distinct codes of the M1 quote as drawn VDP1
  cells.
- From a cold boot, a one-byte change to `FIX.PRS` on a rebuilt image
  appears in the loaded font; the original image is the control.

Reproduce: `research/experiments/EXP-0019/README.md`, "Procedure".

## D-015 (M2): The quote font draws the arcade English codes; a quote is 2 × 19 cells (`FONT-002`, `EXP-0020`)

**Codes.** The Saturn win-quote font (`FIX.PRS`) has quote-style 16×16 Latin
glyphs at the arcade English codes. Printable ASCII row `0x2_`-`0x7_` starts
at `0x0670`, `0x06D0`, `0x0680`, `0x06E0`, `0x0690` and `0x06F0`, and space is
`0x0020` (`tools.reference.xvsf_text`). The exceptions are `@` (`0x0680`),
which is ♥, and `{ | }` (`0x06FB`-`0x06FD`), which are two fractions and ∞.

**Evidence.** Written into record 10 from `pre_ko`, three trials covering all
94 codes drew exactly the decoded glyphs, 38/38 cells each, and two runs were
byte-identical. The no-write control equals the live capture.

**Grid.** A quote line is 19 sprites of 16 px (x = 26-314, y = 178 and 194).
All 38 cells and 38 distinct glyphs display. Latin glyphs fill the cell
(ink 6-15 px wide).

**Capacity.** Of the 161 arcade English win quotes (2 × 25 codes), 25 fit
2 × 19 as written and 59 after re-wrapping at word boundaries.

Reproduce: `research/experiments/EXP-0020/README.md`, "Procedure".

## D-016 (M3): The win-quote record is `RNG() & 0x0F` and can be forced (`RE-002`, `EXP-0021`)

**How the record is chosen.** When the quote starts, after the K.O., the
quote script sets up a task (`0x060F8AC0` in the tested session):

1. It stores the record index `RNG() & 0x0F` at task + 38 (`0x06066696`).
   The RNG is `0x06056B54`, with seed `0x060F545A` and seed = seed × 176 mod
   32,749.
2. It stores the table base at task + 52.
3. It writes the record pointer base + 76 × index to WRAM-H `0x060F2490`
   (`0x0606698C`), which the reader `0x06066A84` uses.

**Forcing.** An agent `onhit` write of index `k` right after `0x06066696`
shows record `k`. Indices 0, 1, 5, 8 and 15 drew all 38 cells exactly, over
two sessions. The no-write control equals the live capture.

Reproduce: `research/experiments/EXP-0021/README.md`, "Procedure".

## D-017 (M3): Saturn record k pairs with arcade English record k mod 8 (`PAIR-001`, `EXP-0022`)

The arcade win-quote selector at `0x04F396` (`xmvsfu`) works as follows:

- It draws `r = rand() & 0x0F`.
- When the language word `0xFF547A` is nonzero (English is 2), it shows
  record `remap[r]`, where `remap = [0..7, 0..7]`, with 100-byte records from
  the English table `0x17E1E8`.
- Otherwise it shows record `r`, with 76-byte records from the Japanese table
  `0x17E19C`.

The Saturn runs a port of the same routine with the language word 0
(`EXP-0021`), so Saturn record `k` (arcade Japanese slot 9 record `k`) pairs
with English slot 9 record `k mod 8`. Ryu's English record 8 is never chosen
by this selector.

**Evidence.** In MAME, forcing the draw with Ryu's slot forced read exactly
the predicted English record for all 16 draws, and the predicted Japanese
record for 4 draws. A natural draw in both languages from one state gave
English record 2 and Japanese record 10, for r = 10. The table is in
`data/translations/ryu_pairing.json`.

Reproduce: `research/experiments/EXP-0022/README.md`, "Procedure".

## D-018 (M3): The Saturn keeps the arcade's English quote mode; a patch enables it for Ryu (`LAYOUT-001`, `EXP-0023`)

**The mode.** The Saturn quote renderer (`0x06066948`, in `MMPACK.PCA`) still
has the arcade's English mode: 100-byte records drawn 2 × 25 at a 12 px pitch
(color word `0x7000`). A nonzero language word selects it, but that word
cannot be set globally: hints and endings share the renderer, and the
neighbouring size word is a mode word read every frame.

**The patch** (version 2), same-size changes in `MMPACK.PCA`:

- When the speaker is Ryu, the win-quote selector sets task byte `+0x5C` and
  uses index `r & 7`.
- The renderer reads that byte instead of the global words.
- Ryu's 8 official English records replace the start of his table in
  `MC09.SHP`.

The full table is in `research/experiments/EXP-0023/README.md`.

**Evidence.**

- From a cold boot of the rebuilt image, Ryu's win quotes showed in English
  (two play checks).
- Wolverine's quote and the continue hint drew in Japanese, 38/38 cells
  each.
- From one state, Storm's quote with version 2 was byte-identical to the
  unpatched game.
- Version 1, which had no slot test, drew other characters' Japanese in the
  English grid. It was rejected.

Reproduce: `research/experiments/EXP-0023/README.md`, "Procedure".

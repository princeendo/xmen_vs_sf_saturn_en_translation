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

## D-019 (M3): All of Ryu's win quotes in English from the source image (`RE-003`, `EXP-0024`)

`tools.disc.build_english` builds `MMPACK.PCA` and `MC09.SHP` from the
untouched source. It reads `data/translations/ryu_win_quotes.json` (source
addresses and hashes; the English text comes from the user's arcade ROM) and
compiles the text with `tools.text.caption`. The resulting image (Track 01
`1034b8d7…`) shows, for each of Ryu's 16 Saturn draws, his official arcade
English record `draw mod 8`, which is the user's pairing.

**Evidence.**

- Every draw was steered live through the RNG seed and drew all 50 cells as
  compiled.
- The unpatched control drew 38/38.
- Two cold-boot Ryu wins showed English.

Reproduce: `research/experiments/EXP-0024/README.md`, "Procedure".

## D-020 (M4): Ken's quotes come from `MC0A.SHP`; the selector sees slot 10 (`RE-004`, `EXP-0025`)

When Ken is picked, the loader at `0x0600D124` decodes `MC0A.SHP` (23,258
bytes) to file base WRAM-L `0x0024D000`. Ken's quote table is at decompressed
offset `0x2A4C` (WRAM-L `0x0024FA4C`). When Ken is the second team member,
the same file loads at WRAM-H `0x060B0000`, so the table is at `0x060B2A4C`.
The table's records 0-15 are the arcade's Japanese win quotes for slot 10,
byte for byte, and records 16-20 are his first 5 ending records. At the
English-mode test site `0x06066668`, `@(6,gbr)` holds `0x0014` (slot 10 × 2)
when Ken speaks.

**Evidence.**

- From a state with the cursor on Ken, a write breakpoint on the table did
  not fire with no input. Pressing the pick button halted at `0x0600D124`
  with R12 = `0x0024FA4C` and file size `0x5ADA`, which only `MC0A.SHP` has.
  A repeat gave identical registers and RAM.
- RAM equals the decoded file plus 302 relocation fields (+ base + `0x40`)
  at both bases.
- Ken's draw 14 gives the pointer read at the quote screen, `0x0024FE74`.
- Ryu's reference state gave `0x0012` at the same halt.
- File base `0x060B0000` held the second member's file in both sessions
  (Gouki behind Ryu, Ken behind Gouki). Opponents' files were at
  `0x060C1000` and `0x060D2000`.

Reproduce: `research/experiments/EXP-0025/README.md`, "Procedure".

## D-021 (M4): Ken's Saturn record `k` pairs with English slot 10 record `k mod 8` (`PAIR-002`, `EXP-0026`)

The arcade's win-quote selector treats Ken (slot 10) as it treats Ryu: for
the same draw `r`, it shows Japanese record `r` and English record `r mod 8`.
Ken's Saturn records `k` and `k + 8` therefore both pair with English record
`k`. English record 8 is never chosen. All 9 English records fit 2 × 25 and
recompile byte for byte with `tools.text.caption`.

**Evidence.** In MAME, with the slot forced to 10, all 16 English draws and
4 Japanese draws (3, 8, 9 and 15) read exactly the predicted records. The
unforced control matched `EXP-0022`. At draw 9 the English bubble showed
English record 1 and the Japanese bubble showed Japanese record 9. The table
is `data/translations/ken_pairing.json` (addresses only).

Reproduce: `research/experiments/EXP-0026/README.md`, "Procedure".

## D-022 (M4): A per-slot byte in the fixed-index table selects English (`RE-006`, `EXP-0027`)

The win-quote selector's fixed-index table at WRAM-H `0x060666E0` holds one
big-endian word per slot (19 slots), with values 0-7. Only the fixed-index
path reads it (`0x06066688`, through the literal at `0x060666D8`), and arcade
play never took that path. Version 3 of the English-mode patch
(`tools.disc.english_mode.patches_v3`) uses each word's high byte as the
slot's quote language. It reads that byte in the same 11-word selector block
as version 2. Setting `0x060666E0` + 2 × slot to 2 turns English on for that
speaker; 0 leaves it Japanese.

**Evidence.**

- **Static:** in four RAM dumps, the only reference to the table is the
  literal at `0x060666D8`, loaded only at `0x06066688`.
- **Live:** a read breakpoint on the table logged nothing over 5 replays (K.O.,
  quote, select screens, fights). The same breakpoint on the neighbouring
  language table caught its reads.
- **Ken:** with v3 and Ken's English records in RAM, his table byte alone
  switched his quote. Byte 0 gave a screen identical to the unpatched game;
  byte 2 gave English record 6 at 50/50 cells.
- **Ryu:** all 16 draws were byte-identical to version 2 (`EXP-0024`).
- **Storm** (unmarked) was byte-identical to the unpatched game.

Reproduce: `research/experiments/EXP-0027/README.md`, "Procedure".

## D-023 (M4): Ryu and Ken in English from the source image (`RE-007`, `EXP-0028`)

One command builds the image from the untouched source:
`tools.disc.build_english SPEC... OUT --image DIR`, with
`data/translations/ryu_win_quotes.json` and
`data/translations/ken_win_quotes.json`. Only `MMPACK.PCA` (version 3,
slots 9 and 10), `MC09.SHP` and `MC0A.SHP` change, each at its own size.
The result is Track 01 `b5dd07c2…`. For each of their 16 Saturn draws, Ryu
and Ken show their official arcade English record `draw mod 8`. Unmarked
speakers and continue hints stay Japanese.

**Evidence.**

- **Build:** all sectors pass EDC/ECC, the layout is unchanged, and three
  builds are identical. The decoded code differs from the original only
  inside `patches_v3([9, 10])`.
- **Forced draws:** all 16 of each character's draws were steered by seed
  with the built files. Each showed the predicted record at 50/50 cells.
  Ryu's runs were byte-identical to `EXP-0024`.
- **Disc and cold boot:** picking either character from the built disc loads
  the built file. A cold boot has only slots 9 and 10 marked.
- **Play:** in the user's cold-boot play check, Ryu showed `MC09` English
  record 3 and Ken showed `MC0A` English record 7. Rogue's CPU win quote and
  the continue hint were Japanese.

Reproduce: `research/experiments/EXP-0028/README.md`, "Procedure".

## D-024 (M5): `MCxx` holds arcade win-quote slot `xx` for slots 0-17 (`RE-005`, `EXP-0029`)

Each of the 18 files `MC00.SHP`-`MC11.SHP` holds exactly one 16-record
Japanese win-quote table, equal byte for byte to arcade slot `xx` (table
`0x17E19C`). The table is followed by 4-12 of that slot's Japanese ending
records. Offsets, sizes and counts are in `data/text/slot_census.json`.
Arcade slots 0-17 have 9 English records each, except slot 8 (Apocalypse),
which has 8. Slot 18 aliases slot 11 in both languages and has no file of
its own. `MCED.SHP` holds no arcade quote or ending record.

**Evidence.**

- **Static census** of every file from the untouched track. Every stream
  decodes and ends in its last sector.
- **Load traces:** slots 9 (`EXP-0017`), 10 (`EXP-0025`) and 1 (Cyclops as
  the second member: a loader halt at `0x0600D124` with R5 = `0x8A53`,
  which is `MC01` only, at base `0x060B0000`). The Cyclops trace was
  repeated identically, and its no-input control had no event.

Reproduce: `research/experiments/EXP-0029/README.md`, "Procedure".

## D-025 (M5): Every roster slot pairs Saturn record `k` with English record `k mod 8` (`PAIR-003`, `EXP-0030`)

For all 18 slots of the M5 roster (0-17), the arcade selector shows English
record `r mod 8` and Japanese record `r` for draw `r`, from the slot's own
pointers. This holds for Apocalypse's 8-record slot too. So Saturn record `k`
of slot `s` (the census's table in `MCxx`) pairs with slot `s`'s English
record `k mod 8`, and English record 8 is never shown. The tables are in
`data/translations/<name>_pairing.json`.

All 144 shown English records recompile exactly as 2 × 25 codes, and none
uses a code with an unexpected Saturn glyph
(`data/translations/m5_english_fit.json`). Only Cammy's English records 0
and 4 name a character whose names differ between versions ("Bison").

**Evidence.** There were 360 forced MAME runs (`xmvsfu`, MAME 0.289), all
matching: 288 English (16 draws per slot) and 72 Japanese (draws 3, 8, 9 and
15). The unforced controls equal `EXP-0026`'s. Ryu's and Ken's results equal
their earlier tables.

Reproduce: `research/experiments/EXP-0030/README.md`, "Procedure".

## D-026 (M5): Every roster file fits its original size with its English records (`RE-009`, `EXP-0031`)

For each of the 18 M5 roster files (`MC00`-`MC11`), the slot's 8 official
English records are written over the start of its quote table. Re-encoded
by the build's own path (`tools.disc.build_english.build_mc`), the file
keeps its original size, its stream ends in its last sector, and it decodes
unchanged outside the 800 English bytes. The margins run from 175 bytes
(`MC08`, Apocalypse) to 1,176 bytes (`MC0B`, Chun-Li). Sizes are in
`data/text/m5_sector_fit.json`.

**Evidence.** All 18 rebuilds succeeded, and the round-trip decode matched.
Ryu's and Ken's rebuilt files equal the play-checked `EXP-0028` build. A
second run was byte-identical.

Reproduce: `research/experiments/EXP-0031/README.md`, "Procedure".

## D-027 (M5): All 18 roster characters in English from the source image (`RE-010`, `EXP-0032`)

One command builds the image from the untouched source:
`tools.disc.build_english` with the 18 specs in `data/translations/` and
`--image`. Only `MMPACK.PCA` (version 3, slots 0-17) and `MC00`-`MC11`
change, each at its own size. The result is Track 01 `36672c5d…`. For every
draw, each roster character shows its official arcade English record
`draw mod 8`. This holds as the first member, as the second member (the
WRAM-H copy) and as a CPU opponent. The continue hint stays Japanese.

**Evidence.**

- **Build:** all sectors are valid, the layout is unchanged, two builds are
  identical, and the code differs only at version-3 sites.
- **Records:** all 144 English records were drawn live, 50/50 cells as
  compiled.
- **Ryu and Ken:** byte-identical to `EXP-0028`.
- **Loads:** 16 grid characters picked from the built disc loaded as built.
- **Play:** in the user's cold-boot play check, Gouki, Cyclops (second
  member), Storm (CPU), Nash, Ken (second member, `0x060B2BDC`) and
  Apocalypse (CPU boss, `0x060C1AA0`) all showed English.

Reproduce: `research/experiments/EXP-0032/README.md`, "Procedure".

## D-028 (M5): Every confirmed build reproduces from the untouched source (`RE-011`, `EXP-0033`)

`tools.disc.regression` rebuilds the three confirmed English builds byte
for byte, checking every changed file and Track 01 against
`data/regression/references.json`:

- `EXP-0024`: Ryu, version 2, Track 01 `1034b8d7…`;
- `EXP-0028`: Ryu and Ken, `b5dd07c2…`;
- `EXP-0032`: the roster, `36672c5d…`.

The inputs are the untouched disc image and the US arcade program image.
`tools.reference.xvsf_text --program-out` now writes the program image from
the ROM set and the pinned driver source (`1b1a5a26…`).

**Evidence.** All 27 hashes matched in this working copy and in a fresh
clone with only the three inputs linked. A copy of the references with one
hash changed was reported as a mismatch.

Reproduce: `research/experiments/EXP-0033/README.md`, "Procedure".

## D-029 (M6): Nash's ending follows the partner fight and replays deterministically (`END-001`, `EXP-0034`)

On the untouched image, with Nash and Ryu, beating Apocalypse leads to a
win-quote screen and then a fight between the two team members, marked by
a `⚠乱入禁止` ("no challengers") warning at the top right. Winning it as Nash
plays Nash's ending:

- six timed pages (1, 2, 1, 2, 1 and 2 lines of Japanese);
- a picture window at the top and a purple box at the bottom;
- Latin speaker labels above the box on pages 3-6 (`Nash`, `Nazo no koe`,
  `Nash`, `Nash's friend`);
- then an English staff roll and `GAME OVER`.

Losing that fight (no input) gives `CONTINUE?` and `GAME OVER`, with no
ending.

**Evidence.** Two no-input replays from `local/checkpoints/end001/f00220064.mcs`
(after the last hit, before `K.O.`) were pixel-identical to each other at
all six pages and the first credits screen. The six page screenshots were
also identical to the session's own, whole image, text box and picture.
Which team member an ending follows in general is not settled (SUPPORTED
only; `docs/known_unknowns.md`).

Reproduce: `research/experiments/EXP-0034/README.md`, "Procedure".

## D-030 (M6): Nash's ending pages are `MC10` records 16-21, drawn by the type-4 selector and the quote renderer (`END-002`, `EXP-0035`)

- **Code:** during Nash's ending, the type-4 selector `0x060668A2` runs once
  per scene (pages 1, 3, 5, 6), and the shared renderer `0x06066948` runs
  once per page. The win, hint and type-6 selectors do not run.
- **Selector:** it reads the language word and picks a run-time list
  (language 0: `0x060854F8`; language 2: `0x06085544`). It takes the
  speaker slot's entry and keeps it at task + `0x34`.
- **Language-0 list:** holds one ending base per loaded character (Nash
  `0x0024FEC0`). The quote pointer `0x060F2490` steps 76 bytes per page.
- **Records:** the six records equal decoded `MC10.SHP` at `0x2EC0` + 76k
  (records 16-21, after the 16 win quotes).
- **Font and grid:** every drawn cell equals the `FIX.PRS` quote-font glyph
  for its code, 2 × 19 at a 16 px pitch (VDP1 x 26-314, rows 178 and 194,
  colour word `0x7020`). Zeroing one glyph's 128 bytes in VDP1 removed
  exactly that glyph.
- **The version-3 patch:** written over the code in RAM, it leaves all six
  pages pixel-identical.
- **English grid:** setting the global size and language words to 2 draws
  the ending box as 2 × 25 at 12 px. But the language-2 list is not filled
  on the Saturn (its slot-16 value `0x09EC0B8E` is not work RAM), and the
  speaker labels and pictures change too (a Latin `Charlie` label
  appeared).

Reproduce: `research/experiments/EXP-0035/README.md`, "Procedure".

## D-031 (M6): A disc edit of `MC10.SHP` reaches Nash's ending (`END-003`, `EXP-0036`)

- **Loading:** when Nash is picked first, the file loader `0x0600D124`
  (R5 = `0x5D69`, R6 = `0x0024D000`) writes all six ending records. The
  buffer equals decoded `MC10.SHP` plus the 263 `EXP-0025` fix-ups.
- ~~**No rewrite:** from the pre-boss checkpoint through the last page,
  nothing writes to the records again (write log, 0 hits).~~ **Withdrawn
  2026-10-29** (`EXP-0041`): those replays had no input, lost the boss fight
  and never reached the ending. The disc edit below was shown in play, so
  the result stands without this bullet.
- **RAM edit:** one code changed in RAM before page 3 changed exactly that
  page's first cell, to the new code's `FIX.PRS` glyph.
- **Disc edit:** an 8-byte, same-size edit at decoded `0x2EC0` (record 16)
  was built from the untouched source (`build/end003_marker`, Track 01
  `547359de…`; only `MC10`'s 12 sectors differ). In a user play-through
  to Nash's ending:
  - page 1 showed the four marker glyphs in exactly its first four cells
    (x 27-88, y 187-200);
  - pages 2-6 had text boxes byte-identical to the original game's.
- **Census:** every roster file keeps its slot's arcade Japanese ending
  block at quote table + `0x4C0`. For slots 0-16 the whole block is there
  (`data/text/ending_census.json`).

Reproduce: `research/experiments/EXP-0036/README.md`, "Procedure", and a
play-through of the marker image with Nash first.

## D-032 (M6): Arcade English for Nash's ending, and how ending records are picked (`END-004`, `EXP-0037`)

- **Route:** on `xmvsfu` (MAME 0.289), Charlie picked first reaches his
  ending with no play when the CPU side's vitality words `0xFF4610` and
  `0xFF4E10` are set to 0 every 20 frames. With `0xFF547A` and `0xFF5478`
  also set to 0 before the ending, the ending runs in Japanese.
- **Indexing:** the ending selector (PC `0x04F53C`) reads the point
  character's pointer from the English table `0x17E318` or the Japanese
  table `0x17E2CC`. Page k then reads record k (PC `0x04F612`; 100-byte or
  76-byte records). This was predicted before the logged runs. With
  partner Cyclops and with partner Ryu, the reads were identical in each
  language.
- **Pairing:** Saturn `MC10.SHP` record 16 + k (decoded `0x2EC0` + 76k)
  equals arcade Japanese slot 16 record k byte for byte. It pairs with
  arcade English slot 16 record k (`0x18D0AE` + 100k), k = 0-5. All six
  pairs were confirmed by four reads each
  (`data/translations/nash_ending_pairing.json`). English records 1 and 4
  say "Charlie".
- **The scene script depends on the language:**
  - The arcade Japanese ending matches the Saturn's: scenes start at pages
    1, 3, 5 and 6, with the labels `Nash`, `Nazo no koe`, `Nash` and
    `Nash's friend`.
  - The English ending starts scenes at pages 1, 2, 4 and 5, shows other
    pictures, and labels page 4 `Charlie` and page 5 `Charlie's friend`.

Reproduce: `research/experiments/EXP-0037/README.md`, "Procedure".

## D-033 (M7): The Saturn has the arcade's English ending script for Nash (`END-005`, `EXP-0038`)

- **Where:** `MCED.SHP` is the ending overlay, at `0x060D2000` with
  `+0x060D2040` relocations.
- **The routine** `0x060D4710`:
  - takes the ending slot's script from a 19-entry table (`0x060D46C4`);
  - reads the language word to pick the Japanese (header word 0) or
    English (header word 2) script;
  - reads each scene's entries: page length, record index and label index.
- **Labels:** a label index points into a 40-entry, 16-bit ASCII list at
  decoded `MCED` `0x3DA8`. It holds the roster names, `Bison`, `Akuma`,
  `Charlie`, `Nazo no koe`, `Nash's friend`, `Charlie's friend` and others.
  The labels are read from it when drawn: a one-letter RAM edit (`Nash` →
  `Xash`) changed only that letter on screen.
- **Nash's two scripts:**
  - Japanese: scenes of records 0-1, 2-3, 4, 5; labels `Nash`, `Nazo no
    koe`, `Nash`, `Nash's friend`.
  - English: scenes of records 0, 1-2, 3, 4-5; `0x180`-frame pages; labels
    `Charlie` and `Charlie's friend`.
- **Trial** (RAM only, global words left at 0): the script reader, the
  type-4 selector and the renderer's grid reads return 2, and the
  selector's language-2 list points at the six arcade English records in
  free RAM. The Saturn then shows the arcade English ending, matching
  `EXP-0037`'s arcade snapshots in pictures, labels and text, page for page.
  Every drawn cell equals its `FIX.PRS` glyph in the 2 × 25 grid.

Reproduce: `research/experiments/EXP-0038/README.md`, "Procedure".

## D-034 (M7): Version 4 turns on English endings per slot (`END-006`, `EXP-0040`)

- **The selector rewrite:** a same-size rewrite of the type-4 selector
  (`0x060668C2`-`0x060668EF`, literals at `0x0606690C`). The selector always
  takes the slot's language-0 ending pointer. If bit 7 of the slot's
  fixed-table low byte is set, it subtracts `0x1A0`, landing at quote table
  + 800, after the 8 English win quotes, and sets the task's English flag.
- **The data change:** Nash's `MCED` script header word (`0x2CF0`) set to
  his English script's offset.
- **Results** (RAM trials from Nash's pre-K.O. checkpoint):
  - unmarked: pixel-identical to the untouched game at all 91 frames;
  - marked, with the records at table + 800: identical to the `EXP-0038`
    English ending at 90 of 91 frames (one fade frame differs in the
    picture window only).
- **Win quotes:** Ryu's 8 English draws are unchanged, even with his own
  slot marked.
- **Fit:** `MMPACK.PCA` and `MCED.SHP` fit their sectors.
- **Tools:** `patches_v4`, `ending_slot_patches` and `mced_english_scripts`
  in `tools/disc/english_mode.py`.

Reproduce: `research/experiments/EXP-0040/README.md`, "Procedure".

## D-035 (M7): Nash's English ending records sit after his English win quotes, and the build shows them (`END-007`, `EXP-0041`)

- **Placement:** `MC10.SHP` holds the 800 English win-quote bytes then the
  600 English ending bytes at decoded `0x2A00`, and fits its 12 sectors
  with 814 bytes to spare. Built with `tools.disc.build_english --patch-version 4`
  and `data/translations/nash_ending.json`, together with version 4 in
  `MMPACK.PCA` and Nash's `MCED` script header (`build/m7_nash_ending`,
  Track 01 `2abe9771…`).
- **No-play route:** picked from the select checkpoint, with the build's
  code in RAM and the CPU side's vitality (`0x060F4610`, `0x060F4E10`) set
  to 0 every 20 frames.
- **What the route showed:**
  - after the pick, `MC10` loads exactly (file + 263 fix-ups);
  - the bytes after the win quotes are read only by the ending renderer
    while it shows them (one read just past page 6, with no effect on
    screen);
  - the six pages are byte-identical to the English layout chosen in
    `LAYOUT-002`.
- **Loading:** `MCED` is loaded with the boss stage.

Reproduce: `research/experiments/EXP-0041/README.md`, "Procedure".

## D-036 (M7): Nash's ending in English, from a built image, in play (`END-008`, `EXP-0042`)

`build/m7_nash_ending` (Track 01 `2abe9771…`) was booted cold and played by
the user to Nash's ending (Nash first, Ryu partner).

- **Ending:** all six pages have session screenshots byte-identical to the
  layout the user chose (`LAYOUT-002`, `EXP-0038`, `EXP-0041`). That is
  official arcade English, the Saturn's English scene breaks and pictures,
  and the labels `Charlie` and `Charlie's friend`.
- **Win quotes:** all seven in the session were English, including the
  second member's and the one after Apocalypse.

Reproduce: `research/experiments/EXP-0042/README.md`, "Procedure".

## D-037 (M7): The Nash-ending build reproduces from the untouched source (`END-009`)

`data/regression/references.json` now holds `nash_ending_v4` (`EXP-0041`,
play-checked in `EXP-0042`):

- the 18 win-quote specs plus `data/translations/nash_ending.json`;
- patch version 4;
- 20 file hashes, including `MCED.SHP` `cca9332d…`, `MC10.SHP` `d97633a6…`
  and `MMPACK.PCA` `276d534c…`;
- Track 01 `2abe9771…`.

`tools.disc.regression` rebuilt all four references from the untouched image
and matched all 48 hashes (`docs/regression_report.md`, run at `f2ed18a`).

Reproduce: `./invenv.sh python -m tools.disc.regression`.

## D-038 (M8): Every roster slot has an English ending script that fits (`END-010`, `EXP-0043`)

- **Scripts:** every roster slot 0-17 has an English script in `MCED.SHP`.
  Each shows its arcade English ending records 0 to n − 1, once each, in
  order, under its own scene breaks and labels. The Japanese scripts show
  each file's Japanese records in order, except slot 8.
- **Aliases explained:**
  - Slots 8 and 9 share Ryu's script (labels Cyclops and Ryu), and the
    arcade English pointer for slot 8 equals Ryu's.
  - Slots 11 and 18 share Chun-Li's script and pointers.
- **Space:** each file's English ending (100 × the arcade English count)
  fits after its English win quotes. The free space ranges from 720 to
  1,328 bytes, and lazy re-encoding leaves 259 to 1,293 bytes per file.
- **Labels:** the English labels include `Akuma` (Gouki), `Charlie` and
  `Charlie's friend` (Nash), `Bison` (Rogue) and `Vega` (Magneto).

Output: `data/text/ending_script_census.json`. Reproduce:
`research/experiments/EXP-0043/README.md`, "Procedure".

## D-039 (M8): Every roster ending pairs page k with record k, and the arcade's scene breaks equal the Saturn scripts' (`END-012`, `EXP-0044`)

38 no-play MAME runs on `xmvsfu` met every prediction committed before
them. They covered all 17 M8 roster characters (Gouki by forcing his pick)
in English and Japanese, plus a second partner for Wolverine and Chun-Li:

- the ending selector reads the point character's table entry;
- page k reads record k (100-byte English or 76-byte Japanese), k = 0 to
  n − 1;
- the table is re-read exactly where the character's Saturn `MCED` script
  of that language starts a scene;
- the partner changes nothing.

Every Saturn Japanese ending record equals its arcade record. Pairing files:
`data/translations/<name>_ending_pairing.json`. Names for the gate:
"Bison" in Vega's English records 1 and 4, and the labels `Akuma`, `Bison`
and `Vega` (Magneto's page 3, as the arcade shows).

Reproduce: `research/experiments/EXP-0044/README.md`, "Procedure".

## D-040 (M8): The ending is the first pick's, and a route reaches any roster ending (`END-013`, `EXP-0045`)

- **The fighter blocks:** the four blocks are at `0x060F4200`/`4A00` (the
  player's side; `4200` is the active fighter) and `0x060F4600`/`4E00`
  (the CPU's side). Each holds its character at + `0x23` (slot × 2) and
  vitality at + `0x10`. This is the arcade's `0xFF4xxx` layout.
- **The route tool:** `tools.mednafen.route` picks any grid character first
  or second from the select checkpoint (Gouki from a state where he is
  already the first pick). It checks that both members' files load, and
  sets vitality to win or lose fights with no play.
- **Whose ending** (two teams plus Gouki's, untouched image):
  - the partner fight always puts the first pick on the player's side;
  - if the player wins it, the first pick's ending plays, from the first
    member's buffer;
  - if the partner wins it, the partner's win quote is read from the second
    member's buffer (WRAM-H `0x060B0000` + its table), then the continue
    screen, with no ending.
- **No second pick's ending was reached.** Knocking out the first pick at
  the boss loses the match, and a sent tag (Z + C) did not take effect.

Reproduce: `research/experiments/EXP-0045/README.md`, "Procedure".

## D-041 (M8): Every roster ending is built and loads from the disc (`END-014`, `EXP-0046`)

- **The build:** `build/m8_roster_endings` (Track 01 `7bb8ab82…`),
  from the untouched source with `tools.disc.build_english` version 4.
  - The inputs are the 18 roster win-quote specs and 17 ending specs
    (`data/translations/<name>_ending.json`).
  - It is reproducible, and all 71,908 sectors pass EDC/ECC.
  - Each roster MC file changes only at its quote table: 8 English win
    quotes, then the n arcade English ending records.
  - `MCED.SHP` changes only in 17 script header words. Ryu's script is
    switched with Apocalypse's, and Chun-Li's with slot 18's, by explicit
    permission (`mced_shared_with`).
  - `MMPACK.PCA` has exactly `patches_v4` (48).
  - The smallest compressed margin is 494 bytes (`MC0E`).
- **Load:** every roster character's built file loads from the disc into
  both team buffers, equal to the file plus fix-ups. Gouki is picked from
  his cell.
- **Rogue:** the game writes into four `9999 9999` longs of Rogue's loaded
  `MC03` (decoded `0x9332`, `0xA446`, `0xB018`, `0xBDE4`) after loading,
  on the untouched image too.
- **Select cursor:**
  - the second cursor skips the first pick's cell, and starts on Wolverine
    when Cyclops is the first pick;
  - Gouki's cell is reached by "u" from Juggernaut (route select state).

Reproduce: `research/experiments/EXP-0046/README.md`, "Procedure".

## D-042 (M8): Every roster ending shows in English, first or second pick (`END-015`, `EXP-0047`)

- **Pages:** on `build/m8_roster_endings`, the route reaches all 17
  roster endings (Gouki picked from his cell). Every page (112) matches
  the arcade's English page in picture, label, text, line breaks and
  scene breaks. Nash's pages are byte-identical to M7's.
- **Reads:** the English ending bytes are read only by the renderer
  (`0x06066A84`) during the ending. The one exception is a read in the
  20 frames when a win quote showing English record 7 begins: the
  renderer reads once past the record. Ryu's and Ken's 16 forced draws
  on the M8 code and files are byte-identical to M5's, record 7
  included.
- **Play:** booted cold and played by the user, Cammy's ending and Ryu's
  ending as the second pick match the route's screens.
- **Second pick:** Ryu's ending was read from the second member's buffer
  (WRAM-H `0x060B0000`) + his quote table + 800 + 100k, version 4's rule
  for a second pick. Ryu got the player's side of the partner fight
  after tags (Z + C by hand) during the stages and the boss fight.

Reproduce: `research/experiments/EXP-0047/README.md`, "Procedure".

## D-043 (M8): The M8 build reproduces from the untouched source, and its coverage is registered (`END-016`)

`data/regression/references.json` now holds `roster_endings_v4`
(`EXP-0046`, verified in `EXP-0047`):

- the 18 win-quote specs plus the 17 roster ending specs;
- patch version 4;
- 20 file hashes, including `MCED.SHP` `b37c3a64…` and `MMPACK.PCA`
  `36179171…`;
- Track 01 `7bb8ab82…`.

`tools.disc.regression` rebuilt all five references from the untouched
image and matched all 69 hashes (`docs/regression_report.md`, run at
`acad50a`). `nash_ending_v4` still matches. Its spec gained a description
and two size fields in `END-014`, and its records are unchanged.

`docs/coverage_exceptions.md` ("M8 coverage register") lists the ending
text M8 leaves Japanese or does not show, and why:

- slot 8's ending records;
- slot 18;
- the tails of the old Japanese endings;
- the unused Japanese scripts;
- second-pick endings other than Ryu's;
- Gouki's unlock;
- the boss-stage text and the warning.

Reproduce: `./invenv.sh python -m tools.disc.regression`.

## D-044 (Names): The Saturn's name art follows the Japanese convention on every surface (`LOC-001`, `EXP-0048`)

- **Saturn art:** on the M8 build, the select label, VS screen, life bar
  and win banner show `VEGA`, `GOUKI` and `NASH`, as the Japanese arcade
  (`xmvsfjr2`) does. The US arcade (`xmvsfu`) shows `BISON`, `AKUMA` and
  `CHARLIE` on the same surfaces.
- **The M8 build is mixed:** its English text and ending labels are
  American (from the arcade English), while its art is in the Saturn
  convention.
- **Boss-stage boxes:** the Saturn's Japanese pre-Apocalypse boxes name
  the player's character in katakana (ベガ, ゴウキ, ナッシュ).
- **No names:** stage cards, the staff roll, initials entry, the rankings
  (default entries), attract mode, the title menu and Option Mode name no
  character.
- **Arcade:** Gouki has a reachable cell on the arcade grid in both sets.

Reproduce: `research/experiments/EXP-0048/README.md` and
`research/experiments/EXP-0048/arcade/RESULTS.md`.

## D-045 (Names): Every name surface's art is on the disc in both conventions (`LOC-002`, `EXP-0049`)

- **Life bar:** cells of **`FIX.PRS`**, which is loaded raw at WRAM-L
  `0x002C3EA0`.
  - Decoded by `0x06024CF0` (cell index R3; base at `0x0602586C`; block
    table at + 16; size/type bytes at + `0x390`) and sent to VDP1 by SCU
    DMA (`0x06024010`).
  - The player's set (`0x0880`-`0x08CF`) and the CPU's set
    (`0x0822`-`0x087F`) both hold BISON and AKUMA. CHARLIE is at
    `0x03C8`-`0x03CF`.
- **Select label:** **`VS00.PRS`** frames `0x96`-`0xA7` (slots 0-17), plus
  BISON `0xA8`, AKUMA `0xA9` and CHARLIE `0xAA`. `VS00.PRS` is loaded raw
  at WRAM-L `0x002F7030`. Its frame table is at + 16, 6 bytes a frame;
  the frames are unpacked by a second decoder (`0x060252BA`).
- **VS-screen name and win banner:** spelled from two `VS00.PRS` letter
  fonts, one cell (N = `0x7E`) and 2 × 2 cells (N = `0xBD`). Every letter
  the American names need is there.
- **Controlled changes** (patches to the RAM copies):
  - the life bar showed AKUMA and CHARL…;
  - the select label showed BISON, AKUMA and CHARLIE;
  - the VS name and the banner showed HASH.
- **No `Balrog`:** no file holds a `Balrog` label or text.

Reproduce: `research/experiments/EXP-0049/README.md`.

## D-046 (Names): The name calls, their table and the American calls (`LOC-003`, `EXP-0050`)

- **When:** the Saturn calls the character's name when they are picked and
  on the win screen.
- **The clips:** they are ADPCM clips in the 113-clip bank that
  `INITDATA.PCA` part 5 puts in sound RAM at `0x5C00`:
  - a u32 count;
  - (u16 ID, u16 length, u32 offset) entries;
  - the data from `0x5F8C`.

  The SH-2 mixer (16 channel records at WRAM-H `0x0601776C`) decodes them
  with MSHvSF's algorithm (the same multiplier table, at `0x060168F4`).
  Replaying each active channel reproduced the stored step and predictor
  in 102 of 102 records.
- **The choice:** the call ID is the first word of table A, 12-byte
  records indexed by slot, in `MMPACK.PCA` (decoded `0x79EE`, WRAM-H
  `0x0601B9EE`). Vega `0x121`, Gouki `0x01D`, Nash `0x149`. Changing
  entry 14 or 16 changed the call at the pick and at the win.
- **American calls:** on the disc already, identified by the user from
  single clips:
  - "Bison" `0x147` (table entry 18, slot 18's call);
  - "Akuma" `0x021` (entry 19);
  - "Charlie" `0x01B` (entry 20).

Reproduce: `research/experiments/EXP-0050/README.md`.

## D-047 (Names): A region word picks every name surface; the American variant reads it as US at 10 sites (`LOC-005`, `EXP-0051`)

- **The word:** R11 + `0xD478`, WRAM-H **`0x060F5478`** (the arcade's
  `0xFF5478`; D-018's size word). The Saturn keeps it at 0. Set to 2 in
  RAM, the select label, VS screen, life bar and win banner all showed
  the American names.
- **The lists:** each name surface takes slot × 2 into a 19-word Japanese
  list, or into the American list 38 bytes after it when the word is
  non-zero:
  - life bar: `0x06080F00` (CPU side) and `0x06080F4C` (player side) cell
    codes (cell + `0x5400`), widths from `0x06080F98`; CHARLIE is cell
    `0x03C8` or `0x03CC`, 4 cells wide;
  - select label `0x06084720`/`0x06084746`, VS screen
    `0x060845D8`/`0x060845FE`, banner `0x0606E348`/`0x0606E36E`;
  - name call `0x0604FBFC`/`0x0604FC22`: requests `0xA0` + slot, and
    `0xB2`-`0xB4` (table A entries 18-20: "Bison", "Akuma", "Charlie")
    for slots 14-16.
- **The sites:** the 10 reads of the word that choose those lists
  (`tools/disc/names.py`; a static scan found 45 readers in `MMPACK.PCA`,
  the rest choose no per-character list). Each `00BD` changed to `E002`
  (`mov #2,r0`), with the word left at 0, gave American names on every
  surface and the American calls, in RAM and from a cold boot of the
  built image.
- **The build:** `tools.disc.build_english --names us` (the default). The
  decoded `MMPACK.PCA` differs from the M8 build's in exactly those 20
  bytes.

Reproduce: `research/experiments/EXP-0051/README.md`.

## D-048 (Names): The Saturn-names variant; ending label entry 9 is unused (`LOC-006`, `EXP-0052`)

- **Label list:** `MCED.SHP`'s 40-entry list (decoded `0x3DA8`, RAM
  `0x060D5DA8`) has one reader, `0x060D5CF8`, indexed by the label byte of
  the script page. Entry 9 (`Apocalypse`) is used by no script of any
  slot in any language.
- **The variant:** `build_english --names saturn` writes the approved name
  edits (`data/translations/saturn_names.json`): six recompiled official
  records, five label switches in the English ending scripts, and
  `Balrog` in entry 9. It changes no code; `MMPACK.PCA` equals the M8
  build's.
- **Shown on the built image:** Cammy's forced quotes 0 and 4 and the
  routed endings of Rogue, Magneto, Vega, Gouki and Nash read with the
  Saturn names and labels as approved. Against the American build, only
  the edited records, the label bytes, entry 9 and the 10 American name
  sites differ.

Reproduce: `research/experiments/EXP-0052/README.md`.

## D-049 (Boot): The boot check and its five warning pictures (`BOOT-001`, `EXP-0053`)

- **The check:** `CPK.PCA` (decoded at WRAM-H `0x06022000`) loads `CPK.EMM`
  into `0x06080000` and runs a cart test and a backup-memory test
  (`0x060228D4`). A failure loads `ERRn.BIN` (names at `0x06023D74`, 16
  bytes each) into `0x06080000` and draws it (`0x060221E0`).
- **Conditions and pictures,** shown in Mednafen and identified by the
  bitmap in RAM:
  - no cart, or a backup cart: `ERR4.BIN` (cart test −2), then the BIOS;
  - unformatted backup memory: `ERR1.BIN` (backup test −1), then the BIOS;
  - a damaged save: `ERR2.BIN` (−3), then the game;
  - 18 blocks or fewer free: `ERR3.BIN` (−2), then the game.
- **`ERR5.BIN`** (cart test −1): an unsteady cart ID or a 1 MB cart failing
  its RAM test, from `CPK.EMM`'s code; not produced in Mednafen.
- **No warning:** a 1 MB cart, and the 16 MiB CS1 RAM (which then hangs on
  "NOW LOADING").
- **Not MSHvSF's mapping:** there the no-cart picture was `ERR5` and a 1 MB
  cart gave `ERR4`.

Reproduce: `research/experiments/EXP-0053/README.md`.

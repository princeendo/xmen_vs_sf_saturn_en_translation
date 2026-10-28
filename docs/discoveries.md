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
`ebfbb7da…e662`. Source hashes were unchanged.

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

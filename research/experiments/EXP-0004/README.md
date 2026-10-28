# EXP-0004: Stock Debugger Dumps, a Memory Write, and a Write Breakpoint

Task: EMU-007
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0003` drove Mednafen hotkeys unattended. The stock 1.32.1 debugger is
keyboard-only: Alt+A frame advance, Alt+D debugger, Alt+3 memory editor
(`.`/`,` change address space, `d` dump, `l` load), and in the CPU view
Shift+W write breakpoints (`src/drivers/debugger.cpp`, `memdebugger.cpp`).

## Hypothesis

Driven by `tools/mednafen/hotkeys.py`, the stock debugger can (1) dump WRAM-L
and WRAM-H at a frozen instant, repeatably; (2) write a prepared file into
WRAM-H and restore it; (3) halt the CPU on a write breakpoint.

## Controlled Change

No change to binary, BIOS, configuration or source. Input only, in the silent
home with `sav/` emptied before each run. Memory was written only while
frozen and was restored before any frame ran.

## Prediction

- Two dumps of each work RAM taken during one freeze are byte-identical,
  1,048,576 bytes each.
- After `l` of a 16-byte pattern, a dump of the same range equals the
  pattern; after `l` of the saved original, it equals the original.
- With a write breakpoint on WRAM-H the game stops: window captures taken
  seconds apart are identical, and the CPU view shows a store instruction.

## Inputs and Provenance

As `EXP-0001`: source `local/disc_images/xmvsf_saturn_jp_3m/` (42
components), BIOS `sega_101.bin` (`dcfef4b9…deac`), stock 1.32.1 binary
(`892bb60a…29dd`), home `local/mednafen_quiet/` (`aad9a7ef…57cf`, unchanged
after all runs). Pattern file `research/memory_dumps/emu007/w-pattern.bin`:
the 16 ASCII bytes `EMU-007 WRITE OK`.

## Tools and Environment

`tools/mednafen/hotkeys.py`, extended for this experiment:

- `option+X` chords are posted as CoreGraphics keyboard events with the
  left-Option device flag (`0x80020`) through JavaScript for Automation. The
  debugger's view switch tests SDL's `KMOD_LALT`; System Events'
  `using option down` passed Mednafen's own Alt hotkeys (A, D) but not that
  test.
- `window=FILE` captures Mednafen's window alone with `screencapture -o -l
  <window id>`. Mednafen's own screenshots (F9, Shift+F9) do not include the
  debugger overlay. When the first capture ran, macOS showed the user a
  dialog: "Claude" is requesting to bypass the system private window picker
  and directly access your screen and audio. Captures worked; the agent did
  not answer the dialog.
- `--keep-focus` keeps Mednafen frontmost for the run; `type=` sends text one
  character at a time.

## Procedure

Step files are in [`steps/`](steps/) (copies of the ignored
`local/emu007/run-*.steps`; outputs go to ignored paths). Each run:

```bash
find local/mednafen_quiet/sav -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/emu007/run-X.log --script local/emu007/run-X.steps --keep-focus
```

- Run A (70 s, title): `option+a`, `F5`, `option+d`, `option+3`, `period`
  (Low Work RAM), two `d` dumps `00000000 000fffff …/wraml-N.bin`; `period`
  (High Work RAM), two dumps `wramh-N.bin`; then on `000f0000 000f000f`:
  `d` before, `l` pattern, `d` after, `l` before, `d` revert.
- Run B: freeze, editor on High Work RAM, `option+d` (hide), `option+r`
  (resume), `option+d`, two dumps while running.
- Runs C/D: write breakpoint `06007058-0600705b 26007058-2600705b` (see
  Uncertainty).
- Run F: captures at 70 s and 72 s; `option+d`, `shift+w`, type
  `06000000-060fffff 26000000-260fffff`, `return`, `option+d`; captures at
  80 s and 84 s; `option+d`; captures at 86 s and 88 s.

## Actual Result

All runs exited 0 (F12). Source manifests identical before and after.

Dumps (ignored `research/memory_dumps/emu007/`):

| File | Size | SHA-256 |
| --- | ---: | --- |
| `wraml-1.bin`, `wraml-2.bin` | 1,048,576 | `e55529cf…bf94` (both) |
| `wramh-1.bin`, `wramh-2.bin` | 1,048,576 | `a384c0ef…6702` (both) |
| `w-before.bin`, `w-revert.bin` | 16 | `2059ac10…f8a8` (both) |
| `w-pattern.bin`, `w-after.bin` | 16 | `b0771fd5…a3fe` (both) |
| run B `wramh-run-1.bin` / `-2.bin` | 1,048,576 | `8d107906…7010` / `4da1c39e…afe3` |

- WRAM-L and WRAM-H differ; WRAM-H begins `06 01 40 10 06 00 18 00`, as the
  editor showed (capture `a2`).
- Write test at WRAM-H offset `0xF0000`: before
  `66666790000000006666669000000000`, after = the pattern, after revert = the
  original.
- State saved during the run A freeze (`F5`; capture shows "State 0
  saved."): `local/emu007/run-a-state/X-Men vs. Street Fighter (Japan)
  (3M).cead02d9d3cc1b97c82dbf063fba19bf.mc0`, 3,499,031 bytes,
  `62837cf2…fc3f`. It and the four work-RAM dumps are the same instant, for
  `DBG-001`.
- Run A's first `option+r` (debugger visible) did not resume: its running
  dumps equalled the frozen ones. Run B (hide, then `option+r`) resumed: the
  two running dumps differ in 434,184 bytes.
- Run F: captures at 70 s and 72 s differ (running title). After the
  breakpoint, captures at 80 s and 84 s are identical (black window), and
  with the debugger shown, captures at 86 s and 88 s are identical
  (`d746b7f9…`). The CPU view shows PC `06021B26`, highlighted `mov.b
  r0,@r9`, R9 `060C9047`, R0 `00000042` (read from the capture's small font;
  a digit may be misread). R9 lies in the watched WRAM-H range.

## Conclusion

**CONFIRMED.** Unattended, the stock debugger dumps WRAM-L and WRAM-H
repeatably at a frozen instant, writes and restores WRAM-H bytes exactly, and
halts on a write breakpoint at a byte store into WRAM-H.

## Uncertainty and Alternatives

- Breakpoint on the WRAM-H frame counter `0x06007058` (it rose about 60 per
  second between run B dumps) did not halt the game in runs C and D. Stock
  1.32.1 checks write breakpoints only for the debugger's active CPU
  (`src/ss/debug.inc`, `DBG_CPUHandler`). The counter may be written by the
  slave SH-2 or by DMA: **HYPOTHESIS**, untested.
- The editor's "Low/High Work RAM" offsets `0x00000-0xFFFFF` are taken to be
  bus `0x00200000-0x002FFFFF` and `0x06000000-0x060FFFFF` by name; the
  breakpoint store target `060C9047` is consistent but does not prove the
  offset mapping.
- After the breakpoint fired and the debugger was hidden, the window was
  black until the debugger was shown again.
- Earlier attempts failed because `option+3` was not delivered as left Alt:
  the CPU view stayed active, so `l` in typed paths opened its "Trace
  Log(filename end_pc)" prompt and the rest of the path became a trace-log
  filename ("Error opening file "ocal/…" for writing"). Window captures
  showed this.
- Screen-area captures in run D picked up another app's window when focus
  moved. The agent deleted them on noticing; their content is not recorded.
  Capture now uses Mednafen's window ID only.

## Reproduction

Use the procedure with `--script research/experiments/EXP-0004/steps/run-X.steps`
(delete earlier outputs first; `type=` dumps overwrite, captures need
Screen Recording). Expect repeat dumps within run A to match, the write test
to read back the pattern and then the original, and run F to show a halted
CPU view at a store into WRAM-H. Whether run A's dump hashes repeat across
cold boots was not tested.

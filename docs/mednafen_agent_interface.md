# Mednafen Agent Interface: Why Stock Is Not Enough (`EMU-020`)

`AGENTS.md` rule 16 allows reusing the MSHvSF frontend-only agent-interface
patch once stock Mednafen boots XvSF (`EMU-004`, done) and this record says
why stock is insufficient, citing the MSHvSF evidence. The user chose reuse
on 2026-10-27 (`DOC-002`, "Yes, reuse it (Recommended)").

## MSHvSF Evidence

- MSHvSF `EMU-012` (2026-10-17): stock 1.32.1 was sufficient for manual work
  and insufficient for agent-driven experiments (`SUPPORTED`).
- MSHvSF `EMU-020` (`docs/mednafen_agent_interface.md` there): every memory
  and debugger action needed hand-typed prompts, relayed screenshots, and
  beating the game's timing; `-remote` changes settings only. It rejected GUI
  automation because it needed Accessibility and Screen Recording, prompt
  typing was timing-fragile, and registers would need OCR. The user
  authorized the patch on 2026-10-17.

## XvSF Evidence: Stock Driven by GUI Automation

Unlike MSHvSF, this project tried the GUI-automation route on XvSF with
stock 1.32.1 (`tools/mednafen/hotkeys.py`, `EXP-0003`, `EXP-0004`). It works
for M0 checks, and its limits are now observed, not assumed:

| Need | Stock + GUI automation on XvSF | Observed limit |
| --- | --- | --- |
| Read memory | Memory-editor `d` dumps (`EXP-0004`) | About 1 s per key plus typing; works only while Mednafen is frontmost; the address spaces have offsets, not bus addresses. |
| Write memory | `l` loads from a file (`EXP-0004`) | As above; the prompt reports errors only on screen. |
| Breakpoints | CPU-view `shift+w` (`EXP-0004`) | A hit halts until a key is pressed; no log-and-continue; checked only for the active CPU. |
| Registers at a hit | Read from a window capture (`EXP-0004`) | Read by eye from a small font; "a digit may be misread". No machine-readable registers. |
| States | `F5`/`F7` slots (`EXP-0003`) | Slot-named files; no explicit path. |
| Screenshots | `F9` counter-named; overlay only by window capture | Window capture needs Screen Recording. |
| Act right after a hit | Not attempted | Key latency (about 1 s) cannot act within one frame. |

Costs observed on XvSF:

- **Permissions.** Accessibility had to be granted to the Claude Code bundle
  (`~/Library/Application Support/Claude/claude-code/2.1.304/…/claude.app`),
  a versioned path, after a first grant to Claude.app did not apply
  (`EXP-0003`). Window capture raised a macOS screen-access dialog for the
  user (`EXP-0004`).
- **Focus and privacy.** Every key takes focus from the user's app. In
  `EXP-0004` run D, focus moved mid-run and screen-area captures showed
  another app's window; they were deleted and capture now uses the window ID.
- **Fragility.** A modifier-side detail (left vs generic Option) silently sent
  keys to the wrong debugger view for six runs, and was found only by
  capturing the screen (`EXP-0004`).

## Conclusion

The same limits MSHvSF found apply to XvSF: stock Mednafen has no programmatic
interface for memory, breakpoints, registers, halts or states. GUI automation
reaches some of them but is slow, takes the user's focus, depends on two
macOS grants to a versioned path, and gives registers only by eye.
Agent-driven M1+ experiments (forcing, breakpoint logs, act-after-hit) need
the interface. Proceed with `EMU-021`: reuse the MSHvSF patch unchanged and
re-run validations V1-V4 on XvSF before using it as evidence.

## Patch To Reuse (provenance, `EMU-021`)

- Upstream: Mednafen 1.32.1, `mednafen-1.32.1.tar.xz`, SHA-256
  `de7eb94a…3832` (this repository's archive matches, `EMU-001`), GPL-2.0.
- MSHvSF `vendor/mednafen/patches/0001-agent-interface.patch`, SHA-256
  `c30146efab0cb60bfb7a4465bc95d9935c63c0d7bf172b02f886b4ae2cff5244`, added in
  MSHvSF commit `b9a6593`. Frontend only (`src/drivers/agent.inc`,
  `debugger.cpp`, `debugger.h`, `main.cpp`); active only when
  `MEDNAFEN_AGENT_DIR` is set.
- Workflow: copy the patch here with its provenance, apply it to a separate
  copy of the stock source (`vendor/mednafen/src-agent/`), build in
  `vendor/mednafen/build-agent/` with the `EMU-001` options, keep the stock
  tree and binary unchanged, and copy `tools/mednafen/agent.py` and its tests
  with provenance.
- Validations to repeat on XvSF (MSHvSF V1-V4): stock equivalence and smoke
  commands; `read` equals a validated extraction of a state saved in the same
  poll; write, read back and restore with halt control; a breakpoint log of a
  real transition. V4 needs an XvSF target of its own.

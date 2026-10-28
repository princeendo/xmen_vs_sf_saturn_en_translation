# Dependency-Controlled Research Plan

This is an evidence gate, not a generic backlog. `AGENTS.md` is authoritative.
Statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and `REJECTED`.
At most one reverse-engineering experiment may be `IN_PROGRESS`.

The task order follows the consolidated checklist in
`docs/playbook_from_mshvsf.md`. Task IDs are this project's own; where a task
repeats an MSHvSF task, the note names the MSHvSF task for its method only.

## Current State

- **2026-10-27: repository set up** (`SESSION-0001`). Phase A is done: the
  Python project, rules, ignore list, and the identity of the Saturn source
  image (`ENV-006`, `references/saturn_jp/README.md`).
- Reverse-engineering experiments in progress: none.
- **2026-10-27: policy confirmed** (`DOC-002`, `docs/localization_policy.md`):
  official arcade English, opt-in grammar fixes, recorded new translations
  for gaps, two name variants, all special surfaces in
  eventual scope, xdelta and SSP released only after the open tasks.
- **2026-10-28:** playbook re-copied from MSHvSF `69c666c` (through MSHvSF
  release 0.1.0). The user made American names the XvSF default, like MSHvSF
  (`docs/localization_policy.md`).
- **2026-10-28** (`SESSION-0005`): stock Mednafen 1.32.1 built (`EMU-001`,
  `docs/mednafen.md`); arcade sets identified and the US set booted in MAME
  0.289 (`REF-001`, `references/arcade/`); PS1 images recorded (`REF-002`,
  `references/ps1/`).
- **2026-10-28** (`SESSION-0006`): project-local Mednafen homes (interactive
  and silent) pinned by `tools/mednafen/home.py`; Saturn BIOS hashes match
  Mednafen's documentation (`EMU-002`, `docs/mednafen.md`).
- **2026-10-28** (`SESSION-0007`, `EXP-0001`): three unattended cold boots
  reach the title screen identically (`EMU-003`, `docs/discoveries.md` D-001).
- **2026-10-28** (`SESSION-0008`, `EXP-0002`): the 4 MiB cart is required;
  forced `extram4` equals `auto`, and no cart stops on a warning (`EMU-004`,
  D-002).
- **2026-10-28** (`SESSION-0009`): MSHvSF pad bindings copied to both
  homes; the user's in-game check passed (`EMU-005`).
- **2026-10-28** (`SESSION-0010`, `EXP-0003`): screenshots and save/load
  states work by hotkey, sent unattended through System Events (`EMU-006`,
  D-003).
- **2026-10-28** (`SESSION-0011`, `EXP-0004`): stock debugger dumps, a
  memory write, and a write breakpoint, all unattended (`EMU-007`, D-004).
- **2026-10-28** (`SESSION-0012`): `EMU-020` recorded
  (`docs/mednafen_agent_interface.md`). `SESSION-0013` / `EXP-0005`: the
  state extractor matches debugger dumps for WRAM-L, WRAM-H, VDP1 and VDP2
  VRAM (`DBG-001`, D-005); cart RAM stays HYPOTHESIS.
- **2026-10-28** (`SESSION-0014`, `EXP-0006`): the MSHvSF agent interface is
  rebuilt and validated on XvSF, V1-V4 (`EMU-021`, D-006). The agent can now
  read, write, halt and log breakpoints without GUI automation.
- **2026-10-28** (`SESSION-0015`, `EXP-0007`): one recorded play session;
  Japanese text on attract captions, win quotes and continue hints
  (`REF-005`, `docs/text_surfaces.md`). US arcade attract captions are
  English.
- **2026-10-28** (`SESSION-0016`, `EXP-0008`): arcade English located and
  decoded: 161 win-quote, 109 ending and 23 hint records in the shared ROM,
  same in every held set (`REF-003`, D-007). MSHvSF's arcade map is
  disproven for XvSF.
- **2026-10-28** (`SESSION-0017`, `EXP-0009`): the US arcade draws the
  decoded win quote and hints exactly; work RAM `0xFF8BB4` selects the
  win-quote slot (`REF-004`, D-008).
- **2026-10-28** (`SESSION-0018`, `EXP-0010`): the US PS1 holds the arcade
  English win quotes and endings byte-identically, plus a 7-record PS1 hint
  variant (`REF-006`, D-009).
- **2026-10-28** (`SESSION-0019`, `EXP-0011`): names inventoried
  (`docs/names.md`): Saturn GOUKI vs US arcade AKUMA (art), Saturn NASH vs
  English Charlie, English Bison; Saturn Bison/Vega and voice unknown
  (`REF-007`).
- **2026-10-28** (`SESSION-0020`, `EXP-0012`): the user kept American names
  as the default. M1 target chosen: Ryu, the quote after the player's win in
  the `EXP-0007` session, transcribed and blind-checked (`REF-008`).
- **2026-10-28** (`SESSION-0021`): analysis tools copied from MSHvSF with
  provenance and smoke-tested on XvSF data (`DBG-002`).
- **2026-10-28** (`SESSION-0022`, `EXP-0013`): a second user session (Ryu
  and Gouki, first-fight win). 12 of 12 replays of four pre-quote states,
  the earliest before the K.O., show the same quote; it differs from the
  first session's (`DBG-003`). Checkpoints kept in `local/checkpoints/dbg003/`.
- Next unblocked task: `DBG-004` (quote checkpoints; mostly available from
  this session).
- Nothing about XvSF's internals is confirmed yet.

## Milestones

| ID | Required outcome |
| --- | --- |
| M0 | Mednafen runs; XvSF boots with the 4 MB RAM cartridge; pad, screenshots, save states, debugger, agent interface, validated extraction, documentation, and Python tooling work. |
| M1 | One ordinary character's post-fight win quote is visibly modified in live Saturn RAM. |
| M2 | The same change is reproduced from an untouched source image. |
| M3 | All of that character's win quotes are handled programmatically. |
| M4 | A second character works through the same generalized mechanism. |
| M5 | All ordinary win quotes can be localized systematically. |
| M6 | Investigation of ending text begins only after M5. |
| M7 | One ending is localized. |
| M8 | A general ending-localization pipeline works. |
| M9 | Special cases (secret characters, bosses, other surfaces) may be investigated, each with an explicit task. |

Two gates control the work, as in MSHvSF: `GATE-M0` (technical prerequisites
for the first live RAM mutation) and `GATE-TRANSLATION` (reference and policy
prerequisites before English text goes on disc).

## Phase A: Repository And Environment

### ENV-001 - Create Python uv project

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Define an installable Python 3.12+ project managed by uv.
- **Acceptance criteria:** `pyproject.toml` declares the project, Python floor, build backend, and development dependency group; `uv.lock` is committed after synchronization.
- **Notes:** Done 2026-10-27, adapted from the MSHvSF `pyproject.toml`. uv 0.11.7; the venv resolved Python 3.13.13.

### ENV-002 - Implement setup_venv.sh and invenv.sh

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001.
- **Blockers:** None.
- **Objective:** One command creates the environment; one wrapper runs tools in it.
- **Acceptance criteria:** `./setup_venv.sh` syncs all groups; `./invenv.sh CMD` runs `CMD` in the project environment without an activated shell.
- **Notes:** Copied unchanged from MSHvSF. Both worked on 2026-10-27.

### ENV-003 - Add linting, formatting, typing, and tests

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Make `pytest`, `ruff check`, `ruff format --check`, and strict `mypy` pass from the first commit.
- **Acceptance criteria:** All four commands pass through `./invenv.sh`.
- **Notes:** 2026-10-27: 4 tests passed; ruff and mypy clean.

### ENV-004 - Create repository documentation skeleton

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Rules, protocol, task list, log, discoveries, unknowns, and experiment template exist.
- **Acceptance criteria:** `AGENTS.md`, `README.md`, `TASKS.md`, `research_log.md`, `docs/research_protocol.md`, `docs/discoveries.md`, `docs/known_unknowns.md`, `research/README.md`, and `research/experiments/README.md` exist and are non-empty.

### ENV-005 - Create .gitignore and local guidance

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Keep game data, evidence, and machine-local guidance out of git.
- **Acceptance criteria:** `git check-ignore` reports `local/`, disc formats, archives, states, and `local_agent_guidance.md` as ignored.
- **Notes:** The ignore list is MSHvSF's plus `local_agent_guidance.md` (user decision, 2026-10-27). The guidance file holds the user preferences and git identity that MSHvSF kept as per-project agent memory.

### ENV-006 - Record immutable source identity

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Record filename, size, SHA-256, and release description of every Saturn source component.
- **Acceptance criteria:** Every component is hashed with `tools/disc/hash_source.py` and recorded with a release description.
- **Notes:** 2026-10-27: 42 components of `X-Men vs. Street Fighter (Japan) (3M)` in `references/saturn_jp/README.md`. Header `T-1226G V1.002 19970925`. Track 01's user data equals the earlier ISO rip held by MSHvSF. Identity is **SUPPORTED**, not database-verified (see `ENV-007`).

### ENV-007 - Verify the source image against a database

- **Status:** `BACKLOG`
- **Milestone:** M0 (optional)
- **Dependencies:** ENV-006.
- **Blockers:** Needs a Redump entry or `chdman` and MAME's `xmvssf`/`xmvssfdou` CHD hashes; ask before installing or downloading anything.
- **Objective:** Raise the image identity from **SUPPORTED** to **CONFIRMED**.
- **Acceptance criteria:** Track hashes match a named database entry, or a mismatch is recorded with its consequence.
- **Notes:** Not required for M0. The release patch must name the exact image it applies to either way.

## Phase B: Documentation And Decisions

### DOC-001 - Carry over the MSHvSF playbook

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Give every session the MSHvSF method, pitfalls, and tools list without treating any of it as XvSF fact.
- **Acceptance criteria:** `docs/playbook_from_mshvsf.md` is a copy of the current MSHvSF `docs/playbook_cross_game.md`, with the source commit recorded.
- **Notes:** Copied 2026-10-27 from MSHvSF commit `e70e60b`, which brought the playbook up to date through MSHvSF `EXP-0088` first. Re-copied 2026-10-28 from MSHvSF commit `69c666c` (through `EXP-0102` and MSHvSF release 0.1.0). Re-copy when the MSHvSF playbook changes; record the new commit.

### DOC-002 - Confirm the MSHvSF user decisions for XvSF

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** DOC-001.
- **Blockers:** None.
- **Objective:** Ask the user to confirm, change, or defer each decision in the playbook's "The User's MSHvSF Localization Decisions" table.
- **Acceptance criteria:** Each decision has a recorded XvSF answer (verbatim, dated) or an explicit deferral, in `research_log.md` and the relevant policy file.
- **Notes:** Policy questions only; facts are still found by experiment. Done 2026-10-27: eight decisions answered and recorded in `docs/localization_policy.md` and `research_log.md`; seven evidence-dependent decisions deferred there, each to the task that produces its evidence.

### DOC-003 - Point to the shared platform references

- **Status:** `BACKLOG`
- **Milestone:** M0
- **Dependencies:** DOC-001.
- **Blockers:** None.
- **Objective:** Reuse MSHvSF's Saturn, SH-2, CD/ISO 9660, and Mednafen reference catalog instead of re-collecting it.
- **Acceptance criteria:** `docs/references.md` lists the platform references with their MSHvSF source, and separately lists any XvSF-specific prior art found.
- **Notes:** MSHvSF `DOC-007` found no public XvSF Saturn translation or internals research (2026-10-24).

## Phase C: Emulator

### EMU-001 - Pin and build stock Mednafen

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-002.
- **Blockers:** Ask before downloading source or installing build dependencies.
- **Objective:** Have a stock Mednafen build under ignored `vendor/` with its exact version, source URL, hash, and build commands recorded.
- **Acceptance criteria:** `docs/mednafen.md` records the version, source hash, configure and build commands, and the binary's `-help` banner.
- **Notes:** MSHvSF used stock Mednafen 1.32.1 (MSHvSF `EMU-001`, `docs/mednafen.md`). Using the same version lets the MSHvSF agent-interface patch apply unchanged. Done 2026-10-28: the archive (download approved by the user) hashed `de7eb94a…3832`, equal to MSHvSF's record; built binary `892bb60a…29dd`; `-help` shows 1.32.1 with the `ss` module.

### EMU-002 - Create the project-local Mednafen configuration

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-001.
- **Blockers:** None.
- **Objective:** Run Mednafen with a configuration and BIOS path local to this checkout, never the user's global configuration.
- **Acceptance criteria:** The launch command, base directory, BIOS identity (filename, size, SHA-256), and forced settings are recorded.
- **Notes:** The Japanese Saturn BIOS used by MSHvSF can be reused; record its hash here. Done 2026-10-28: `sega_101.bin` `dcfef4b9…deac` and `mpr-17933.bin` `96e106f7…266f` match Mednafen 1.32.1's documented hashes; 17 settings pinned in `local/mednafen/` and `local/mednafen_quiet/` by `./invenv.sh python -m tools.mednafen.home`; both load 7,904 settings, 0 unknown.

### EMU-003 - Boot XvSF

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-002, ENV-006.
- **Blockers:** None.
- **Objective:** Reach the title screen from a cold boot of the untouched image.
- **Acceptance criteria:** Three cold boots reach a stable title screen; the boot log shows `T-1226G`; source hashes match before and after; screenshots kept locally.
- **Notes:** Run unattended boots silently (MSHvSF `local/mednafen_quiet` approach) so they do not disturb the user. Done 2026-10-28 (`EXP-0001`): three boots with no input log `T-1226G` and show the title at frames 068-075; all 89 per-second frames identical across boots; source unchanged. Frames come from stock `-qtrecord` video via `tools/mednafen/cold_boot.py`.

### EMU-004 - Verify the 4 MB RAM cartridge

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003.
- **Blockers:** None.
- **Objective:** Confirm the cartridge setting the game needs, with a control.
- **Acceptance criteria:** With `ss.cart=extram4` the log shows the 4 MiB cart and the game runs; one control boot without it records what happens.
- **Notes:** The user states the 4 MB cart is required (2026-10-27). The control documents the failure mode, which helps diagnose later misconfiguration. Done 2026-10-28 (`EXP-0002`): three `extram4` boots match `auto` frame for frame; the `none` control stops at about 14 s on a cart-missing warning screen.

### EMU-005 - Configure and document the pad

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003.
- **Blockers:** None.
- **Objective:** The user's controller drives all six attack buttons and Start in game.
- **Acceptance criteria:** A mapping table is recorded and each button is observed in the game's button test or in play.
- **Notes:** Reuse the MSHvSF fightpad mapping as the starting configuration. 2026-10-28: the 13 port 1 bindings were copied from MSHvSF's current configuration (`docs/mednafen.md`, "Pad Mapping"); the pad is connected with the bound ID. The user's in-game check passed: "Everything worked as expected" (D-pad, Start, pause, six attack buttons).

### EMU-006 - Verify screenshots and save states

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003.
- **Blockers:** None.
- **Objective:** Screenshots and save/load states work and are stored under ignored paths.
- **Acceptance criteria:** A state saved and reloaded reproduces the same screen; files are ignored by git.
- **Notes:** Done 2026-10-28 (`EXP-0003`, D-003): hotkeys sent by `tools/mednafen/hotkeys.py` after the user granted Accessibility; F7 restored the title in the same session and after a cold boot.

### EMU-007 - Verify debugger access and memory dumps

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-006.
- **Blockers:** None.
- **Objective:** Dump WRAM-L and WRAM-H at a paused instant with the stock debugger.
- **Acceptance criteria:** Dumps of `0x00200000-0x002FFFFF` and `0x06000000-0x060FFFFF` are saved with sizes and hashes recorded; a memory write and a write breakpoint are each observed once.
- **Notes:** Done 2026-10-28 (`EXP-0004`, D-004), unattended. A breakpoint on the WRAM-H frame counter `0x06007058` did not fire (writer unknown; `docs/known_unknowns.md`).

### EMU-020 - Record why stock Mednafen is insufficient

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-007.
- **Blockers:** None.
- **Objective:** Satisfy `AGENTS.md` rule 16 before using the patched build.
- **Acceptance criteria:** A short record cites MSHvSF `EMU-012`/`EMU-020` and confirms the same limits apply here (no scripted memory access, breakpoints, or states without manual debugger work).
- **Notes:** Done 2026-10-28: `docs/mednafen_agent_interface.md`. Refinement of the wording: on XvSF, stock *can* be scripted through GUI automation (`EXP-0003`, `EXP-0004`), but only with key latency, focus stealing, two macOS grants, and registers read by eye; there is still no programmatic interface. The conclusion (reuse the patch) stands.

### EMU-021 - Reuse and validate the agent interface

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-020.
- **Blockers:** None.
- **Objective:** Drive Mednafen from Python so the user only plays.
- **Acceptance criteria:** The MSHvSF patch applies to the pinned version and builds; validations V1-V4 (MSHvSF `docs/mednafen_agent_interface.md`) pass on XvSF states; `tools/mednafen/agent.py` and its tests are copied with provenance.
- **Notes:** Done 2026-10-28 (`EXP-0006`, D-006). V4 target: the WRAM-H store found by the stock debugger in `EXP-0004`.

### DBG-001 - Copy and validate the save-state extractor

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-007.
- **Blockers:** None.
- **Objective:** Extract WRAM-L, WRAM-H, VDP1 and VDP2 VRAM from states, validated byte for byte against debugger dumps of the same instant on XvSF.
- **Acceptance criteria:** Each region matches a stock debugger dump exactly; the result goes to `docs/discoveries.md`; cart RAM stays `HYPOTHESIS`.
- **Notes:** MSHvSF found each stored 16-bit element byte-swapped (MSHvSF `DBG-012`, `EXP-0008`). Re-test, do not assume. Done 2026-10-28 (`EXP-0005`, D-005): byte swap re-tested and confirmed on XvSF; all four regions identical to same-instant dumps; cart RAM unvalidated.

### DBG-002 - Copy the game-independent analysis tools

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-003.
- **Blockers:** None.
- **Objective:** Bring over the memory diff, encoding search, equality-pattern search, code-sequence search, VDP1 sprite walker, session recorder, and replay tools with their tests.
- **Acceptance criteria:** Each copied file has a provenance note; tests pass; nothing with an MSHvSF address, offset, or file format is copied without parameterization.
- **Notes:** Copy each tool when the first task needs it, not all at once. Copied with earlier tasks: `mame_audit.py`, `mame_snap_frames.lua` (`REF-001`), `mcs_extract.py` (`DBG-001`), `agent.py` (`EMU-021`), `session_recorder.py` (`REF-005`), `iso9660.py` (`REF-006`), `mame_timeline.lua` (`REF-004`). Done 2026-10-28 for the `DBG-003` to `DBG-005` set: `tools/memory/diff.py` (+ schema), `tools/text/search.py`, `pattern_search.py`, `code_search.py`, `tools/memory/vdp1_sprites.py` (unchanged, with tests), and `tools/mednafen/replay_state.py` (its `quiet_home()` replaced by `tools.mednafen.home.configure`; MSHvSF's quiet-home test not copied). 89 tests pass; each tool smoke-tested on XvSF dumps or states.

## Phase D: References And The Translation Oracle

### REF-001 - Intake the arcade sets

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Identify every arcade zip and key against a pinned MAME, and boot the sets needed for capture.
- **Acceptance criteria:** Each file is hashed and matched to a MAME set name; the pinned MAME version is recorded; the US set boots headless.
- **Notes:** MSHvSF intake (2026-10-24): 10 of 11 sets verify in MAME 0.289; `xmvsfb.key` is missing (a bootleg set). Re-hash here; the source files are in `~/Downloads/xmvsf/`. Done 2026-10-28 (`references/arcade/`): all 11 zips and 6 keys identified by SHA-1 against MAME 0.289 `-listxml`; `-verifyroms` 10 of 11 OK (`xmvsfb.key` missing); `xmvsfu` boots headless to the title. Frame-3000 hashes equal MSHvSF's.

### REF-002 - Intake the PlayStation images

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Record the PS1 US and JP EX Edition images as secondary references.
- **Acceptance criteria:** Every component hashed; identity status recorded per image.
- **Notes:** MSHvSF intake: US **CONFIRMED** against MAME 0.289 `psx.xml` `xmvsf`; JP EX **UNKNOWN**. Done 2026-10-28 (`references/ps1/README.md`): the same result reproduced here; US `SLUS-00627`, JP EX boot file `SLPS_012.84`.

### REF-003 - Locate and decode the arcade English text

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-001.
- **Blockers:** None.
- **Objective:** Find where the arcade stores its English win quotes and ending text, and how it is encoded.
- **Acceptance criteria:** A decoder reproduces known English strings from the local ROM; the table shape and any regional differences are recorded; punctuation mappings are tested statistically.
- **Notes:** Done 2026-10-28 (`EXP-0008`, D-007): `tools/reference/xvsf_text.py`. Arrow codes and hint grouping are HYPOTHESIS/UNKNOWN; which region shows which language is `REF-004`.

### REF-004 - Confirm the decoded arcade text on screen

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-003.
- **Blockers:** None.
- **Objective:** Show that the decoded table is what the arcade draws.
- **Acceptance criteria:** A scripted MAME route shows a predicted entry on screen, with the RAM pointer that selects it.
- **Notes:** Done 2026-10-28 (`EXP-0009`, D-008). Route needs four coins (2 coins per credit). `0xFF2490` was a copy, not the selector.

### REF-005 - Inventory the Saturn text surfaces

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** EMU-021.
- **Blockers:** None.
- **Objective:** List every place the Saturn release shows Japanese text, from one recorded play session.
- **Acceptance criteria:** A table of surfaces (screen, when shown, sample screenshot path, whether the arcade has English for it) recorded from screenshots the agent reviewed.
- **Notes:** One user play session with `session_recorder.py` running: boot, attract, select, one fight won, one lost with continue, options.
  Done 2026-10-28 (`EXP-0007`): `docs/text_surfaces.md`. Arcade English observed for attract captions; for win quotes and continue hints it is still UNKNOWN (`REF-003`, `REF-004`, `UI-003`).

### REF-006 - Compare the PS1 US English with the arcade

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-002, REF-003.
- **Blockers:** None.
- **Objective:** Decide whether the PS1 US release is a second oracle for any surface.
- **Acceptance criteria:** Byte or text comparison per surface, with differences listed.
- **Notes:** Done 2026-10-28 (`EXP-0010`, D-009): second oracle for win quotes and endings (byte-identical) and arcade hints; adds a PS1 hint variant; not compared: attract captions (needs a PS1 BIOS).

### REF-007 - Inventory character names across releases

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-004, REF-005.
- **Blockers:** None.
- **Objective:** List every name the Saturn shows as art or speaks, and where the arcade English differs.
- **Acceptance criteria:** A name table with sources; options and costs presented to the user.
- **Notes:** Done 2026-10-28 (`EXP-0011`): `docs/names.md`, with options and costs. Open for `LOC-001`: Saturn Bison/Vega, arcade art for Charlie and Bison, voice, and whether American-name art is on the disc.

### REF-008 - Choose the first character and quote

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** REF-005.
- **Blockers:** None.
- **Objective:** Pick one ordinary character and one win quote as the M1 target.
- **Acceptance criteria:** The choice and the reason are recorded; the Japanese is captured on screen and transcribed.
- **Notes:** Done 2026-10-28 (`EXP-0012`): Ryu; quote at session frame 11244, two lines, blind-checked. Speaker identity and arcade slot 9 are HYPOTHESIS. No pre-KO state yet.

## Phase E: Checkpoints And Memory Analysis

### DBG-003 - Observe win-quote selection behaviour

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** EMU-021, REF-008.
- **Blockers:** None.
- **Objective:** Learn whether the quote varies from one pre-KO checkpoint before planning checkpoints.
- **Acceptance criteria:** Several replays of one pre-KO state, with the quotes shown recorded.
- **Notes:** Done 2026-10-28 (`EXP-0013`): the quote is fixed from a pre-KO state (12/12 replays) but varies between sessions. One checkpoint gives one quote.

### DBG-004 - Capture quote checkpoints

- **Status:** `READY`
- **Milestone:** M1
- **Dependencies:** DBG-003.
- **Blockers:** None.
- **Objective:** States and screenshots before the fight end, after the KO, with the quote visible, and after it disappears.
- **Acceptance criteria:** Each checkpoint is reproducible from its state and named in an experiment record.

### DBG-005 - Find the quote renderer and its RAM text

- **Status:** `BLOCKED`
- **Milestone:** M1
- **Dependencies:** DBG-001, DBG-004.
- **Blockers:** DBG-004.
- **Objective:** Determine whether the quote is VDP1 sprites or VDP2 tiles, and find the code table that drives it.
- **Acceptance criteria:** The renderer is identified by a controlled change; the RAM text table is located by plain-encoding search or by equality-pattern search.

## Gates

### GATE-M0 - Confirm environment and checkpoint prerequisites

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** ENV-001 to ENV-006, EMU-001 to EMU-007, EMU-020, EMU-021, DBG-001, DBG-003, DBG-004, DBG-005, REF-008.
- **Blockers:** Dependencies not done.
- **Objective:** Make an explicit go/no-go decision before the first live RAM mutation.
- **Acceptance criteria:** Every dependency is `DONE`; no unresolved workflow blocker can invalidate M1 evidence.

### GATE-TRANSLATION - Confirm reference and translation prerequisites

- **Status:** `BLOCKED`
- **Milestone:** M2
- **Dependencies:** DOC-002, REF-001 to REF-007.
- **Blockers:** Dependencies not done.
- **Objective:** No English text goes on disc before the oracle, the pairing method, and the user's policy are settled.
- **Acceptance criteria:** Every dependency is `DONE`; the user gives a recorded GO.

## Later Milestones (outline only)

These are placeholders so the order is visible. Each becomes a full task, with
its own acceptance criteria, only when its prerequisites are done. The method
for each is in `docs/playbook_from_mshvsf.md`.

| ID | Milestone | Outline |
| --- | --- | --- |
| RE-001 | M1 | Change the chosen quote in live RAM, with a no-write control. |
| DISC-001 | M2 | Map the ISO 9660 layout; trace the RAM table to its disc file by a write breakpoint; identify the format. |
| DISC-002 | M2 | Reproduce the M1 change from a rebuilt image (same-size, in place, EDC/ECC regenerated); cold boot. |
| FONT-001 | M2 | Find the glyph routine and font; prove the font format by a byte-identical repack. |
| FONT-002 | M2 | Find which Latin codes exist and how they look; measure line length and cell grid. |
| LAYOUT-001 | M3 | Choose a capacity route (pair glyphs or other) from measured headroom. |
| RE-002 | M3 | Selection: record pointer, index setter, forcing from a checkpoint; all quote states. |
| RE-003 | M3 | Caption compiler for one character; every record verified live by forcing. |
| RE-004 | M4 | Second team slot and a second character through the same mechanism. |
| RE-005 | M5 | File census against arcade slots; roster and exceptions (user decision); capacity; roster image; regression references. |
| END-001 | M6 | Reach, renderer, RAM, disc source, arcade English, and indexing of one ending. |
| END-002 | M7 | One ending localized. |
| END-003 | M8 | All roster endings; combined image with win quotes; coverage register. |
| REL-001 | after M5 | Release patches (xdelta3 and SSP of the changed files) with a rebuild README; may be GitHub Release assets, never committed. Splice rather than re-compress changed streams to keep patches small. |
| SPECIAL-001 | M9, user approval | Secret characters and bosses: which slots have their own official English and which reuse another's; boss pre-fight text; save- or progress-gated unlocks. |
| UI-001 | after M8, user request | UI art: inventory English art already in every font before drawing anything; caption colour and style. |
| UI-002 | after M8, user request | Attract-mode captions: which layer draws them, which container and codecs hold them, arcade and PS1 oracles. |
| UI-003 | after M8, user request | Other UI text (continue screen, hints): find the arcade English by tracing the arcade code, not only by data search. |
| TXT-001 | after M8, user request | Rare, random, or region-gated text: trace every reader of every text table. |
| LOC-001 | after M8 | Name variants (user decisions: both variants, 2026-10-27; American names default, 2026-10-28): whether both conventions' art and voice are already on the disc. |

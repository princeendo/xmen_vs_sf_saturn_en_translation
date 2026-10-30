# Research Log

This chronological journal preserves both successful and failed work. Durable,
confirmed findings are separately summarized in `docs/discoveries.md`.

## Entry Template

```markdown
## YYYY-MM-DD HH:MM TZ — EXP-NNNN or SESSION-NNNN

Task: TASK-ID

Goal:

Observation:

Hypothesis:

Action:

Result:

Conclusion:

Next action:
```

## 2026-10-27 — SESSION-0001: repository set up

Task: ENV-001 to ENV-006, DOC-001

Goal: create the repository from the MSHvSF project's method, and record the
Saturn source image before any research.

User decisions (2026-10-27):

- XvSF "absolutely needs the 4M cart" (the user's statement; `EMU-004`
  confirms the emulator setting).
- Machine-local agent guidance goes in `local_agent_guidance.md`, listed in
  `.gitignore`.
- The MSHvSF playbook was to be brought up to date before this repository was
  populated. Done as MSHvSF commit `e70e60b`.

Action:

- Rules: `AGENTS.md` adapted from MSHvSF. Rules 13, 16, 24 and 25 were
  rewritten for this direction (MSHvSF is the read-only reference), and rule
  26 (provenance for copied code) was added. A "Before Each Session" section
  points to `local_agent_guidance.md`.
- Scaffolding: `pyproject.toml` (renamed), `setup_venv.sh`, `invenv.sh`,
  `LICENSE`, the research protocol, and the experiment template, copied from
  MSHvSF. `tools/disc/hash_source.py` and its test were copied unchanged from
  MSHvSF commit `f871e21`, with a provenance note.
- `.gitignore`: MSHvSF's list plus `local_agent_guidance.md`.
  `git check-ignore` confirmed `local/` and the guidance file are ignored.
- Source image: `~/Downloads/xmvsf/X-Men vs. Street Fighter (Japan) (3M).7z`
  (364,853,662 bytes, SHA-256
  `31957de13041636e9c2d8c333b77b78043ff9c7db141c78c2f7454bd02a43345`) was
  listed with `bsdtar -tvf`, then extracted with `bsdtar -xf` into the new,
  empty, ignored folder `local/disc_images/xmvsf_saturn_jp_3m/`.
  `./invenv.sh python -m tools.disc.hash_source --json ...` hashed all 42
  files; an independent `shasum -a 256` agreed on every file.
- Comparison with the old rip: a script compared bytes 16-2063 of each
  2352-byte sector of Track 01 with consecutive 2048-byte blocks of the
  MSHvSF-held ISO (`e2b65dfd…`).

Result:

- Header `T-1226G V1.002 19970925`, area `J`, the same as the old rip.
- Track 01 is `MODE1/2352`, 71,908 sectors. Sectors 0-71,905 equal the old
  ISO's data byte for byte. Sectors 71,906-71,907 are Mode 1 with zero user
  data. Tracks 02-41 are audio.
- `./invenv.sh pytest -q`: 4 passed. `ruff check`, `ruff format --check`, and
  `mypy` (strict): clean. uv 0.11.7, Python 3.13.13.

Conclusion: the image's identity is **SUPPORTED** (header, names and layout
agree; same data as the earlier rip) but not database-verified (`ENV-007`,
`BACKLOG`). It replaces the old ISO-plus-MP3 rip for all purposes.

Next action: `EMU-001` (pin and build stock Mednafen; ask before downloading),
`REF-001` and `REF-002` (arcade and PS1 intake), and `DOC-002` (ask the user to
confirm the carried-over decisions).

## 2026-10-27 — SESSION-0002: carried-over decisions confirmed

Task: DOC-002

Goal: confirm, change or defer each MSHvSF user decision for XvSF.

Action: two rounds of multiple-choice questions, each option describing the
MSHvSF precedent. Evidence-dependent decisions (capacity route, roster and
exclusions, ending dialogue layout, caption font and colour, attract-caption
style, per-option defaults, name-variant presentation) were not asked; they
are deferred to the tasks that produce their evidence.

Result (the user's chosen options, verbatim):

- English source: "Official; fixes opt-in (Recommended)".
- Text with no official English: "Recorded new translation (Recommended)".
- Names: "Both variants, Saturn default".
- Eventual scope: "Secret characters & bosses", "UI art & attract captions",
  "Hints, story & rare text", "Optional unlocks".
- Release formats: "xdelta + SSP (Recommended)".
- Release timing: "After open tasks (Recommended)".
- Patched Mednafen reuse after a short `EMU-020`: "Yes, reuse it
  (Recommended)".
- Workflow: "Cold-boot play check closes tasks", "Silent unattended runs",
  "Ask before downloads/installs", "Prune uncited states".

Conclusion: recorded in `docs/localization_policy.md`; `AGENTS.md` rule 16
notes the decision; `DOC-002` is `DONE`. Scope answers do not lift any gate:
special surfaces still wait for M9 and their own tasks (rule 24).

Next action: `EMU-001`, `REF-001`, `REF-002`.

## 2026-10-28 — SESSION-0003: playbook re-copied after MSHvSF release 0.1.0

Task: DOC-001 (re-copy)

Goal: carry the MSHvSF work done after `e70e60b` into this repository.

Action:

- MSHvSF commit `69c666c` brought its playbook up to date through `26c54bc`
  (`EXP-0089` to `EXP-0102`, release 0.1.0). `docs/playbook_from_mshvsf.md`
  was re-copied from it; `diff` against the source, below the provenance
  note, reports no difference.
- `git diff --stat e70e60b 26c54bc` in MSHvSF over `AGENTS.md`,
  `docs/research_protocol.md`, the experiment templates, `pyproject.toml`,
  `setup_venv.sh`, `invenv.sh`, `.gitignore` and `tools/disc/hash_source.py`
  (with its test) is empty, so this repository's copies stand.
- `docs/localization_policy.md`: release timing now reads "done, or deferred
  by the user by name", as MSHvSF 0.1.0 was handled. A note records that
  MSHvSF moved to American names by default on 2026-10-28, after this
  project's `DOC-002` answer ("Both variants, Saturn default"). The answer is
  not changed; the user is asked.
- `local_agent_guidance.md` (ignored): `gh` is the work account, so the user
  publishes releases on github.com; real-Saturn boots.

Result: documentation only; no experiment run.

Next action: the user's answer on the default names; then `EMU-001`,
`REF-001`, `REF-002`.

## 2026-10-28 — SESSION-0004: American names by default

Task: DOC-002 (amended)

Decision (user, 2026-10-28, verbatim): "Make American names the XvSF default,
like MSHvSF. Record it in the policy." This replaces the 2026-10-27 answer
"Both variants, Saturn default". Both variants are still built; the American
variant is the default and is listed first in a release.

Action: `docs/localization_policy.md` (names row, note, deferred row) and
`TASKS.md` (Current State, `LOC-001` outline) updated. Documentation only.

Next action: `EMU-001`, `REF-001`, `REF-002`.

## 2026-10-28 — SESSION-0005: stock Mednafen, arcade and PS1 intake

Task: EMU-001, REF-001, REF-002

Goal: build the pinned stock emulator and identify the reference releases.

User decision (2026-10-28): asked how to get the Mednafen source (MSHvSF kept
only an extracted tree, which cannot be hash-checked), the user chose
"Download archive (Recommended)".

Action and result:

- `EMU-001`: downloaded `mednafen-1.32.1.tar.xz` into the new, ignored
  `local/downloads/mednafen-1.32.1/`. Size 3,571,236 bytes and SHA-256
  `de7eb94a…3832`, both equal to MSHvSF's record. Extracted to
  `vendor/mednafen/src/`, configured with `--enable-debugger --enable-ss`, and
  built out of tree with `make -j12` (both exit 0). Binary SHA-256
  `892bb60a…29dd`. `-help` prints `Starting Mednafen 1.32.1` with the `ss`
  module and exits 255. The MSHvSF stock binary also exits 255 for the same
  command, so 255 is how 1.32.1 handles `-help`. MSHvSF's docs say "exited
  successfully"; that wording does not match what the binary returns. Details
  in `docs/mednafen.md`.
- `REF-001`: copied the 11 zips and 6 keys unchanged (`cmp` clean) to
  `local/arcade_roms/xmvsf/`. The copied `mame_audit.py` matches by member
  name, so it reported 0 matches for relabelled zips (for example
  `xmvsfur1.zip`). Added `tools/reference/listxml_match.py`, which matches by
  SHA-1 against `mame -listxml 'xmvsf*'` (MAME 0.289). Every zip maps to one
  set and every member matches; every key maps to its sets.
  `-verifyroms 'xmvsf*'` on the renamed rompath: 10 of 11 OK (`xmvsfb.key`
  missing). Headless boots of `xmvsfu` and `xmvsfjr2` exited 0. Frame-3000
  PNG hashes `e8a8ab8e…` and `e19f6bae…` equal MSHvSF's. The agent reviewed
  all four snapshots: the `xmvsfu` title shows `INSERT COINS`.
- `REF-002`: extracted both PS1 archives into new ignored folders and hashed
  them. US `.bin` and `.cue` match MAME 0.289 `psx.xml` `xmvsf`
  (`SLUS-00627`): **CONFIRMED**. JP EX is in no MAME 0.289 hash file:
  **UNKNOWN**. Text search of the images finds the boot lines
  `SLUS_006.27` and `SLPS_012.84`.

Tools copied from MSHvSF `69c666c` with provenance notes:
`tools/reference/mame_audit.py`, `tests/unit/test_mame_audit.py`,
`tools/reference/mame_snap_frames.lua`. `qsound.zip` (SHA-256 `55feb9b7…5356`)
and the MAME driver source `cps2.cpp` (SHA-256 `a8c09ef8…1602`, equal to
MSHvSF's pin) were copied from MSHvSF's ignored `local/` folder.

Checks: `./invenv.sh pytest -q` 12 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `EMU-001`, `REF-001`, and `REF-002` are `DONE`. Nothing about XvSF
internals is confirmed by this work.

Next action: `EMU-002` (project-local configuration and BIOS identity), then
`EMU-003` (boot); `REF-003` (arcade English text) can run alongside.

## 2026-10-28 — SESSION-0006: project-local Mednafen configuration

Task: EMU-002

Goal: run Mednafen only with configuration and BIOS inside this checkout, and
record the BIOS identity.

Action:

- Copied `sega_101.bin` and `mpr-17933.bin` unchanged from MSHvSF's ignored
  `local/mednafen/firmware/` (`cmp` clean). Their SHA-256 values equal the
  ones Mednafen 1.32.1's `Documentation/ss.html` gives, read from this
  checkout's verified source archive.
- Added `tools/mednafen/home.py` (adapted from MSHvSF `replay_state.py`
  `quiet_home()` at `69c666c`) with three unit tests. It pins 17 settings in
  `local/mednafen/` and, for unattended runs, those plus three silent
  settings in `local/mednafen_quiet/`, whose `firmware/` links to the
  interactive home's.
- `./invenv.sh python -m tools.mednafen.home`, run twice: the first run
  changed only the quiet home's three settings (all 17 pinned values are
  1.32.1 defaults); the second reported `no change` for both.
- `-help` with each home: `Loaded 7904 valid settings and 0 unknown
  settings`, base directory the chosen home; config SHA-256 unchanged after
  the run (`48a7cf6b…28fc`, `ef897288…5019`).
- Mednafen's `src/ss/db.cpp` lists `T-1226G` as `CART_EXTRAM_4M` ("Game
  requirement"), so `ss.cart auto` is expected to select the 4 MiB cart. This
  is a **HYPOTHESIS** until `EMU-004`.

Checks: `./invenv.sh pytest -q` 15 passed; `ruff check`, `ruff format`, and
`mypy` clean.

Conclusion: `EMU-002` is `DONE`. No game was booted; boot, BIOS acceptance
and cart selection are `EMU-003` and `EMU-004`.

Next action: `EMU-003` (three cold boots of the untouched image to the title
screen, in the quiet home, source hashes checked before and after).

## 2026-10-28 — SESSION-0007 / EXP-0001: unattended cold boots

Task: EMU-003

Goal: three cold boots of the untouched image reach a stable title screen.

Action:

- Chose stock `-qtrecord` video plus SIGTERM as the way to see unattended
  runs (no input, no agent interface, no setting change). A 20 s pilot showed
  SIGTERM is caught, exit 0, and the movie finalized; it reached only the
  SEGA licence screen, so the runs use 90 s.
- The pilot left backup RAM in `local/mednafen_quiet/sav/`; it was emptied
  before each boot so all three start alike.
- Added `tools/mednafen/cold_boot.py` (run, record, stop, extract 1 fps
  frames and contact sheets, hash, delete the movie).
- Three boots, source hashed before and after.

Result: all three exit 0 and log `T-1226G`, area `J`, `Cart: 4MiB Extended
RAM`. All 89 per-second frames are byte-identical across boots. The title
logo with `PRESS START BUTTON` shows at frames 068-075 (frame 070
`ebfbb7da…e662`). Source manifests identical; config and binary hashes
unchanged. Details: `research/experiments/EXP-0001/README.md`.

Not tested: whether emulation stalls while the display sleeps (MSHvSF's
vsync observation), and frame-exact determinism between samples.

Checks: `./invenv.sh pytest -q` 15 passed; `ruff check`, `ruff format
--check`, and `mypy` clean. `cold_boot.py` has no unit test; it wraps
Mednafen and ffmpeg, and this experiment exercised it end to end.

Conclusion: `EMU-003` is `DONE` (**CONFIRMED**, D-001). `EMU-004`,
`EMU-005`, and `EMU-006` are now `READY`.

Next action: `EMU-004` (forced `extram4` boots and one control boot without
the cart), unattended with the same tool.

## 2026-10-28 — SESSION-0008 / EXP-0002: forced cart and no-cart control

Task: EMU-004

Goal: confirm the cart setting with three forced `extram4` boots and one
control boot without a cart.

Action: added `--setting KEY=VALUE` to `tools/mednafen/cold_boot.py`. Ran
`extram4` three times and `none` once (90 s each, no input, `sav/` emptied
first). After each run Mednafen had saved the value into the quiet home;
`tools.mednafen.home` restored `ss.cart auto` and the config SHA-256 returned
to `ef897288…5019`.

Result: `extram4` logs `Cart: 4MiB Extended RAM` and all 89 frames equal
`EXP-0001`'s. `none` logs `Cart: None`; frames 001-014 match, then from 015
one static Japanese warning that the 4MB extended RAM cartridge is not
inserted correctly (agent transcription and translation in `EXP-0002`). It
never reaches the title. Source manifests identical before and after.

Checks: `./invenv.sh pytest -q` 15 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `EMU-004` is `DONE` (**CONFIRMED**, D-002). The warning screen is
recorded as a Saturn-only text surface for `REF-005`.

Next action: `EMU-006` (screenshots and save states, which may need input or
the debugger: decide the method first), `EMU-005` (needs the user's pad), or
`REF-003`.

## 2026-10-28 — SESSION-0009: pad bindings from MSHvSF

Task: EMU-005

Request (user, 2026-10-28): "Can you re-use the map from the MSHvSF repo?"

Action:

- Diffed MSHvSF's interactive `mednafen.cfg` (`b308aab2…9a50`) against this
  home's. Differences: the 13 `ss.input.port1.gamepad.*` lines, `cheats`,
  and `psx.bios_na`. Only the 13 pad lines were copied.
- MSHvSF's documented M30 table (D-pad buttons 12-15, Start button 9) does
  not match its configuration (D-pad on `abs_0`/`abs_1`, Start `button_6`,
  C `button_10`, Z `button_9`). The configuration, last changed 2026-10-28
  11:02, is what MSHvSF was played with, so it was used. MSHvSF's docs were
  not changed (rule 25).
- Added `--bindings-from` and `read_settings` to `tools/mednafen/home.py`
  with a unit test; applied to both homes; a second plain run reports no
  change; both load 7,904 settings, 0 unknown.
- An 8 s silent probe boot logged the connected pad as
  `0xecccd365fc40db2f0006000c00010000 - PS4 Controller`, the bound ID.

Checks: `./invenv.sh pytest -q` 16 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: mapping configured and recorded. `EMU-005` stays `IN_PROGRESS`
until the user observes each control in game.

Next action: the user's in-game check (interactive home).

### SESSION-0009 addendum: in-game check

The agent launched the interactive home (`local/mednafen/`) and gave the user
a step table: Start at the title, D-pad in the menu, first menu item,
character select with the D-pad, a fight pressing each of the six face
buttons and walking, Start to pause and resume, F12 to quit.

User report (2026-10-28, verbatim): "Everything worked as expected".

Session log `local/emu005/session.log` (5,593 bytes): pad ID
`0xecccd365fc40db2f0006000c00010000`, `SGID: T-1226G`, `Cart: 4MiB Extended
RAM`; exit 0. `local/mednafen/mednafen.cfg` unchanged (`cb1c2d3b…a1e9`). No
screenshots were taken. Physical button labels per attack were not reported;
L/R were not tested (unbound on the pad, as in MSHvSF).

Conclusion: `EMU-005` is `DONE` on the user's observation. Next: `EMU-006`
(screenshots and save states) or `REF-003`.

## 2026-10-28 — SESSION-0010 / EXP-0003: screenshots and states

Task: EMU-006

Goal: show that screenshots and save/load states work and stay ignored.

Observation: stock 1.32.1 has these only as hotkeys (F9, F5, F7). Added
`tools/mednafen/hotkeys.py` to press them through System Events at fixed
times.

Blocker and resolution:

- First attempts: `osascript is not allowed to send keystrokes. (1002)`.
  The user granted Accessibility to Claude ("I granted Accessibility to
  Claude in System Settings"); still 1002.
- Process chain: `/Applications/Claude.app` → `Helpers/disclaimer` → Claude
  Code `~/Library/Application Support/Claude/claude-code/2.1.304/6bbba6adc37f/claude.app`
  → zsh. The agent told the user the inner bundle is the responsible app.
  The user then "flipped a switch"; the next pilot (F9 at 10 s) worked.
- A zsh empty-glob error stopped the first real attempt before launch; the
  rerun used `find -delete`.

Result: run 1 screenshots show the title (71 s), the attract fight (86 s),
and the title again 1.1 s after F7. Run 2 (fresh cold boot) shows black at
21 s and the title 2.0 s after F7. State `.mc0` 3,508,722 bytes,
`739ef207…2f2d`, unchanged by loading. Title shots differ in bytes
(animated background; SSIM 0.82-0.90) but not in scene (title vs fight SSIM
0.09). Source manifests identical. All outputs are git-ignored.

Checks: `./invenv.sh pytest -q` 16 passed; `ruff check`, `ruff format
--check`, and `mypy` clean. `hotkeys.py` has no unit test; it drives macOS
and Mednafen, and this experiment exercised it end to end.

Conclusion: `EMU-006` is `DONE` (**CONFIRMED**, D-003). `EMU-007` is `READY`.

Next action: `EMU-007` (debugger dumps of WRAM-L and WRAM-H at a paused
instant, one memory write, one write breakpoint), or `REF-003`.

## 2026-10-28 — SESSION-0011 / EXP-0004: stock debugger, unattended

Task: EMU-007

Goal: dump WRAM-L and WRAM-H at a paused instant; observe one memory write
and one write breakpoint; all driven by the agent.

Path to a working method (all recorded so later agents do not repeat it):

- First pilots froze correctly (identical F9 screenshots) but every typed
  dump path came back as "Error opening file "ocal/…" for writing". Tested
  and rejected in turn: typing speed (0.05 s and 0.15 s per character),
  Shift (lowercase hex), focus switching (`--keep-focus`), Mednafen's
  `trio_sscanf` (compiled from our source in the scratchpad: parses the
  strings correctly), and the prompt code (no special case for `l`).
- A window capture showed the real cause: `option+3` never switched to the
  memory editor. The CPU view's `l` key opened "Trace Log(filename end_pc)"
  and the rest of the path became its filename. The view switch requires
  SDL `KMOD_LALT`; System Events' option flag was not seen as left Alt.
  Posting left-Option CGEvents (flag `0x80020`) through JXA fixed it.
- Side finding: trio's `%08x` accepts `+00100000`, so the `+size` dump form
  is parsed by the inclusive form first. That explains MSHvSF `EXP-0007`'s
  1,048,577-byte dumps better than its "the `+` was omitted" inference. MSHvSF
  is not edited here (rule 25).
- macOS showed the user a dialog when the first window capture ran
  ("Claude" requests to bypass the private window picker and access screen
  and audio). The agent did not answer it; captures worked.
- Privacy: run D used screen-area captures; when focus moved to another app,
  four captures (and a strip in two others) showed that app's window. The
  agent deleted them and switched to `screencapture -l <window id>`.
- `option+r` with the debugger visible did not resume; hiding it first did.
- A write breakpoint on the frame counter `0x06007058` (+60/s) never fired;
  a whole-WRAM-H breakpoint halted the CPU at `06021B26 mov.b r0,@r9`
  (R9 `060C9047`).

Result: WRAM-L `e55529cf…bf94` and WRAM-H `a384c0ef…6702`, each 1,048,576
bytes and identical when repeated in one freeze; write test exact; breakpoint
halt confirmed by identical captures 2-4 s apart. Same-instant state
`62837cf2…fc3f` (3,499,031 bytes) kept for `DBG-001`. Source unchanged.

Checks: `./invenv.sh pytest -q` 33 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `EMU-007` is `DONE` (**CONFIRMED**, D-004). `EMU-020` and
`DBG-001` are `READY`.

Next action: `EMU-020` (short record that stock Mednafen is insufficient,
citing MSHvSF), then `DBG-001`; or `REF-003`.

## 2026-10-28 — SESSION-0012: EMU-020 record

Task: EMU-020

Action: wrote `docs/mednafen_agent_interface.md`. It cites MSHvSF `EMU-012`
and `EMU-020`, then sets out what this project observed on XvSF with stock
1.32.1 driven by GUI automation (`EXP-0003`, `EXP-0004`): it works for M0
checks, but each key costs about 1 s and the user's focus, it needs
Accessibility (on a versioned Claude Code bundle path) and screen capture,
breakpoint hits only halt, registers are read by eye from captures, and
act-after-hit is out of reach. MSHvSF rejected GUI automation without trying
it; here it was tried, and the conclusion is the same. The patch's
provenance (`c30146ef…5244`, MSHvSF `b9a6593`) and the V1-V4 re-validation
plan are recorded for `EMU-021`.

Conclusion: `EMU-020` is `DONE`; `EMU-021` is `READY`. Documentation only.

## 2026-10-28 — SESSION-0013 / EXP-0005: extractor validated on XvSF

Task: DBG-001

Action: copied `tools/memory/mcs_extract.py` and its test unchanged from
MSHvSF `69c666c` with provenance notes; re-checked its region table against
this repository's Mednafen source. Extracted the `EXP-0004` run A state and
a new run G state (freeze, `F5`, dumps of all four spaces with name-checking
window captures).

Result: WRAM-L and WRAM-H identical at two instants; VDP1 and VDP2 VRAM
identical at one. The raw stored order equals the dumps only after a 16-bit
swap, confirming MSHvSF's byte-order finding on XvSF. Cart RAM identical
between the two states but unvalidated (no debugger space). Source
unchanged.

Checks: `./invenv.sh pytest -q` 47 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `DBG-001` is `DONE` (**CONFIRMED** for four regions, D-005).

Next action: `EMU-021` (copy the MSHvSF agent patch and client, build,
re-run V1-V4 on XvSF), or `REF-003`.

## 2026-10-28 — SESSION-0014 / EXP-0006: agent interface reused and validated

Task: EMU-021

Action: copied the MSHvSF patch (`c30146ef…5244`), client and tests (two
MSHvSF-only tests dropped) with provenance; applied the patch to a copy of
the stock source (drivers equal MSHvSF's patched tree) and built
`290d4717…f9f8`. V1 equivalence by `cold_boot` with the patched binary and no
agent directory; V1 smoke and V2-V4 by `research/experiments/EXP-0006/validate.py`.

Result: V1 89/89 frames equal stock; 13 spaces; registers returned. V2 four
regions identical to same-poll extraction, two runs. V3 exact round trip;
`frames 30` exact; `savestate` refused while halted. V4: a 120-frame window
(run 1) had no hits on `060C9047`; a 1,800-frame window (run 2) logged 6,
at PCs `06021B26` (the `EXP-0004` halt) and `06021B6A`, R9 `060C9047`,
without halting. Halt mode on all of WRAM-H stopped at frame 6038 with
registers as text. Stock binary and source unchanged.

Checks: `./invenv.sh pytest -q` 52 passed; `ruff check`, `ruff format
--check`, and `mypy` clean (validate.py also `mypy --strict`).

Conclusion: `EMU-021` is `DONE` (**CONFIRMED**, D-006). `REF-005` is
`READY`.

Next action: `REF-005` needs one recorded user play session (MSHvSF's
`session_recorder.py` would be copied first), or `REF-003` without the user.

## 2026-10-28 — SESSION-0015 / EXP-0007: play session and text surfaces

Task: REF-005

Action: copied `tools/mednafen/session_recorder.py` and its test from MSHvSF
`69c666c`; smoke-tested it unattended; launched the patched build in the
interactive home with the recorder; the user played a 13-step route and
reported "done, no surprises". Reviewed all 414 unique screenshots; ran the
US and JP arcade attract loops headless in MAME for comparison.

Result: Japanese text appears on attract captions, win quotes (player and
CPU wins), and continue-screen hints. Menus, options, HUD, stage cards,
names, game over and rankings are already English. The US arcade attract
shows English captions where the Saturn and JP arcade show Japanese ones.
Win quotes and continue hints were not reached in the arcade.

Notes: ffmpeg 9.0.1 here lacks `drawtext`, so contact-sheet tiles were
mapped to frames by position. Game text (including the arcade captions)
is kept in ignored `local/ref005/notes.md`.

Checks: `./invenv.sh pytest -q` 54 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `REF-005` is `DONE`; `REF-008` is `READY`.

Next action: `REF-008` (pick the M1 character and win quote; the session's
Ryu/Gouki win at frame 11244 and its states are candidates, but the states
kept are only the last 3 minutes), or `REF-003`.

## 2026-10-28 — SESSION-0016 / EXP-0008: arcade English text located and decoded

Task: REF-003

Action and results, in order (details in `EXP-0008`):

- Rebuilt the `maincpu` region of each held set from its zips (68000 order:
  each 16-bit word swapped). Stage names and UI words are plain 8-bit ASCII
  near `0x4300`; long ASCII runs are boot, legal and test-menu text.
- **DISPROVEN for XvSF:** MSHvSF's arcade map (16-bit, `A` = `0x0140`,
  `a` = `0x0161`, space `0x0020`) gives 0 phrase runs in all three tested
  sets.
- An offset histogram of common words found ASCII + `0x80` (Spanish and
  Portuguese twins) and a single-case English hit (`hadaloo`, offset 1584).
  Context fixed the English map as a tile-sheet layout of ASCII.
- Pointer tables `0x17E1E8` (win quotes) and `0x17E318` (endings), 19 slots
  each; records of 2 × 25 codes. A first guess at the endings' end
  (`0x18D55E`) truncated the last slot. Reading on, the real end is record
  270, and records 270-292 are the continue-screen hints. The area totals
  294 records exactly.
- Punctuation in expected context: 88-100% per mark. Unmapped codes only in
  hints (`0x0134`-`0x013A`), probably joystick arrows (HYPOTHESIS).
- All 11 held sets carry the same English; Japan 960909 has it `0x4C` bytes
  earlier. The loader now falls back to SHA-1 for relabelled zip members
  (`xmvsfur1`).
- Game text stays in ignored `local/ref003/`.

Checks: `./invenv.sh pytest -q` 58 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `REF-003` is `DONE` (**CONFIRMED**, D-007). `REF-004` and
`REF-006` are `READY`.

Next action: `REF-004` (show a decoded win quote on the arcade screen in
MAME, with the RAM pointer that selects it), `REF-006`, or `REF-008`.

## 2026-10-28 — SESSION-0017 / EXP-0009: decoded arcade text on screen

Task: REF-004

Action: copied `tools/reference/mame_timeline.lua` (MSHvSF `69c666c`, body
unchanged). Scripted routes on `xmvsfu` with a read tap on the English area.

Results and failures, in order:

- Runs 1-2 never left the title: the set's coinage is 2 coins per credit
  ("CREDIT 0(1/2)"); one coin is not a credit. Run 3 used four coins and
  repeated Start and button 1; the CPU won.
- Run 3: the game read record 109 (`0x189936`, slot 12 record 2), then hint
  records 270 and 271. The screen showed exactly the decoder's text for each,
  and `0x0134` as ↑.
- Run 4: identical replay; two-state search found `0xFF2490` (= `0x189936`)
  and `0xFF8BB4` (= slot 12 base).
- **REJECTED:** `0xFF2490` selects the record. Forcing its low word (run 5)
  changed nothing; write logs (run 6) show it is written just before
  printing, a copy of the address.
- **CONFIRMED:** `0xFF8BB4` selects the slot. Forcing its low word to slot 0's
  base (run 7) made the game read `0x186F6A` and draw slot 0 record 2, as
  predicted.

Checks: `./invenv.sh pytest -q` 58 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `REF-004` is `DONE` (**CONFIRMED**, D-008). `REF-007` is
`READY`.

Next action: `REF-006`, `REF-007`, or `REF-008`.

## 2026-10-28 — SESSION-0018 / EXP-0010: PS1 US English vs arcade

Task: REF-006

Action: copied `tools/disc/iso9660.py` and its test from MSHvSF `69c666c`;
listed (295 entries) and extracted (269 files) the US PS1 data track;
searched every arcade English record in every file in both byte orders.

Result: 293/294 records, all in `P/P4/SELECT.BIN`, little-endian,
byte-identical. Win quotes and endings complete and in order. Hints appear
twice: set A is the arcade's minus record 286; set B has 16 arcade records
(one repeated) and 7 PS1-only records. Record 293 ("coming soon") is
absent. No Spanish, Portuguese or Japanese tables in any file. MSHvSF's
little-endian finding holds for XvSF.

Not done: attract-caption comparison (needs the PS1 running, so a PS1
BIOS); the JP EX image.

Checks: `./invenv.sh pytest -q` 63 passed; `ruff check`, `ruff format
--check`, and `mypy` clean (compare.py also `mypy --strict`).

Conclusion: `REF-006` is `DONE` (**CONFIRMED**, D-009).

Next action: `REF-007` (names) or `REF-008` (first character and quote).

## 2026-10-28 — SESSION-0019 / EXP-0011: character names

Task: REF-007

Result: the Saturn shows GOUKI and NASH (select labels; GOUKI also on VS
screen and win banner). The arcade JP set shows GOUKI and the US set AKUMA on
the same select label. The arcade English text names Charlie (2) and Bison
(4), never Akuma or Gouki. No Saturn file holds any name as text. The arcade's
16-bit name list has both conventions in every region, so it is not evidence
of display.

Failed attempt: a down-first cursor sweep in MAME showed no labels; labels
appeared only during the partner-select phase of the first run.

Not observed: the Saturn's name for Bison/Vega; arcade art for Charlie and
Bison; voice. These go to `LOC-001`.

Checks: `./invenv.sh pytest -q` 63 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `REF-007` is `DONE` with options and costs in `docs/names.md`.

Next action: `REF-008`.

## 2026-10-28 — SESSION-0020 / EXP-0012: M1 target chosen

Task: REF-008

User decision (2026-10-28, verbatim): "Keep American names as the default."

Choice: Ryu, and the win quote after the player's win in the `EXP-0007`
session (frame 11244, `8428bf99…11a6`). Reasons: ordinary character,
reachable again by a player win, captured by the agent interface, and an
arcade English slot exists (slot 9 by name-list order, HYPOTHESIS).

Transcription by the agent from a 3x enlargement; a separate agent's blind
transcription is identical (two lines, six dots as two ellipses, full-width
exclamation mark). Keyword counts over arcade slots 9, 10 and 15 did not
single out Ryu's slot; slot 9 stays a hypothesis.

Not available: a pre-KO state (the recorder kept only the last 3 minutes).

Conclusion: `REF-008` is `DONE`; `DBG-003` is `READY` and needs one user
session with Ryu.

## 2026-10-28 — SESSION-0021: analysis tools copied (DBG-002)

Task: DBG-002

Action: copied from MSHvSF `69c666c`, each with a provenance note and its
tests: `tools/memory/diff.py` (+ `diff_result.schema.json`),
`tools/text/search.py`, `tools/text/pattern_search.py`,
`tools/text/code_search.py`, `tools/memory/vdp1_sprites.py`. The audit found
only Saturn hardware constants in them (work-RAM bus bases, the VDP1 command
layout from Mednafen's source), no MSHvSF addresses or formats.
`tools/mednafen/replay_state.py` was adapted: its own `quiet_home()` is
replaced by `tools.mednafen.home.configure`, so one tool pins the silent
home. MSHvSF's quiet-home test was not copied.

Smoke tests on XvSF data: `replay_state` replayed the `EXP-0005` state to the
title (2 screenshots; silent-home config hash unchanged); `diff` of the two
validated WRAM-H instants reports 3,990 changed bytes, matching `EXP-0005`;
`code_search` and `search` find the known WRAM-H start words at
`0x06000000`; `vdp1_sprites` lists 649 commands from the run-G VDP1 dump.

Checks: `./invenv.sh pytest -q` 89 passed; `ruff check`, `ruff format
--check`, and `mypy` clean.

Conclusion: `DBG-002` is `DONE`. Next: `DBG-003` (needs a user session with
Ryu).

## 2026-10-28 — SESSION-0022 / EXP-0013: win-quote selection from one state

Task: DBG-003

Action: launched the patched build in the interactive home with the
recorder at one state per second (keep 180); the user picked Ryu and Gouki
and won the first fight (user: "I completed the playthrough. Not sure if the
quote was the same (don't read Japanese)"). Replayed four states (before the
K.O., K.O., WIN banner, pre-quote transition) three times each with
`replay_state`.

Result: all 12 replays show the live session's quote (bubble crop hashes
equal). It is a different line from session 1's, with the same team and a
first-fight win.

Pitfall: a contact-sheet step used `rm -f DIR/*`; the built-in safety check
refused it (target not statically resolvable). It was not needed: the step
now writes to a fresh folder.

Checks: `./invenv.sh pytest -q` 89 passed; `ruff check`, `ruff format
--check`, and `mypy` clean (documentation and local evidence only).

Conclusion: `DBG-003` is `DONE` (**CONFIRMED**): one checkpoint yields one
quote; quotes vary between sessions. `DBG-004` is `READY`.

Next action: `DBG-004` (name checkpoints before the fight end, after the K.O.,
with the quote visible, and after it disappears; most exist in
`local/checkpoints/dbg003/`).

## 2026-10-28 — SESSION-0023 / EXP-0014: M1 target switched; checkpoints named

Task: REF-008 (amended), DBG-004

User decision (2026-10-28, verbatim): "Yes, switch the M1 target to this
session's Ryu quote and start DBG-004." Recorded in `EXP-0012` and `TASKS.md`.
A separate agent's blind transcription of the new line matches the agent's.

Action: `research/experiments/EXP-0014/checkpoints.py` reloads each kept state
and screenshots it, then runs 480 frames from the quote-visible state and
saves `after_quote.mcs`.

Pitfall: `savestate` after `run` in the same command file is still refused
("not allowed while halted"); separate exchanges work.

Result: every checkpoint reloads to its screen. The quote-visible reload
screenshot is byte-identical to the live session's. The after-quote state
shows the post-quote transition and reloads to it.

Checks: `./invenv.sh pytest -q` 89 passed; `ruff check`, `ruff format
--check`, and `mypy` clean (`checkpoints.py` also `mypy --strict`).

Conclusion: `DBG-004` is `DONE` (**CONFIRMED**). `DBG-005` is `READY`.

## 2026-10-28 — SESSION-0024 / EXP-0015: quote renderer and RAM text

Task: DBG-005

Result:

- VDP1 walk at `quote_visible`: the text is 2 rows × 19 16×16 4 bpp sprites
  (`0x7020`), one cell per distinct glyph (line 2's う reuses line 1's).
- Controlled change: zeroing glyph cell `0x4A800` removed only も; the control
  screenshot equals the live capture. Renderer **CONFIRMED** as VDP1.
- Plain Shift-JIS, EUC-JP and UTF-16BE: 0 hits in any region.
- **REJECTED** as non-discriminating: a two-line search allowing any gap
  (thousands of hits).
- The full 38-cell equality pattern with blanks: 1 hit, WRAM-L `0x0024F8D0`,
  16-bit, blank `0x0020`. A 22-record table of 38 codes at `0x0024F5D8`,
  resident from `pre_ko` on. Hiragana = Unicode − `0x2661` (13/13).
- Records 0-15 are byte-identical to the arcade Japanese win-quote slot 9;
  16-21 to the first six records of the arcade Japanese endings' slot 9.
  This also supports arcade slot 9 = Ryu.

Checks: `./invenv.sh pytest -q` 89 passed; `ruff check`, `ruff format
--check`, and `mypy` clean (experiment scripts also `mypy --strict`).

Conclusion: `DBG-005` is `DONE` (**CONFIRMED**, D-010). Every `GATE-M0`
dependency is `DONE`; the gate awaits the user's go/no-go before `RE-001`
(the first live RAM mutation).

## 2026-10-28 — SESSION-0025 / EXP-0016: M1, quote changed in live RAM

Task: GATE-M0, RE-001

User decision (2026-10-28, verbatim): "GATE-M0: go. Start RE-001: change the
chosen quote in live RAM, with a no-write control." `GATE-M0` marked `DONE`;
`RE-001` written up as a full task before work.

Action: `research/experiments/EXP-0016/m1_trial.py` from `pre_ko`: control
(no write), then trial writing `09E1 09E3 09E5` (あいう) over `0A21 09E5 0AC8`
(もう一) at WRAM-L `0x0024F8D6`.

Result: trial quote line 1 reads あいう度鍛え直してこい。; control is
byte-identical to the live capture. 318 pixels differ, all within cells 3-5
of line 1. The record held the written bytes at the quote screen. Source
image unchanged.

Checks: `./invenv.sh pytest -q` 89 passed; `ruff check`, `ruff format
--check`, and `mypy` clean (`m1_trial.py` also `mypy --strict`).

Conclusion: **M1 reached** (**CONFIRMED**, D-011). Next is M2; its tasks must
be written in full first (rule 8: nothing past M1 before M1 is confirmed, and
it now is).

## 2026-10-28 — SESSION-0026 / EXP-0017: quote table traced to `MC09.SHP`

Task: DISC-001 (M2 tasks `DISC-001`, `DISC-002`, `FONT-001`, `FONT-002`
written in full first, at the user's request: "Start M2: write up the M2
tasks, then begin DISC-001").

Actions and results:

- ISO listing regenerated with `--check`: 71,908 Mode 1 sectors, no errors,
  236 files, identical to `EXP-0011`'s. Committed as
  `references/saturn_jp/iso_listing.json`.
- Raw search of all files for the 1,672-byte table: no hit.
- **DISPROVEN for XvSF:** a standard PRS decoder (LE long word, from offset
  0). It failed at output 0 on all 60 `.PRS` files. The real format has a
  4-byte count header and a big-endian long word.
- Not tried after the trace made them moot: the playbook's MSHvSF LZSS
  (MSB-first flags, header 0x10/0x14) and treating the `SELALL.PRS` header as
  an entry table.
- Control: from state 5696, a write breakpoint on the table and no input for
  120 frames gave 0 hits.
- Trial (`catch_loader.py`): pad A was bound to K in a scratch home and held
  0.2 s. It halted at `0x0600D124` with R12 = `0x0024F5D8`; a second run gave
  identical registers and WRAM-L.
- Disassembly (MSHvSF `tools/sh2/disasm.py` copied from `69c666c`, with
  `bsrf`/`braf` added): sector reader `0x0600D09C`, file size `0x50CE`,
  destination `0x0024D000`, LZ77 decompressor `0x0601077C`.
- `MC09.SHP` is the only 20,686-byte file. Decoding gives 43,064 bytes with
  the table at offset `0x25D8`. They equal RAM at state 5750 apart from 259
  fields relocated by `+0x0024D040`.

Checks: `./invenv.sh pytest -q` 119 passed (new `test_prs.py` and
`test_sh2_disasm.py`); `ruff check`, `ruff format --check` and `mypy` clean
(`catch_loader.py` also `mypy --strict`). Source track hash unchanged
(`c904a386…`).

Conclusion: `DISC-001` is `DONE` (**CONFIRMED**, D-012). `DISC-002` and
`FONT-001` are now unblocked.

## 2026-10-28 — SESSION-0027 / EXP-0018: M2, quote change from a rebuilt image

Task: DISC-002 ("Start DISC-002: reproduce the M1 change from a rebuilt image.")

Decision recorded in `TASKS.md`: the marker goes into all 16 win-quote
records, because the shown record varies between sessions; record 10 gets
exactly the M1 bytes.

Actions and results:

- **DISPROVEN:** an in-place literal edit of the compressed stream. Only 41
  of the 96 marker bytes are literals, and 203 later copies read the records.
- **Encoder added** (`compress`/`compress_file`). It repacks `MC09.SHP` byte
  for byte; 40 of the 51 fully decodable files repack exactly. Marker file
  `60f2d10e…`, stream end 20,659 of 20,686.
- **Tools:** `sector.py` and `patch_image.py` copied from MSHvSF `69c666c`.
  EDC/ECC is reproduced on all 71,908 source sectors.
- **Image:** rebuilt Track 01 `9b819618…`. Only LSN 53,722-53,729 changed;
  all sectors are valid; two builds are identical.
- **Cold boot:**
  - The rebuilt image's frames diverged from the `EMU-003` frames at second 43.
  - Control: the original booted now diverges identically, and the rebuilt
    image equals it (93/93), so the divergence comes with the time of the run.
  - The patched-build traces show no attract-time writes to the table, and
    WRAM-H noise of 6-9 bytes between any two runs.
  - D-001 annotated.
- **Pick from state 5696:** with the rebuilt image mounted, the marked table
  loads (the whole buffer equals the marked decode plus 259 fix-ups); the
  original image loads the original.
- **User play check from power-on** ("done"): two wins showed あいう in
  records 1 and 8. The session's RAM table equals the marked decode.

Checks: `./invenv.sh pytest -q` 127 passed; `ruff check`, `ruff format
--check` and `mypy` clean (EXP-0018 scripts also `mypy --strict`). Source
hashes unchanged (all 42 match `references/saturn_jp/README.md`).

Conclusion: `DISC-002` is `DONE` (**CONFIRMED**, D-013). **M2 reached.**
Next unblocked: `FONT-001`.

## 2026-10-28 — SESSION-0028 / EXP-0019: quote font found and proven

Task: FONT-001 ("Start FONT-001: find the quote font and prove its format.")

Actions and results:

- **REJECTED** as the cell writer: a CPU write to VDP1 cell `0x4A800`. A
  write log from `pre_quote` had 0 hits, though the cell changed.
- **Glyph in RAM:** absent in every layout tried. The last glyph's cell is
  also at WRAM-H `0x06024DDC`.
- **Staging-cell write log:** the writes come from `0x06024D28`-`0x06024DC0`.
  Disassembly shows the routine `0x06024CF0` and the font pointer
  `0x0602586C` (`0x002C3EA0`).
- **Decoder:** copied MSHvSF `font.py`/`font_pack.py`; only docstrings and
  CLIs changed. They decode 22/22 of the M1 quote's codes to the drawn cells.
- **Font file:** the font image equals `FIX.PRS` (209,285 bytes, uncompressed)
  and repacks byte-identically.
- **First tries at a load trace:**
  - The cold-boot header-word log over 30 s had only the BIOS clear.
  - Bisection of the `EXP-0013` states: the font loads after the Start
    press (5116 to 5169).
  - **DISPROVEN** as a disc test: a Start replay from 5116 on a probe image.
    It loads the original font, from a copy already in cart RAM in the state.
  - A halt from 5116 caught the CD-port copy loop at `0x06013120` writing
    other data into the shared buffer.
- **Controlled test:** `FIX.PRS` with one byte changed (`0x1E0B7`: `07` →
  `F8`, glyph あ). Cold boot and Start: the original image loads the original
  font (1 run); the probe image loads the probe font in 2 valid runs (a third
  could not focus the window).
- **Cart copy:** the cart copy at `0x346490` matches only up to `0xB2C0` in
  those states (cart extraction is unvalidated).

Checks: `./invenv.sh pytest -q` 134 passed; `ruff check`, `ruff format
--check` and `mypy` clean (EXP-0019 scripts also `mypy --strict`). Source
hashes unchanged (42 of 42).

Conclusion: `FONT-001` is `DONE` (**CONFIRMED**, D-014). `FONT-002` is
unblocked.

## 2026-10-28 — SESSION-0029 / EXP-0020: Latin codes, line length and grid

Task: FONT-002 ("Start FONT-002: Latin codes, line length and cell grid.")

Actions and results:

- **Atlas:** rendered all 3,584 font codes. There are five Latin sets; the
  quote-style one is at `0x0660`-`0x06FF`.
- **First reading:** a grid reading put its rows 0x10 lower than the arcade
  map. That was **wrong**: labelled single-code renders showed the arcade map
  exactly (`0x0681` = A, and so on).
- **Coverage:** all 94 mapped codes are non-empty; `@ { | }` are not ASCII
  glyphs.
- **Live trials** (`latin_trial.py`, `pre_ko`, record 10): control plus three
  38-code trials. Every drawn cell equals the decoded glyph (38/38 each); a
  second run is byte-identical; the control equals the live capture.
- **Grid:** 2 × 19 cells, all shown; 38 distinct cells allocated.
- **Capacity:** 25 of 161 arcade English win quotes fit 2 × 19 as written,
  59 after word re-wrap, 159 in 3 × 19.

Checks: `./invenv.sh pytest -q` 134 passed; `ruff check`, `ruff format
--check` and `mypy` clean (EXP-0020 scripts also `mypy --strict`). Source
hashes unchanged (42 of 42).

Conclusion: `FONT-002` is `DONE` (**CONFIRMED**, D-015). The M2 tasks are all
done. Further translation work needs the user's `GATE-TRANSLATION` decision
and new tasks for layout (fitting 102 quotes) and M3.

## 2026-10-28 — SESSION-0030: M3 tasks written (not started)

User request (verbatim): "Write up the next tasks: GATE-TRANSLATION, a layout
task for quotes that don't fit 2 × 19, and M3 (all of Ryu's quotes). Don't
start them yet."

Facts gathered for the task text (read-only, `tools.reference.xvsf_text` on
`local/ref003/xmvsf-68k.bin`):

- The arcade English win-quote slots hold 8-9 records each, and slot 18
  aliases slot 11. **Slot 9 (Ryu) has 9 English records**, against 16
  Japanese.
- Ryu's English texts are 43-50 characters, with lines of up to 25. None fits
  2 × 19 even when re-wrapped.

Written in `TASKS.md`:

| Task | Status |
| --- | --- |
| `RE-002` (selector and forcing) | `READY` |
| `LAYOUT-001` (capacity route) | `READY` |
| `PAIR-001` (Ryu's pairing; needs `RE-002`) | `BLOCKED` |
| `GATE-TRANSLATION` (now depends on `PAIR-001`; synthetic test text is outside its scope) | `BLOCKED` |
| `RE-003` (all 16 records from a rebuilt image) | `BLOCKED` |

The outline rows for `LAYOUT-001`, `RE-002` and `RE-003` were replaced by
these full tasks. No experiment was run.

## 2026-10-28 — SESSION-0031 / EXP-0021: win-quote selector found and forced

Task: RE-002 ("Start RE-002: identify the win-quote selector and force any record.")

Actions and results:

- **Reads:** a table read log from `pre_ko` gave 38 reads at `0x06066A84`
  with R8 = record 10 and MACL = 10 × 76. The code loads R8 from WRAM-H
  `0x060F2490`. The pointer is 0 through `pre_quote` and set by
  `quote_visible`.
- **Pointer write:** the write log from `pre_quote` shows the writer
  `0x0606698C`. It computes base (task + 52) + index (task + 38) × 76, or ×
  100 under a flag.
- **Index write:** the write log shows the task cleared, then the index
  stored at `0x06066696` and the base at `0x060666D0`, in the same frame as
  the pointer. The index is `RNG() & 0x0F`; the RNG is `0x06056B54`, an LCG
  mod `0x7FED` with its seed at `0x060F545A`.
- **Forcing** (`force_record.py`): `onhit` after the setter. Indices
  0/5/15, then 5/1/8, each 38/38 cells exact. The controls equal the live
  capture, and the repeats are byte-identical.

The MSHvSF method carried over (find the record pointer, then the index
setter, then force by `onhit`); every address and the random choice are
XvSF's own findings. Only one task address was seen.

Checks: `ruff check`, `ruff format --check`, `mypy` and `pytest` (134
passed) clean; `force_record.py` also `mypy --strict`. No disc change.

Conclusion: `RE-002` is `DONE` (**CONFIRMED**, D-016). `PAIR-001` is
unblocked.

## 2026-10-28 — SESSION-0032 / EXP-0022: Ryu's English pairing

Task: PAIR-001 ("Start PAIR-001: pair Ryu's Saturn records with the arcade English.")

Actions and results:

- **Saturn lead:** the selector's unused mode has 100-byte records and a
  remap table `[0..7, 0..7]` (`0x06066718`). Its two per-language base lists
  point Ryu's slot at records 0 and 16 of the loaded table.
- **Arcade search:** a raw search of `xmvsfu-68k.bin` found no copy of the
  remap table. The PC-relative tables are encrypted in ROM.
- **Disassembly:** MAME (`-debug -debugger none`, the timeline `debug` event)
  disassembled `0x04F000`-`0x04F800` from the decrypted opcodes. The selector
  `0x04F396` is the same routine as the Saturn's, with identical tables.
- **First runtime attempts:**
  - `en_r9`: a fresh NVRAM diverged from the route, so the force came too
    late. **Mistake**, fixed by copying `EXP-0009`'s NVRAM.
  - `probe`: read the language word at `0xFFD47A` (0). **Wrong address**:
    A5 − `0x2B86` = `0xFF547A`.
  - `probe2`: the right registers. Language word 2, r = 10, index 2,
    English base `0x18986E`.
- **Controlled runs** (`run_pair.py`):
  - The natural draw r = 10 gives English record 2 and Japanese record 10.
  - With Ryu's slot forced: English draws 0-15 all read record `r mod 8`;
    Japanese draws 3, 8, 9 and 15 read record `r`.
  - The draw-9 snapshots show English record 1 and Japanese record 9.
- **Pairing table:** `make_pairing.py` wrote
  `data/translations/ryu_pairing.json`, 16 entries, all CONFIRMED.

Checks: `ruff check`, `ruff format --check`, `mypy` and `pytest` clean; the
EXP-0022 scripts also pass `mypy --strict`. A stray MAME `debug.log` written
to the repository root was moved under `local/`. No disc change.

Conclusion: `PAIR-001` is `DONE` (**CONFIRMED**, D-017).
`GATE-TRANSLATION`'s dependencies are all done; it waits for the user's
decision.

## 2026-10-28 — GATE-TRANSLATION passed for Ryu's win quotes

User decision (verbatim): "GATE-TRANSLATION: go for Ryu's win quotes. Use the
k mod 8 pairing (Saturn records k and k+8 both show English record k),
official arcade English, no rewording. Record it."

Recorded in `TASKS.md` (`GATE-TRANSLATION` `DONE`, with scope, pairing and
wording) and `docs/localization_policy.md`.

- **Checked:** DOC-002, REF-001 to REF-008 and PAIR-001 are all `DONE`.
- **Scope:** Ryu's records 0-15 only; endings, other characters and specials
  stay gated.
- **RE-003:** now blocked only by `LAYOUT-001`.

No experiment was run and no files other than documentation changed.

## 2026-10-28 — SESSION-0033 / EXP-0023: LAYOUT-001, the game's own English mode

Task: LAYOUT-001 ("Start LAYOUT-001: choose how English quotes fit the quote box.")

Actions and results:

- **Renderer constants:** a nonzero language word gives a 12 px pitch and
  25 cells. Setting both global words from `pre_ko` drew a 2 × 25 English
  grid (`english_mode.py`).
- **Readers:**
  - The language word is read only by the quote code (14 sites).
  - The size word is a mode word with 45 readers, some every frame.
  - The code lives in `MMPACK.PCA`. The first catch attempt found
    `OPENPACK.PCA` overwriting the region, not the code's own load.
  - A raw and decoded search of every file found `MMPACK.PCA`.
- **Route (a) measured offline:** a census found 409 unused kanji codes;
  Ryu needs 113 pairs and the roster 430; a mock-up was rendered.
- **User decision:** "Use route (d), the game's native English mode. Build
  and test it from disc."
- **Patch version 1:**
  - A per-task flag (`+0x5C`) and renderer reads retargeted.
  - **Mistake:** I first assumed the word at `0x06066A72` was padding; it is
    a literal, caught by the originals check.
  - Live RAM: 50/50 cells.
  - Build: `prs.py` gained lazy matching and multi-entry support (greedy
    `MMPACK.PCA` was 5 bytes too large).
  - Image, cold-boot and pick checks passed.
- **Play check 1 (user):** Ryu's quotes were English and the hint was
  Japanese, but **Storm's quote was broken** (Japanese in the English grid).
  Cause: version 1 switched every speaker. **DISPROVEN:** that the selector
  change was safe for all characters.
- **Version 2:** a slot test (Ryu only) in the same block, plus the unused
  remap-table pointer.
  - A forced slot by PC-breakpoint `onhit` did not take effect.
  - The control instead came from the play session's Storm state: version 2
    equals the unpatched code byte for byte, and version 1 reproduces the
    defect.
  - Rebuilt image `1034b8d7…`; cold-boot and pick checks passed.
- **Play check 2 (user, version 2):** Ryu English; Wolverine's quote and the
  continue hint Japanese, 38/38 cells from session states.
- The version-1 image (`build/layout001_english`) was deleted, as announced.

Checks: `./invenv.sh pytest -q` 138 passed; `ruff check`, `ruff format
--check` and `mypy` clean (EXP-0023 scripts also `mypy --strict`). Source
hashes unchanged.

Conclusion: `LAYOUT-001` is `DONE` (**CONFIRMED**, D-018). `RE-003`'s
blockers are cleared. Its core (Ryu's 8 English records from disc) already
works; what remains is the compiler, provenance and full verification.

## 2026-10-28 — SESSION-0034 / EXP-0024: M3, all of Ryu's win quotes in English

Task: RE-003 ("Start RE-003: build all of Ryu's win quotes in English from the source image.")

Actions and results:

- **Round trip:** all 9 of Ryu's English records decode and re-encode
  exactly.
- **Compiler:** `tools/text/caption.py` with 7 tests.
- **Patch:** `tools/disc/english_mode.py`, promoted from the `EXP-0023`
  version-2 patch.
- **Build tool:** `tools/disc/build_english.py`, with 5 tests.
- **Spec:** `data/translations/ryu_win_quotes.json` holds addresses, hashes,
  pairing and line lengths, but no text (rule 21).
- **Build:** two builds are identical, and both equal the `EXP-0023`
  version-2 files. The image `build/re003_ryu_english` is identical to the
  play-checked image (all 42 components), so the duplicate was deleted. 138
  sectors changed, all valid.
- **Forcing the draw:**
  - **Failed:** an `onhit` write after the draw store (`0x06066666`) was
    applied but not seen by the read two instructions later (likely the SH-2
    cache).
  - **Worked:** steering through the RNG seed. A first scan read two
    different "original" seeds, a race between `loadstate` and `pause`;
    fixed by reloading until the paused seed is 8520.
  - Seeds 1-40 scanned twice, identically; 41-60 and a spread of 24 more
    found draw 7 (seed 27,029).
- **All 16 draws:** the predicted pointer, the record equal to the compiled
  bytes, and 50/50 cells; the control 38/38.
- **User play check** (cold boot): two Ryu wins in English (records 0 and 1).

Checks: `./invenv.sh pytest -q` 150 passed; `ruff check`, `ruff format
--check` and `mypy` clean (EXP-0024 scripts also `mypy --strict`). Source
hashes unchanged.

Conclusion: `RE-003` is `DONE` (**CONFIRMED**, D-019). **M3 reached.** Next
is M4 (a second character through the same mechanism), whose tasks are to be
written first.

## 2026-10-28 — SESSION-0035: M4 tasks written (not started)

User request (verbatim): "Write up the M4 tasks (a second character through
the same mechanism). Don't start them yet."

Facts gathered for the task text (read-only):

- The data track has `MC00`-`MC11.SHP` (18 files) and `MCED.SHP`.
- English win-quote slots 0-17 hold 9 records each, except slot 8 (8);
  slot 18 aliases 11.
- The original remap table at `0x06066718` is loaded only by the code the
  English-mode patch replaced (`0x06066672`), so it is a candidate for a
  slot table.

Written in `TASKS.md` (Phase I):

| Task | Status |
| --- | --- |
| `RE-004` (choose and map the second character) | `READY` |
| `RE-006` (a version-3 patch with an English-slot table) | `BLOCKED` |
| `PAIR-002` (pairing in MAME) | `BLOCKED` |
| A `GATE-TRANSLATION` extension for the new character | user decision |
| `RE-007` (generalized build of both characters, with live and play checks) | `BLOCKED` |

The `RE-004` outline row was replaced. No experiment was run.

## 2026-10-29 — SESSION-0036 / EXP-0025: Ken's quote file mapped (`RE-004`)

User request (verbatim): "Start RE-004: choose the second character and map
its quote file."

- **Choice.** The arcade's 16-bit name list (`0x503E4`) gives the slot order.
  The user picked from Ken, Wolverine, Cyclops and Zangief: "Ken
  (Recommended)". Ken is slot 10, file `MC0A`, with 9 English records.
- **Static prediction.** Decoded `MC0A.SHP` holds arcade Japanese slot 10
  records 0-15 at `0x2A4C`, then 5 ending records.
- **Session.** One user session of 186 states (`local/re004/session/`): Ken
  and Cammy won, a reset, then Gouki and Ken. The first contact sheets were
  misaligned by mixed image widths (330 and 352 px); rebuilt from per-image
  scaled copies.
- **Trace.**
  - Control from state 2973: no hit.
  - Trial: halted at `0x0600D124`, R12 = `0x0024FA4C`, R5 = `0x5ADA`
    (`MC0A.SHP`).
  - Repeat: registers and WRAM-L identical.
- **File to RAM.** The decoded file plus 302 relocation fields
  (+ base + `0x40`, 123 only 2-byte aligned). Ken's file is at
  `0x0024D000` when he is first and at `0x060B0000` when he is second. A
  recount of Ryu's file gives the same 259 fields as `EXP-0017`.
- **Slot.** At `0x06066668` (unpatched): Ken `@(6,gbr)` = `0x0014` with
  draw 14 (pointer `0x0024FE74`, as at the quote screen); Ryu `0x0012`.
- **Disproven note.** `TASKS.md` placed a partner's file at `0x060D5F94`.
  That is Rogue's record 0 in an opponent's file (base `0x060D2000`).
  Opponents' files were at `0x060C1000` and `0x060D2000`.
- **Not explained.** 8 bytes of Rogue's resident file; not pursued.

Conclusion: `RE-004` is `DONE` (**CONFIRMED**, D-020). `RE-006` and
`PAIR-002` are now `READY`.

## 2026-10-29 — SESSION-0037 / EXP-0026: Ken's pairing (`PAIR-002`)

User request (verbatim): "Start PAIR-002: pair Ken's records with the arcade
English."

- **Arcade bases** (ROM pointer tables): Japanese slot 10 `0x18137C`,
  English slot 10 `0x189166`, 9 English records.
- **MAME runs** (`EXP-0022`'s `run_pair.py`, unchanged; three batches in
  parallel, `local/pair002/r1`-`r3`):
  - the unforced control matched `EXP-0022` (r = 10, slot 12, English 2,
    Japanese 10);
  - 16 English and 4 Japanese forced draws with slot 10, all 20 at the
    predicted address.
- **On screen:** at draw 9, English record 1 and Japanese record 9
  (agent-checked against the decoder and Ken's `MC0A` record 9).
- **Fit:** 9 of 9 English records recompile exactly, and no line exceeds
  25. No policy-sensitive name appears.
- **Pairing:** `make_pairing.py` was generalized from `EXP-0022`
  (slot argument, bases from ROM). `data/translations/ken_pairing.json` has
  16 CONFIRMED entries, and English record 8 is unreachable.

Conclusion: `PAIR-002` is `DONE` (**CONFIRMED**, D-021). Next are `RE-006`
and the user's `GATE-TRANSLATION` extension for Ken.

## 2026-10-29 — SESSION-0038: `GATE-TRANSLATION` extended to Ken

User decision (verbatim): "GATE-TRANSLATION: go for Ken's win quotes. Use
the k mod 8 pairing (Saturn records k and k+8 both show English record k),
official arcade English, no rewording. Record it."

- Checked: `RE-004` and `PAIR-002` are `DONE` (`EXP-0025`, `EXP-0026`).
- Recorded under `GATE-TRANSLATION` in `TASKS.md` and in
  `docs/localization_policy.md`. Scope: Ken's Saturn records 0-15 of
  `MC0A.SHP`'s table, added to Ryu's. His ending records 16-20 and everything
  else stay gated.
- `RE-007` now waits only on `RE-006`. No experiment was run.

## 2026-10-29 — SESSION-0039 / EXP-0027: version 3, an English-slot table (`RE-006`)

User request (verbatim): "Start RE-006: let the English mode cover a set of
characters."

- **Location.** The suggested remap table (`0x06066718`) has 16 bytes, too
  few for 19 slots, and a bitmask needs a shift loop that does not fit. The
  fixed-index table at `0x060666E0` has one word per slot with values 0-7, so
  its high bytes are spare. The type-6 routine (`0x06066728`) has its own
  remap at `0x060667A8`.
- **Unused check.**
  - Static (`table_refs.py`): only the literal `0x060666D8`, loaded only by
    the fixed path at `0x06066688`.
  - Live (read breakpoint, log mode): 0 reads in 5 replays. The positive
    control on the language table logged `0x060666AE`/`0x060666B2`.
  - The "ken_fight" replay from 3302 stayed on select screens (its
    screenshots), so fights are covered by the other two fight replays.
- **Version 3** (`tools/disc/english_mode.py`: `SELECTOR_V3`,
  `slot_patches`, `patches_v3`; `check`/`apply` take a patch list). The new
  11-word block is disassembled in a unit test.
- **Seeds:** Ken's `pre_ko` pauses at seed 9501 (or 1977, one frame later);
  Ryu's at 8520.
- **Live:**
  - Ken: slot table {9} gave a screen byte-identical to the unpatched game;
    {9, 10} gave English record 6, 50/50 cells.
  - Ryu: 17 runs byte-identical to `EXP-0024` (screenshot and VDP1).
  - Storm: identical to the unpatched game, twice.
- **Observation.** Storm's quote was a CPU win, read from her file in WRAM-H
  (base `0x060C1000`, record 12). So the quote task is not always at
  `0x060F8AC0`; the patch uses r6 and does not depend on it.

Checks: `pytest` 157 passed; `ruff check`, `ruff format --check`, `mypy` and
`mypy --strict` on the EXP-0027 scripts are clean.

Conclusion: `RE-006` is `DONE` (**CONFIRMED**, D-022). `RE-007` is `READY`.

## 2026-10-29 — SESSION-0040 / EXP-0028: Ryu and Ken from the source image (`RE-007`)

User request (verbatim): "Start RE-007: build Ryu and Ken from the source
image."

- **Specs.** `make_spec.py` is generalized from `EXP-0024`. With Ryu's
  arguments it reproduces `ryu_win_quotes.json`, apart from the description.
  It wrote `ken_win_quotes.json` (slot 10, `MC0A.SHP;1`, `0x2a4c`), and a
  rerun reproduces that file byte for byte.
- **Build tool.** `tools.disc.build_english` now:
  - takes several specs and applies version 3 with their slots;
  - rejects a repeated slot or file;
  - keeps version 2 behind `--patch-version 2`;
  - builds the image in one command with `--image DIR`.

  The version-2 Ryu build still gives `EXP-0024`'s `MC09`.
- **Image** `build/re007_ryu_ken_english`, Track 01 `b5dd07c2…`:
  - `MC09` `507b1f46…`, `MC0A` `585f9e99…`, `MMPACK` `6d7e50a0…`;
  - 71,908 sectors valid, layout unchanged, builds b1 = b2 = b3;
  - the decoded code differs in 42 bytes, all at the version-3 sites;
  - source Track 01 still `c904a386…`.
- **Seeds (Ken).** Seeds 1-60 cover all 16 draws, and a repeat agreed.
  Chosen seeds: `[15,20,25,2,35,24,4,9,7,12,1,3,8,13,5,10]`.
- **Forced draws** (built files):
  - Ken: 17/17 as predicted. The control is 38/38 at 16 px; the draws are
    50/50 at 12 px.
  - Ryu: 17/17, byte-identical to `EXP-0024`.
- **Disc.** Pick loads equal the built file plus fix-ups: Ryu 259 (106),
  Ken 302 (123). The cold boot has the v3 bytes, and only slots 9 and 10
  are marked.
- **Play check.**
  - The first recorder stopped at frame 4,685: no agent reply within 10 s
    in the attract demo. Mednafen ran on at full CPU, and requests with 10 s
    and 30 s timeouts got no reply. When the user returned (they had been
    away), it answered at frame 206,743. Recording restarted in
    `local/re007/session2`. Cause unknown (`docs/known_unknowns.md`).
  - The user played: Ryu (with Cammy) won in English, Rogue's CPU win quote
    and the continue hint were Japanese, and Ken (with Gouki) won in English.
  - `play_pointers.py`: Ryu `0x0024F704` (`MC09` English 3), Ken
    `0x0024FD08` (`MC0A` English 7), continue `0x0608583C`.
  - Contact sheets came from per-image scaled copies with ffmpeg (no
    Pillow in the venv).
- **Not observed:** a win finished by the second member, and a CPU win by
  Ryu or Ken.

Checks: `pytest` 162 passed; `ruff check`, `ruff format --check`, `mypy`, and `mypy --strict` on the EXP-0028 scripts (`MYPYPATH=research/experiments/EXP-0025`) are clean.

Conclusion: `RE-007` is `DONE` (**CONFIRMED**, D-023). M4 is reached. M5
(`RE-005`) is outline only and needs a full task and a user decision.

## 2026-10-29 — SESSION-0041: M5 tasks written (not started)

User request (verbatim): "Let's continue on to M5, then."

M4 is confirmed (`RE-007`, D-023), so M5 may begin (rule 8). Facts used for
the task text (read-only): the 19 quote files `MC00`-`MC11` and `MCED` on the
data track (`references/saturn_jp/iso_listing.json`), the MSHvSF Phase 3
method (`docs/playbook_from_mshvsf.md`, at most HYPOTHESIS here), and
`EXP-0008`, `EXP-0022`, `EXP-0025`, `EXP-0028`.

Written in `TASKS.md` (Phase J):

| Task | Status |
| --- | --- |
| `RE-005` (census of quote files against arcade slots) | `READY` |
| `RE-008` (roster and exceptions, user decision) | `BLOCKED` |
| `PAIR-003` (pairing for every roster slot in MAME) | `BLOCKED` |
| `RE-009` (every roster file fits its sectors) | `BLOCKED` |
| A `GATE-TRANSLATION` extension for the roster | user decision |
| `RE-010` (roster image, every record live, structural play check) | `BLOCKED` |
| `RE-011` (regression references) | `BLOCKED` |

The `RE-005` outline row was replaced. No experiment was run.

## 2026-10-29 — SESSION-0042 / EXP-0029: census of the quote files (`RE-005`)

User request (verbatim): "Start RE-005: census the quote files against the
arcade slots."

- **Census** (`census.py` to `data/text/slot_census.json`; a rerun is
  byte-identical):
  - Each of `MC00`-`MC11` holds one 16-record table, equal to arcade
    Japanese slot `xx`. Then come 4-12 Japanese ending records (counted
    only).
  - Every stream ends in its last sector.
  - English: 9 records per slot for slots 0-17, 8 for slot 8 (Apocalypse).
    Slot 18 aliases slot 11 in both languages.
- **Pitfall.** The first run labelled slot `s` with name-list entry `s`. The
  list's first 32-byte entry is blank, so slot `s` is entry `s + 1`. Fixed;
  the names then agree with every slot seen in play.
- **`MCED`.** It holds no quote or ending record of any slot. A scan for
  runs of text-like words (`0x0020` or `0x09E0`-`0x0DFF`, at least 38)
  found three runs of 40-50 codes at `0x654E`-`0x66A1`. For comparison,
  `MC09` and `MC08` each have one long run at their table. Not decoded.
- **Live** (`catch_pick.py`, state 3193, cursor on Cyclops as Ken's
  partner; range `0x060B3C60`-`0x060B4333` and the mirror):
  - Control: no event.
  - Trial and repeat: halt at `0x0600D124` (frames 308 and 315) with
    identical registers. R5 = `0x8A53` (only `MC01` has this size), base
    `0x060B0000`, R12 = `0x060B3C60`.
  - In both dumps WRAM-H `0x060B0000`-`0x060B3C5F` equals decoded `MC01`.
    The dumps differ in 6,252 bytes, none in the file.
- **Mypy pitfall:** reusing `endings` for an int and a dict in `census.py`
  failed strict typing; renamed.

Checks: `pytest` 162 passed; `ruff check`, `ruff format --check`, `mypy`, and `mypy --strict` on the EXP-0029 scripts are clean.

Conclusion: `RE-005` is `DONE` (**CONFIRMED**, D-024). `RE-008` (the roster
decision) is `READY`.

## 2026-10-29 — SESSION-0043: M5 roster chosen (`RE-008`)

User request (verbatim): "Start RE-008: choose the M5 roster and its
exceptions."

- **Evidence offered.** The select grid in the `EXP-0025` session (frame
  3083, enlarged and read by the agent) shows 16 portraits:
  - Magneto, Juggernaut, Dhalsim, Vega;
  - Sabretooth, Storm, Chun-Li, Zangief;
  - Gambit, Rogue, Cammy, Nash;
  - Wolverine, Cyclops, Ryu, Ken.

  Gouki (slot 15) and Apocalypse (slot 8, the boss) are not on it.
  Census facts from `EXP-0029`.
- **Question.** Options: the 16 on the grid (recommended); 16 plus Gouki;
  all 18 with Apocalypse.
- **Answer** (verbatim): "All 18, with Apocalypse".
- **Written:**
  - `data/text/m5_roster.json`, generated from `data/text/slot_census.json`
    by an inline script: slots 0-17, the file and table offset from the
    census, American names from `docs/names.md`, and spec paths for Ryu and
    Ken;
  - `docs/coverage_exceptions.md`: `MCED`, slot 18, ending records, English
    record 8, and the rule-24 permission for Gouki's and Apocalypse's
    ordinary win quotes.
- **`TASKS.md`:** `RE-008` is `DONE`; `PAIR-003` and `RE-009` are `READY`.
  `RE-010` gained a fallback for Apocalypse's play check.

No experiment was run.

## 2026-10-29 — SESSION-0044 / EXP-0030: pairing for the whole roster (`PAIR-003`)

User request (verbatim): "Start PAIR-003: confirm the pairing for every
roster character."

- **Timing.** One `run_pair.py` run takes about 8 s. Batches of 20 runs per
  slot ran 6 at a time, about 7 minutes per full set.
- **First batch** (`local/pair003`, `EXP-0022/run_pair.py` unchanged):
  - English 288/288 as predicted.
  - On slots 0-5, 23 of 24 Japanese runs logged no text read. The script
    logs reads only from `0x180000`, and those records sit at
    `0x17E3FC`-`0x17FFFF`. Sabretooth's draw 15 (`0x180030`) was logged.
  - The steps (D1 and index) were right in all runs.
  - The first pairing files, written despite the failures, were deleted.
    `make_pairing.py` now writes nothing for a slot with a failed run.
- **Fix:** `EXP-0030/run_pair.py` is a copy with `READ_START = 0x17E000`.
- **Rerun** (`local/pair003b`): 360/360 as predicted. English reads are
  identical to the first batch, and the controls repeat (`0x189936`,
  `0x181FF4`). Ryu's and Ken's English addresses agree with their files.
- **Fit check:** 161 records (144 shown) recompile exactly; the longest
  line is 25 codes, and no `@ { | }` codes are used. Names: "Bison" in
  Cammy's English records 0 and 4 only. `docs/names.md` counts 4 "Bison"
  mentions across all English text, so the other 2 are in endings or
  hints.
- **Reproduction:** the pairing files and `m5_english_fit.json` regenerate
  byte for byte.

Checks: `pytest` 162 passed; `ruff check`, `ruff format --check`, `mypy`, and `mypy --strict` on the EXP-0030 scripts are clean.

Conclusion: `PAIR-003` is `DONE` (**CONFIRMED**, D-025). Next: `RE-009`;
the gate extension is the user's.

## 2026-10-29 — SESSION-0045 / EXP-0031: sector fit for the roster (`RE-009`)

User request (verbatim): "Start RE-009: check that every roster file fits
its sectors."

- **Method.** `fit_sectors.py` takes each slot's English records 0-7 from
  the US program, with a recompile check, and writes them over the
  census's table. It then rebuilds with `build_mc`, the build's own path,
  and compares the decode with the original outside the English area. It
  runs in about 2.5 minutes.
- **Result.** 18/18 fit. Margins run from 175 bytes (`MC08`) to 1,176
  (`MC0B`).
  - Every rebuilt file has its original size, ends its stream in its last
    sector, and is unchanged outside the English bytes.
  - The project encoder beats every original file by 0.7-3.7 %. The English
    edit grows the stream for 7 files (28-82 bytes) and shrinks it for 11.
- **Cross-check.** Ryu's and Ken's rebuilt hashes equal `EXP-0028`'s
  (`507b1f46…`, `585f9e99…`). A second run was byte-identical.
- **Answered:** the known unknown "Will longer (English) quote files fit 11
  sectors?".

Checks: `pytest` 162 passed; `ruff check`, `ruff format --check`, `mypy`, and `mypy --strict` on the EXP-0031 script are clean.

Conclusion: `RE-009` is `DONE` (**CONFIRMED**, D-026). `RE-010` waits on the
user's gate extension for the roster.

## 2026-10-29 — SESSION-0046: `GATE-TRANSLATION` extended to the M5 roster

User request (verbatim): "Let's do the GATE-TRANSLATION extension for the
M5 roster."

- Prerequisites checked: `RE-005`, `RE-008`, `PAIR-003` and `RE-009` are
  `DONE`.
- **Question 1** (scope, pairing, wording; options: go; go but not
  Apocalypse; not yet). Answer: "Go (Recommended)".
- **Question 2** ("Bison" in Cammy's English records 0 and 4; options: keep
  as written; keep, and require "Vega" in a Saturn-names build now).
  Answer: `Keep "Bison" (Recommended)`.
- Recorded under `GATE-TRANSLATION` in `TASKS.md` and in
  `docs/localization_policy.md`. `RE-010` is `READY`.

No experiment was run.

## 2026-10-29 — SESSION-0047 / EXP-0032: the roster image (`RE-010`)

User request (verbatim): "Start RE-010: build the roster image and verify
it." Mid-session the user added: "we need to translate the 4MB cart
message that pops up when you try to load the game without the ram cart"
(added as `UI-004`, backlog, order not yet set). They also asked: "update
the repo-level README.md because it looks really stale" (done). After the
play check they noted "some dialogue right as Apocalypse appears that needs
translation" (captured; `SPECIAL-001` boss pre-fight text).

- **Specs.** `EXP-0028`'s `make_spec.py` gave Cammy (slot 17) no unused
  record, because slot 18 aliases slot 11. The copy
  `EXP-0032/make_spec.py` uses the census's count. Ryu's and Ken's specs
  reproduce; Ken's byte for byte.
- **Build.** Two builds with 18 specs, one with `--image`.
  `image_checks.py` passed:
  - only Track 01 differs (`36672c5d…`); the source matches the manifest;
  - 0 invalid sectors; the layout is the same;
  - the changed files are exactly `MC00`-`MC11` and `MMPACK.PCA`
    (`4e81b64f…`);
  - `b1` = `b2`;
  - 58 code bytes, all at `patches_v3(0-17)` sites;
  - the MC files equal `EXP-0031`'s rebuilds.
- **Records.** `force_records.py` writes each character's 800 English bytes
  into Ryu's table at `pre_ko` with the roster code.
  - Pitfall: five of six parallel groups died at start. Mednafen's lockfile
    refuses a second instance on one home unless `MEDNAFEN_ALLOWMULTI=1`.
    They were rerun with it.
  - Result: 144/144 at 50/50 (12 px). The 6 controls are 38/38 and
    identical.
- **Ryu and Ken.** `EXP-0032/force_draws.py` (roster slot table): 17 + 17
  runs byte-identical to `EXP-0028`.
- **Picks.** `pick_roster.py` (scratch home `local/mednafen_pick`, pad
  directions on I/M/J/L) from state 2973. 14 of 16 passed first time.
  - Storm: A was not registered.
  - Juggernaut: the lefts were dropped, so Vega was picked.
  - Both retries passed.
  - Gouki: "uuuuu" from state 9348 stopped on Juggernaut; the cell's
    entry move is unknown (`docs/known_unknowns.md`).
- **Play check** (`local/re010/session`, 1,074 shots, the newest 200
  states): no recorder stall. Quote screens were found by the bubble
  colour; 42 hits, two of them false (ranking, super flash).
  - English: Gouki first member (record 1), Cyclops second member (0),
    Storm CPU (4), Nash (5, 4), Ken second member from WRAM-H (4, 5), and
    Apocalypse CPU from `0x060C1000` (0).
  - Records were named by pointer where a state survived. Otherwise the text
    was matched locally against the roster's English, one record each.
  - The continue hint is Japanese and normal (frames 29244 on).
  - Apocalypse's pre-fight line, a Japanese top-screen box at frames
    58,191-58,366, was added to `docs/text_surfaces.md`.
- **README.** Rewritten: the status, what is still Japanese, the build
  command and its inputs.
  - Gap: no command writes `local/ref003/xmvsfu-68k.bin`. It is noted under
    `RE-011`, where a clean-checkout run needs it.

Checks: `pytest` 162 passed; `ruff check`, `ruff format --check`, `mypy`, and `mypy --strict` on the EXP-0032 scripts (`MYPYPATH=research/experiments/EXP-0025`) are clean.

Conclusion: `RE-010` is `DONE` (**CONFIRMED**, D-027). `RE-011` is `READY`;
M5 closes with it.

## 2026-10-29 — SESSION-0048 / EXP-0033: regression references (`RE-011`)

User request (verbatim): "Start RE-011: regression references for the
confirmed builds."

- **Program image.** `tools.reference.xvsf_text` gains `--program-out`
  (`--out` becomes optional; one of them is required). The output
  `1b1a5a26…` is byte-identical to `local/ref003/xmvsfu-68k.bin`. Two unit
  tests were added.
- **References.** `data/regression/references.json` was written from the
  confirmed builds' outputs (`local/re003/b1`, `local/re007/b1`,
  `local/re010/b1`, the three `build/` images): 2, 3 and 19 files, plus
  Track 01 for each.
- **Tool.** `tools.disc.regression`:
  - checks the inputs (exit 2 if they differ; a missing source counts as
    differing);
  - rebuilds under `build/regression/<name>/` (deleting only there; the
    guard is unit-tested);
  - compares the hashes and deletes each image after hashing unless
    `--keep`;
  - writes the report with `--report`;
  - takes `--references` for controls.
- **Runs:**
  - Working copy: 3/3 match, 5 min 24 s.
  - Altered `MC09` hash: `MISMATCH`, exit 1.
  - The tooling was committed locally (`2d4d224`) so a fresh clone could
    hold it.
  - Clean clone in the scratchpad (symlinks for the source folder,
    `cps2.cpp` and the ROM folder; `tools` imported from the clone):
    program image `1b1a5a26…`, 3/3 match (27 hashes), 5 min 20 s.
  - Its report is `docs/regression_report.md`.
- **Docs.** The README's build section now gives the program-image command
  and the regression command.

Checks: `pytest` 167 passed; `ruff check`, `ruff format --check` and `mypy` are clean.

Conclusion: `RE-011` is `DONE` (**CONFIRMED**, D-028). **M5 is complete.**
Next: M6 (endings) needs its tasks written; nothing in it has started.

## 2026-10-29 — SESSION-0049: M6 tasks written (not started)

User request (verbatim): "Write up the M6 tasks for the endings. Don't start
them yet."

M5 is complete (D-027, D-028), so rule 23 allows ending investigation.
Facts gathered for the task text (read-only):

- **Arcade English ending table** (`0x17E318`): per-slot record counts
  are 6, 9, 6, 6, 5, 6, 6, 7, 7, 7, 4, 6, 6, 5, 5, 6, 6, 13, 6 (slots
  0-18).
  - English pointers: slot 9 equals slot 8, and slot 18 equals slot 11.
  - Japanese table (`0x17E2CC`): slot 8 equals slot 7, and slot 18 equals
    slot 11.
- **Saturn after-table counts** (`data/text/slot_census.json`) differ from
  these, for example Cyclops 7 against 9 and Juggernaut 9 against 6.
- `EXP-0023`: the type-4 selector `0x060668A2` shares the renderer
  `0x06066948`. Its language read has been 0 since version 2.
- The `RE-010` session kept states from the Apocalypse fight (57999-63975).

Written in `TASKS.md` (Phase K):

| Task | Status |
| --- | --- |
| `END-001` (choose an ending, reach it, inventory its surfaces) | `READY` |
| `END-002` (font, code, grid; English-mode reachability; patch regression) | `BLOCKED` |
| `END-003` (RAM records, disc writers, marker edit, file census) | `BLOCKED` |
| `END-004` (MAME no-play route, English per surface, indexing, pairing) | `BLOCKED` |

The outline row `END-001` was replaced. The M7 and M8 rows are now
`END-005` and `END-006`. No experiment was run.

## 2026-10-29 — SESSION-0050: Nash's ending reached and inventoried (END-001, EXP-0034)

User request (verbatim): "Start END-001: choose an ending and reach it."
The user's choice (verbatim): "Nash (Recommended)". Nash is slot 16
(`MC10`): 6 arcade English ending records, 6 after-table records.

- **Session.** Cold boot of the untouched image (Track 01 `c904a386…`
  checked), user playing, `tools.mednafen.session_recorder --state-interval 3
  --keep-states 0`. 18:30-19:38 UTC, frames 134-229,689, 3,935 screenshots,
  1,345 states (6.5 GB, all kept). The game sat on the pause screen for most
  of the session while the user was away; the recorder did not stall.
- **Finding the ending.** ffmpeg contact sheets (every 30th shot, then every
  2nd over the end) and region hashes of the text box and picture window
  per shot. Every cited screenshot was checked by the agent, the speaker
  labels at 6× zoom.
- **Route.** Pre-boss story line, Apocalypse (K.O. ~216,444), a black
  screen with Nash and `⚠乱入禁止`, a win quote, then **Nash against Ryu**
  (his partner). K.O. at 220,117. Ending pages 220,539-222,930, staff roll,
  `GAME OVER`, initials, attract.
- **Ending.** Six timed pages; Latin labels `Nash`, `Nazo no koe`, `Nash`,
  `Nash's friend` on pages 3-6. Text not copied (rule 21).
- **Mid-session note from the user** (verbatim): "It looks like, in the
  top right, there's some sort of message with a warning indicator." It is
  `⚠乱入禁止` ("no challengers"), already in the inventory; added to the
  `UI-001` row.
- **Repeatability.** `replay_ending.py` from `f00220064` (after the last
  hit), two processes with `MEDNAFEN_ALLOWMULTI=1`: r1 = r2 at all 7
  targets; the 6 pages equal the session's screenshots (image, box,
  picture). The credits frame differs from the session by a ~3 px scroll
  (same names); attributed to screenshot timing, not checked further.
- **Partner fight lost.** From `f00217852` with no input for 9,000 frames:
  Ryu wins, `CONTINUE?`, `GAME OVER`; no ending.
- **Kept.** 12 checkpoints copied to `local/checkpoints/end001/` (hashes in
  `EXP-0034`). The full session states remain in `local/end001/session/states`
  (6.5 GB; about 12 GB free on the disk).
- **Team rule.** Not separable in one run (Nash was first pick, point and
  partner-fight winner); SUPPORTED only, left to `END-004`.

Docs: `EXP-0034`, D-029, `docs/text_surfaces.md` (new section),
`docs/known_unknowns.md` (4 new rows), `TASKS.md` (`END-001` DONE; `END-002`
and `END-004` READY).

Checks: `pytest` 167 passed; `ruff check`, `ruff format --check` and `mypy --strict tools tests` are clean; `mypy` on `replay_ending.py` is clean.

Conclusion: `END-001` is `DONE` (**CONFIRMED**, D-029). Next: `END-002` and `END-004`.

### SESSION-0050 follow-up: checkpoints pruned; UI-004 widened

User request (verbatim): "Yes, let's delete the checkpoints you didn't keep.
Additionally, make sure you add to the backlog to translate any error
messages that come up when you first load the game (like ones that are
related to not having a 4M RAM cart, etc.)"

- The 12 kept checkpoints in `local/checkpoints/end001/` were compared
  byte for byte (`cmp`) with their session originals (all equal). Then
  `local/end001/session/states` (1,345 states, 6.5 GB) was deleted. The
  session's screenshots and index remain. Free disk space: 18 GB.
- `UI-004` now covers every error or warning the game shows when it first
  loads, not only the cart warning. Its first step is to list them; the
  Saturn BIOS's own messages are out of scope. The README's "Still
  Japanese" list now names these and the "no challengers" warning.

## 2026-10-29 — SESSION-0051: How Nash's ending is drawn (END-002, EXP-0035)

User request (verbatim): "Let's continue on with END-002. Do we have plans
to see if Akuma, Bison, and Charlie are currently present as text that can
be substituted in for Gouki, Vega, and Nash?"

- **Names question:** answered from `docs/names.md` and `LOC-001` (after
  M8). The select labels are art, and no name is plain text on the disc
  (`EXP-0011`). During this experiment a Latin `Charlie` speaker label
  appeared in English mode; it was added to `docs/names.md`.
- **Code** (`trace_pages.py`, runs `trace1` and `trace2`): the type-4
  selector hit at pages 1, 3, 5 and 6 (scene starts) and the renderer once
  per page. No other selector hit. Quote pointer `0x0024FEC0` + 76k for
  pages 1-6, equal to decoded `MC10` records 16-21.
- **Disassembly:** the first attempt used base `0x06014000` and gave
  garbage. The decoded `MMPACK.PCA` starts at `0x06014BA0` (second entry
  `0x0601F000` minus the first entry's 42,080 bytes).
- **Font:** `cell_check_en.py` (EXP-0023) on the six pages: 38/38 or 76/76
  exact. Zero test (`zero_cell.py`, page 3): 139 pixels in one cell; the
  first glyph vanished (checked at zoom).
- **Modes** (`ending_modes.py`):
  - The first run (`modes1`) crashed reading the English pointer
    `0x09EC0B8E` (not work RAM); the script now records that.
  - In `modes2`, v3 equals control at all six pages.
  - English: 2 × 25 at 12 px, empty or meaningless text, a black picture
    and a `Charlie` label at 222,037.
- **Lists at run time:** language 0 holds Nash, Ryu and Apocalypse bases
  and placeholders elsewhere. Language 2 holds no addresses.

Docs: `EXP-0035`, D-030, `TASKS.md` (`END-002` DONE; `END-003` READY),
`docs/known_unknowns.md`, `docs/names.md`.

After the runs, `ruff format` reflowed the three scripts, one docstring line was shortened and the list read in `ending_modes.py` became a hex string of the same 4 bytes. None of these changes what is run or read; the scripts were not re-run.

Checks: `pytest` 167 passed; `ruff check`, `ruff format --check` and `mypy --strict tools tests` are clean; `mypy` on each EXP-0035 script is clean.

Conclusion: `END-002` is `DONE` (**CONFIRMED**, D-030). Next: `END-003` and `END-004`.

## 2026-10-29 — SESSION-0052: Where Nash's ending text lives (END-003, EXP-0036, in progress)

User request (verbatim): "Keep LOC-001 after M8; continue with END-003 or
END-004 next." The agent chose `END-003`, which follows directly from
`EXP-0035`'s RAM records.

- **Write logs on the six records** (`write_log.py`):
  - untouched image, frames 210,163-222,100: 0 writes;
  - marker image, frames 210,163-220,700: 0 writes, original bytes kept.

  So `MC10` is not reloaded from the boss stage on, and the screen check
  needs a run from the pick.
- **RAM write** (`ram_write.py`): `0x0AF4` → `0x09F2` in record 18 before
  page 3. One cell changed (139 px, x 27-40, y 187-200; 何 → こ at zoom),
  and its VDP1 data is the new glyph.
- **Marker build:**
  - `make_marker.py`: 8 bytes at decoded `0x2EC0`; re-encoded
    `026ab640…`, same size (23,913).
  - Image `build/end003_marker`: Track 01 `547359de…`, 12 sectors changed
    (LSN 53,813-53,824), all sectors valid.
- **Pick** (`pick_writer.py`, from `re004/f00002973`, key `u`):
  - The first try failed: Mednafen was not frontmost, so no key was sent.
    A retry loop was added.
  - Untouched image: 114 writes, all from `0x0600D124` (R5 `0x5D69`, R6
    `0x0024D000`). The buffer equals MC10 plus 263 fix-ups.
  - Marker image: the same writer. The records hold the marker, and the
    buffer equals the marker file plus fix-ups.
- **Census** (`census_endings.py` → `data/text/ending_census.json`):
  - Slots 0-16 hold the whole arcade Japanese ending block at table +
    `0x4C0`.
  - Cammy (17): 12 records; the arcade block is unbounded.
  - Apocalypse's file has text-like data after his 4 records.
  - The English counts reproduce `SESSION-0049`'s list.
  - The first run crashed: the English blocks run past `ENGLISH_END`, so
    the bound became `0x18D81A`, where the hints start.

Checks: `ruff check` clean; `mypy --strict` on each EXP-0036 script, with
`MYPYPATH` set to the EXP-0025, EXP-0029, EXP-0032 and EXP-0035 folders, is
clean.

Status: `END-003` stays `IN_PROGRESS` until the user's play check on the
marker image shows the marker on screen.

### SESSION-0052 follow-up: the marker play check (END-003 done)

The user played the marker image from a cold boot to Nash's ending and said
"done".

- **Session:** `local/end003/session`, 21:49-22:05 UTC, frames 258-53,202,
  901 screenshots, the last 150 states kept. Nash and Ryu again; Nash won
  the partner fight.
- **Found:** from contact sheets of the last 300 shots (every 5th), page 1
  starts これは！.
- **Text-box hashes** against `EXP-0034`: page 1 differs; pages 2-6 are
  identical.
- **Page 1 whole-screen diff** (`f00050550` against `f00220654`): 550
  pixels in x 27-88, y 187-200 (four cells). Checked at zoom.
- **Kept:** `local/checkpoints/end003/f00050471.mcs` and
  `f00050643.mcs`.
- Two new rows in `docs/known_unknowns.md`: Cammy's block end, and the text
  after Apocalypse's records.

Conclusion: `END-003` is `DONE` (**CONFIRMED**, D-031). Next: `END-004`.

## 2026-10-29 — SESSION-0054: Arcade English and indexing for Nash's ending (END-004, EXP-0037)

User request (verbatim): "Start END-004: arcade English and indexing for
Nash's ending."

- **Route discovery** (`discover1`, `discover2`):
  - The arcade select cursor starts on Cyclops; Up, Right, Right reach
    Charlie.
  - Work-RAM dumps of an idle fight gave the fighter blocks at `0xFF4200`
    + 0x400·n, with vitality at +`0x10`.
  - Zeroing `0xFF4610` and `0xFF4E10` every 20 frames won every fight,
    through Apocalypse and the partner fight, to Charlie's English ending
    (34 s run).
- **Predictions** were committed (`91be3e3`) before any read-logged run.
- **Partner mistake:** the first "Ryu" run pressed Right too early and
  picked Cyclops again. This was caught by checking its snapshots, not its
  reads. The timing was fixed, all four runs regenerated and rerun, and
  the Ryu pick was checked on the select snapshot and in the partner
  fight.
- **Reads:** English `0x18D0AE` + 100k and Japanese `0x1856E0` + 76k,
  k = 0-5, identical across partners. The table is re-read at pages 1, 2,
  4, 5 (English) and 1, 3, 5, 6 (Japanese).
- **Screens:** the arcade Japanese ending equals the Saturn's. The English
  ending has other scene breaks and pictures, and the labels `Charlie` and
  `Charlie's friend`, so prediction 4 (no labels) is refuted. `NO
  CHALLENGERS` replaces the warning.
- **Pairing:** `make_pairing.py` → `data/translations/nash_ending_pairing.json`,
  6/6 CONFIRMED (24/24 reads). Names flagged: records 1 and 4 ("Charlie").

Docs: `EXP-0037`, D-032, `TASKS.md` (`END-004` DONE, M6 complete),
`docs/known_unknowns.md`, `docs/names.md`, `docs/text_surfaces.md`.

Checks: `pytest` 167 passed; `ruff check` and `ruff format --check` clean; `mypy --strict tools tests` and each EXP-0037 script clean. Regenerating a timeline and the pairing file gave byte-identical outputs.

Conclusion: `END-004` is `DONE` (**CONFIRMED**, D-032). **M6 is complete.** Next: write the M7 tasks (not started).

## 2026-10-29 — SESSION-0055: M7 tasks written (not started)

User request (verbatim): "Write up the M7 tasks for localizing Nash's
ending. Don't start them yet."

Written in `TASKS.md` (Phase L), from D-029 to D-032 and `EXP-0031`'s
`MC10` margin (671 bytes):

| Task | Status |
| --- | --- |
| `END-005` (the Saturn's English ending script: language reads, a clean per-ending RAM trial against the arcade snapshots, label storage) | `READY` |
| `LAYOUT-002` (the user chooses: English script, or Japanese script with English text, or another option `END-005` finds; labels) | `BLOCKED` |
| `GATE-TRANSLATION` extension for Nash's ending (scope, pairing, wording, "Charlie") | waits on `LAYOUT-002` |
| `END-006` (version-4 code, per slot) | `BLOCKED` |
| `END-007` (English records in `MC10`, fit, spec) | `BLOCKED` |
| `END-008` (build from the untouched source and a user play check) | `BLOCKED` |
| `END-009` (regression reference) | `BLOCKED` |

The outline row `END-005` (M7) was replaced. The M8 row is now `END-010`,
and `docs/known_unknowns.md`'s reference to it was updated. No experiment
was run.

## 2026-10-29 — SESSION-0056: The Saturn's English ending script (END-005, EXP-0038)

User request (verbatim): "Start END-005: the Saturn's English ending
script."

- **Read log** on `0x060F5478`-`0x060F547B` over the ending. The agent's
  hit lines have no address, so readers were identified from their code:
  - four size-word mode checks every frame;
  - per scene: `0x060D4738` (new) and the selector;
  - per page: the six renderer sites;
  - ten others before page 1.
- **`MCED.SHP`** = the ending overlay at `0x060D2000`: decoded file + 317
  relocations, 18 bytes of variables. The routine at `0x060D4710` picks the
  slot's script and the language's script from header words. Nash's two
  scripts were parsed:
  - JP: scenes 0-1 | 2-3 | 4 | 5;
  - EN: scenes 0 | 1-2 | 3 | 4-5.

  Label bytes index a 40-entry name list (decoded `0x3DA8`).
- **Free RAM:** `0x00259050`-`0x0025E3DF` stays zero at the K.O., at page
  1 and after the credits (three debugger dumps).
- **Trial** (`english_trial.py`): eight `00BD` → `E002` reads, the
  language-2 list repointed to a one-entry list, and six arcade English
  records in free RAM. The pointer stepped through `0x00259200` + 100k
  about every 390 frames. The screens match the arcade English snapshots
  page for page, and the cells match 50/50 or 100/100. Global words 0;
  scratch otherwise untouched.
- **Label edit** (`label_write.py`): `Nash` → `Xash` on page 3, 27 px in
  one letter cell.

Checks: see below.

`ruff format` reflowed `word_reads.py` after its run; nothing it runs or reads changed.

Checks: `pytest` 167 passed; `ruff check`, `ruff format --check` and `mypy --strict tools tests` clean; `mypy --strict` on each EXP-0038 script clean (`MYPYPATH=research/experiments/EXP-0035`).

Conclusion: `END-005` is `DONE` (**CONFIRMED**, D-033). `LAYOUT-002` is ready: the user chooses, after option (b) has its own RAM trial.

## 2026-10-29 — SESSION-0057: Layout for Nash's English ending (LAYOUT-002, EXP-0039)

User request (verbatim): "Start LAYOUT-002: choose how Nash's ending shows
English."

- **Option (b) trial:** `english_trial.py` gained `japanese-script`, which
  leaves the `MCED` script reader at its original byte; 10 writes. The
  English records ran on the Japanese timing (~4.3 s per page) under the
  Japanese pictures and labels. Pages 3-5 mismatch: the scream under `Nazo
  no koe`, and the dog-tag line labelled `Nash` over a black picture.
- **Shown to the user:** a 2 × 6 comparison image of options (a) and (b)
  (sent to the user, not committed).
- **User answers** (verbatim): "(a) English layout (Recommended)";
  "Arcade names (Recommended)". Recorded in `docs/localization_policy.md`
  and under `LAYOUT-002`.

`ruff check` and `mypy --strict` (`MYPYPATH=research/experiments/EXP-0035`)
on the changed `english_trial.py` are clean.

Conclusion: `LAYOUT-002` is `DONE`. Next: the `GATE-TRANSLATION` extension
for Nash's ending.

## 2026-10-29 — SESSION-0058: GATE-TRANSLATION extended to Nash's ending

User decision (verbatim): "GATE-TRANSLATION: go for Nash's ending. MC10
ending records 16-21 plus whatever the English script needs; page k shows
English record k; official arcade English with no rewording; keep "Charlie"
in the text and the labels Charlie and Charlie's friend. Record it."

- Checked at acceptance: `END-001` to `END-005` and `LAYOUT-002` are
  `DONE`.
- Recorded under `GATE-TRANSLATION` (gate extension, Nash's ending), in the
  M7 gate subsection and in `docs/localization_policy.md`.
- `END-006` and `END-007` are now `READY`; `END-008` waits on them only.
- No experiment was run.

## 2026-10-29 — SESSION-0059: Version 4, English endings per slot (END-006, EXP-0040)

User request (verbatim): "Start END-006: code to turn the English ending on
for Nash only."

- **Design:**
  - Every PC-relative load and absolute long in the decoded `MMPACK.PCA`
    was searched. Only the type-4 selector reads `0x0606690C`-`0x0606691F`,
    so that space holds the new literals.
  - The selector was rewritten in place (23 words) to use the language-0
    list always and, for marked slots, pointer − `0x1A0` (quote table +
    800) and task flag 2.
  - Marking is bit 7 of the fixed-table low byte.
  - The `MCED` script switch is a data change (header word 0 = word 1),
    found while reading the header format: no `MCED` code change is needed.
- **Encoding:** checked by disassembling the patched decoded code.
- **`v4_trial.py`:** v4_off = control at 91/91 frames. v4_on =
  `EXP-0038` English at 90/91; the exception is the picture window during
  page 5's fade-in, identical one sample later.
- **`win_regression.py`:** 8 draws × {v3, v4, v4 with Ryu's slot marked}:
  no difference.
- **`fit_check.py`:** `MMPACK.PCA` rebuilds to size (`276d534c…`).
  `MCED.SHP` has a 204-byte margin (`cca9332d…`).
- **Promoted** to `tools/disc/english_mode.py`: `patches_v4`,
  `ending_slot_patches`, `mced_english_scripts` (shared scripts refused).
  10 new unit tests. The tools' bytes equal the trial's.

Checks: `pytest` 177 passed; `ruff check`, `ruff format --check` and
`mypy --strict tools tests` clean; `mypy --strict` on the EXP-0040 scripts
(`MYPYPATH=research/experiments/EXP-0040`) clean. `ruff format` reflowed
the experiment scripts after their runs; behaviour unchanged.

Conclusion: `END-006` is `DONE` (**CONFIRMED**, D-034). Next: `END-007`.

## 2026-10-29 — SESSION-0060: Correction to EXP-0036 (found during END-007)

While setting up `EXP-0041`'s read logs from `local/checkpoints/end001/f00210163.mcs`
with no input, the screenshots showed Nash losing to Apocalypse, then the
continue screen and the title. `EXP-0036`'s write logs `wlog1` and
`wlog_marker` replayed the same checkpoint with no input, so they never
reached the partner fight or the ending. Their "no rewrite before the
ending" claim is withdrawn in `EXP-0036` and in D-031, with a note. The
disc-to-screen marker result stands: it came from the user's play-through.

This is a recorded failure (AGENTS.md rule 6): a no-input replay from a
checkpoint taken mid-play does not replay the play. A replay is valid only
over spans where the outcome no longer depends on input, such as after the
last hit (`f00220064`). Otherwise the route must force the outcome.

## 2026-10-29 — SESSION-0061: Nash's English ending records placed and built (END-007, EXP-0041)

User request (verbatim): "Start END-007: place Nash's English ending
records."

- **Spec and tools:** `data/translations/nash_ending.json` (addresses and
  hashes). `tools.disc.build_english` takes ending specs with
  `--patch-version 4` (writes after the win quotes, `patches_v4`, `MCED`
  re-encode). 6 new tests.
- **Build:** `build/m7_nash_ending` (Track 01 `2abe9771…`, all sectors
  valid). `MC10` margin 814 bytes. `MCED` and `MMPACK` equal `EXP-0040`'s
  fit-check outputs.
- **Failures on the way:**
  1. `area_reads.py` from `f00210163`: `MCED` not yet loaded there; then
     Nash lost with no input. This also invalidated `EXP-0036`'s write logs
     (correction recorded in `SESSION-0060`).
  2. Route runs without `--mmpack` used the original code from the select
     state (Japanese 76-byte pointers). Caught from the pointer log;
     `--mmpack` added.
  3. One route run lost window focus at the pick; rerun.
- **Saturn vitality:** found from 8 debugger dumps across one fight of the
  marker session. The CPU side's blocks are `0x060F4610` and `0x060F4E10`,
  the arcade layout (`0xFF4xxx`) at `0x060Fxxxx`.
- **Valid runs** (`route_after2`, `route_rest3`):
  - load check passed;
  - the space after the win quotes was read only during the ending (306
    hits), plus one read just past page 6;
  - the six pages are byte-identical to `EXP-0038`'s English trial;
  - all win quotes are English, including the post-Apocalypse one (record
    0).

Checks: see below.

Checks: `pytest` 183 passed; `ruff check`, `ruff format --check` and `mypy --strict tools tests` clean; `mypy --strict` on the EXP-0041 scripts clean (`MYPYPATH` with EXP-0025, EXP-0032 and EXP-0036). `tools.disc.regression`: `ryu_v2`, `ryu_ken_v3` and `roster_v3` all match after the `build_english` change (5 min 8 s).

Conclusion: `END-007` is `DONE` (**CONFIRMED**, D-035). Next: `END-008`, the user's cold-boot play check.

## 2026-10-30 — SESSION-0062: Play check of Nash's English ending (END-008, EXP-0042)

User request (verbatim): "Start END-008: build Nash's English ending and
play-check it." The image was already built in `EXP-0041` (Track 01
`2abe9771…`, re-hashed before the session). Mednafen was cold-booted on it
with the recorder (`--keep-states 150`). The user played (Nash and Ryu) and
said "done".

- **Ending:**
  - the six pages' text boxes match the approved pages in order (6-11
    shots each);
  - each page has session screenshots byte-identical to `EXP-0041`'s route
    pages.
- **Win quotes:** found from contact sheets (a bubble-colour detector was
  tried first and was too noisy). All seven are English (hashes in
  `EXP-0042`).
- **Kept:** `local/checkpoints/end008/f00050413.mcs` and
  `f00050757.mcs`.

Conclusion: `END-008` is `DONE` (**CONFIRMED**, D-036). Next: `END-009`.

## 2026-10-30 — SESSION-0063: Regression reference for the ending build (END-009); M7 complete

User request (verbatim): "Start END-009: regression reference for the
ending build."

- **New reference:** `nash_ending_v4` added to
  `data/regression/references.json`. Its hashes come from
  `local/end007/b1/changes.json`; each was re-hashed from the built file
  and Track 01 from `build/m7_nash_ending`. Against `roster_v3`, only
  `MC10` and `MMPACK.PCA` differ, plus the new `MCED.SHP`.
- **Regression:** `./invenv.sh python -m tools.disc.regression --report
  docs/regression_report.md` gave `ryu_v2`, `ryu_ken_v3`, `roster_v3` and
  `nash_ending_v4`: match; 48/48 hashes; exit 0.
- **README:** M7 status, the "still Japanese" list, and the build command
  with the ending spec and `--patch-version 4`.

Checks: `pytest` 183 passed; `ruff check` clean.

Conclusion: `END-009` is `DONE` (D-037). **M7 is complete.** Next: write
the M8 tasks (not started).

## 2026-10-30 — SESSION-0064: M8 tasks written (not started)

User request (verbatim): "Write up the M8 tasks for all roster endings.
Don't start them yet."

Facts gathered (read-only) for the task text:

- **Space:** from `data/text/ending_census.json` and the M5 fit margins.
  The free space after each file's English win quotes (416 + 76 × its
  Japanese ending count) holds every roster slot's English ending
  (100 × the arcade English count). Tightest: Cammy (1,300 of 1,328), and
  Magneto and Apocalypse (700 of 720). The compressed fit is not measured.
- **Aliases:** English 9 = 8, Japanese 8 = 7, and `MCED`'s shared scripts
  (8/9, 11/18).

Written in `TASKS.md` (Phase M):

| Task | Status |
| --- | --- |
| `END-010` (static census of scripts, aliases, space, labels) | `READY` |
| `END-011` (the user's ending roster and exceptions) | `BLOCKED` |
| `END-012` (MAME pairing for every roster ending, predictions first) | `BLOCKED` |
| `END-013` (Saturn route tool; team rule; second-pick buffer) | `BLOCKED` |
| `GATE-TRANSLATION` extension for the roster endings | waits on `END-010` and `END-012` |
| `END-014` (build every roster ending) | `BLOCKED` |
| `END-015` (verify every ending: route, win quotes, user play check of two) | `BLOCKED` |
| `END-016` (coverage register, regression, README) | `BLOCKED` |

The outline row `END-010` (M8) was replaced. Three references to it now
point at `END-012` or `END-013`. No experiment was run.

## 2026-10-30 — SESSION-0065: Census of roster ending scripts and space (END-010, EXP-0043)

User request (verbatim): "Start END-010: census of every roster ending's
scripts and space."

- **Script format:** read in full from raw bytes. Scenes are (length,
  record·256 + label) pairs, then `FFFF` and a trailing word; the
  scene-offset table length is its first entry / 2.
- **`census_scripts.py`** → `data/text/ending_script_census.json`:
  - All 18 roster English scripts show records 0 to n − 1 in order.
  - The Japanese scripts are in order except slot 8 (Ryu's script against
    `MC08`'s copy of Magneto's 4 records).
  - Trailing words don't always repeat the last page in English scripts;
    meaning unknown.
- **Aliases:** 8/9 = Ryu's ending, matching the arcade English pointer
  equality. 11/18 = Chun-Li's.
- **Fit:** every roster file fits, compressed margins 259 (Apocalypse) to
  1,293 bytes. Nash's margin (814) equals the M7 build, a cross-check.
- **Labels flagged:** `Akuma`, `Charlie`, `Charlie's friend`, `Bison`, and
  `Vega` in Magneto's English script (to check in MAME).

Conclusion: `END-010` is `DONE` (D-038). Next: `END-011`, the user's
choice.

Checks: `pytest` 183 passed; `ruff check` and `mypy --strict` on the census script clean. `ruff format` reflowed the script after the run; a rerun gave a byte-identical JSON.

## 2026-10-30 — SESSION-0066: M8 ending roster chosen (END-011)

User request (verbatim): "Start END-011: choose the M8 ending roster and
its exceptions."

Asked with the `EXP-0043` census. Answers (verbatim):

- "All 17 playable (Recommended)";
- "Switch shared layout (Rec.)" (Ryu's script shared with Apocalypse's
  slot; Apocalypse not marked);
- "Yes, include (Recommended)" (second-pick endings).

Recorded:

- `data/text/m8_ending_roster.json`: 17 members, slots 0-7 and 9-17;
  exclusions 8 and 18 with reasons;
- `docs/coverage_exceptions.md` (M8 endings section);
- `TASKS.md`: `END-011` DONE; `END-012` and `END-013` READY.

No experiment was run.

## 2026-10-30 — SESSION-0067: Arcade pairing for every roster ending (END-012, EXP-0044)

User request (verbatim): "Start END-012: arcade pairing for every roster
ending."

- **Route:** generalized to any grid character (moves from Cyclops). The
  select snapshots confirmed all 16 grid picks. For Gouki, 7 words holding
  the first pick's slot × 2 were found by dumps after three picks; forcing
  them to `0x1E` made Gouki the first pick (his tables were read; his win
  quote and English ending were shown).
- **Predictions:** `predictions.json` was committed (`8caed7c`) before the
  logged runs. The Gouki probe had shown some of his ending before; this is
  recorded.
- **First attempt at the 38 timelines:** a zsh loop split arguments wrongly
  (`--force-char` and `read`); regenerated from Python. A safety check
  blocked an `rm` on shell-variable paths; files were overwritten instead.
- **Runs:** 38, six in parallel; all met every prediction. Wolverine's and
  Chun-Li's partner checks were identical.
- **Pairing:** 16 new files, all CONFIRMED; Nash's addresses equal
  `EXP-0037`'s.
- **Names:** "Bison" in Vega's records 1 and 4. Labels `Akuma`, `Bison`,
  `Vega` (Magneto's page 3, checked on the arcade snapshot).

Checks: `ruff check`, `ruff format --check` and `mypy --strict` on the
EXP-0044 scripts are clean. `compare.py` and `make_pairing.py` reran to
byte-identical outputs after formatting.

Conclusion: `END-012` is `DONE` (**CONFIRMED**, D-039). Next: `END-013`;
the gate extension can be asked.

## 2026-10-30 — SESSION-0068: Saturn route to any roster ending; whose ending plays (END-013, EXP-0045)

User request (verbatim): "Start END-013: Saturn route to any roster ending,
first or second pick."

- **Fighter blocks:** found from the `EXP-0041` dumps. The arcade's 7
  first-pick words hold the same values at `0x060Fxxxx`. The per-block
  character is at + `0x23`. The block contents swap at a tag (4 fields and
  vitality swap), and `0x060F4200` is the active fighter.
- **Tool:** `tools/mednafen/route.py` promoted from `EXP-0041`, with grid
  moves, policies, a Gouki start state and `MC0F` patching. 11 tests.
- **Failures:**
  1. A zsh loop ran nothing (the command was passed as one word); a Python
     driver was used instead.
  2. Three versions of the "second" policy failed to make the second pick
     finish the boss (one write; a 900-frame window that ended in the
     dialogue; "partner active" already true in the dialogue).
  3. The fourth knocked out the first pick, and the team lost the match.
  4. The tag policy (Z + C) did not tag.
- **Results:**
  - `first`: the first pick's ending (Nash, Wolverine, Gouki).
  - `cpu_final`: the partner's win quote from WRAM-H, continue, no ending.
  - The partner fight always had the first pick on the player's side.
- **Gouki:** the state with his cell shown is the second pick, with Gouki
  already chosen; used as the Gouki start state.

Checks: `pytest` 194 passed; `ruff check`, `ruff format --check` and
`mypy --strict tools tests` clean.

Conclusion: `END-013` is `DONE` (D-040). The second-pick ending is not
reached; it passes to `END-015`'s user play check. Next: the
`GATE-TRANSLATION` extension for the M8 roster endings.

## 2026-10-30 — SESSION-0069: Translation gate for the M8 roster endings

User request (verbatim): "Let's do the GATE-TRANSLATION extension for the M8
roster endings."

- **Inputs:** `END-010` (scripts and space), `END-011` (roster),
  `END-012` (pairing for all 17, D-039) and `END-013` (route, D-040).
- **Asked:** GO or NO-GO for the endings of slots 0-7 and 9-17 (records,
  English records after the win quotes, `MCED` English scripts with the
  shared slots 8 and 18, the switch code), page k = arcade English record
  k, no rewording. Answer: "Go (Recommended)".
- **Names:** asked about "Bison" in Vega's records 1 and 4 and the labels
  `Akuma`, `Bison` and `Vega` (Magneto's page 3). Answer: "Keep arcade
  names (Recommended)".
- Recorded under `GATE-TRANSLATION` in `TASKS.md` and in
  `docs/localization_policy.md`. `END-014` is now `READY`.

No experiment was run; no code changed.

Conclusion: the gate is passed for the M8 roster endings. Next: `END-014`.

## 2026-10-30 — SESSION-0070: Build every roster ending (END-014, EXP-0046)

User request (verbatim): "Start END-014: build every roster ending."

- **Specs:** `make_specs.py` wrote 17 ending specs from the pairing files.
  Nash's records equal the M7 spec's.
- **Shared scripts:** `mced_english_scripts` gained `shared`, passed by a
  spec's `mced_shared_with` (Ryu 8, Chun-Li 18). 2 tests.
- **Build:** `build/m8_roster_endings`, Track 01 `7bb8ab82…`; all 71,908
  sectors valid. `check_build.py`: every MC file holds exactly its English
  bytes and is otherwise unchanged; 17 `MCED` words as the census gives;
  `MMPACK` = `patches_v4`; smallest margin 494. A second build gave 21
  identical files. Its `--image` into `local/` was refused, as designed:
  images go under `build/`.
- **Failures on the way:**
  1. `load1`: 4 of 17 teams failed. The driver's summary overwrote the
     slot numbers with the pass flags (fixed). Every failure was during a
     parallel rebuild, which looked like CPU load, but that was not the
     cause (below).
  2. `load2`-`load4`: still failing on an idle machine. A "picked" readout
     from the fighter blocks right after the pick gave nonsense ([5, 1]
     for a Cyclops team) and was dropped. The buffers were saved instead.
  3. `identify_buffers.py`: the failed buffers held another character's
     file exactly (wrong picks), except Rogue's, which differed in 8
     bytes.
  4. Screenshots before each A press (`control2`, `control3`, untouched
     image): the second cursor skips the first pick's cell, and starts on
     Wolverine when Cyclops is taken. The route was fixed to plan for it.
  5. Rogue's 8 bytes: the same on the untouched image. They are four
     `9999 9999` longs the game writes after loading.
  6. `load5`: the first planner refused Cyclops to Ken with Ryu taken.
     It was rewritten as a breadth-first search with the skip. Two first
     picks lost a key ("l" and A), so the driver now retries wrong picks.
  7. `load6`: all 17 teams pass (one retry).
- **Gouki:** a wrong pick in `load4` had loaded his file from the build,
  which showed his cell. `gouki_cell.py`: "uuullu" from Ken and "uuuu"
  from Cyclops pick him first and second; the built `MC0F` loads into
  either buffer with no differences.

Checks: `pytest` 198 passed; `ruff check`, `ruff format --check`, `mypy
--strict tools tests` and the `EXP-0046` scripts are clean.

Conclusion: `END-014` is `DONE` (D-041). Next: `END-015`.

## 2026-10-30 — SESSION-0071: Verify every roster ending (END-015, EXP-0047)

User request (verbatim): "Start END-015: verify every roster ending."

- **Route change:** Gouki is now picked from his cell (`GOUKI_CELL`),
  which replaces `GOUKI_STATE`. 1 test.
- **Runs:** `run_endings.py` ran 17 routes on the build, 4 at a time,
  in 20 runs:
  - Rogue: one wrong pick (Ken), and one strict-check miss on her
    game-written longs;
  - Dhalsim: one run stopped at its pick (Mednafen not in front).

  Every page pointer was reached.
- **Pages:** `compare_pages.py` sheets, reviewed by the agent. All 112
  pages match the arcade's. Colour-cycling pictures differ only in
  timing.
- **Reads:** besides the ending, only in the 20 frames of record-7 win
  quotes. Counts: 51 per page − 1, plus 1 per record-7 quote; Dhalsim
  has 1 more.
- **Forced draws:** `force_draws.py` (copied from `EXP-0032`, version 4
  and ending bytes). Ryu 17/17 and Ken 17/17 are byte-identical to M5,
  screens and VDP1.
- **Play check:** the user played Cammy's ending, then Wolverine (first)
  with Ryu (second), tagging with Z + C. Ryu's ending played.
  - `play_pages.py`: all 13 and 7 pages found. Colour-cycling pages
    matched by text box, and their pictures were checked.
  - `state_reads.py`: Ryu's pages read from `0x060B28F8` + 100k.
- **Failures:**
  1. ffmpeg had no `drawtext`, and zsh read `$n:l` as a modifier. Sheets
     were made from Python instead.
  2. `state_reads.py` first failed on a second state ("loadstate not
     allowed while halted"); it now resumes between states.
- **Not settled:** who gets the partner fight. "The character active at
  the boss fight's start" fits both plays (HYPOTHESIS).

Checks: `pytest` 199 passed; `ruff check`, `ruff format --check`, `mypy
--strict` on tools, tests and the EXP-0046/0047 scripts are clean.

Conclusion: `END-015` is `DONE` (D-042). Next: `END-016`.

## 2026-10-30 — SESSION-0072: M8 coverage register and regression (END-016)

User request (verbatim): "Start END-016: coverage register and regression
references for M8."

- **Reference:** `roster_endings_v4` was added to
  `data/regression/references.json`. Its file hashes come from
  `local/end014/b1/changes.json`, and its Track 01 hash was computed from
  `build/m8_roster_endings`.
- **Regression:** `./invenv.sh python -m tools.disc.regression --report
  docs/regression_report.md` rebuilt all 5 references from the untouched
  source, and all 69 hashes match (exit 0, about 10 minutes).
  `nash_ending_v4` still matches after `END-014` rewrote
  `nash_ending.json` with the same records.
- **Coverage:** `docs/coverage_exceptions.md` has a new "M8 coverage
  register". Two older rows were updated: the Japanese ending records
  (taken up by M8, except slot 8) and `MCED.SHP` (the ending overlay).
- **README:** the status now covers all 17 endings, the "still Japanese"
  list is updated, and the build command makes `build/m8_roster_endings`.

Checks: `pytest` 199 passed; `ruff check` and `ruff format --check` are
clean.

Conclusion: `END-016` is `DONE` (D-043), and M8 is complete. No task is
`READY`. The next work (M9 special cases, `LOC-001`, UI tasks, release)
waits for the user's choice.

## 2026-10-30 — SESSION-0073: Name-variant tasks written (Phase N)

User request (verbatim): "Write up the LOC-001 tasks (name variants). Don't
start them yet."

- **Inputs:** the policy (American default, both variants, every surface
  switched together), `docs/names.md` (`EXP-0011`), the `MCED` label
  list (`EXP-0038`), the `END-012` names, and the MSHvSF method
  (playbook, "Names and voice").
- **Static check while writing:** in `ending_script_census.json`, Rogue's
  Japanese ending labels Shadaloo's leader with entry `0x0F` (`Vega`),
  and her English ending uses `0x13` (`Bison`). Magneto's English page 3
  uses `0x0F` (`Vega`), so who speaks there (leader or claw fighter) is a
  `LOC-001` item. There is no `Balrog` label.
- **Tasks:**
  - `LOC-001` census (`READY`);
  - `LOC-002` storage and the other convention's art;
  - `LOC-003` voice;
  - `LOC-004` the user's plan, with a `GATE-TRANSLATION` extension for
    the Saturn-names edits;
  - `LOC-005` American build;
  - `LOC-006` Saturn-names build;
  - `LOC-007` verify and register.

  `LOC-008` (an in-game toggle) is an outline row. The old `LOC-001`
  outline row was replaced.
- `docs/names.md`'s open questions now point to `LOC-002` and `LOC-003`.

No experiment was run, and no code changed.

Conclusion: Phase N is written. `LOC-001` is `READY` and not started.

## 2026-10-30 — SESSION-0074: Census of every name surface (LOC-001, EXP-0048)

User request (verbatim): "Start LOC-001: census of every name surface. If
there are tasks that can be completed in parallel, you are authorized to
set up several sub-sessions."

- **Parallel work:** the arcade side (MAME, headless) went to a subagent
  rather than a separate session, because its result was needed in this
  task. It wrote `EXP-0048/arcade/` (13 runs, `RESULTS.md`), committed
  nothing, and touched no Saturn state. Spot-check: the agent re-cropped
  four life bars and viewed Magneto's page 5, which agree with
  `RESULTS.md`.
- **Saturn screens:** from the `EXP-0047` route runs and session, plus a
  9,000-frame cold-boot attract recording (`menu_walk.py`).
- **Failures:**
  1. `menu1`-`menu8`: scripted Start presses landed on the wrong screens
     (disc-load timing; the await step matched attract mode's own
     title). The user opened Option Mode instead.
  2. A first life-bar crop used transition frames; it was redone.
- **Route key map:** `KEYS` gained Start (N) and B (H).
- **Voice session:** `local/loc001/session`, user, sound on. The user
  reported: "Heard 'Vega' and 'Gouki' and 'Nash'."
- **Results:** see D-044 and `docs/names.md`.
  - Saturn art is in the Japanese convention on every surface.
  - The boss boxes name the player's character.
  - Magneto's page 3 is most plausibly the claw fighter (Balrog in Saturn
    naming).
  - Option Mode labels the taunt button "CHOUHATU" (for the UI tasks).

Checks: `pytest`, `ruff check`, `ruff format --check` and `mypy --strict`
on tools, tests and `EXP-0048` are clean.

Conclusion: `LOC-001` is `DONE`. `LOC-002` and `LOC-003` are `READY`.

## 2026-10-30 — SESSION-0075: Where the name art is stored (LOC-002, EXP-0049, in progress)

User request (verbatim): "Start LOC-002: where each name surface is stored,
and whether its US version exists."

- **Life bar:** traced from the VDP1 sprites to the SCU DMA (`0x06024010`),
  the composition buffer (`0x06024DDC`), the cell decoder (`0x06024CF0`)
  and the pack, which is `FIX.PRS` loaded raw at `0x002C3EA0`.
  - `cells.py` reproduces 18 of 18 VRAM cells.
  - Both name sets hold BISON and AKUMA; CHARLIE has separate cells.
  - `swap1`: GOUKI's cells became AKUMA's and the life bar read AKUMA.
    CONFIRMED.
- **Select label:** same cells as the CPU-side life bar.
- **Win banner:** a 2 × 2 letter font in `FIX.PRS`.
- **VS screen:** one-cell letters matching `FIX.PRS`, but drawn from the
  face files through a second decoder (`0x060252BA`) reading `FC0C.PRS` /
  `FCALL.PRS` in VDP1 VRAM.
- **Failures:**
  1. Write breakpoints on VRAM saw nothing (DMA).
  2. The agent's `physical` space returns zeros.
  3. My first cell-to-VRAM pairing was off (fixed by brute-force match).
  4. `swap2`: a lost key.
  5. `swap3`: the select labels are decoded before the select state.
  6. `swap_vs`/`swap_vs2`: no effect, which led to the face-file path.
  7. `swap_banner`: no banner without input.
  8. Name-text searches (linear codes, strides 1-16, glyph cell numbers)
     found nothing.
- **Asides:** 19 face files exist (`FC00`-`FC12`, slots 0-18), and
  voice files are named per character (`019_SVEG.ADP`, `01A_SGOU.ADP`,
  `01B_SNAS.ADP`).

Checks: `ruff check`, `ruff format --check` and `mypy --strict` on
`EXP-0049` are clean; `pytest` passes.

Conclusion: `LOC-002` stays `IN_PROGRESS`. The life bar is done. The select
label, banner and VS screen remain.

## 2026-10-30 — SESSION-0076: Name surfaces located, LOC-002 done (EXP-0049)

User request (verbatim): "Keep going on LOC-002: the select-label and
banner controlled changes, then the face-file format for the VS screen."

- **Select label:** from the title state `f00004409` with Start
  (`keys:s`), a decode log showed `VS00.PRS` frames `0x97` (CYCLOPS) and
  `0x9F` (RYU). Patching frame `0x97`'s entry showed BISON (`0xA8`), AKUMA
  (`0xA9`) and CHARLIE (`0xAA`).
- **VS screen:**
  - the pack descriptors at `0x060255F8` + 16 × slot are the face files,
    slices of `FCALL.PRS` (VDP1 `0x8000`);
  - `0x06025808` is `VS00.PRS` (WRAM-L `0x002F7030`);
  - the letter frames were mapped by DMA order, and the `vs_patch1` patch
    (N → H data) showed HASH.
- **Banner:** a decode log with vitality 0 showed `VS00` frames
  `0xB8`-`0xC2`, and the `banner_vs00` patch showed HASH.
- **CHARLIE's life-bar cells:** block `0x0880` repointed to them; the life
  bar showed CHARL….
- **Balrog:** no text anywhere.
- **Failures:**
  1. `FIX.PRS` swaps had no effect on the select, VS and banner screens
     (same art, different file).
  2. Key timing spoiled `label_a8` and `label_a8b`.
  3. Searches for the VS and banner letter lists (`VS00` codes, strides
     1-12) found nothing; this is left for `LOC-005`.
- **Tools:** `patch_run.py` added; `write_log.py` gained RAM patches and
  keys.

Checks: `ruff check`, `ruff format --check` and `mypy --strict` on
`EXP-0049` are clean; `pytest` passes.

Conclusion: `LOC-002` is `DONE` (D-045). Next: `LOC-003`.

## 2026-10-30 — SESSION-0077: Name calls in voice (LOC-003, EXP-0050)

User request (verbatim): "Start LOC-003: name calls in voice."

- **Recording:** Mednafen's `-soundrecord` works with scripted runs
  (`voice_record.py`). The user heard "Vega" in the pick moment (clip 1).
- **Sound path:**
  - The `.ADP` files are stereo ADPCM music (`SELE` and `VS` are
    `INITDATA` parts 3 and 4).
  - The clip bank is `INITDATA` part 5 in sound RAM.
  - The mixer's channel records are at `0x0601776C`.
- **Decoder:** copied from MSHvSF (`6161166`); it matched 102 of 102
  channel states.
- **Failures:**
  1. Write breakpoints on sound RAM, SCU DMA and the channel records saw
     no mixer activity (slave SH-2, HYPOTHESIS).
  2. A late dump gave stale records; clips 2 and 3 were sound effects.
  3. Real-time polling (`channel_poll.py`) found the true pick clips.
- **Clips identified by the user, one at a time:** `0x121` "Vega",
  `0x147` "Bison", `0x021` "Akuma", `0x01B` "Charlie".
- **Table:** table A in `MMPACK.PCA` (decoded `0x79EE`). Patching entries
  14 and 16 changed the pick and win calls; table B changed neither.

Checks: `ruff check`, `ruff format --check` and `mypy --strict` on
`EXP-0050` are clean; `pytest` passes.

Conclusion: `LOC-003` is `DONE` (D-046). `LOC-004` is `READY`.

## 2026-10-30 — SESSION-0078: The user's plan for each variant (LOC-004)

User request (verbatim): "Start LOC-004: the user's plan for each variant."

- **Edited lines:** the six Saturn-names lines were compiled from the
  arcade English records (`local/ref003/xmvsfu-68k.bin`); each fits the
  25-code line. The four Saturn labels are already in `MCED`'s list; no
  `Balrog` label exists.
- **Questions and answers** (`AskUserQuestion`):
  - American variant with the disc's own assets: "Go (Recommended)".
  - Saturn-names text edits (every edited line shown): "Go (Recommended)".
  - Magneto's page 3 label: "Balrog (Recommended)".
  - VS screen and win banner if the letter lists stay unfound: "Keep
    tracing (Recommended)".
- **Switch:** `build_english --names us|saturn`, default `us`, named by the
  agent from the task's example.
- **Recorded:** `docs/localization_policy.md` ("Name variants"),
  `GATE-TRANSLATION` and `LOC-004` in `TASKS.md`, `docs/names.md`.

No experiment was run; no code changed.

Conclusion: `LOC-004` is `DONE`. `LOC-005` is `READY`.

## 2026-10-30 — SESSION-0079: Build the American-names variant (LOC-005, EXP-0051)

User request (verbatim): "Start LOC-005: build the American-names variant."

- **Life bar:** a PC log on the cell decoder and a write log on its
  request record led to the HUD's sprite list (`0x060E3020`) and four
  19-word code lists at `0x06080F00`, each with an American twin 38
  bytes later (BISON, AKUMA, CHARLIE). The routine adds 38 when R11 +
  `0xD478` (`0x060F5478`) is non-zero.
- **Hypothesis tested:** the same word picks every name surface. Set to
  2 in RAM, it turned the select label, VS screen, life bar and banner
  American. It cannot ship that way (D-018: the quote and ending layout
  follow it).
- **Sites:** read logs of the word on the select, VS and win screens, and
  a static scan of `MMPACK.PCA` (45 readers), gave 10 name sites. Changed
  to `mov #2,r0` with the word at 0, they turned every surface American
  and played `0x147`, `0x021`, `0x01B` at the picks and the win. The voice
  goes through the game's own American list (requests `0xB2`-`0xB4` =
  table A entries 18-20), not by editing table A as planned in `LOC-004`;
  the clips are the same ones.
- **Build:** `tools/disc/names.py`; `build_english --names {us,none,saturn}`
  (default `us`; `none` for the older references; `saturn` refused until
  `LOC-006`). Image `build/loc005_names_us`, Track 01 `441c9cfc…92f3`.
  Only `MMPACK.PCA` differs from M8 (20 decoded bytes); 71,908 sectors
  pass EDC/ECC.
- **Cold boot** (`cold_walk.py`): the select cursor starts on Cyclops,
  and menus take Start only at some moments, so a press-until-match step
  was added. Run A picked Cyclops by mistake (one Start too many in the
  plan); run A2 and run B passed.
- **Regression:** 17 endings (7 retries for lost keys) and 34 forced
  draws. 91/109 pages and all 34 draw screenshots byte-identical to
  `END-015`; the rest differ by capture timing (pictures' colour
  cycling) or by AKUMA's banner letters left in VDP1 (Ryu's case has
  Gouki as partner).
- **Failure:** three wait loops matched their own command line in
  `pgrep` and never ended; they were stopped and the process was matched
  by a pattern that cannot match itself.

Checks: `pytest` (202 passed), `ruff check`, `ruff format --check`,
`mypy --strict` are clean.

Ear check: five clips from the cold-boot recordings, sent one at a time
without the expected name. The user heard: clip 1 (Gouki picked) "I heard
Akuma."; clip 2 (Vega picked) "I think I heard \"Bison\"."; clip 3
(Gouki's team wins) "Akuma"; clip 4 (Nash picked) "Charlie"; clip 5
(Nash's team wins) "Charlie".

Conclusion: `LOC-005` is `DONE` (D-047). `LOC-006` is `READY`.

## 2026-10-30 — SESSION-0080: Build the Saturn-names variant (LOC-006, EXP-0052)

User request (verbatim): "Start LOC-006: build the Saturn-names variant."

- **Unused label entry:** the label list's only reader (`0x060D5CF8`, in
  the ending overlay) is indexed by the script's label byte. A scan of all
  19 slots' scripts in all four languages found entry 9 (`Apocalypse`)
  unused, and code right after the list. `Balrog` goes into entry 9.
  Entry 19 (`Bison`) was considered and not used: it is in use in the
  American variant, and the slot + 1 layout of entries 1-19 suggested
  other readers until the reader was traced.
- **Build support:** `data/translations/saturn_names.json` (names only, no
  dialogue) and `tools/disc/names.py` (`edit_lines`, `label_edits`,
  `entry_edits`); `build_english --names saturn` recompiles the six
  records after their edit and logs each with its source hash. A label
  that ends a scene also has its scene-end word switched (Nash page 4).
- **Build:** `build/loc006_names_saturn`, Track 01 `b11c8cd9…e26e`, 0
  invalid sectors. `MMPACK.PCA` equals M8's. Decoded against the American
  build, differences only in the edited records, labels, entry 9 and the
  10 name sites.
- **Cammy's quotes:** no forced-draw case existed for Cammy, so a state was
  saved at her first fight on a cold boot of the built image
  (`cold_walk.py` gained `save:`), and `quote_seeds.py` set the seed and
  CPU vitality. Seed 1 gave record 0, seed 9 record 4. The first scan ran
  1,300 frames and missed the quote screen; 800 frames showed both.
- **Endings:** Rogue, Magneto, Vega, Gouki and Nash routed on the built
  image (all first-attempt loads). Every edited line and label read as
  approved; 18 of 19 unedited pages byte-identical to the American build,
  the other differing only in the picture's moment.
- **Failure:** a wait loop for the Cammy run matched a process other than
  the walker and timed out; it was stopped.

Checks: `pytest` (206 passed), `ruff check`, `ruff format --check`,
`mypy --strict` are clean.

Conclusion: `LOC-006` is `DONE` (D-048). `LOC-007` is `READY`.

## 2026-10-30 — SESSION-0081: Verify and register both variants (LOC-007)

User request (verbatim): "Start LOC-007: verify and register both variants."

- **References:** `names_us_v4` and `names_saturn_v4` added to
  `data/regression/references.json` (with a `names` field; older
  references rebuild with `none`).
- **Regression:** `./invenv.sh python -m tools.disc.regression --report
  docs/regression_report.md`: all seven references match.
- **Play check, American** (`local/loc007/us`, sound recorded): the user
  hovered Vega and Gouki, picked Nash and Gouki, won the first fight, and
  said "done". Screens viewed: BISON, AKUMA, CHARLIE labels; VS and life
  bar CHARLIE / AKUMA; banner CHARLIE / AKUMA / WIN.
- **Play check, Saturn names** (`local/loc007/saturn`): the same route;
  "done". VEGA, GOUKI, NASH labels; VS and life bar NASH / GOUKI; banner
  NASH / GOUKI / WIN.
- **README:** the build section had no `--names`, so its command would now
  build the American variant and its win-quotes-only hash would not match;
  it now gives both variants and notes `--names none` for the older hashes.
- **Coverage:** "Name variants" section in `docs/coverage_exceptions.md`.

Checks: `pytest`, `ruff check`, `ruff format --check`, `mypy --strict` are
clean.

Conclusion: `LOC-007` is `DONE`; Phase N is complete. No task is `READY`;
the next work needs the user's choice (M9 `SPECIAL-001`, `UI-004`,
`REL-001`, `LOC-008`, or the "after M8" UI and text tasks).

## 2026-10-30 — SESSION-0082: Write up UI-004 (boot-time messages)

User request (verbatim): "Write up UI-004 (boot-time error messages) as a
full task. Don't start it yet."

- **Read:** `EXP-0002` (the no-cart warning, D-002), `docs/text_surfaces.md`,
  the localization policy, and MSHvSF `TASKS.md` `UI-008` (read only).
- **Observed (metadata only):** the disc's `ERR1.BIN`-`ERR5.BIN` are each
  42,358 bytes with a BMP header for 352 × 240 at 4 bits per pixel. That the
  game draws them, and which screen each is, is untested.
- **Written:** Phase O, `BOOT-001` (census, `READY`) to `BOOT-005`
  (verify), with every MSHvSF fact marked as a hypothesis. The `UI-004`
  outline row points to it.

No experiment was run; no code changed.

## 2026-10-30 — SESSION-0083: Census of the boot-time messages (BOOT-001, EXP-0053)

User request (verbatim): "Start BOOT-001: census of the boot-time messages."

- **Tools copied from MSHvSF** (read only there): `frame_capture.py`
  (`d95a62a`, unchanged) and `backup_ram.py` with its tests (`447e573`;
  corruption offset made a parameter). The `.bkr` layout matched a real
  XvSF save (`XMEN_VS_SF_`, 992 bytes, block 2).
- **Census** (`census.py`, 12 cases, one fresh home each): four warnings.
  The first run stopped on a bug in the copied tool (a one-block dummy
  file got a negative size); fixed with a test, then rerun.
- **Files:** the bitmap at `0x06080000` in each warning's RAM dump equals
  `ERR4` (no cart, backup cart), `ERR1` (unformatted), `ERR2` (damaged),
  `ERR3` (18 free).
- **Code:** `CPK.PCA` at `0x06022000`, boot check `0x060228D4`, picture
  loader `0x060221E0`, cart test `CPK.EMM` (ID at `0x24FFFFFF`, RAM tests).
  `ERR5` = −1 (unsteady ID, failing 1 MB cart): not producible here.
- **Disproven for XvSF** (MSHvSF hypotheses, rule 13):
  1. "No cart shows `ERR5`": it shows `ERR4`.
  2. "A 1 MB cart shows `ERR4`": a 1 MB cart passes the check and the
     game runs its attract with demo fights.
- **Buttons:** A and B leave to the BIOS multiplayer screen; C and D
  continue (the `cold_walk.py` home override was added for this).
- **Other text:** developer English in file `0` and `MMPACK.PCA`, not
  triggered; `.FHD` names unused.
- **Failure:** a frame-sampled grid first picked black frames for two
  crops; the right frames were then taken from the sheet order.

Checks: `pytest`, `ruff check`, `ruff format --check`, `mypy --strict` are
clean.

Conclusion: `BOOT-001` is `DONE` (D-049). `BOOT-002` is `READY`.

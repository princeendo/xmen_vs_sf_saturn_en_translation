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

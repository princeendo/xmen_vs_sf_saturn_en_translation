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

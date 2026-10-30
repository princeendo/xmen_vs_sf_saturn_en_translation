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
- **2026-10-28** (`SESSION-0023`, `EXP-0014`): the user switched the M1
  target to the `EXP-0013` session's Ryu quote (blind-checked). Six named
  checkpoints bracket it (`DBG-004`).
- **2026-10-28** (`SESSION-0024`, `EXP-0015`): the quote is VDP1 glyph cells
  (controlled change); its text is a WRAM-L table at `0x0024F5D8` that equals
  the arcade Japanese slot 9 (Ryu) byte for byte; the M1 quote is record 10
  (`DBG-005`, D-010).
- **2026-10-28** (`SESSION-0025`): the user passed `GATE-M0` ("GATE-M0: go").
  **M1 reached** (`RE-001`, `EXP-0016`, D-011): writing あいう into Ryu's
  quote record in live RAM changed exactly those glyphs on screen; the
  no-write control showed the original.
- **2026-10-28** (`SESSION-0026`, `EXP-0017`): M2 tasks written in full.
  Ryu's quote table is loaded from `MC09.SHP` (LSN 53,719), a 4-byte header
  plus an LZ77 stream decoded by `tools/disc/prs.py`; the table is at
  decompressed offset `0x25D8` (`DISC-001`, D-012). ISO listing committed.
- **2026-10-28** (`SESSION-0027`, `EXP-0018`): **M2 reached.** An image
  rebuilt from the untouched source, with only `MC09.SHP` re-encoded
  (あいう in all 16 Ryu win-quote records), showed the change in two
  cold-boot Ryu wins (`DISC-002`, D-013).
- **2026-10-28** (`SESSION-0028`, `EXP-0019`): the quote font is `FIX.PRS`,
  loaded unchanged to WRAM-L `0x002C3EA0`. Its format is proven by a
  byte-identical repack and 22/22 drawn cells, and a one-byte disc change
  reaches the loaded font from a cold boot (`FONT-001`, D-014).
- **2026-10-28** (`SESSION-0029`, `EXP-0020`): the quote font draws the
  arcade English codes directly. A quote is 2 × 19 cells, all shown; only 59
  of 161 arcade English win quotes fit after re-wrapping (`FONT-002`, D-015).
- **2026-10-28:** M3 tasks written at the user's request (not started):
  `RE-002` (selector), `LAYOUT-001` (capacity route), `PAIR-001` (Ryu's
  English pairing), `GATE-TRANSLATION` (now waiting on `PAIR-001`) and
  `RE-003` (all of Ryu's quotes from a rebuilt image).
- **2026-10-28** (`SESSION-0031`, `EXP-0021`): Ryu's shown record is
  `RNG() & 0x0F`, chosen when the quote starts; pointer `0x060F2490`. Any
  record can be forced from `pre_ko`: 5 indices, 38/38 cells, with a control
  (`RE-002`, D-016).
- **2026-10-28** (`SESSION-0032`, `EXP-0022`): in the arcade, the same
  random draw shows Japanese record `r` and English record `r mod 8`. So
  Saturn record `k` pairs with Ryu's English record `k mod 8`; all 16 were
  checked in MAME, and English record 8 is never chosen (`PAIR-001`, D-017).
- **2026-10-28:** the user passed `GATE-TRANSLATION` for Ryu's win quotes
  (GO; pairing `k mod 8`; official arcade English, no rewording).
- **2026-10-28** (`SESSION-0033`, `EXP-0023`): the user chose the game's own
  English mode. A per-task patch in `MMPACK.PCA` plus Ryu's English records
  in `MC09.SHP` show his win quotes in English (2 × 25) from a cold boot,
  with other characters and hints unchanged. The first version broke other
  characters' quotes; it was found in play and fixed (`LAYOUT-001`, D-018).
- **2026-10-28** (`SESSION-0034`, `EXP-0024`): **M3 reached.** A caption
  compiler and a spec-driven build make Ryu's English image from the
  untouched source. All 16 draws show their paired English, cell for cell,
  and two cold-boot wins showed English (`RE-003`, D-019).
- **2026-10-28:** M4 tasks written at the user's request (not started):
  `RE-004` (choose and map the second character), `RE-006` (an English-slot
  table instead of one slot), `PAIR-002` (its pairing), a
  `GATE-TRANSLATION` extension, and `RE-007` (build both characters).
- **2026-10-29** (`SESSION-0036`, `EXP-0025`): the user chose Ken. His
  quotes load from `MC0A.SHP` (table offset `0x2A4C`) to WRAM-L
  `0x0024FA4C` when he is first and WRAM-H `0x060B2A4C` when he is second.
  The selector sees slot 10 (`0x0014`), and the table is the arcade
  Japanese slot 10 (`RE-004`, D-020).
- **2026-10-29** (`SESSION-0037`, `EXP-0026`): Ken's Saturn record `k`
  pairs with English slot 10 record `k mod 8`, as Ryu's does. All 16 are
  confirmed in MAME, and all 9 English records fit 2 × 25 (`PAIR-002`,
  D-021).
- **2026-10-29:** the user extended `GATE-TRANSLATION` to Ken's win quotes
  (GO; pairing `k mod 8`; official arcade English, no rewording).
- **2026-10-29** (`SESSION-0039`, `EXP-0027`): version 3 of the English
  mode keeps the English slots in data. Each slot's fixed-index word's spare
  high byte (2 = English) selects it. Ken switches with his byte alone, Ryu's
  16 draws are unchanged, and Storm is untouched (`RE-006`, D-022).
- **2026-10-29** (`SESSION-0040`, `EXP-0028`): **M4 reached.** One
  command builds an image from the untouched source in which Ryu and Ken
  speak their official arcade English win quotes (Track 01 `b5dd07c2…`).
  All 16 draws of each were checked, and the user's cold-boot play check
  passed (`RE-007`, D-023).
- **2026-10-29:** M5 tasks written at the user's request ("Let's continue
  on to M5, then."), none started: `RE-005` (census of the quote files),
  `RE-008` (roster and exceptions, a user decision), `PAIR-003` (pairing),
  `RE-009` (sector fit), a `GATE-TRANSLATION` extension, `RE-010` (roster
  image) and `RE-011` (regression references).
- **2026-10-29** (`SESSION-0042`, `EXP-0029`): census done. `MCxx` holds
  arcade slot `xx` for all 18 files `MC00`-`MC11`. A third load trace
  (Cyclops, `MC01`, as second member) agrees. `MCED` and slot 18 (an alias
  of Chun-Li's slot 11) are irregular (`RE-005`, D-024).
- **2026-10-29** (`SESSION-0043`): the user chose the M5 roster: all 18
  characters of slots 0-17, including Gouki and Apocalypse ("All 18, with
  Apocalypse"; `data/text/m5_roster.json`, `docs/coverage_exceptions.md`;
  `RE-008`).
- **2026-10-29** (`SESSION-0044`, `EXP-0030`): every roster character
  follows `r mod 8` in MAME (360 forced runs). Pairing files exist for all
  18. One name needs the gate: "Bison" in two of Cammy's records
  (`PAIR-003`, D-025).
- **2026-10-29** (`SESSION-0045`, `EXP-0031`): every roster file fits its
  sectors with its English records (margins 175-1,176 bytes; `RE-009`,
  D-026).
- **2026-10-29** (`SESSION-0046`): the user extended `GATE-TRANSLATION` to
  all 18 roster characters' ordinary win quotes (GO; `k mod 8`; official
  arcade English; "Bison" kept in Cammy's two records).
- **2026-10-29** (`SESSION-0047`, `EXP-0032`): the roster image is built
  and verified. All 18 roster characters show their official English win
  quotes, as first member, second member or CPU (`RE-010`, D-027). The user
  also added `UI-004` (the 4 MB cart warning) to the backlog.
- **2026-10-29** (`SESSION-0048`, `EXP-0033`): regression references. All
  three confirmed builds (Ryu; Ryu and Ken; the roster) rebuild byte for
  byte from the untouched source, including from a fresh clone
  (`tools.disc.regression`, `docs/regression_report.md`; `RE-011`, D-028).
  **M5 is complete.**
- **2026-10-29:** M6 tasks written at the user's request ("Write up the M6
  tasks for the endings. Don't start them yet."), none started: `END-001`
  (choose and reach an ending, user choice), `END-002` (how it is drawn),
  `END-003` (where it lives), `END-004` (arcade English and indexing). The
  M7 and M8 outline rows are renumbered `END-005` and `END-006`.
- **2026-10-29** (`SESSION-0050`, `EXP-0034`): the user chose Nash's
  ending ("Nash (Recommended)") and reached it on the untouched image. After
  Apocalypse the two team members fight; winning it as Nash gives six timed
  Japanese pages with Latin speaker labels, then an English staff roll.
  The ending replays pixel-identically from a checkpoint after the last hit
  with no input; losing the partner fight gives no ending (`END-001`,
  D-029). New surfaces: the pre-boss story line, the post-Apocalypse win
  quote, the `⚠乱入禁止` ("no challengers") warning (the user spotted it),
  the ending pages and labels, and one Japanese line in the QSound notice
  (`docs/text_surfaces.md`).
- **2026-10-29** (`SESSION-0051`, `EXP-0035`): Nash's ending is drawn
  by the type-4 selector (once per scene) and the quote renderer (once per
  page). It uses the `FIX.PRS` quote font in the 2 × 19 grid, and its six
  pages are `MC10` records 16-21. The version-3 patch leaves the ending
  pixel-identical. The English grid is reachable, but the selector's English
  list is empty on the Saturn, and English mode also changes the labels and
  pictures (a Latin `Charlie` label appeared; `END-002`, D-030).
- **2026-10-29** (`SESSION-0052`, `EXP-0036`): Nash's
  ending records are loaded once, at the pick, by the file loader
  `0x0600D124` from `MC10.SHP`. Nothing rewrites them before the ending,
  and a RAM edit changes exactly the predicted cell. A same-size marker in
  `MC10.SHP` (image `build/end003_marker`) reaches RAM at the pick. Every
  roster file keeps its arcade Japanese ending block at table + `0x4C0`
  (`data/text/ending_census.json`). In the user's play check on the
  marker image, page 1 showed the marker in exactly its four cells, and
  pages 2-6 were unchanged (`END-003`, D-031).
- **2026-10-29** (`SESSION-0053`, `EXP-0037`): Charlie's arcade ending is
  reached in MAME with no play, by zeroing the CPU side's vitality, in
  English and in Japanese. Page k reads the point character's ending record
  k, in either language and with either partner. Saturn `MC10` record
  16 + k pairs with arcade English slot 16 record k
  (`data/translations/nash_ending_pairing.json`, all six CONFIRMED). The
  English scene script differs: other scene breaks, pictures and labels
  (`Charlie`, `Charlie's friend`). English records 1 and 4 say "Charlie"
  (`END-004`, D-032). **M6 is complete.**
- **2026-10-29:** M7 tasks written at the user's request ("Write up the M7
  tasks for localizing Nash's ending. Don't start them yet."), none
  started:
  - `END-005`: the Saturn's English ending script, RAM only (ready);
  - `LAYOUT-002`: the user's layout choice;
  - the `GATE-TRANSLATION` extension for Nash's ending;
  - `END-006` (code) and `END-007` (data);
  - `END-008` (build and play check);
  - `END-009` (regression).

  The M8 outline row is renumbered `END-010`.
- **2026-10-29** (`SESSION-0056`, `EXP-0038`): the Saturn holds the
  arcade's English ending script for Nash, in `MCED.SHP` (the ending
  overlay). It has its own scenes, page lengths and labels; the labels
  `Charlie` and `Charlie's friend` come from a 16-bit ASCII list in `MCED`.
  With only the ending's own language reads set to English and a pointer
  to the six arcade records in RAM, the Saturn shows the arcade English
  ending page for page (`END-005`, D-033).
- **2026-10-29** (`SESSION-0057`, `EXP-0039`): option (b) (English text
  in the Japanese script) was trialled in RAM next to option (a). The user
  chose (a), the Saturn's English script, with the arcade labels `Charlie`
  and `Charlie's friend` (`LAYOUT-002`).
- **2026-10-29** (`SESSION-0058`): the user extended `GATE-TRANSLATION` to
  Nash's ending (GO). It covers `MC10` records 16-21 plus what the English
  script needs, page k = English record k, official English unchanged, and
  "Charlie" kept in the text and labels.
- **2026-10-29** (`SESSION-0059`, `EXP-0040`): version 4 of the patch, a
  same-size type-4 selector rewrite, turns on English endings per slot
  (one bit in the fixed-index table). The records are read at quote table +
  800, and the slot's `MCED` script header selects its English script. In
  RAM: the unmarked ending is pixel-identical to the original, the marked
  one shows `EXP-0038`'s English ending, and Ryu's win quotes are unchanged.
  Both files fit (`END-006`, D-034; `tools/disc/english_mode.patches_v4`).
- **2026-10-29** (`SESSION-0061`, `EXP-0041`): Nash's English ending
  records sit at `MC10` table + 800, after his English win quotes (814
  bytes to spare). `tools.disc.build_english` builds ending specs
  (`data/translations/nash_ending.json`, version 4). The M7 image
  `build/m7_nash_ending` loads correctly. A no-play Saturn route (vitality
  forcing) from the select checkpoint to the credits showed that the space
  is read only by the ending, and that the six pages match the chosen
  layout. Found on the way: no-input replays from mid-play checkpoints lose
  the fight. `EXP-0036`'s "no rewrite" claim was withdrawn for that reason
  (`END-007`, D-035).
- **2026-10-30** (`SESSION-0062`, `EXP-0042`): the user played
  `build/m7_nash_ending` from a cold boot to Nash's ending. All six pages
  are byte-identical to the chosen English layout, and all seven win quotes
  in the session are English (`END-008`, D-036).
- **2026-10-30** (`SESSION-0063`): `nash_ending_v4` is in
  `data/regression/references.json`, and `tools.disc.regression` rebuilds
  all four confirmed builds byte for byte (48 of 48 hashes;
  `docs/regression_report.md`). The README describes Nash's English ending
  and its build command (`END-009`, D-037). **M7 is complete.**
- **2026-10-30:** M8 tasks written at the user's request ("Write up the M8
  tasks for all roster endings. Don't start them yet."), none started:
  - `END-010`: static census (ready);
  - `END-011`: the user's ending roster;
  - `END-012`: arcade pairing;
  - `END-013`: Saturn route tool, team rule and second pick;
  - the gate extension;
  - `END-014`: build;
  - `END-015`: verify;
  - `END-016`: coverage and regression.
- **2026-10-30** (`SESSION-0065`, `EXP-0043`): static census. Every
  roster slot 0-17 has an English `MCED` script that shows its arcade
  English ending records in order, and every MC file fits its English
  ending (compressed margins 259-1,293 bytes). Slots 8/9 share Ryu's ending
  and 11/18 share Chun-Li's. English labels to gate: `Akuma`, `Charlie`,
  `Charlie's friend`, `Bison`, and `Vega` in Magneto's script (`END-010`,
  D-038).
- **2026-10-30** (`SESSION-0066`): the user chose the M8 ending roster:
  all 17 playable characters (slots 0-7 and 9-17, Gouki and Cammy
  included), first and second pick. Ryu's script, shared with Apocalypse's
  slot, is switched, and Apocalypse is not marked (`END-011`;
  `data/text/m8_ending_roster.json`).
- **2026-10-30** (`SESSION-0067`, `EXP-0044`): arcade pairing for all 17
  roster endings. 38 MAME runs (Gouki by a forced pick) met every
  prediction committed beforehand: page k = record k in both languages,
  the partner changes nothing, and the arcade's scene breaks equal the
  Saturn scripts'. Pairing files are in `data/translations/`. Names for the
  gate: "Bison" in Vega's text; the labels `Akuma`, `Bison`, `Vega`
  (Magneto, as the arcade shows); and Nash's `Charlie` (`END-012`, D-039).
- **2026-10-30** (`SESSION-0068`, `EXP-0045`): `tools.mednafen.route`
  reaches any roster character's ending on the Saturn with no play (Gouki
  from a state where he is already picked). Both members' files load
  correctly. The ending is always the first pick's: the partner fight puts
  the first pick on the player's side, and if the partner wins there is no
  ending. A second pick's ending was not reached; that passes to the
  `END-015` play check (`END-013`, D-040).
- **2026-10-30** (`SESSION-0069`): the user extended `GATE-TRANSLATION`
  to the endings of all 17 M8 roster characters (GO): page k shows the
  arcade English ending record k, no rewording, and the arcade names are
  kept ("Bison" in Vega's text; the labels `Akuma`, `Bison`, `Vega`).
- **2026-10-30** (`SESSION-0070`, `EXP-0046`): `build/m8_roster_endings`
  holds every roster character's English win quotes and ending. Every
  built file loads into both team buffers, Gouki included (picked from his
  cell above Juggernaut's). The second select cursor skips the first
  pick's cell, and the route now plans for it (`END-014`, D-041).
- **2026-10-30** (`SESSION-0071`, `EXP-0047`): every roster ending is
  verified on the M8 build.
  - **Route:** all 17 endings, every page matching the arcade's English.
    Gouki is now picked from his cell.
  - **Win quotes:** unchanged from M5 (forced draws byte-identical).
  - **Play check:** the user played Cammy's ending, then Ryu's as the
    second pick after tagging with Z + C. A second pick's ending is
    reachable and shows in English from the second buffer (`END-015`,
    D-042).
- **2026-10-30** (`SESSION-0072`, D-043): **M8 is complete.**
  - **Regression:** the M8 build is reference `roster_endings_v4`, and all
    five references rebuild byte for byte.
  - **Coverage:** `docs/coverage_exceptions.md` registers what M8 leaves
    (`END-016`).
- **2026-10-30** (`SESSION-0073`): the name-variant tasks are written,
  `LOC-001` to `LOC-007` (Phase N). Not started.
- **2026-10-30** (`SESSION-0074`, `EXP-0048`): the name census is done
  (`LOC-001`, D-044).
  - **Saturn art:** VEGA, GOUKI and NASH on every art surface, like the
    Japanese arcade; the US arcade shows BISON, AKUMA and CHARLIE.
  - **Voice:** the user heard the Saturn names spoken.
  - **Boss stage:** the Japanese boxes name the player's character.
  - **Magneto's page 3:** most plausibly the claw fighter.
- **2026-10-30** (`SESSION-0075`, `EXP-0049`, in progress): the life-bar
  names are compressed cells in `FIX.PRS`, decoded by `0x06024CF0`.
  - **US names:** BISON, AKUMA and CHARLIE are all there, and a RAM swap
    made the life bar read AKUMA.
  - **Select label:** uses the same cells.
  - **Win banner:** a `FIX.PRS` letter font.
  - **VS screen:** comes from the face files (`FC00`-`FC12.PRS`) through
    a second decoder.
- **2026-10-30** (`SESSION-0076`, `EXP-0049`): `LOC-002` is done (D-045).
  - **Storage:** every name surface is located by a controlled change.
  - **American art:** BISON, AKUMA and CHARLIE are already on the disc
    for the life bar (`FIX.PRS`) and the select label (`VS00.PRS`); the VS
    and banner fonts can spell them.
  - **Absent:** a `Balrog` label.
- **2026-10-30** (`SESSION-0077`, `EXP-0050`): `LOC-003` is done (D-046).
  - **Calls:** the Saturn calls the name at the pick and on the win
    screen, from a slot-indexed table in `MMPACK.PCA`.
  - **American calls:** "Bison", "Akuma" and "Charlie" are already on the
    disc (identified by the user).
  - **So:** every name surface, voice included, has its American version
    on the disc.
- **Next:** `LOC-004` (the user's plan for each variant; `READY`). M9 (special cases) needs the user's
  explicit task (rule 24). Backlog: `UI-004`, `SPECIAL-001`, `REL-001`,
  `LOC-008`, and the "after M8" UI and text tasks.
  The backlog also holds `UI-004` (boot-time error messages, including the
  cart warning), `SPECIAL-001` (including
  Apocalypse's pre-fight line) and `REL-001` (release patches).

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
- **Target switched (user, 2026-10-28):** Ryu's quote from the `EXP-0013` session (frame 10336), which has checkpoints; the first line has none.

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

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** DBG-003.
- **Blockers:** None.
- **Objective:** States and screenshots before the fight end, after the KO, with the quote visible, and after it disappears.
- **Acceptance criteria:** Each checkpoint is reproducible from its state and named in an experiment record.
- **Notes:** Done 2026-10-28 (`EXP-0014`): `pre_ko`, `after_ko`, `win_banner`, `pre_quote`, `quote_visible`, `after_quote` in `local/checkpoints/dbg003/`.

### DBG-005 - Find the quote renderer and its RAM text

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** DBG-001, DBG-004.
- **Blockers:** None.
- **Objective:** Determine whether the quote is VDP1 sprites or VDP2 tiles, and find the code table that drives it.
- **Acceptance criteria:** The renderer is identified by a controlled change; the RAM text table is located by plain-encoding search or by equality-pattern search.
- **Notes:** Done 2026-10-28 (`EXP-0015`, D-010).

## Gates

### GATE-M0 - Confirm environment and checkpoint prerequisites

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001 to ENV-006, EMU-001 to EMU-007, EMU-020, EMU-021, DBG-001, DBG-003, DBG-004, DBG-005, REF-008.
- **Blockers:** None; every dependency is `DONE` (2026-10-28). Needs the explicit go/no-go.
- **Objective:** Make an explicit go/no-go decision before the first live RAM mutation.
- **Acceptance criteria:** Every dependency is `DONE`; no unresolved workflow blocker can invalidate M1 evidence.
- **Decision:** GO, by the user on 2026-10-28 (verbatim): "GATE-M0: go. Start RE-001: change the chosen quote in live RAM, with a no-write control."

### GATE-TRANSLATION - Confirm reference and translation prerequisites

- **Status:** `DONE`
- **Milestone:** M3 (entry gate)
- **Dependencies:** DOC-002, REF-001 to REF-008, PAIR-001 (all done).
- **Blockers:** None.
- **Objective:** Make an explicit go/no-go decision before any official or
  translated English text goes into a disc build. The oracle, the pairing
  method and the user's policy must be settled first.
- **Scope:** Synthetic test strings (alphabets, pair-glyph samples, markers)
  are not covered, as in `FONT-002` and `LAYOUT-001`. Live-RAM tests are not
  covered either.
- **Acceptance criteria:**
  - Every dependency is `DONE`.
  - `PAIR-001` gives, with evidence, the arcade English record (or none) for
    each of Ryu's 16 Saturn win-quote records.
  - The user records GO or NO-GO in their own words, with the scope (which
    character, which surface), and chooses the pairing policy where the
    evidence leaves a choice. An example is a Saturn record with no unique
    English counterpart.
- **Outputs:** A gate acceptance entry here and in `docs/localization_policy.md`.
- **Notes:**
  - The policy already says official arcade English, paired by the game's own
    selection logic, with no rewording, and grammar fixes opt-in.
  - Endings, special cases and other characters stay gated (rules 23 and 24).
  - The arcade has 9 English records for Ryu (slot 9) but 16 Japanese, and
    the Saturn copies the 16 (`EXP-0015`), so pairing is not one-to-one.
- **Gate acceptance (2026-10-28):**
  - The user's decision is **GO**, in their words: "GATE-TRANSLATION: go for Ryu's win quotes. Use the k mod 8 pairing (Saturn records k and k+8 both show English record k), official arcade English, no rewording. Record it."
  - Checked at acceptance: DOC-002, REF-001 to REF-008 and PAIR-001 are all
    `DONE`.
  - **Scope:** Ryu's ordinary win quotes only (Saturn records 0-15 of
    `MC09.SHP`'s table). Records 16-21 (ending text), endings, other
    characters and special cases remain gated (rules 23 and 24).
  - **Pairing policy:** Saturn record `k` shows Ryu's official arcade English
    record `k mod 8` (`EXP-0022`, `data/translations/ryu_pairing.json`).
    Records `k` and `k + 8` therefore show the same English quote, and
    English record 8 is not used.
  - **Wording:** the official arcade English, with no rewording. Grammar
    fixes stay opt-in only (policy).
- **Gate extension, Ken (2026-10-29):**
  - The user's decision is **GO**, in their words: "GATE-TRANSLATION: go for Ken's win quotes. Use the k mod 8 pairing (Saturn records k and k+8 both show English record k), official arcade English, no rewording. Record it."
  - Checked at acceptance: `RE-004` and `PAIR-002` are `DONE` (`EXP-0025`,
    `EXP-0026`).
  - **Scope:** Ken's ordinary win quotes only (Saturn records 0-15 of
    `MC0A.SHP`'s table), added to Ryu's. Records 16-20 (ending text),
    endings, other characters and special cases remain gated (rules 23 and
    24).
  - **Pairing policy:** Saturn record `k` shows Ken's official arcade
    English record `k mod 8` (slot 10; `data/translations/ken_pairing.json`).
    Records `k` and `k + 8` show the same English quote, and English record
    8 is not used.
  - **Wording:** the official arcade English, with no rewording. Grammar
    fixes stay opt-in only (policy).
- **Gate extension, M5 roster (2026-10-29, `SESSION-0046`):**
  - The user's decision is **GO**. They were asked: "Extend GATE-TRANSLATION to the M5 roster's ordinary win quotes (Saturn records 0-15 of each MC00-MC11 table, the 16 new characters added to Ryu and Ken), using the k mod 8 pairing and the official arcade English with no rewording?" Answer: "Go (Recommended)".
  - Checked at acceptance: `RE-005`, `RE-008`, `PAIR-003` and `RE-009` are
    `DONE` (`EXP-0029`-`EXP-0031`).
  - **Scope:** the ordinary win quotes (Saturn records 0-15 of the quote
    table) of all 18 roster characters, slots 0-17 (`data/text/m5_roster.json`).
    That includes Gouki and Apocalypse, by the `RE-008` decision. Ending
    records, endings, slot 18, `MCED` and every other surface remain gated
    (rule 23; `docs/coverage_exceptions.md`).
  - **Pairing policy:** Saturn record `k` of slot `s` shows slot `s`'s
    official arcade English record `k mod 8` (D-025,
    `data/translations/<name>_pairing.json`).
  - **Wording:** the official arcade English, with no rewording. Grammar
    fixes stay opt-in only.
  - **Names:** Cammy's English records 0 and 4 say "Bison". The user was
    asked how to handle them; answer: `Keep "Bison" (Recommended)`. The
    official text stays as written, which matches the American-names
    default. A Saturn-names variant decides its own wording under
    `LOC-001`.
- **Gate extension, Nash's ending (2026-10-29, `SESSION-0058`):**
  - The user's decision is **GO**, in their words: "GATE-TRANSLATION: go for Nash's ending. MC10 ending records 16-21 plus whatever the English script needs; page k shows English record k; official arcade English with no rewording; keep "Charlie" in the text and the labels Charlie and Charlie's friend. Record it."
  - Checked at acceptance: `END-001` to `END-005` and `LAYOUT-002` are
    `DONE` (`EXP-0034`-`EXP-0039`).
  - **Scope:**
    - `MC10.SHP` ending records 16-21 (decoded `0x2EC0` + 76k);
    - whatever the Saturn's English ending script needs to show them
      (`LAYOUT-002` option (a)): the code that switches Nash's ending to
      the English script, the English records' pointer, and the records
      wherever `END-007` places them.

    Only Nash's ending with Nash as the first pick is covered. Other
    endings, Nash as second pick, Apocalypse's lines, the pre-boss line,
    the post-boss quote and the warning stay gated.
  - **Pairing:** page k (k = 0-5) shows arcade English slot 16 record k
    (`0x18D0AE` + 100k; D-032, `data/translations/nash_ending_pairing.json`).
  - **Wording:** the official arcade English, with no rewording.
  - **Names:** "Charlie" stays in English records 1 and 4. The labels are
    `Charlie` and `Charlie's friend`, as in the arcade (already in `MCED`).
- **Gate extension, M8 roster endings (2026-10-30, `SESSION-0069`):**
  - The user's decision is **GO**. They were asked: "Extend GATE-TRANSLATION to the endings of all 17 M8 roster characters (slots 0-7 and 9-17, Gouki included)? That covers each MC file's ending records, the English records placed after the win quotes, each slot's MCED English script (Apocalypse's shared with Ryu's, slot 18's with Chun-Li's), and the switch code. Page k shows the character's arcade English ending record k (END-012), in the official arcade English with no rewording." Answer: "Go (Recommended)".
  - Checked at acceptance: `END-010` to `END-013` are `DONE`
    (`EXP-0043`-`EXP-0045`).
  - **Scope:**
    - the ending records of the 17 `END-011` roster slots
      (`data/text/m8_ending_roster.json`), first or second pick;
    - each slot's arcade English ending records, placed after its win
      quotes (version 4: quote table + 800 + 100k);
    - each slot's `MCED` English script. Slot 8's script is switched with
      Ryu's and slot 18's with Chun-Li's, because they are shared
      (`END-011`). Slots 8 and 18 are not marked, and `MC08` gets no
      English ending records;
    - the version 4 switch code and the fixed-table marks.

    Apocalypse's lines, the pre-boss line, the post-boss quote, slot 18's
    character (`SPECIAL-001`) and the warning stay gated.
  - **Pairing:** page k shows the slot's arcade English ending record k
    (D-039, `data/translations/<name>_ending_pairing.json`).
  - **Wording:** the official arcade English, with no rewording.
  - **Names:** the user was asked: "How should the flagged names be handled? The official English says "Bison" in Vega's (M. Bison's) ending records 1 and 4. The arcade's own labels are "Akuma" (Gouki's page 5), "Bison" (Rogue's page 1) and "Vega" (Magneto's page 3, the claw-wielding Shadaloo member, as the US arcade shows)." Answer: "Keep arcade names (Recommended)". The text and labels stay as the US arcade shows them; a Saturn-names variant is `LOC-001`'s.

## Phase F: M1

### RE-001 - Change the chosen quote in live RAM

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** GATE-M0.
- **Blockers:** None.
- **Objective:** Show that writing known codes into the WRAM-L quote record (`0x0024F5D8` table, record 10, `EXP-0015`) changes the Saturn's on-screen win quote.
- **Acceptance criteria:** From the `pre_ko` checkpoint, a trial writes a few known codes into record 10 and the quote screen shows exactly the predicted glyphs in those cells, with everything else unchanged; a no-write control from the same checkpoint shows the original quote; original bytes, written bytes, address, purpose, expected and observed results are recorded (`AGENTS.md` rule 12); the source image is unchanged.
- **Notes:** Live RAM only; nothing is written to the disc image. Glyph codes come from the hiragana relation measured in `EXP-0015` (Unicode − `0x2661`).
- **Evidence:** 2026-10-28, `EXP-0016`, D-011. A cold-boot play check does not apply to a live-RAM change (a boot clears it); it applies from M2, when the change is on the disc image.

## Phase G: M2

### DISC-001 - Trace the quote table to its disc file

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** RE-001.
- **Blockers:** None.
- **Objective:** Find the disc file (and offset) that the WRAM-L quote table (`0x0024F5D8`, `EXP-0015`) is loaded from, and its storage format.
- **Acceptance criteria:** The data track's ISO 9660 layout is recorded (file list with LSN, size, SHA-256); a controlled trace (write breakpoint or read correlation) links the table's bytes to one file and offset; compression, pointers, lengths, checksums and alignment are tested as applicable; facts and uncertainty are recorded.
- **Notes:** The table equals the arcade's Japanese slot-9 data (`EXP-0015`), so a raw search of the files is the first test.
- **Evidence:** `EXP-0017`, D-012. Listing: `references/saturn_jp/iso_listing.json`. The no-input control had no hit; two picks halted in the loader identically. `MC09.SHP` decodes to 43,064 bytes with the table at `0x25D8`, equal to RAM after the load except 259 fields relocated by `+0x0024D040`.

### DISC-002 - Reproduce the M1 change from a rebuilt image

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** DISC-001 (done).
- **Blockers:** None.
- **Objective:** Make the same あいう change on a disc image built from the untouched source, and see it after a cold boot.
- **Acceptance criteria:** A tool patches the source file found by `DISC-001` into a new image under `build/` (same size, in place, Mode 1 EDC/ECC regenerated for every changed sector); unchanged sectors stay byte-identical to the source; the source hashes are unchanged; an unattended cold boot plus the `pre_ko`-style route (or a user play check) shows the changed glyphs; the user does a cold-boot play check (policy).
- **Notes:** Original and new bytes, offsets and sector numbers recorded (rule 12). From `DISC-001`: `MC09.SHP` is compressed. Record 10 is at decompressed offset `0x28D0`, and the M1 bytes `0A21 09E5 0AC8` are at `0x28D6`. The file takes 11 sectors (20,686 bytes, 1,842 bytes of slack). Either re-encode (an encoder the game's decoder accepts) or change the stream in place, and test both against the decoder first. **Marker (2026-10-28):** the quote shown varies between sessions (`EXP-0007` vs `EXP-0013`) and its selector is unknown. So the rebuilt image writes あいう over line-1 cells 3-5 of all 16 Ryu win-quote records; record 10 gets exactly the M1 bytes. (Same method as MSHvSF's M2 marker.)
- **Evidence:** `EXP-0018`, D-013.
  - Only LSN 53,722-53,729 changed, and every sector passes EDC/ECC.
  - Two builds are identical, and the source hashes are unchanged.
  - The cold boot matches the original frame for frame.
  - A pick from a state with the rebuilt image mounted loads the marked
    table; the control loads the original.
  - The user's cold-boot play check (2026-10-28) showed あいう in two wins
    (records 1 and 8).

### FONT-001 - Find the quote font and prove its format

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** DISC-001 (done).
- **Blockers:** None.
- **Objective:** Locate the glyph data behind the quote codes (in RAM and on disc) and the routine that copies glyphs into the VDP1 cells.
- **Acceptance criteria:** The font's RAM location and disc source are found by a controlled trace; its format is proven by a byte-identical repack of the original; the code-to-glyph mapping is tested against the rendered cells.
- **Notes:** MSHvSF's font was compressed and loaded once (a HYPOTHESIS here).
- **Evidence:** `EXP-0019`, D-014.
  - **RAM:** glyph routine `0x06024CF0` and font pointer `0x0602586C` (font at
    `0x002C3EA0`), found from a write log on the staging cell.
  - **Disc:** `FIX.PRS`. A one-byte probe image loads the probe font from a
    cold boot, and the original image is the control.
  - **Format:** byte-identical repack.
  - **Mapping:** 22/22 drawn cells.

### FONT-002 - Latin codes, line length and cell grid

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** FONT-001 (done).
- **Blockers:** None.
- **Objective:** Find which Latin glyphs the quote font has and their codes, and measure how many cells a line and a record hold.
- **Acceptance criteria:** A live display with a control shows the predicted Latin glyphs; the per-line cell count and any width limits are measured on screen; capacity against the arcade English records (2 × 25 codes) is stated.
- **Evidence:** `EXP-0020`, D-015.
  - Arcade English codes draw directly; the exceptions are `@ { | }`.
  - Three live trials and a control: 38/38 exact cells each, and two runs are
    byte-identical.
  - The grid is 2 × 19 cells of 16 px, all shown.
  - Capacity: 25 of 161 quotes fit as written, 59 after re-wrapping.

## Phase H: M3 (Ryu's Win Quotes)

M3: all of Ryu's win quotes are handled programmatically. The order is
`RE-002` and `LAYOUT-001` (no English needed), then `PAIR-001`, then
`GATE-TRANSLATION`, then `RE-003`. Records 16-21 of Ryu's table are ending
text (`EXP-0015`) and stay out of scope (rule 23).

### RE-002 - Identify the win-quote selector and force any record

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** DBG-005, RE-001 (done).
- **Blockers:** None.
- **Objective:** Find what chooses which of Ryu's 16 records is shown, and
  force any record from one checkpoint, so every record can be verified live
  without gameplay.
- **Acceptance criteria:**
  - The selector (index or pointer, its address and writer) is found by a
    controlled trace from the `EXP-0013` checkpoints. For example: a read
    breakpoint on the table from `pre_ko`, then the routine that computes the
    record address.
  - Forcing at least 3 distinct records from one checkpoint shows exactly
    those records (cell check, as in `EXP-0020`), with a no-write control.
  - When the choice is made (before or after the K.O., `EXP-0013`) is stated.
- **Outputs:** An experiment, a forcing script (a debug harness only; it never
  ships), and a runbook entry.
- **Notes:**
  - MSHvSF found an index store and a record pointer written between the K.O.
    and the quote (MSHvSF `EXP-0025`). That is at most a HYPOTHESIS here.
  - The arcade selects the slot at `0xFF8BB4` (`EXP-0009`); its index choice
    is not traced.
- **Evidence:** `EXP-0021`, D-016.
  - The reader `0x06066A84` uses the pointer `0x060F2490`, written by
    `0x0606698C` from the index at task + 38.
  - The index is `RNG() & 0x0F`, stored at `0x06066696` when the quote
    starts.
  - Forcing indices 0, 1, 5, 8 and 15 showed exactly those records over two
    sessions, with controls equal to the live capture. The runbook is in
    `docs/mednafen.md`.

### LAYOUT-001 - Choose how English quotes fit the quote box

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** FONT-001, FONT-002, DISC-002 (done).
- **Blockers:** None.
- **Objective:** Find and test a way to show quotes longer than 2 × 19
  full-cell characters, and record the capacity of each route. The user
  chooses the route (the "Capacity route" in `docs/localization_policy.md`).
- **Why:** None of Ryu's 9 arcade English quotes fits 2 × 19, even
  re-wrapped. They are 43-50 characters long, with lines of up to 25. In all,
  102 of 161 English win quotes do not fit (`EXP-0020`).
- **Candidate routes** (each is a HYPOTHESIS until tested):
  - **(a) Pair glyphs.** New 16×16 glyphs holding two narrow letters each,
    stored in `FIX.PRS` over unused or sacrificed codes, or in a grown file,
    giving up to 76 characters. The same-size limits are 1,659 bytes of slack
    in the file's last sector and an unknown cart-RAM buffer size.
  - **(b) More lines or cells.** Change the renderer's grid. This is a code
    patch; the 38-code record size, the sprite count and the bubble size are
    unmeasured.
  - **(c) Narrower drawing.** For example, an 8-px advance. Also a code patch.
- **Acceptance criteria:**
  - **Limits:** the constraints of each route are measured. This includes
    unused and seldom-used font codes (a census of every quote and ending
    record that uses the font), `FIX.PRS` growth room on disc and in RAM, and
    the renderer's grid constants.
  - **Live test:** at least one route shows synthetic test text (for example
    pair glyphs such as `Th`) in a live quote from a rebuilt image, after a
    cold boot, with an unchanged control, and the original glyphs still draw
    correctly.
  - **Capacity:** a model is recorded (characters per line and per record,
    and how many of the 161 English quotes fit). The user picks the route,
    recorded in the policy.
- **Outputs:** An experiment, font-build tooling (pair glyph rendering and a
  repack via `tools/text/font_pack.py`), and a census report.
- **Notes:**
  - MSHvSF chose pair glyphs and repacked its font at the same size
    (MSHvSF `LAYOUT-001`, `FONT-003`). That is a HYPOTHESIS here.
  - The font passes through cart RAM, and a replayed state keeps its own copy
    (`EXP-0019`), so font tests must start from a cold boot.
- **Evidence:** `EXP-0023`, D-018.
  - Routes measured: (a) pair glyphs offline (113 glyphs for Ryu, 430 for
    the roster, 409 free kanji codes), and (d) the native English mode found
    and shown live.
  - The user chose (d).
  - The image was rebuilt from the untouched source (`MMPACK.PCA` patch +
    `MC09.SHP` records); every sector is valid.
  - Live RAM: 50/50 cells.
  - Two user cold-boot play checks. The first found and rejected version 1;
    the second confirmed version 2 (Ryu English; Wolverine's quote and the
    hint Japanese, 38/38).

### PAIR-001 - Pair Ryu's Saturn records with the arcade English

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** REF-003, REF-004, RE-002 (done).
- **Blockers:** None.
- **Objective:** For each of Ryu's 16 Saturn win-quote records (= the arcade
  Japanese slot 9), find which arcade English record the arcade shows for the
  same game situation, or that none corresponds.
- **Why:** The arcade has 16 Japanese but 9 English records for slot 9
  (`EXP-0015`, `EXP-0008`). So index `k` cannot simply map to English record
  `k`. The policy requires pairing by the game's own selection logic.
- **Acceptance criteria:**
  - The arcade's record-index choice for Japanese and English is traced in
    MAME, from the code, not from data alone. For example: what computes the
    index, and whether English and Japanese draw on the same state.
  - The Saturn's index choice from `RE-002` is compared with the arcade's.
  - A pairing table for records 0-15 is recorded, each entry labelled with
    its evidence and confidence.
  - At least 2 pairs are confirmed by running the same situation in both
    arcade languages (`EXP-0009` method), or the experiment records why that
    is not possible.
- **Outputs:** An experiment and `data/translations/ryu_pairing.json` (codes
  and record numbers only; no game text beyond the official English already
  documented).
- **Notes:** This reads English but writes none to disc, so it runs before the
  gate.
- **Evidence:** `EXP-0022`, D-017, and `data/translations/ryu_pairing.json`.
  - The arcade selector `0x04F396`, a twin of the Saturn's, draws `r =
    rand() & 0xF`. Japanese shows record `r`; English shows `remap[r] = r
    mod 8`.
  - With the draw forced in MAME, all 16 English draws and 4 Japanese draws
    read the predicted record.
  - A natural draw in both languages from one state (r = 10) gave English
    record 2 and Japanese record 10.
  - Ryu's English record 8 is unreachable through this selector.

### RE-003 - Build all of Ryu's win quotes in English from the source image

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** GATE-TRANSLATION, LAYOUT-001, RE-002, PAIR-001, DISC-002.
- **Blockers:** None.
- **Objective:** Compile each of Ryu's 16 win-quote records from its paired
  official English (the gate's policy), through the chosen layout route, into
  `MC09.SHP` (and `FIX.PRS` if the route needs it). Build the image from the
  untouched source and verify every record live.
- **Acceptance criteria:**
  - **Compiler:** a caption compiler turns the pairing table plus the English
    text into record codes (and glyphs) deterministically. It rejects text
    that does not fit, and it has synthetic tests.
  - **Build:** the image is built from the untouched source with
    `tools/disc/patch_image.py`.
    - Only the intended files' sectors change, with valid EDC/ECC.
    - Two builds are identical, and the source hashes are unchanged.
    - Rule 12 records are kept for every changed record.
  - **Live check:** all 16 records are verified live by forcing (`RE-002`)
    from one checkpoint, with each drawn cell equal to the compiler's
    prediction. The original image is the control.
  - **Play check:** the user's cold-boot play check shows English in at least
    two independent Ryu wins (policy).
  - **Provenance:** `data/translations/ryu_win_quotes.json` records the
    arcade source address, English text, pairing, and any opt-in grammar fix
    for each record.
- **Outputs:** An experiment, the compiler and its tests, the translation
  record, and a regression reference.
- **Notes:** Records 16-21 (ending text) are untouched. Other characters are
  M4.
- **Evidence:** `EXP-0024`, D-019, and `data/translations/ryu_win_quotes.json`.
  - **Tools:** `tools/text/caption.py` (the compiler, with tests) and
    `tools/disc/build_english.py`, which rebuilds the play-checked image
    exactly.
  - **Image:** `build/re003_ryu_english`; 138 changed sectors, all valid.
  - **All 16 draws, live:** 50/50 cells as compiled; the control 38/38.
  - **Play check:** two cold-boot Ryu wins in English.
  - **Provenance:** source addresses and hashes in the spec; the text is
    read from the ROM (rule 21).

## Phase I: M4 (A Second Character)

M4: a second character's win quotes work through the same mechanism as
Ryu's, without changing Ryu's. The order is `RE-004`, then `RE-006` and
`PAIR-002` (independent), then the user's gate extension, then `RE-007`.
Endings, special characters and the rest of the roster stay out of scope
(rules 23 and 24; `RE-005` is M5).

### RE-004 - Choose the second character and map its quote file

- **Status:** `DONE`
- **Milestone:** M4
- **Dependencies:** RE-003 (done).
- **Blockers:** None.
- **Objective:** With the user, choose the second character. Find its Saturn
  quote file, the table offset inside it, and the slot number the selector
  sees.
- **Acceptance criteria:**
  - **Choice:** the user's choice is recorded in their words. The candidates
    are offered with their arcade slot, English record count, and whether the
    user can easily win with them (they will need wins in play checks).
  - **Trace:** a controlled trace links the character's quote table to one MC
    file and offset, as `DISC-001` did for Ryu. That is a write breakpoint on
    the table at the character's pick from a session checkpoint, and the
    decoded file matching RAM. This also tests the hypothesis that `MCxx`
    holds slot `0xXX`.
  - **Slot:** the slot × 2 that the selector reads (`@(6,gbr)`) when this
    character speaks is logged. It must match the arcade slot, or the
    difference is recorded.
  - **Identity:** the Saturn table equals the arcade Japanese records for
    that slot, or the differences are recorded.
  - **Load addresses:** where the table loads is recorded both when the
    character is the first team member and when it is the second.
- **Notes:**
  - Done 2026-10-29 (`EXP-0025`, D-020). The user chose **Ken** (arcade
    slot 10; their answer: "Ken (Recommended)").
  - Trace: a write breakpoint on Ken's table halted in the loader at
    `0x0600D124` with file size `0x5ADA` (`MC0A.SHP` only). The control had
    no hit, and a repeat was identical.
  - Ken's table is at decompressed offset `0x2A4C`. It loads at WRAM-L
    `0x0024FA4C` when Ken is first and at WRAM-H `0x060B2A4C` when he is
    second (file bases `0x0024D000` and `0x060B0000`).
  - The selector sees `@(6,gbr)` = `0x0014` (Ryu `0x0012`).
  - Records 0-15 equal arcade Japanese slot 10, and 16-20 are his 5 ending
    records (21 records against Ryu's 22).
  - Correction: the earlier note here placed a partner's file at
    `0x060D5F94`. That is Rogue's table in an opponent's file (base
    `0x060D2000`); the second member's base is `0x060B0000`.

### RE-006 - Let the English mode cover a set of characters

- **Status:** `DONE`
- **Milestone:** M4
- **Dependencies:** RE-004 (done).
- **Blockers:** None.
- **Objective:** Replace the single-slot test in `tools/disc/english_mode.py`
  (`slot × 2 == 18`) with a table of English slots. Adding a character is
  then a data change.
- **Acceptance criteria:**
  - **Patch:** a version-3 patch, still same-size, tests the speaker's slot
    against a per-slot table. A candidate location is the original remap
    table at `0x06066718` (16 bytes), now loaded by nothing; it must be shown
    unused before it is reused. Every original byte is checked.
  - **Live check (RAM):** the slot table switches Ryu and the second
    character to English, while a third character's quote stays
    byte-identical to the unpatched game (the `EXP-0023` Storm control).
  - **Regression:** Ryu's 16 draws still show the same cells as `EXP-0024`.
  - **Tests:** unit tests for the patch table and for the slot-table data.
- **Notes:**
  - The fixed-index mode, endings and type-6 text are still not reached.
    Note any change in the selector paths they share.
  - Done 2026-10-29 (`EXP-0027`, D-022). The remap table holds 16 bytes,
    too few for 19 slots, so version 3 uses the spare high byte of each
    slot's fixed-index word (`0x060666E0` + 2 × slot; 2 = English) instead.
    It was shown unused (static scan, read-breakpoint logs with a positive
    control).
  - Live checks:
    - Ken's byte alone switched his quote (English record 6, 50/50). Without
      it, the screen was byte-identical to the unpatched game.
    - Ryu's 16 draws were byte-identical to `EXP-0024`.
    - Storm was byte-identical to the unpatched game.
  - The fixed-index path changes only in reading the marked word: an
    English slot keeps its fixed index through `and #7`. The remap table at
    `0x06066718` is untouched. `tools.disc.build_english` still uses
    version 2 until `RE-007`.

### PAIR-002 - Pair the second character's records with the arcade English

- **Status:** `DONE`
- **Milestone:** M4
- **Dependencies:** RE-004 (done), PAIR-001 (done).
- **Blockers:** None.
- **Objective:** Confirm that the second character follows the same rule as
  Ryu (Saturn draw `r` shows English record `r mod 8`) and record its
  pairing table.
- **Acceptance criteria:**
  - **MAME runs:** with the character's slot forced, forced draws in MAME
    (`EXP-0022`'s `run_pair.py`) read the predicted English and Japanese
    records. Cover at least 4 draws, including one ≥ 8, in both languages.
  - **Records:** `data/translations/<character>_pairing.json` holds addresses
    and record numbers only.
  - **Fit:** the character's English records 0-7 all fit 2 × 25 and use only
    mapped characters (checked by `tools/text/caption.py`).
- **Notes:**
  - All arcade slots hold 9 English records except slot 8, which holds 8
    (`EXP-0022`), so English record 8 is unused for all of them.
  - Done 2026-10-29 (`EXP-0026`, D-021). Ken follows `r mod 8`: 16 English
    and 4 Japanese forced draws (3, 8, 9, 15) read the predicted records, and
    the control matched `EXP-0022`.
  - `data/translations/ken_pairing.json`: 16 CONFIRMED entries.
  - All 9 English records fit 2 × 25 and recompile exactly. None uses a
    policy-sensitive name.

### GATE-TRANSLATION extension for the second character

Before `RE-007`, the user extends `GATE-TRANSLATION` to the second character
in their own words (the scope is Ryu only today). The extension is recorded
under `GATE-TRANSLATION` and in `docs/localization_policy.md`.

Done 2026-10-29: the user extended the gate to Ken (GO; pairing `k mod 8`;
official arcade English, no rewording). It is recorded under
`GATE-TRANSLATION` and in `docs/localization_policy.md`.

### RE-007 - Build Ryu and the second character from the source image

- **Status:** `DONE` (2026-10-29, `SESSION-0040`, `EXP-0028`, D-023)
- **Milestone:** M4
- **Dependencies:** RE-004 (done), RE-006 (done), PAIR-002 (done), the gate extension above (done).
- **Blockers:** None.
- **Objective:** Generalize `tools/disc/build_english.py` to build several
  characters from their specs, and produce one image with both characters'
  English win quotes.
- **Acceptance criteria:**
  - **Spec:** `data/translations/<character>_win_quotes.json` holds source
    addresses, hashes and pairing, but no text (rule 21).
  - **Build:** one command builds the image from the untouched source. Only
    `MMPACK.PCA` and the two MC files change, every sector passes EDC/ECC,
    the ISO layout is unchanged, two builds are identical, and the source
    hashes are unchanged.
    - Every re-encoded file keeps its size, with its stream ending in its
      last sector.
  - **Live check:** all 16 draws of the second character are shown by
    steering the RNG seed from a checkpoint (`EXP-0024` method), cell for
    cell as compiled. Ryu's 16 draws are re-checked (regression). Other
    characters' quotes stay byte-identical to the unpatched game.
  - **Play check:** the user's cold-boot play check shows English for both
    characters (at least one win each), plus another character's Japanese
    quote and a Japanese continue hint.
- **Outputs:** an experiment record, the generalized build tool and its tests,
  the specs, and a regression reference.
- **Result:** every criterion met (`EXP-0028`).
  - `tools.disc.build_english` takes several specs, applies version 3 with
    their slots, and with `--image` builds the image in one command.
  - Track 01 is `b5dd07c2…`. Only the three files change, at their own
    sizes. All sectors are valid, the layout is unchanged, three builds are
    identical, and the source is unchanged.
  - Ken's 16 forced draws and Ryu's 16 are at 50/50 cells. Ryu's runs are
    byte-identical to `EXP-0024`, which is the regression reference.
  - Play: Ryu and Ken won in English. Rogue's CPU quote and the continue hint
    were Japanese.
  - A win finished by the second member, or a CPU win by Ryu or Ken, was not
    observed (`docs/known_unknowns.md`).

## Phase J: M5 (All Ordinary Win Quotes)

M5: every ordinary character's win quotes are localized by one systematic
build, using the M4 mechanism (version-3 slot table, specs, `k mod 8`
pairing). The order is `RE-005`, then the user's roster decision (`RE-008`),
then `PAIR-003` and `RE-009` (independent), then the user's gate extension,
then `RE-010`, then `RE-011`. Endings (ending records in the MC files
included), special cases and other text surfaces stay out of scope (rules 23
and 24). The one exception is the ordinary win quotes of Gouki and
Apocalypse, which the user put in the roster (`RE-008`). Every fact below about a character other than Ryu and Ken is a
HYPOTHESIS until its task confirms it.

Known before M5:

- The data track has 19 quote files: `MC00`-`MC11` and `MCED`.
  - `MCxx` holds slot `xx` is CONFIRMED for slots 9 and 10 (`EXP-0017`,
    `EXP-0025`). It is SUPPORTED for 3, 0x0B, 0x0F and 0x11 by file content
    (`EXP-0025`).
  - `MCED` has no known slot.
- The arcade has 19 win-quote pointers.
  - 17 slots hold 9 English records and one (slot 8) holds 8.
  - Two pointers alias earlier slots; slot 18 aliases slot 11
    (`EXP-0008`, `EXP-0022`, `SESSION-0035`).
  - The slot order is known only by the arcade name list (`EXP-0011`).
- Two quote-loading cases are unobserved: a win finished by the second team
  member (WRAM-H copy) and a CPU win by an English character
  (`docs/known_unknowns.md`).

### RE-005 - Census the quote files against the arcade slots

- **Status:** `DONE` (2026-10-29, `SESSION-0042`, `EXP-0029`, D-024)
- **Milestone:** M5
- **Dependencies:** RE-007 (done).
- **Blockers:** None.
- **Objective:** For every quote file on the data track, find which arcade
  win-quote slot it holds and where, and list the files that do not fit the
  pattern. This is static analysis of the decoded files and the arcade
  program, with no emulator.
- **Acceptance criteria:**
  - **Per file:** for each of the 19 files, record:
    - its size;
    - whether the stream decodes;
    - the offset of a 16-record Japanese win-quote table equal byte for byte
      to an arcade Japanese slot (table `0x17E19C`), or the closest match and
      its differences;
    - the number of records after the table (ending text);
    - the sector budget (the size the re-encoded file must keep).
  - **Per slot:** for each of the 19 arcade slots, record:
    - the character, from the arcade name list (`EXP-0011`);
    - its English record count, and any alias to an earlier slot;
    - the Saturn file that holds its Japanese table, if any.
  - **Irregular cases:** every file or slot that breaks
    "`MCxx` holds slot `xx`, 16 records, English records 0-7" is listed with
    its evidence. That includes `MCED`, the aliased slots and slot 8.
  - **Live sample:** for one file not yet traced (not `MC09`, `MC0A` or
    `MC0F`), a loader halt or pick-load confirms that the file loads when its
    character is picked. This upgrades the mapping rule from SUPPORTED, or
    rejects it.
  - **Output:** a census script under the experiment, and
    `data/text/slot_census.json` holding offsets, counts, sizes and hashes
    only, no text (rule 21).
- **Notes:** method from MSHvSF `RE-041` (`docs/playbook_from_mshvsf.md`,
  Phase 3). Its findings (18 ordinary files, 5 irregular) are not XvSF facts.
- **Result:** every criterion met (`EXP-0029`, `data/text/slot_census.json`).
  - `MC00`-`MC11` each hold exactly one 16-record table, equal to arcade
    Japanese slot `xx`, followed by 4-12 ending records. All streams end in
    their last sector.
  - Slots 0-17 have 9 English records each, except slot 8 (Apocalypse),
    which has 8.
  - Live: picking Cyclops (second member) halted in the loader with R5 =
    `0x8A53` (`MC01` only) at base `0x060B0000`. A repeat was identical, and
    the control had no event.
  - Irregular: `MCED` holds no quote or ending record (role unknown), and
    slot 18 aliases slot 11 with no file of its own.

### RE-008 - Choose the M5 roster and its exceptions

- **Status:** `DONE` (2026-10-29, `SESSION-0043`)
- **Milestone:** M5
- **Dependencies:** RE-005 (done).
- **Blockers:** None; the decision is the user's.
- **Objective:** With the user, fix which characters M5 localizes. Record
  every excluded slot or file with its reason and evidence.
- **Acceptance criteria:**
  - **Choice:** the candidates come from the census, each with its slot,
    file, English record count and any irregularity. The user's decision is
    recorded in their words.
  - **Roster file:** `data/text/m5_roster.json` lists each character's slot,
    MC file and table offset.
  - **Exceptions:** `docs/coverage_exceptions.md` lists every file and slot
    not in the roster with its reason, evidence and the task that would take
    it up (for example `SPECIAL-001`).
- **Notes:** Rule 24 keeps secret characters, bosses and other special cases
  out until a task allows them. Which XvSF characters count as special is
  part of this decision. The census, not the name list alone, provides the
  evidence.
- **Result:** the user chose all 18 characters of slots 0-17. Their answer,
  verbatim: "All 18, with Apocalypse".
  - The options put to them were: the 16 on the select grid; 16 plus Gouki;
    all 18 with Apocalypse.
  - Evidence offered: the select grid (`EXP-0025` session, frame 3083) shows
    16 portraits. Gouki (slot 15) and Apocalypse (slot 8, the boss) are not
    on it.
  - `data/text/m5_roster.json` lists the 18 (slot, file, table offset,
    English record count, American name).
  - `docs/coverage_exceptions.md` lists `MCED`, slot 18, the ending records
    and English record 8.
  - This is the task permission rule 24 requires, for Gouki's and
    Apocalypse's ordinary win quotes only.

### PAIR-003 - Confirm the pairing for every roster character

- **Status:** `DONE` (2026-10-29, `SESSION-0044`, `EXP-0030`, D-025)
- **Milestone:** M5
- **Dependencies:** RE-008 (done).
- **Blockers:** None.
- **Objective:** Confirm in MAME that every roster character follows
  `r mod 8`, and record each pairing table.
- **Acceptance criteria:**
  - **MAME runs:** for each roster slot, forced draws in MAME read the
    predicted English record for all 16 draws. Japanese reads are checked
    for at least 4 draws, including one ≥ 8. This generalizes `EXP-0022`'s
    `run_pair.py` and `EXP-0026` to take the slot.
  - **Records:** `data/translations/<character>_pairing.json` for each
    character, with addresses and record numbers only.
  - **Fit:** every English record 0-7 of every roster slot fits 2 × 25,
    recompiles exactly, and uses only codes whose Saturn glyph is the
    expected character. `@`, `{`, `|` and `}` draw other glyphs (D-015) and
    must be listed if used.
  - **Names:** any record that names a character whose American and Saturn
    names differ (`docs/names.md`) is listed for the gate decision.
- **Notes:** the selector and its remap are shared by all slots, so the rule
  is expected to hold everywhere, but that is a HYPOTHESIS (rule 3). An
  aliased or 8-record slot may break it.
- **Result:** every criterion met (`EXP-0030`).
  - 360 forced MAME runs, all as predicted: 16 English draws and 4
    Japanese draws (3, 8, 9, 15) for each of the 18 slots, including
    Apocalypse's 8-record slot.
  - 16 new pairing files (Ryu's and Ken's agree and are unchanged).
  - Fit: all 144 shown English records recompile exactly, with no
    unexpected glyph (`data/translations/m5_english_fit.json`).
  - Names for the gate: Cammy's English records 0 and 4 (Saturn records 0,
    8, 4, 12) say "Bison", the US name of the Saturn's Vega. No other shown
    record names a character whose names differ.
  - The first batch used `EXP-0022`'s script unchanged. Its read log
    started above slots 0-5's Japanese records, so the script was copied
    with a wider log and everything was rerun.

### RE-009 - Check that every roster file fits its sectors

- **Status:** `DONE` (2026-10-29, `SESSION-0045`, `EXP-0031`, D-026)
- **Milestone:** M5
- **Dependencies:** RE-008 (done).
- **Blockers:** None.
- **Objective:** Before building, show that each roster MC file, with its 8
  English records written over the start of its table, re-encodes within
  its original size, with its stream ending in its last sector.
- **Acceptance criteria:**
  - **Sizes:** for every roster file, the original size, the re-encoded
    size and the margin are recorded.
  - **Untouched bytes:** outside the 800-byte English area, the rebuilt
    file decodes to the original decoded file byte for byte.
  - **Options:** if a file does not fit, measure the alternatives and put
    them to the user before `RE-010`. Examples: a better encoder, or fewer
    changed bytes where English equals the original. Do not choose one.
- **Notes:** `MC09` and `MC0A` fit (`EXP-0024`, `EXP-0028`). The open
  question "Will longer (English) quote files fit 11 sectors?"
  (`docs/known_unknowns.md`) is answered here for the roster.
- **Result:** every criterion met (`EXP-0031`, `data/text/m5_sector_fit.json`).
  - All 18 files fit, with margins from 175 bytes (Apocalypse, `MC08`) to
    1,176 bytes (Chun-Li, `MC0B`).
  - Each rebuilt file keeps its size, ends its stream in its last sector,
    and is unchanged outside the 800 English bytes.
  - Ryu's and Ken's rebuilt files equal `EXP-0028`'s. No option needs the
    user.

### GATE-TRANSLATION extension for the M5 roster

Before `RE-010`, the user extends `GATE-TRANSLATION` to the roster's
ordinary win quotes in their own words. They decide on the pairing, the
wording and any names listed by `PAIR-003`. The extension is recorded under
`GATE-TRANSLATION` and in `docs/localization_policy.md`.

Done 2026-10-29: GO for all 18 roster characters (`k mod 8`, official arcade
English, no rewording), with "Bison" kept as written in Cammy's two records.
It is recorded under `GATE-TRANSLATION` and in `docs/localization_policy.md`.

### RE-010 - Build the roster image and verify it

- **Status:** `DONE` (2026-10-29, `SESSION-0047`, `EXP-0032`, D-027)
- **Milestone:** M5
- **Dependencies:** PAIR-003 (done), RE-009 (done), the gate extension above
  (done).
- **Blockers:** None.
- **Objective:** One command builds, from the untouched source, an image in
  which every roster character shows its official English win quotes. Every
  file outside the roster stays unchanged.
- **Acceptance criteria:**
  - **Build:** the `RE-007` build criteria, for every roster file:
    - only `MMPACK.PCA` and the roster's MC files change, at their sizes;
    - all sectors pass EDC/ECC, and the layout is unchanged;
    - two builds are identical, and the source is unchanged;
    - the slot table marks exactly the roster slots.
  - **Every record, live:** every roster English record (8 per character)
    is drawn through the English renderer from a checkpoint, cell for cell
    as compiled (50/50). Writing the records into a known speaker's table in
    RAM (the `EXP-0028` method) is enough for this.
  - **Loads:** every roster file, picked from the built disc, loads equal to
    the built file plus its fix-ups. If the pick states this needs do not
    exist, one recorded user session supplies them.
  - **Structural classes, in play:** the user's cold-boot play check covers:
    - a first-member win;
    - a win finished by the second member;
    - a CPU win by a roster character;
    - a non-roster speaker's Japanese quote;
    - a continue hint;
    - an irregular file if one is in the roster.
    Apocalypse's quote shows only when he beats the player. If the play
    check cannot reach it, a forced draw from a checkpoint of his win
    covers his file instead, and the gap is recorded.
    Each English quote's pointer is read from a play state (`EXP-0028`'s
    `play_pointers.py`).
  - **Ryu and Ken:** their forced draws stay byte-identical to `EXP-0028`.
- **Outputs:** an experiment record, the roster build and its tests, the
  specs, and the play-check evidence.
- **Result:** every criterion met (`EXP-0032`).
  - **Image:** `build/re010_roster_english`, Track 01 `36672c5d…`, built in
    one command. Only `MC00`-`MC11` and `MMPACK.PCA` change. All sectors
    are valid, the layout is unchanged, `b1` = `b2`, and the 58 code bytes
    are all at `patches_v3(0-17)` sites.
  - **Records:** 144/144 drawn 50/50 at 12 px.
  - **Ryu and Ken:** 34 runs byte-identical to `EXP-0028`.
  - **Loads:** 16 grid characters picked from the built disc load as built.
    Gouki's and Apocalypse's files loaded from the disc in play.
  - **Play:** English for a first-member win (Gouki), second-member wins
    (Cyclops; Ken from WRAM-H) and CPU wins (Storm; Apocalypse). The
    continue hint stayed Japanese.
  - **Not applicable:** no Japanese win quote remains in ordinary play,
    because every ordinary speaker is in the roster. Only slot 18, whose
    user is unknown, could show one.
  - **Observed in passing:** Apocalypse's pre-fight line, a Japanese box
    at the top of the screen (`docs/text_surfaces.md`, `SPECIAL-001`).

### RE-011 - Regression references for the confirmed builds

- **Status:** `DONE` (2026-10-29, `SESSION-0048`, `EXP-0033`, D-028)
- **Milestone:** M5
- **Dependencies:** RE-010 (done).
- **Blockers:** None.
- **Objective:** Every confirmed build can be rebuilt from the untouched
  source, with its hashes compared, by one script.
- **Acceptance criteria:**
  - **References:** each confirmed build is recorded with its command,
    inputs and expected file and Track 01 hashes: `EXP-0024` (Ryu, version
    2), `EXP-0028` (Ryu and Ken) and `RE-010` (roster).
  - **Script:** one command rebuilds each reference under `build/` and
    reports match or mismatch per file. A run on a clean checkout matches
    every reference.
  - **Report:** `docs/regression_report.md` lists the references and the
    last run.
- **Notes:**
  - Method from MSHvSF `RE-047` (`docs/playbook_from_mshvsf.md`).
  - Gap found while writing the README (`SESSION-0047`): every build reads
    the US program in 68000 byte order at `local/ref003/xmvsfu-68k.bin`. It
    was assembled by `tools.reference.xvsf_text.build_program`, but no
    command writes that file. A clean-checkout run needs one, checked
    against the image's SHA-256 (`1b1a5a26…`,
    `data/text/slot_census.json`).
- **Result:** every criterion met (`EXP-0033`).
  - `tools.reference.xvsf_text --program-out` now writes the program image
    (`1b1a5a26…`, byte-identical).
  - `data/regression/references.json` holds the three builds.
    `tools.disc.regression` rebuilds and compares them.
  - Results: all match from the working copy and from a fresh clone (27 of
    27 hashes). An altered hash is caught (exit 1).
  - `docs/regression_report.md` is the clean run's report.

## Phase K: M6 (Ending Investigation)

M6: one ordinary character's ending is understood well enough to localize
it. That means how to reach it, which text it shows, how that text is drawn,
where it lives in RAM and on disc, and which official English exists for it.
Nothing is changed on disc for English in M6. That is M7, after a
`GATE-TRANSLATION` extension for endings.

Rule 23 is satisfied: win quotes are proven and generalized (M5, D-027,
D-028). Assume **nothing** about endings from win quotes (playbook
Phase 4). The order is `END-001` (user choice and session), then `END-002`
and `END-004` (independent), then `END-003`. Special cases stay out (rule
24): Apocalypse's own pre-fight and post-fight lines belong to
`SPECIAL-001`, even where an ordinary ending begins after his fight.

Known before M6 (each is at most SUPPORTED for the Saturn's endings):

- **Arcade English** (`EXP-0008`): the ending table is `0x17E318`, with 19
  pointers to 2 × 25-code records, 109 unique records, 4-13 per slot.
  Japanese twin table: `0x17E2CC`, 76-byte records. Pointer equalities:
  - English: slot 9 (Ryu) equals slot 8 (Apocalypse), and slot 18 equals
    slot 11 (Chun-Li);
  - Japanese: slot 8 equals slot 7 (Magneto), and slot 18 equals slot 11.

  What these equalities mean is UNKNOWN.
- **Saturn files** (`EXP-0029`): each `MCxx` holds, after its 16 quotes,
  4-12 records equal to arcade slot `xx`'s first Japanese ending records
  (counted, not read). The counts differ from the arcade English counts:
  Cyclops 7 against 9, Juggernaut 9 against 6, Cammy 12 against 13. So
  endings cannot be assumed to pair like win quotes.
- **Saturn code** (`EXP-0023`; `EXP-0035`, D-030): the type-4 selector
  `0x060668A2` and the quote renderer `0x06066948` draw Nash's ending
  (confirmed). Since version 2, the selector's language read is the
  constant 0, and the version-3 patch leaves the ending unchanged.
- **`MCED.SHP`** (`EXP-0029`) holds no quote or ending record. Its name may
  suggest "ending", but that is not evidence.
- **Reach** (`EXP-0034`, D-029): Nash's ending (chosen by the user: "Nash
  (Recommended)") is reached by winning the fight between the two team
  members after Apocalypse. It is six timed pages, with Latin speaker labels
  on pages 3-6, and replays pixel-identically from
  `local/checkpoints/end001/f00220064.mcs` with no input. Losing that
  fight gives no ending. Whose ending plays in general is SUPPORTED only.

### END-001 - Choose an ending and reach it

- **Status:** `DONE` (`EXP-0034`, D-029)
- **Milestone:** M6
- **Dependencies:** RE-011 (done).
- **Blockers:** None.
- **Objective:** With the user, choose one ordinary character's ending.
  Reach it in a recorded session, keep checkpoints before and during it,
  and inventory every text surface it shows.
- **Acceptance criteria:**
  - **Choice:** the candidates are offered with:
    - their arcade English ending record count;
    - their Saturn after-table record count;
    - whether the user can beat Apocalypse with them.

    The user's choice is recorded in their words.
  - **Session:** a recorded cold-boot session (untouched source image)
    reaches the chosen ending. It keeps checkpoints just before the final
    K.O., at the first ending text, and at each later text page. Use
    `--keep-states` large enough, or keep the cited states, so none is
    pruned.
  - **Inventory:** every text surface between the final K.O. and the credits
    or attract is listed in `docs/text_surfaces.md`, with screenshots
    verified by the agent. Examples are post-fight lines, ending pages,
    speaker boxes and credits. For each surface, note its frame range, its
    look (box, font size, position) and whether it is Japanese.
  - **Repeatability:** the ending replays from the checkpoint before the
    K.O. with no input, twice, giving the same screens. If not, record what
    differs.
  - **Team:** record which team member the ending follows: the point
    character, the K.O. scorer or the first pick. This is a HYPOTHESIS
    to test in `END-004`.
- **Notes:** method from MSHvSF `END-001` (playbook Phase 4, step 1). A
  no-play route on the Saturn (forcing the boss's vitality or the stage
  word in RAM) is welcome but not required. Any such address must be
  found by experiment, not borrowed.

### END-002 - How the ending text is drawn

- **Status:** `DONE` (`EXP-0035`, D-030)
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None; checkpoints are in `local/checkpoints/end001/` (`EXP-0034`).
- **Objective:** Find which code, font and grid draw each Japanese ending
  surface from `END-001`.
- **Acceptance criteria:**
  - **Font:** the drawn cells of one ending page match a decoded font. That
    is the quote font in `FIX.PRS` (`EXP-0020`) or another one, to be found.
    One VDP1 or VDP2 cell is zeroed, and exactly that glyph disappears
    (the MSHvSF `EXP-0038` method, re-run on XvSF).
  - **Code:** a halt or read breakpoint shows whether the type-4 selector
    `0x060668A2` and the renderer `0x06066948` run for the ending. If they
    do not, the code that does is identified.
  - **Grid:** cells per line, lines per box and the pixel pitch are
    measured.
  - **English mode:** say whether the arcade's English mode (2 × 25 at
    12 px, `EXP-0023`) is reachable for this surface, from code and from a
    RAM trial on a checkpoint. No disc change.
  - **Patch regression:** the ending on the roster image matches the
    unpatched game. Test it by replaying an ending checkpoint twice, once
    with the version-3 patch sites set back to their original bytes in RAM
    and once without, so that the only change is the patch. This answers
    the open question of whether the English-mode patch leaves endings
    unchanged (`docs/known_unknowns.md`).

### END-003 - Where the ending text lives

- **Status:** `DONE` (`EXP-0036`, D-031)
- **Milestone:** M6
- **Dependencies:** END-002.
- **Blockers:** None. `EXP-0035` found the RAM records (`MC10` records 16-21 at `0x0024FEC0` + 76k, matching the decoded file); the writer, marker and census criteria remain.
- **Objective:** Find the chosen ending's records in RAM, trace them to
  their disc file, and prove a disc edit reaches the screen.
- **Acceptance criteria:**
  - **RAM:** the records shown are found live with their address and
    record size. A single RAM write before the page changes exactly the
    predicted cells.
  - **Disc:** a write breakpoint from a before-load checkpoint catches each
    writer. The source file and offset are identified, and the decoded file
    matches RAM, allowing for relocation fields if any. Check the
    after-table records in `MCxx` and `MCED.SHP` first, but neither is
    assumed.
  - **Marker:** a same-size marker edit in that file, built into an image
    under `build/` from the untouched source, shows on screen at the
    predicted cells.
  - **Census:** say whether the other characters' endings use the same file
    pattern. This is a static check against the arcade's Japanese ending
    blocks, and it records each file's ending record count.
- **Notes:** where the dialogue lives may differ from where the pages live
  (MSHvSF found them in different files; HYPOTHESIS here).

### END-004 - Arcade English and indexing for the ending

- **Status:** `DONE` (`EXP-0037`, D-032)
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None; Nash's ending and its inventory are in `EXP-0034` and `docs/text_surfaces.md`.
- **Objective:** Find which official English exists for each surface of
  the chosen ending, and how the arcade picks its records, so that each
  Saturn ending record can be paired with its English one by game logic.
- **Acceptance criteria:**
  - **Route:** a scripted MAME run (`xmvsfu`) reaches the chosen ending
    with no play, by forcing documented RAM words found by experiment. It
    also reaches it in Japanese (the `EXP-0022` language-word method). Each
    forced word is recorded with its evidence.
  - **Records:** for each ending surface, the arcade English records read,
    from the read log, are mapped to the Saturn's surfaces from `END-001`.
    Surfaces with no arcade English are listed.
  - **Indexing:** before running, record predictions for two team
    combinations (the same point character with two different partners),
    then check them in MAME. Then record the rule: the records shown as a
    function of point, partner and language.
  - **Pairing:** a pairing table from Saturn ending record to arcade
    English record for the chosen character, with addresses only
    (`data/translations/<character>_ending_pairing.json`). Each entry is
    CONFIRMED by a MAME read or marked as rule only.
  - **Names:** list each English record that names a character whose names
    differ (`docs/names.md`), for the gate.
- **Notes:** the record counts differ between the Saturn files and the
  arcade English (see above). The pairing must explain the difference, not
  assume `k mod n`.

## Phase L: M7 (Nash's Ending In English)

M7: Nash's ending shows the official arcade English on the Saturn, built
from the untouched source image and confirmed in play. M6 is complete
(D-029 to D-032). Assume nothing from win quotes or from MSHvSF: every step
below needs its own XvSF evidence.

Only Nash's ending is in scope, with Nash as the first pick. These are out
of scope:

- other characters' endings (M8);
- Nash's ending when he is the second pick;
- Apocalypse's lines, the pre-boss story line and the post-boss win quote
  (`SPECIAL-001`);
- the `⚠乱入禁止` warning (`UI-001`);
- the QSound notice.

The order:

1. `END-005` (investigation, ready);
2. `LAYOUT-002` (the user's layout choice);
3. the `GATE-TRANSLATION` extension (the user's decision);
4. `END-006` (code) and `END-007` (data), which are independent;
5. `END-008` (build and play check);
6. `END-009` (regression).

Known before M7:

- **Records and pairing** (D-031, D-032): the six pages are decoded
  `MC10.SHP` records 16-21 (`0x2EC0` + 76k), loaded at the pick by
  `0x0600D124` into `0x0024D000`. Page k pairs with arcade English slot 16
  record k (`0x18D0AE` + 100k), CONFIRMED for both partners
  (`data/translations/nash_ending_pairing.json`). English records 1 and 4
  say "Charlie".
- **Drawing** (D-030):
  - The type-4 selector `0x060668A2` (once per scene) and the renderer
    `0x06066948` (once per page) draw the pages in the 2 × 19 quote grid.
  - The renderer's English grid (2 × 25 at 12 px) is reachable. The
    selector has a language-2 branch whose list `0x06085544` is not filled
    on the Saturn.
  - The version-3 patch makes the selector's language read a constant 0.
- **The scene script depends on the language** (D-032). The arcade English
  ending:
  - starts scenes at pages 1, 2, 4 and 5 (Japanese: 1, 3, 5, 6);
  - shows other pictures;
  - labels pages 4 and 5 `Charlie` and `Charlie's friend` (Japanese: `Nash`,
    `Nazo no koe`, `Nash`, `Nash's friend` on pages 3-6).

  With the global words set to 2, the Saturn showed a `Charlie` label and
  a picture change (`EXP-0035`). So it may hold an English script, but
  the global size word has other readers, so that trial is not clean.
- **Space:** `MC10.SHP` is 12 sectors. With its English win quotes, it
  compresses with 671 bytes to spare (`EXP-0031`). Six English records are
  600 bytes, against 456 for the Japanese.

### END-005 - The Saturn's English ending script

- **Status:** `DONE` (`EXP-0038`, D-033)
- **Milestone:** M7
- **Dependencies:** END-004 (done).
- **Blockers:** None.
- **Objective:** Find out whether the Saturn can show Nash's ending with
  the arcade's English scene script, and what that takes, using RAM
  changes only.
- **Acceptance criteria:**
  - **Language reads:** every read of the language word (and of anything
    else that tells the ending's script which language to use) during
    Nash's ending is listed by PC, from a read or PC log over
    `local/checkpoints/end001/f00220064.mcs`. For each, say whether it
    picks text, pictures, labels or scene breaks. Use the arcade's ending
    readers (`0x04F530`-`0x04F5F2`, `0x06F904`; `EXP-0037`) as hints, not
    as facts.
  - **Clean trial:** the English path is turned on for this ending only:
    - no global size word;
    - one change, for example the task flag that version 3 uses for win
      quotes, or a single per-ending value found above;
    - a valid pointer to the six arcade English records written into free
      RAM.

    The six pages are compared with `EXP-0037`'s arcade English snapshots:
    scene breaks, picture per page, label per page, text per page, line
    count, page timing.
  - **Labels:** where the Saturn's labels (`Nash`, `Nazo no koe`, `Nash's
    friend`, `Charlie`) live in RAM and on disc is found, with a one-cell
    RAM edit that changes exactly one label letter on screen. Say whether a
    `Charlie's friend` label exists.
  - **Result:** one of these, with evidence:
    - the Saturn's English script matches the arcade's;
    - it differs (each difference listed);
    - no usable English script exists.
- **Notes:** if the English script does not exist or differs, `LAYOUT-002`
  offers the alternatives. No disc change in this task.

### LAYOUT-002 - Choose how Nash's ending shows English

- **Status:** `DONE` (`EXP-0039`)
- **Milestone:** M7
- **Dependencies:** END-005.
- **Blockers:** None.
- **Objective:** The user chooses the layout of the English ending from
  measured options, each with RAM-trial screenshots of all six pages.
- **Acceptance criteria:**
  - **Options:** each is shown with its six pages and its costs (code
    patch, data size, what differs from the arcade). At least these,
    where `END-005` shows them possible:
    - **(a) English script:** the Saturn's English script with the arcade
      English records, as in the arcade.
    - **(b) Japanese script, English text:** the Japanese scene breaks,
      pictures and labels, with English text in the 2 × 25 grid. The
      mismatches are listed page by page. For example, the scream would
      appear under `Nazo no koe` with the captive picture.
    - **(c) Something else** `END-005` turns up.
  - **Labels:** the user's choice for labels, in the American-names
    default: the arcade's `Charlie` / `Charlie's friend`, or the
    Japanese-script labels rewritten. If a label must be new or changed,
    the cost is measured.
  - **Recorded:** the user's choice, in their words, here and in
    `docs/localization_policy.md`.
- **Decision (2026-10-29):** option (a), the Saturn's English scene
  script, with the arcade labels. In the user's words: "(a) English layout
  (Recommended)" and "Arcade names (Recommended)". Recorded in
  `docs/localization_policy.md`; trials and costs in `EXP-0039`.

### GATE-TRANSLATION extension for Nash's ending

Before `END-008`, the user extends `GATE-TRANSLATION` to Nash's ending: GO
or NO-GO in their own words, recorded under `GATE-TRANSLATION` and in
`docs/localization_policy.md`. The question covers:

- **Scope:** `MC10` ending records 16-21, plus any labels or script data
  that `LAYOUT-002` requires.
- **Pairing:** page k = English record k (D-032).
- **Wording:** the official arcade English, with no rewording.
- **Names:** English records 1 and 4 say "Charlie", and the labels are
  `Charlie` and `Charlie's friend`. This is the American-names default.
  The user is asked to confirm it.

Dependencies: `LAYOUT-002`.

**Status: `DONE` (2026-10-29).** The user said GO; the decision is
recorded under `GATE-TRANSLATION` above and in
`docs/localization_policy.md`.

### END-006 - Code: turn the English ending on for Nash only

- **Status:** `DONE` (`EXP-0040`, D-034)
- **Milestone:** M7
- **Dependencies:** END-005, LAYOUT-002.
- **Blockers:** None; `LAYOUT-002` chose option (a) (`EXP-0039`).
- **Objective:** A same-size code change in `MMPACK.PCA` (version 4 of the
  patch, building on version 3) that shows the chosen layout for Nash's
  ending, with every other ending, win quote and hint unchanged.
- **Acceptance criteria:**
  - **Design:** the patch sites, original and new bytes, and purpose are
    recorded (rule 12). It is turned on per slot, as version 3 is for win
    quotes, and reads no global word the size-word readers depend on.
  - **Pointer:** the source of the English records' pointer for slot 16
    is documented. It must work when Nash is the first pick; say what
    happens if he is the second.
  - **RAM trial:**
    - with the version-4 code in RAM and the English records in RAM, Nash's
      ending shows the chosen layout on all six pages;
    - with no English records for a slot, that slot's ending is unchanged
      (checked on at least one other ending checkpoint, or by code
      argument if none exists);
    - win quotes are unchanged: the `EXP-0032` forced-draw checks pass.
  - **Code location:** the patch fits the code already decoded from
    `MMPACK.PCA`, and the file still fits its sectors.

### END-007 - Data: place Nash's English ending records

- **Status:** `DONE` (`EXP-0041`, D-035)
- **Milestone:** M7
- **Dependencies:** LAYOUT-002.
- **Blockers:** None; `LAYOUT-002` chose option (a) (`EXP-0039`).
- **Fixed by `END-006`:** version 4 reads the English records at quote
  table + 800 (`MC10` decoded `0x2D20`), and Nash's `MCED` script header
  changes (`0x2CF0`: `0008` → `0038`). The offset criterion below becomes:
  show that `MC10`'s bytes from table + 800 to table + `0x578` are unread in
  play once both are English.
- **Objective:** Put the six English records (and any label or script
  data the layout needs) into `MC10.SHP`, or another loaded file, so that
  the `END-006` pointer finds them.
- **Acceptance criteria:**
  - **Offset:** the chosen offset is justified: either free space proven
    unused (a read log over the whole ending and the fights), or a
    replacement of data shown not to be needed. The 456 bytes of
    Japanese records are smaller than the 600 bytes of English.
  - **Fit:** `MC10.SHP` with English win quotes and English ending fits
    its 12 sectors (the `EXP-0031` method). Otherwise the alternative is
    measured.
  - **Spec:** a data spec with addresses and hashes only (rule 21), such
    as `data/translations/nash_ending.json`. It compiles the arcade
    records from the program image at build time, as `build_english.py`
    does for win quotes.
  - **Load check:** after a pick on a build, the buffer equals the built
    file plus fix-ups (the `EXP-0036` `pick_writer.py` method).

### END-008 - Build Nash's English ending and play-check it

- **Status:** `DONE` (`EXP-0042`, D-036)
- **Milestone:** M7
- **Dependencies:** GATE-TRANSLATION extension for Nash's ending, END-006,
  END-007.
- **Blockers:** None. `EXP-0041` already built `build/m7_nash_ending` with the extended tool, and its no-play route (`saturn_route.py`, with the build's code in RAM) showed the six English pages. That covers the "fast check". What remains is the cold-boot play check by the user, the win-quote check in that session, and the before and after record.
- **Objective:** One image, built from the untouched source, with all 18
  roster characters' English win quotes and Nash's English ending, shown
  in play.
- **Acceptance criteria:**
  - **Build:** `tools.disc.build_english` (extended for ending specs) builds
    the image under `build/`. The changed files and sectors are recorded,
    and all sectors pass EDC/ECC.
  - **Fast check:** before play, the agent replays the ending pages from a
    pick on the build plus RAM checkpoints, where possible, to catch faults
    early.
  - **Play check:** the user plays from a cold boot with Nash first to his
    ending. The agent checks every page against the chosen layout and the
    arcade English (`EXP-0037` snapshots): text, labels, pictures, scene
    breaks, no Japanese left.
  - **Win quotes:** the session's win quotes are still English.
  - **Recorded:** before and after screenshots, by hash (rule 11).

### END-009 - Regression reference for the ending build

- **Status:** `DONE` (D-037)
- **Milestone:** M7
- **Dependencies:** END-008.
- **Blockers:** None; `build/m7_nash_ending` is confirmed (`EXP-0042`).
- **Objective:** Add the M7 build to `data/regression/references.json`, and
  show that every reference still rebuilds byte for byte.
- **Acceptance criteria:**
  - The new reference records the specs, the patch version and the expected
    hashes. `tools.disc.regression` matches all references, including the
    earlier three.
  - The README's status and build section mention Nash's ending.

## Phase M: M8 (Every Roster Ending In English)

M8: the M7 pipeline, generalized. Every roster ending that the user puts
in scope shows its official arcade English on the Saturn, whether the
character is picked first or second. All of it is built from the untouched
source, together with the win quotes, verified, and registered.

M7 is complete (D-029 to D-037). Nothing from Nash's ending is assumed for
another character: each character's script, pairing, space and screens get
their own evidence. Special cases stay out until `END-011` puts them in
scope (rule 24). Apocalypse's pre-fight line, the post-boss story screens,
the warning and other UI stay with `SPECIAL-001` and `UI-001`.

The order:

1. `END-010` (static census, ready);
2. `END-011` (the user's roster choice);
3. `END-012` (arcade pairing) and `END-013` (Saturn route), which are
   independent;
4. the `GATE-TRANSLATION` extension;
5. `END-014` (build);
6. `END-015` (verify every ending);
7. `END-016` (coverage and regression).

Known before M8:

- **One ending is proven** (Nash, slot 16, first pick):
  - **Code:** version 4 (`patches_v4`) marks a slot with bit 7 of its
    fixed-table low byte.
  - **Records:** the English records go at quote table + 800.
  - **Script:** the slot's `MCED` script header word 0 is set to its
    English script (`mced_english_scripts`).
  - **Build and check:** `build_english` builds ending specs. The Saturn
    route (`EXP-0041` `saturn_route.py`) reaches the ending with no play.
- **Space** (`data/text/ending_census.json`, D-031). After the 800 bytes of
  English win quotes, each file has 416 + 76 × (its Japanese ending
  records) bytes before the old Japanese ending ends. Every roster slot's
  English ending (100 × the arcade English count) fits there:
  - tightest: Cammy (1,300 of 1,328), Magneto and Apocalypse (700 of 720);
  - widest: Juggernaut (600 of 1,100).

  The compressed fit is not measured. The M5 margins range from 175 bytes
  (Apocalypse) to 1,176.
- **Counts:** arcade English counts per slot 0-17 are 6, 9, 6, 6, 5, 6, 6,
  7, 7, 7, 4, 6, 6, 5, 5, 6, 6, 13. The Saturn Japanese counts are 7, 7, 7,
  8, 6, 4, 9, 4, 4, 6, 5, 7, 4, 4, 4, 4, 6, 12.
- **Aliases:**
  - Arcade English: slot 9 (Ryu) equals slot 8 (Apocalypse).
  - Arcade Japanese: slot 8 equals slot 7 (Magneto).
  - `MCED`: slots 8 and 9 share one script, and slots 11 and 18 share
    another.
  - What these mean is UNKNOWN.
- **Labels** (D-033): `MCED`'s 40-entry list has the roster names, `Bison`,
  `Akuma`, `Charlie` and 18 other speakers.
- **Team rule** (`EXP-0034`, `EXP-0037`): the ending belonged to the
  partner fight's winner, who was the first pick in every run. Whose ending
  plays when the second pick wins the partner fight is untested on the
  Saturn. Nash's English ending as second pick is untested.

### END-010 - Census of every roster ending's scripts and space

- **Status:** `DONE` (`EXP-0043`, D-038)
- **Milestone:** M8
- **Dependencies:** END-009 (done).
- **Blockers:** None.
- **Objective:** A static census, from the decoded files and the arcade
  program only, of what each roster slot's English ending needs.
- **Acceptance criteria:**
  - **Scripts:** for each slot 0-18, both `MCED` scripts are parsed (the
    `EXP-0038` format): scenes, pages, record indices, page lengths, label
    indices and their names. The English script's records must be 0 to the
    arcade English count − 1, once each, in order. Any other shape is
    listed.
  - **Shared scripts and aliases:** slots 8/9 and 11/18 share scripts, and
    the arcade has the English 9 = 8 and Japanese 8 = 7 equalities. Each is
    explained from data (which character's records the shared script reads)
    or recorded as open, with the experiment that would settle it.
  - **Space:** for each slot, the English bytes against the free space
    after the English win quotes. Then the compressed fit, with English win
    quotes and English ending together (the `EXP-0031` method).
  - **Labels:** every label index the English scripts use, and its name.
    Names whose two conventions differ are flagged (`docs/names.md`).
  - **Output:** `data/text/ending_script_census.json` (indices, counts,
    offsets, sizes and flags; no text).
- **Notes:** no emulator run is needed. Anything that cannot be settled
  statically becomes an `END-013` route check.

### END-011 - Choose the M8 ending roster and its exceptions

- **Status:** `DONE`
- **Milestone:** M8
- **Dependencies:** END-010.
- **Blockers:** None; the census is `EXP-0043` (`data/text/ending_script_census.json`).
- **Objective:** The user chooses which endings M8 covers, with the census
  in front of them. This is the `RE-008` method.
- **Acceptance criteria:**
  - **Options:** each is shown with its evidence and costs:
    - all ordinary characters;
    - Gouki (secret);
    - Apocalypse (the boss, with a shared script and aliases);
    - Ryu (his script and English pointer are shared with Apocalypse);
    - Cammy (13 English records, Japanese block unbounded);
    - second-pick endings.
  - **Recorded:** the user's choice, in their words, in
    `data/text/m8_ending_roster.json` and `docs/coverage_exceptions.md`.
- **Decision (2026-10-30, `SESSION-0066`):** "All 17 playable
  (Recommended)", "Switch shared layout (Rec.)" for Ryu and Apocalypse's
  shared script, and "Yes, include (Recommended)" for second-pick endings.
  Recorded in `data/text/m8_ending_roster.json` and
  `docs/coverage_exceptions.md`.


### END-012 - Arcade pairing for every roster ending

- **Status:** `DONE` (`EXP-0044`, D-039)
- **Milestone:** M8
- **Dependencies:** END-011.
- **Blockers:** None; the roster is `data/text/m8_ending_roster.json`.
- **Objective:** Confirm in MAME, for every roster character, which English
  record each Saturn page shows. This is the `EXP-0037` method.
- **Acceptance criteria:**
  - **Route:** `EXP-0037`'s no-play MAME route, generalized to pick any
    roster character first (cursor moves found by snapshot, then checked),
    in English and Japanese. Gouki's pick and any unreachable character are
    recorded as such.
  - **Prediction first:** before the logged runs, a committed prediction
    for every slot: page k reads ending record k of the point character, in
    either language. Then the reads are compared, and every exception is
    recorded.
  - **Partners:** at least two characters are run with two partners each.
  - **Pairing files:** `data/translations/<name>_ending_pairing.json`
    (addresses and hashes), each pair CONFIRMED by reads. Saturn records
    must equal the arcade Japanese ones byte for byte.
  - **Names:** every English record that names a character whose two
    conventions differ, for the gate (the `PAIR-003` method).

### END-013 - Saturn route to any roster ending, first or second pick

- **Status:** `DONE` (`EXP-0045`, D-040)
- **Milestone:** M8
- **Dependencies:** END-011.
- **Blockers:** None; the roster is `data/text/m8_ending_roster.json`.
- **Objective:** Make the `EXP-0041` Saturn route a tool that reaches any
  roster character's ending with no play. Use it to settle what the census
  could not, and whose ending plays.
- **Acceptance criteria:**
  - **Tool:** `saturn_route.py` promoted under `tools/mednafen/`, with unit
    tests for anything testable without the game. It takes the character,
    the partner, which of them is picked first, and the image. It writes the
    build's code into RAM when it starts from a post-Start state (the
    `EXP-0041` lesson), or boots cold.
  - **Team rule:** on the untouched image, for at least two teams, run with
    the character picked first and then second, with the partner fight won
    by each side in turn (vitality forcing on the chosen side). Record whose
    ending plays in each case.
  - **Second pick:** for the second member's ending, show which buffer its
    records are read from (WRAM-H `0x060B0000` + table + `0x4C0` is the
    HYPOTHESIS). Show that version 4's pointer rule points at that copy's
    English records.
  - **Open census items:** each `END-010` item that needs a run is settled
    or recorded.
- **Outcome:**
  - The tool is `tools.mednafen.route`.
  - Whose ending: the first pick's, when the player wins the partner fight.
    When the partner wins it, there is no ending.
  - A second pick's ending was not reached: knocking out the first pick at
    the boss loses the match, and a sent tag did not take effect. The
    second-pick criterion is therefore not shown and passes to
    `END-015`'s user play check (tag by hand before Apocalypse falls).
    If it cannot be done, it is recorded in `END-016`.


### GATE-TRANSLATION extension for the M8 roster endings

Before `END-014`, the user extends `GATE-TRANSLATION` to the `END-011`
roster's endings: GO or NO-GO in their own words, recorded under
`GATE-TRANSLATION` and in `docs/localization_policy.md`. The question
covers:

- the ending records and scripts in scope;
- the pairing (`END-012`);
- the official English, with no rewording;
- every flagged name (`END-010` labels, `END-012` records).

Dependencies: `END-010`, `END-012`.

**Passed 2026-10-30 (`SESSION-0069`):** GO, with the arcade names kept;
recorded under `GATE-TRANSLATION`.

### END-014 - Build every roster ending

- **Status:** `DONE` (`EXP-0046`, D-041)
- **Milestone:** M8
- **Dependencies:** GATE-TRANSLATION extension for the M8 roster endings,
  END-010, END-012 (all done).
- **Blockers:** None.
- **Objective:** One image, built from the untouched source, with all
  roster win quotes and all roster endings in English.
- **Acceptance criteria:**
  - **Specs:** an ending spec per roster slot, generated from its pairing
    file (`EXP-0041` `make_spec.py`, generalized).
  - **Build:** `tools.disc.build_english` (version 4). Every changed file's
    stream ends in its last sector, and the margins are recorded. Every
    `MCED` change is listed (rule 12). All sectors pass EDC/ECC.
  - **Load check:** for every roster character picked first and second,
    the buffer equals the built file plus fix-ups.
- **Outcome:**
  - **Image:** `build/m8_roster_endings` (Track 01 `7bb8ab82…`). It is
    reproducible, and all its sectors pass EDC/ECC.
  - **Specs:** 17 ending specs, from `make_specs.py`. Nash's records are
    unchanged from M7.
  - **Shared scripts:** Ryu's and Chun-Li's are switched with slots 8 and
    18 by `mced_shared_with`.
  - **Margins:** the smallest is 494 bytes. The 17 `MCED` header words
    are listed in `EXP-0046`.
  - **Load:** every roster character loads into both buffers. Rogue
    differs only in four longs the game writes, as on the untouched image.
    Gouki is picked from his cell above Juggernaut's.
  - **Route fix:** the second cursor skips the first pick's cell, so
    second-pick moves are now planned with that rule.

### END-015 - Verify every roster ending

- **Status:** `DONE` (`EXP-0047`, D-042)
- **Milestone:** M8
- **Dependencies:** END-013, END-014 (both done).
- **Blockers:** None. Gouki's cell (`EXP-0046`) can replace `GOUKI_STATE`
  in the route, so his ending runs from a disc load.
- **Objective:** Show every roster ending in English on the build, against
  the arcade.
- **Acceptance criteria:**
  - **Route checks:** for every roster character, first pick, the route
    reaches the ending on the build. Every page is compared with
    `END-012`'s arcade English snapshots (picture, label, text, line count,
    scene breaks) and checked by the agent. A second-pick run is made for
    every character whose second-pick ending `END-013` showed. Reads after
    each character's win quotes happen only during its ending (the
    `EXP-0041` read log).
  - **Win quotes:** unchanged against the M5 checks (the `EXP-0032`
    forced draws).
  - **Play check:** the user plays from a cold boot to at least two
    endings chosen by the agent, neither Nash, and their pages match the
    route's screens. The second one is an attempt at a second-pick ending:
    the user tags to the partner before Apocalypse falls (`EXP-0045` could
    not do it with no play). If the partner fight still puts the first pick
    on the player's side, that is recorded as the answer, and the second
    play-through is a first-pick ending instead.
- **Outcome:**
  - **Route:** all 17 roster endings on the build, Gouki picked from his
    cell. Every page (112) matches the arcade's.
  - **Reads:** the ending bytes are read only during the ending, plus one
    renderer read past win-quote record 7. Ryu's and Ken's forced draws
    are byte-identical to M5's.
  - **Play check:** the user played Cammy's ending, then Ryu's as the
    second pick after tagging. Both match the route's screens.
  - **Second pick:** Ryu's ending was read from the second buffer +
    table + 800 + 100k, version 4's rule.
  - **Who gets the partner fight** is a HYPOTHESIS: the character active
    at the start of the boss fight.

### END-016 - Coverage register and regression references for M8

- **Status:** `DONE` (D-043)
- **Milestone:** M8
- **Dependencies:** END-015 (done).
- **Blockers:** None.
- **Objective:** Record what M8 covers and leaves, and lock the build.
- **Acceptance criteria:**
  - **Coverage:** `docs/coverage_exceptions.md` lists every ending surface
    and record left Japanese, and why. That includes each roster exclusion,
    unused Japanese records, and anything `END-010` to `END-015` could not
    show.
  - **Regression:** the M8 build is added to
    `data/regression/references.json`, and all references match.
  - **README:** the status and build command are updated.
- **Outcome:**
  - **Coverage:** "M8 coverage register" in `docs/coverage_exceptions.md`
    covers six ending items and three surrounding ones.
  - **Regression:** reference `roster_endings_v4`; all five references
    rebuild and match (69 hashes, run at `acad50a`).
  - **README:** it now describes M8 and builds `build/m8_roster_endings`.

## Phase N: Name Variants (after M8)

The policy is decided (2026-10-27, changed 2026-10-28;
`docs/localization_policy.md`): two English variants, built from the same
pipeline.

- **American names** (the default) and **Saturn names** (the alternative).
- Each variant switches every surface together: text, labels, art and
  voice. In the user's words, carried from MSHvSF: "It should be
  consistent. We shouldn't display one name and speak another."
- Releases list the American variant first.

The M8 build is not consistent yet. Its text and ending labels are the
arcade's American English ("Charlie", "Bison", `Akuma`), while its art
still shows the Saturn's names (GOUKI, NASH).

Known before Phase N (`EXP-0011`, `EXP-0038`, `EXP-0044`, `docs/names.md`):

- **Names that differ:** Gouki / Akuma (select label art), Nash /
  Charlie (select label art against English text), and Vega / Bison
  (Shadaloo's leader; the Saturn side not yet observed).
- **Names in the English text:**
  - "Charlie" in Nash's ending records 1 and 4;
  - "Bison" in Cammy's win quotes 0 and 4;
  - "Bison" in Vega's ending records 1 and 4.
- **Ending labels:** `MCED.SHP`'s 40-entry label list holds both
  conventions: `Vega`, `Gouki`, `Nash`, then `Bison`, `Akuma`, `Charlie`,
  `Nash's friend` and `Charlie's friend`.
  - The Japanese scripts use the Saturn names (Rogue's page 1: `Vega`).
  - The English scripts use the American ones (`Bison`, `Akuma`,
    `Charlie`, `Charlie's friend`).
- **Open label question:** Magneto's English page 3 uses entry `0x0F`
  (`Vega`), the entry the Japanese scripts use for Shadaloo's leader. The
  US arcade shows `Vega` there too, which in American naming is the claw
  fighter (Saturn naming: Balrog). There is no `Balrog` entry.
- **Not examined:** where the name art is stored, whether US-name art is
  on the disc, and voice.

Nothing from MSHvSF is assumed (rule 13). In MSHvSF every US-name asset was
already on the disc (art records, speaker fields, voice clips and a
name-call table in sound RAM). For XvSF that is a HYPOTHESIS until
`LOC-002` and `LOC-003`.

The order:

1. `LOC-001` (census);
2. `LOC-002` (art and storage) and `LOC-003` (voice), which are
   independent;
3. `LOC-004` (the user's per-surface plan, and the name edits' gate);
4. `LOC-005` (American variant);
5. `LOC-006` (Saturn-names variant);
6. `LOC-007` (verify and register both).

An in-game toggle between the variants is not planned. MSHvSF deferred
its own; it becomes a task only if the user asks (`LOC-008`, outline).

### LOC-001 - Census of every name surface

- **Status:** `DONE` (`EXP-0048`, D-044)
- **Milestone:** Name variants (after M8)
- **Dependencies:** END-016 (M8 complete).
- **Blockers:** None.
- **Objective:** For every name that differs between the Saturn and
  American conventions, list every surface where the game shows it or
  speaks it. Record what the Saturn shows there and what the US arcade
  shows on the same surface.
- **Acceptance criteria:**
  - **Surfaces:** at least these, each with screen evidence (screenshot
    SHA-256 and frame):
    - character select labels;
    - the VS screen;
    - life-bar names;
    - win banners ("X WIN");
    - win-quote text;
    - ending text and ending labels;
    - the boss-stage and story lines, if they name anyone;
    - initials entry and ranking;
    - any menu that lists characters.

    A surface is recorded as not naming anyone only after it has been
    seen.
  - **Characters:** Gouki, Nash and Vega (Shadaloo's leader) on each
    surface where they appear. That includes Vega's own select label,
    which has not been observed yet. Gouki is reached by his cell
    (`EXP-0046`).
  - **Both arcade conventions:** the same surfaces in `xmvsfu` (US) and
    `xmvsfjr2` (Japan) in MAME 0.289, so that the US arcade's changes are
    known per surface.
  - **Magneto's page-3 speaker:** identified from the arcade and the
    picture. Is it Shadaloo's leader or the claw fighter? The answer
    decides that label's Saturn-names form.
  - **Voice:** every moment a character or the announcer may say a name
    (select, VS, round start, win). The user listens and identifies
    spoken names (the user is the sound oracle). Clips are given one at a
    time, never several at once.
  - **Output:** `docs/names.md` gains a table of surface × name with the
    Saturn and US arcade evidence. Unobserved cells are marked UNKNOWN.
- **Notes:** this task only observes and records. It changes nothing on
  the disc. Where the art lives is `LOC-002`.
- **Outcome:**
  - **Saturn art:** select, VS, life bar and win banner show VEGA, GOUKI
    and NASH, like the Japanese arcade; the US arcade shows BISON, AKUMA
    and CHARLIE.
  - **Boss stage:** the Japanese pre-Apocalypse boxes name the player's
    character in katakana.
  - **Voice:** the user heard "Vega", "Gouki" and "Nash"; when is
    `LOC-003`'s.
  - **Magneto's page 3:** the speaker is SUPPORTED as the claw fighter
    (Balrog in Saturn naming, with no such label).
  - **No names:** rankings, initials, menus, attract mode and credits.

### LOC-002 - Where each name surface is stored, and whether its US version exists

- **Status:** `DONE` (`EXP-0049`, D-045)
- **Milestone:** Name variants (after M8)
- **Dependencies:** LOC-001 (done).
- **Blockers:** None. The surfaces are select label, VS screen, life bar
  and win banner (`EXP-0048`).
- **Objective:** For each art or text surface in `LOC-001` that shows a
  differing name, find where the Saturn stores it and whether the other
  convention's version is also on the disc.
- **Acceptance criteria:**
  - **Location:** per surface, the drawing path, from the VDP1/VDP2
    command or tile to its VRAM data, then to the file and offset it was
    loaded from (the loader `0x0600D124`, as for the MC files). It must
    be CONFIRMED by a controlled change: altering those bytes in RAM
    alters only that name on screen.
  - **The other convention:** present or absent, per surface. "Present"
    needs the asset found and shown on screen by a controlled RAM change.
    "Absent" needs the reader traced to its table, showing that no entry
    holds the other name; a data search alone is not enough (the policy's
    rule for absence).
  - **Speaker labels:** confirm that the switch for each label is the
    script's label byte (`MCED`, `EXP-0038`). Confirm whether a `Balrog`
    label exists anywhere if `LOC-001` needs one.
- **Outcome:** every surface's storage is confirmed by a RAM change.
  - **Life bar:** `FIX.PRS` cells.
  - **Select label:** `VS00.PRS` frames `0x96`-`0xAA`.
  - **VS name and win banner:** `VS00.PRS` letter fonts.
  - **Ending labels:** `MCED.SHP`.
  - **American art:** BISON, AKUMA and CHARLIE are present and shown for
    the life bar and the select label; the VS and banner screens can
    spell them with existing letters.
  - **Absent:** a `Balrog` label.
  - **Open, for `LOC-005`:** where the VS and banner screens get each
    character's letter list.
- **Notes:** the names are not plain text on the disc in any tested
  encoding (`EXP-0011`), so expect art. MSHvSF found its name records by
  searching reversed sprite-pattern sequences; for XvSF that method is a
  HYPOTHESIS.

### LOC-003 - Name calls in voice

- **Status:** `DONE` (`EXP-0050`, D-046)
- **Milestone:** Name variants (after M8)
- **Dependencies:** LOC-001 (done).
- **Blockers:** None. "Vega", "Gouki" and "Nash" are spoken (`EXP-0048`);
  the moments are this task's first step.
- **Objective:** For each spoken differing name, find which clip plays,
  where it is stored, how it is chosen, and whether the other
  convention's clip is on the disc.
- **Acceptance criteria:**
  - **Sound path:** how the Saturn plays voice, observed on XvSF (sound
    CPU, sound RAM, the format of the clips) before any decoder is
    trusted. A decoder is validated against live output before its WAVs
    are evidence.
  - **Clips:** each candidate clip is exported as a WAV and identified by
    the user by ear, one clip at a time. The clip's file and offset are
    recorded.
  - **Choice:** the table or code that picks a name clip, CONFIRMED by a
    controlled change that plays the other clip in its place.
  - **Absent clips:** if no clip exists for the other convention, that is
    shown as in `LOC-002` (reader traced), and recorded for `LOC-004`.
- **Notes:** if `LOC-001` finds that no differing name is spoken, this
  task is closed with that evidence.
- **Outcome:**
  - **When:** the name is called at the pick and on the win screen.
  - **Clips:** they are in the sound-RAM bank from `INITDATA.PCA`, and
    MSHvSF's decoder reproduces 102 of 102 channel states.
  - **The choice:** table A in `MMPACK.PCA` (decoded `0x79EE`), indexed
    by slot, picks the call. A RAM patch changed the call at both
    moments.
  - **American calls:** "Bison" `0x147`, "Akuma" `0x021` and "Charlie"
    `0x01B` are on the disc (identified by the user).

### LOC-004 - The user's plan for each variant

- **Status:** `READY`
- **Milestone:** Name variants (after M8)
- **Dependencies:** LOC-001, LOC-002, LOC-003 (all done).
- **Blockers:** None.
- **Objective:** The user decides, surface by surface, what each variant
  shows, given what is on the disc and what each choice costs.
- **Acceptance criteria:**
  - **Options and costs:** for every surface × name, the options and
    their costs are put to the user:
    - point the game at an existing asset;
    - draw new art, recorded as new work like a new translation;
    - leave the surface unchanged and record an exception.
  - **Saturn-names text:** the Saturn-names variant changes the official
    English's names. That is a `GATE-TRANSLATION` extension for name
    edits only, and the user records it in their own words, covering:
    - "Charlie" → "Nash" in Nash's ending records 1 and 4;
    - "Bison" → "Vega" in Cammy's win quotes 0 and 4 and Vega's ending
      records 1 and 4;
    - the labels: `Charlie` → `Nash`, `Charlie's friend` → `Nash's
      friend`, `Akuma` → `Gouki`, `Bison` → `Vega`, and Magneto's page 3
      as `LOC-001` finds.

    Each edited line must fit the 25-code line, and the user sees every
    edited line before it is built.
  - **Build switch:** the variant switch is named (for example
    `build_english --names us|saturn`), with American as the default.
  - **Recording:** the decisions go into `docs/localization_policy.md`,
    under `GATE-TRANSLATION` here, and in `docs/names.md`.

### LOC-005 - Build the American-names variant

- **Status:** `BLOCKED`
- **Milestone:** Name variants (after M8)
- **Dependencies:** LOC-004.
- **Blockers:** The user's plan.
- **Objective:** One image, built from the untouched source, with every
  M8 change plus every name surface in the American convention, as
  `LOC-004` decided.
- **Acceptance criteria:**
  - **Build:** `tools.disc.build_english` with the variant switch. Every
    changed range is listed with its original and new bytes (rule 12).
    Every changed file fits its sectors, and all sectors pass EDC/ECC.
  - **Surfaces:** each changed surface is shown in the emulator, compared
    with the US arcade's, and checked by the agent. Each spoken name is
    confirmed by the user by ear.
  - **No other change:** the M8 checks still hold. Every ending page and
    the forced win-quote draws are unchanged, apart from the names
    themselves.

### LOC-006 - Build the Saturn-names variant

- **Status:** `BLOCKED`
- **Milestone:** Name variants (after M8)
- **Dependencies:** LOC-004, LOC-005 (the variant switch and its tooling).
- **Blockers:** The user's plan and the American build.
- **Objective:** One image, built from the untouched source, with the
  English text and labels in the Saturn convention, as `LOC-004` decided.
  The art and voice keep the Saturn's own names.
- **Acceptance criteria:**
  - **Build:** as `LOC-005`, with the gated name edits compiled from the
    official records. Each edited record is listed with its source hash
    and the edit.
  - **Screens:** every edited win quote is forced and shown, and every
    edited ending page is shown by the route. Each is checked by the
    agent against the approved lines.
  - **No other change:** everything else equals the American variant.

### LOC-007 - Verify and register both variants

- **Status:** `BLOCKED`
- **Milestone:** Name variants (after M8)
- **Dependencies:** LOC-005, LOC-006.
- **Blockers:** Both builds.
- **Objective:** Play-check both variants, and lock them.
- **Acceptance criteria:**
  - **Play check:** the user plays each variant from a cold boot, through
    surfaces chosen by the agent that show every differing name at least
    once. The pages and screens match the forced ones.
  - **Regression:** both variants are added to
    `data/regression/references.json`, and all references match.
  - **Coverage:** `docs/coverage_exceptions.md` lists any surface left
    unchanged in either variant, and why.
  - **README:** both build commands, American first.

## Later Milestones (outline only)

These are placeholders so the order is visible. Each becomes a full task, with
its own acceptance criteria, only when its prerequisites are done. The method
for each is in `docs/playbook_from_mshvsf.md`.

| ID | Milestone | Outline |
| --- | --- | --- |
| REL-001 | after M5 | Release patches (xdelta3 and SSP of the changed files) with a rebuild README; may be GitHub Release assets, never committed. Splice rather than re-compress changed streams to keep patches small. |
| SPECIAL-001 | M9, user approval | Secret characters and bosses: which slots have their own official English and which reuse another's (slot 18); boss pre-fight text (Apocalypse's pre-fight line is captured, `docs/text_surfaces.md`); save- or progress-gated unlocks. Gouki's and Apocalypse's ordinary win quotes are in M5 (`RE-008`). |
| UI-001 | after M8, user request | UI art: inventory English art already in every font before drawing anything; caption colour and style. Includes the `⚠乱入禁止` ("no challengers") sprite shown before and during the partner fight (spotted by the user, `EXP-0034`). |
| UI-002 | after M8, user request | Attract-mode captions: which layer draws them, which container and codecs hold them, arcade and PS1 oracles. |
| UI-003 | after M8, user request | Other UI text (continue screen, hints): find the arcade English by tracing the arcade code, not only by data search. |
| UI-004 | user requests (2026-10-29); order not yet set | Every error or warning message the game can show when it first loads, not only the 4 MB RAM cart warning (seen in `EXP-0002`, Japanese). First list them: boot with no cart, with the wrong cart, and with other startup faults the game checks for (for example save-memory messages, if any), and record each screen. Count only the game's own messages; the Saturn BIOS's are not the game's. Then, per message, find where its text and art live (disc, BIOS or code) and how it is drawn, look for an official English source, and translate it. With no official English, the policy's recorded new translation applies, approved by the user. User request (verbatim, 2026-10-29): "make sure you add to the backlog to translate any error messages that come up when you first load the game (like ones that are related to not having a 4M RAM cart, etc.)" |
| TXT-001 | after M8, user request | Rare, random, or region-gated text: trace every reader of every text table. |
| LOC-008 | after Phase N, user request | An in-game toggle between the two name variants. MSHvSF deferred its own (`LOC-006` there, `EXP-0095`: the second variant's font did not fit the free cart RAM). If wanted, census the difference between the two variants' images early. |

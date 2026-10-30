# Localization Policy

The user's policy decisions for XvSF. Each was put to the user as a
carried-over MSHvSF decision under `DOC-002` and answered on 2026-10-27; the
"Answer" column is the option the user chose, quoted. These are policy, not
facts: whether each one is achievable on XvSF is found by experiment.

## Decisions (2026-10-27)

| Topic | Answer | Meaning for XvSF | MSHvSF precedent |
| --- | --- | --- | --- |
| English source | "Official; fixes opt-in (Recommended)" | The release uses Capcom's official arcade English, paired to Saturn records by the game's own selection logic, with no rewording even where a line repeats. Grammar fixes may exist only behind an opt-in build flag. | `TR-001`, `EXP-0031`; `TXT-004` (`--fix-grammar`) |
| Text with no official English | "Recorded new translation (Recommended)" | A new translation, with the translator named and source hashes kept, approved by the user surface by surface. Absence of official English must first be shown by tracing the arcade code, not only by a data search. | `EXP-0078`, `EXP-0087`; `EXP-0080` → `EXP-0085` |
| Character names | "Both variants, Saturn default"; changed 2026-10-28 to American default (below) | Two English variants: American (US arcade) names, voices and art by default, Saturn names as the alternative, switching every surface together. Which names differ, and what each convention costs on this disc, is found by `REF-007`. | `LOC-001` to `LOC-005` |
| Eventual scope beyond ordinary win quotes and endings | "Secret characters & bosses", "UI art & attract captions", "Hints, story & rare text", "Optional unlocks" | All four are in eventual scope. Each stays gated behind the ordinary-character pipeline (`AGENTS.md` rule 24, M9) and gets its own task when its turn comes. | `SPECIAL-002` to `-004`, `UI-001` to `-006`, `TXT-001` to `-003`, `OPT-001` |
| Release formats | "xdelta + SSP (Recommended)" | An xdelta3 patch and a Sega Saturn Patcher `.ssp` patch, published as GitHub Release assets, never committed. | `REL-001` to `REL-003` |
| Release timing | "After open tasks (Recommended)" | Nothing is published until every `IN_PROGRESS` and `BACKLOG` task is done, or deferred by the user by name. | MSHvSF decision 2026-10-27; MSHvSF 0.1.0 shipped after the user deferred four tasks (2026-10-28) |
| Patched Mednafen | "Yes, reuse it (Recommended)" | After a stock boot, a short `EMU-020` record citing the MSHvSF evidence suffices; validations V1-V4 are re-run on XvSF states. | MSHvSF `EMU-012`, `EMU-020`, `EMU-021` |
| Workflow | "Cold-boot play check closes tasks", "Silent unattended runs", "Ask before downloads/installs", "Prune uncited states" | A task is `DONE` only after a cold-boot play check by the user, after a forced trial. Scripted Mednafen runs are silent (volume 0, no vsync, separate home). Every download, install, gate change or scope change waits for approval. Save states and builds that no experiment cites may be pruned when the user asks. | `docs/agent_briefing.md`, `docs/mednafen.md` (MSHvSF) |

**Names, changed (2026-10-28).** After the `DOC-002` answer, the MSHvSF
project changed its own default to American names, voices and art (MSHvSF
`LOC-001`): "It should be consistent. We shouldn't display one name and speak
another." Asked whether XvSF should follow, the user answered: "Make American
names the XvSF default, like MSHvSF. Record it in the policy." So American
names are the XvSF default, both variants are still built, and a release lists
the American variant first, as MSHvSF 0.1.0 did. Whether XvSF's disc holds the
American convention's art and voice is not yet known (`REF-007`, `LOC-001`).

**Translation gate, Ryu (2026-10-28).** After `PAIR-001` (`EXP-0022`), the
user passed `GATE-TRANSLATION`: "GATE-TRANSLATION: go for Ryu's win quotes. Use the k mod 8 pairing (Saturn records k and k+8 both show English record k), official arcade English, no rewording. Record it."

| Topic | Decision | Evidence |
| --- | --- | --- |
| Scope | Ryu's ordinary win quotes (Saturn records 0-15) only; endings, other characters and specials stay gated | `TASKS.md` `GATE-TRANSLATION` |
| Pairing | Saturn record `k` shows official arcade English record `k mod 8`; records `k` and `k + 8` repeat one English quote; English record 8 is unused | arcade selector `0x04F396` (`EXP-0022`, D-017); `data/translations/ryu_pairing.json` |
| Wording | Official arcade English, no rewording; grammar fixes opt-in only | the 2026-10-27 policy above |

**Translation gate, Ken (2026-10-29).** After `PAIR-002` (`EXP-0026`), the
user extended `GATE-TRANSLATION` to Ken: "GATE-TRANSLATION: go for Ken's win quotes. Use the k mod 8 pairing (Saturn records k and k+8 both show English record k), official arcade English, no rewording. Record it."

| Topic | Decision | Evidence |
| --- | --- | --- |
| Scope | Ken's ordinary win quotes (Saturn records 0-15 of `MC0A.SHP`'s table) added to Ryu's; his ending records 16-20, endings, other characters and specials stay gated | `TASKS.md` `GATE-TRANSLATION` |
| Pairing | Saturn record `k` shows Ken's official arcade English record `k mod 8` (slot 10); records `k` and `k + 8` repeat one English quote; English record 8 is unused | `EXP-0026`, D-021; `data/translations/ken_pairing.json` |
| Wording | Official arcade English, no rewording; grammar fixes opt-in only | the 2026-10-27 policy above |

**Translation gate, M5 roster (2026-10-29).** After `PAIR-003` (`EXP-0030`)
and `RE-009` (`EXP-0031`), the user extended `GATE-TRANSLATION` to the
roster. Asked to extend it to all 18 characters with the `k mod 8` pairing
and the official arcade English with no rewording, they answered "Go
(Recommended)". Asked about "Bison" in two of Cammy's quotes, they answered
`Keep "Bison" (Recommended)`.

| Topic | Decision | Evidence |
| --- | --- | --- |
| Scope | Ordinary win quotes (Saturn records 0-15 of each table) of all 18 roster characters, slots 0-17, Gouki and Apocalypse included; ending records, endings, slot 18, `MCED` and other surfaces stay gated | `data/text/m5_roster.json`, `docs/coverage_exceptions.md`, `TASKS.md` `GATE-TRANSLATION` |
| Pairing | Saturn record `k` of slot `s` shows slot `s`'s official English record `k mod 8`; English record 8 is unused | `EXP-0030`, D-025; `data/translations/<name>_pairing.json` |
| Wording | Official arcade English, no rewording; grammar fixes opt-in only | the 2026-10-27 policy above |
| Names | "Bison" in Cammy's English records 0 and 4 is kept as written (American default); a Saturn-names variant decides under `LOC-001` | `data/translations/m5_english_fit.json`, `docs/names.md` |

**Capacity route (2026-10-28).** After `LAYOUT-001` (`EXP-0023`) measured
pair glyphs and found the game's own English mode, the user chose: "Use route
(d), the game's native English mode. Build and test it from disc." So English
win quotes use the arcade's own 2 × 25 layout, through a per-character code
patch, with no font changes.

**Nash's ending layout (2026-10-29, `LAYOUT-002`, `EXP-0039`).** The user
was shown all six pages of two RAM trials side by side:

- (a) the Saturn's own English scene script (`EXP-0038`);
- (b) English text in the Japanese script.

Asked "Which layout should Nash's English ending use?", they answered "(a)
English layout (Recommended)". Asked "Which speaker names should the English
ending show?", they answered "Arcade names (Recommended)".

| Topic | Decision | Evidence |
| --- | --- | --- |
| Layout | The Saturn's English scene script for the ending: the arcade's scene breaks, pictures, page lengths and labels, with the arcade English records in the 2 × 25 grid | `EXP-0038`, `EXP-0039`, D-033 |
| Labels | `Charlie` and `Charlie's friend`, as in the arcade (already in `MCED`'s label list); the American-names default | `EXP-0039`, `docs/names.md` |

**Gate extension, Nash's ending (2026-10-29).** The user said GO, in their
words: "GATE-TRANSLATION: go for Nash's ending. MC10 ending records 16-21 plus whatever the English script needs; page k shows English record k; official arcade English with no rewording; keep "Charlie" in the text and the labels Charlie and Charlie's friend. Record it."

| Topic | Decision | Evidence |
| --- | --- | --- |
| Scope | `MC10.SHP` ending records 16-21, plus what the English script needs (the switch to it, the records' pointer, the records' placement); Nash first-pick only | `TASKS.md` `GATE-TRANSLATION`, `EXP-0038` |
| Pairing | Page k shows arcade English slot 16 record k (k = 0-5) | D-032, `data/translations/nash_ending_pairing.json` |
| Wording | Official arcade English, no rewording | the 2026-10-27 policy |
| Names | "Charlie" kept in English records 1 and 4; labels `Charlie` and `Charlie's friend` | `EXP-0037`, `EXP-0039` |

**Gate extension, M8 roster endings (2026-10-30).** The user was asked
whether to extend `GATE-TRANSLATION` to the endings of all 17 `END-011`
roster characters, with page k showing the arcade English ending record k
and no rewording. Answer: "Go (Recommended)". Asked how to handle the
flagged names, they answered "Keep arcade names (Recommended)". The full
questions are under `GATE-TRANSLATION` in `TASKS.md`.

| Topic | Decision | Evidence |
| --- | --- | --- |
| Scope | The ending records of slots 0-7 and 9-17, first or second pick; each slot's arcade English records after its win quotes (version 4); each slot's `MCED` English script (slot 8's switched with Ryu's, slot 18's with Chun-Li's, neither marked); the switch code | `data/text/m8_ending_roster.json`, `EXP-0043`, `TASKS.md` `GATE-TRANSLATION` |
| Pairing | Page k shows the slot's arcade English ending record k | D-039, `data/translations/<name>_ending_pairing.json` |
| Wording | Official arcade English, no rewording | the 2026-10-27 policy |
| Names | "Bison" kept in Vega's English records 1 and 4; labels `Akuma` (Gouki's page 5), `Bison` (Rogue's page 1) and `Vega` (Magneto's page 3), as the US arcade shows. A Saturn-names variant is `LOC-001`'s | `EXP-0044`, `docs/names.md` |

Apocalypse's lines, the pre-boss line, the post-boss quote, slot 18's
character (`SPECIAL-001`), the warning and every other surface stay gated.

**Name variants (2026-10-30, `LOC-004`).** After `LOC-001` to `LOC-003`
(`EXP-0048`-`EXP-0050`) showed that every name surface's American version is
already on the disc, the user was asked four questions. The full questions
and the gate extension are under `GATE-TRANSLATION` and `LOC-004` in
`TASKS.md`.

| Topic | Question (short) | Answer | Meaning |
| --- | --- | --- | --- |
| American variant (default) | Switch every name surface to the US version already on the disc, with no new art or audio? | "Go (Recommended)" | Life bar (`FIX.PRS` cells), select label (`VS00` frames `0xA8`-`0xAA`), voice (the "Bison", "Akuma" and "Charlie" calls, `0x147`, `0x021`, `0x01B`), VS screen and win banner spelled from the existing letters. As built (`LOC-005`, D-047), each comes from the game's own American list; the voice goes through it to the same clips rather than by editing table A. Ending text and labels stay as written (already American). |
| Saturn-names text | Allow six name-only edits to the official English, and four label switches, for the Saturn-names variant? | "Go (Recommended)" | A `GATE-TRANSLATION` extension: "Bison" → "Vega" in Cammy's win quotes 0 and 4 and Vega's ending records 1 and 4; "Charlie" → "Nash" in Nash's ending records 1 and 4; labels `Charlie` → `Nash`, `Charlie's friend` → `Nash's friend`, `Akuma` → `Gouki`, `Bison` → `Vega` (Rogue's page 1). Art and voice keep the Saturn names. |
| Magneto's page 3 (Saturn names) | `Balrog`, keep `Vega`, or no label? | "Balrog (Recommended)" | `Balrog` in 16-bit ASCII written into an `MCED` label entry no script uses. |
| VS screen and win banner | If their letter lists are not found, trace on or allow an exception? | "Keep tracing (Recommended)" | `LOC-005` is not done until both screens show BISON, AKUMA and CHARLIE. |
| Build switch | (named by the agent, not asked separately) | — | `build_english --names us` or `--names saturn`; default `us`. |

The Saturn-names variant's other words are the official arcade English, with
no rewording. The boss-stage katakana boxes are not part of either variant
(`SPECIAL-001`).

**Boot warnings (2026-10-30, `BOOT-003`, `EXP-0055`).** No official
English exists for the five boot warnings (`ERR1`-`ERR5.BIN`): XvSF had no US
Saturn release, and neither the arcade nor the US PlayStation release has
these messages. The user saw each Japanese screen beside the proposed
English, in two looks, and answered:

| Question (short) | Answer | Meaning |
| --- | --- | --- |
| Approve the proposed English as a new translation? | "Approve (Recommended)" | `data/translations/boot_warnings.json`, by Claude, with each source picture's hash; the Saturn BIOS's labels ("Memory Manager", "System Memory") and Capcom's PlayStation register; "16" kept |
| Which look? | "Match Japanese (Recommended)" | The `FIX.PRS` quote font, white with cyan and red highlights and a yellow "WARNING", in the original palette, so the screens look as dim as the Japanese ones |
| The "multiplayer screen" | "control panel (Recommended)" | "…go to the Saturn's control panel." |
| `ERR5`'s verb | `"insert" (Recommended)` | "Turn off the power and insert the 4MB Extended RAM Cartridge." |

## Deferred Until Evidence Exists

These MSHvSF decisions depend on facts not yet known for XvSF. Each is put to
the user when its task produces the evidence, with options and costs.

| Topic | Decide when | MSHvSF choice, for reference |
| --- | --- | --- |
| Roster and exclusions | The file census is done (`RE-005`) | 17 characters first; specials later |
| Ending layout for other characters | Each ending's English script is checked (M8); Nash's is decided above (`LAYOUT-002`) | Each English line whole, one block per speaker (`EXP-0045`) |
| Caption font, style and colour | The caption renderer and font are known | Credits-font pairs, gold (`FONT-010`, `FONT-011`) |
| Attract-caption style | Attract captions are found (`UI-002`) | Saturn win-banner letters, arcade wording and layout (`UI-003`) |
| Per-option defaults (unlocks and similar) | Each option exists | Boss unlock on by default (`OPT-001`) |
| Name-variant presentation and an in-game toggle (the default and each variant's contents are decided: American default, `LOC-004` above) | Both variants build (`LOC-008`) | American names default from 2026-10-28, both variants released, American first; the toggle deferred past 0.1.0 (`LOC-001`, `LOC-006`, `EXP-0095`) |

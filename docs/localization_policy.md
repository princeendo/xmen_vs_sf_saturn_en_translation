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

**Capacity route (2026-10-28).** After `LAYOUT-001` (`EXP-0023`) measured
pair glyphs and found the game's own English mode, the user chose: "Use route
(d), the game's native English mode. Build and test it from disc." So English
win quotes use the arcade's own 2 × 25 layout, through a per-character code
patch, with no font changes.

## Deferred Until Evidence Exists

These MSHvSF decisions depend on facts not yet known for XvSF. Each is put to
the user when its task produces the evidence, with options and costs.

| Topic | Decide when | MSHvSF choice, for reference |
| --- | --- | --- |
| Roster and exclusions | The file census is done (`RE-005`) | 17 characters first; specials later |
| Ending dialogue layout | An ending is reached and its records are known (`END-001`) | Each English line whole, one block per speaker (`EXP-0045`) |
| Caption font, style and colour | The caption renderer and font are known | Credits-font pairs, gold (`FONT-010`, `FONT-011`) |
| Attract-caption style | Attract captions are found (`UI-002`) | Saturn win-banner letters, arcade wording and layout (`UI-003`) |
| Per-option defaults (unlocks and similar) | Each option exists | Boss unlock on by default (`OPT-001`) |
| Name-variant presentation and an in-game toggle (the default itself is decided: American) | Both variants build | American names default from 2026-10-28, both variants released, American first; the toggle deferred past 0.1.0 (`LOC-001`, `LOC-006`, `EXP-0095`) |

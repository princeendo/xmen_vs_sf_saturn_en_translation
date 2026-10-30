# Character Names Across Releases (`REF-007`)

Which names the Saturn shows, which the arcade English uses, and where they
differ. Evidence: `EXP-0011`. Policy (`docs/localization_policy.md`): American
names by default, both variants built.

## Census of Every Name Surface (`LOC-001`, `EXP-0048`)

Observed on the M8 build (`build/m8_roster_endings`) and in MAME 0.289
(`xmvsfu`, `xmvsfjr2`). Every cell was read from an image; the evidence
(file, frame, hash) is in `research/experiments/EXP-0048/`.

| Surface | Saturn (M8 build) | US arcade | Japanese arcade |
| --- | --- | --- | --- |
| Select label | VEGA / GOUKI / NASH | BISON / AKUMA / CHARLIE | VEGA / GOUKI / NASH |
| VS screen | VEGA / GOUKI / NASH | BISON / AKUMA / CHARLIE | VEGA / GOUKI / NASH |
| Life bar | VEGA / GOUKI / NASH | BISON / AKUMA / CHARLIE | VEGA / GOUKI / NASH |
| Win banner | VEGA / GOUKI / NASH | BISON / AKUMA / CHARLIE | VEGA / GOUKI / NASH |
| Win-quote screen | no label; English text says "Bison" (Cammy's quotes 0 and 4) | no label | no label; Japanese text can name ベガ, ゴウキ |
| Ending text | "Charlie" (Nash's 1, 4), "Bison" (Vega's 1, 4) | the same | Japanese |
| Ending labels | `Charlie`, `Charlie's friend`, `Akuma`, `Bison`, `Vega` (Magneto's page 3) | the same | `Nash`, `Nazo no koe`, `Nash's friend`, `Gouki`, `Vega` |
| Apocalypse's pre-fight boxes | Japanese, naming the player's character in katakana (ベガ, ゴウキ, ナッシュ) | none seen | Japanese, the same kind of naming |
| Voice | "Vega", "Gouki", "Nash" heard by the user (moments not recorded) | not checked | not checked |

No character name appears on the stage cards, the staff roll, initials
entry, the rankings, attract mode, the title menu, or Option Mode
(Saturn). The arcade rankings and initials entry name none either.

So the M8 build is mixed: Saturn-convention art and voice, with
American-convention English text and ending labels.

**Magneto's page 3 (`Vega`):** the speaker is most plausibly the masked
claw fighter, who is "Vega" in US naming and Balrog in Saturn naming
(SUPPORTED). The Saturn label list has no `Balrog`, and its `Vega` entry
means Shadaloo's leader in the Japanese scripts.

## Where Each Name Surface Is Stored (`LOC-002`, `EXP-0049`)

| Surface | Stored in | American name present |
| --- | --- | --- |
| Life bar | `FIX.PRS` cells (player's set `0x0880`-`0x08CF`, CPU's set `0x0822`-`0x087F`) | BISON, AKUMA (both sets); CHARLIE at `0x03C8`-`0x03CF`; shown by RAM swaps |
| Select label | `VS00.PRS` frames `0x96`-`0xA7` (slots 0-17) | BISON `0xA8`, AKUMA `0xA9`, CHARLIE `0xAA`; shown by RAM patches |
| VS-screen name | `VS00.PRS` one-cell letter font | spelled from letters; a per-character record from the Japanese list `0x060845D8` or the American list `0x060845FE` (`EXP-0051`) |
| Win banner | `VS00.PRS` 2 × 2 letter font | spelled from letters; the Japanese list `0x0606E348` or the American list `0x0606E36E` (`EXP-0051`) |
| Ending labels | `MCED.SHP` label list | `Bison`, `Akuma`, `Charlie`, `Charlie's friend`; no `Balrog` |
| Voice | clips in the sound-RAM bank (`INITDATA.PCA`), chosen by table A in `MMPACK.PCA` (decoded `0x79EE`), at the pick and on the win screen; the `.ADP` files are music | "Bison" `0x147`, "Akuma" `0x021`, "Charlie" `0x01B` (`EXP-0050`) |

**How the American names are chosen (`EXP-0051`, D-047).** The life bar,
select label, VS screen, win banner and voice each have a Japanese list
and an American list 38 bytes after it, chosen by the region word
`0x060F5478` (the arcade's `0xFF5478`), which the Saturn keeps at 0. The American variant changes the 10 reads of that word that
choose those lists, not the word itself (`tools/disc/names.py`).

## Names That Differ

| Character | Saturn (observed) | Arcade JP set | Arcade US set (art) | Arcade English text | Status |
| --- | --- | --- | --- | --- | --- |
| Akuma / Gouki | **GOUKI**: select label (`f00007661.png` `132c3d60…1d03`), VS screen and win banner (`f00011244.png` session) | **GOUKI** select label (`xmvsfjr2` frame 2650, `0b34de80…91d5`) | **AKUMA** select label (`xmvsfu` frame 2650, `79b2962c…d3f9`) | not named in any quote, ending or hint | **Differs, observed** |
| Charlie / Nash | **NASH**: select label (`f00018389.png` `12e4796c…5695`) | **NASH** (`EXP-0048`) | **CHARLIE** (`EXP-0048`) | **Charlie** (2 mentions) | **Differs, observed** |
| M. Bison / Vega (Shadaloo's leader) | **VEGA** (`EXP-0048`) | **VEGA** (`EXP-0048`) | **BISON** (`EXP-0048`) | **Bison** (4 mentions) | **Differs, observed** |
| Shadaloo (organization) | Japanese text only | — | — | **Shadaloo** (2) | Same romanization in the English; Saturn not checked |

The arcade's region ROMs also hold a 16-bit name list that contains both
conventions side by side (`Vega`, `Gouki`, `Nash`, `Bison`, `Akuma`, `Charlie`)
plus speaker labels. It is identical in every region, so it does not show which
name a region displays.

## Names That Match Where Observed

Saturn and US arcade art agree on CYCLOPS, WOLVERINE, STORM, SABRETOOTH,
GAMBIT, MAGNETO, RYU and KEN (select labels). The Saturn session also showed
ROGUE and CHUN-LI (VS screen, win banner) as in the arcade name lists. Not yet
observed on any screen: Juggernaut, Dhalsim's label, Zangief, Cammy and
Apocalypse. Dhalsim and Sabretooth appear in the US win banner (`EXP-0009`).

## Latin Names Found In Game Data

- **Ending speaker labels** (`EXP-0034`, `EXP-0035`): Nash's ending shows
  Latin labels above the text box: `Nash`, `Nazo no koe` (romanized
  Japanese) and `Nash's friend`. With the global language word set to 2 in
  RAM, a `Charlie` label appeared on one page. So the Saturn game holds at
  least one American-name label, chosen by language. Where those labels
  are stored, and whether `Akuma` and `Bison` labels exist too, is not yet
  traced (`END-003`, `LOC-001`).

- **Arcade English ending** (`EXP-0037`): Charlie's English ending records
  1 and 4 say "Charlie", and its labels are `Charlie` and `Charlie's
  friend`. The Japanese script's labels are `Nash`, `Nazo no koe` and
  `Nash's friend`, on the Saturn and in the arcade alike.

- **Saturn speaker-label list** (`EXP-0038`): `MCED.SHP` (decoded
  `0x3DA8`) holds 40 Latin labels in 16-bit ASCII. These are the roster
  names in the Saturn convention (`Vega`, `Gouki`, `Nash`), then `Bison`,
  `Akuma` and `Charlie`, then other speakers (`Charlie's friend`, `Nash's
  friend`, `Nazo no koe` and more). The English ending script uses
  `Charlie`. So American-name labels are on the disc as text for the
  endings. The select, versus and banner names are still art (`LOC-001`).

## Formerly Not Examined

- **Voice:** answered by `LOC-003` (`EXP-0050`). The Saturn calls the
  name at the pick and on the win screen; the American calls are on the
  disc.
- **Assets on the Saturn disc:** answered by `LOC-002` (`EXP-0049`). The
  American art is on the disc for every art surface; the VS screen and
  win banner spell names from letter fonts.

## The User's Plan (`LOC-004`, 2026-10-30)

Recorded in `docs/localization_policy.md` ("Name variants") and under
`GATE-TRANSLATION` in `TASKS.md`.

| Surface | American variant (default, `--names us`) | Saturn-names variant (`--names saturn`) |
| --- | --- | --- |
| Life bar | BISON / AKUMA / CHARLIE cells already in `FIX.PRS` | unchanged (VEGA / GOUKI / NASH) |
| Select label | `VS00` frames `0xA8` / `0xA9` / `0xAA` | unchanged |
| VS screen, win banner | spelled from the existing `VS00` letters; no exception allowed | unchanged |
| Voice | table A entries 14-16 → "Bison" `0x147`, "Akuma" `0x021`, "Charlie" `0x01B` | unchanged |
| Win-quote text | as written ("Bison" in Cammy's 0 and 4) | "Vega" in Cammy's 0 and 4 |
| Ending text | as written ("Bison", "Charlie") | "Vega" in Vega's records 1 and 4; "Nash" in Nash's records 1 and 4 |
| Ending labels | as written (`Charlie`, `Charlie's friend`, `Akuma`, `Bison`, `Vega`) | `Nash`, `Nash's friend`, `Gouki`, `Vega`, and a new `Balrog` for Magneto's page 3 |
| Boss-stage boxes | not part of either variant (`SPECIAL-001`) | the same |

All the American assets already exist, so no new art or audio is drawn.

Built: the American variant in `LOC-005` (`EXP-0051`, D-047), the
Saturn-names variant in `LOC-006` (`EXP-0052`, D-048). Magneto's `Balrog`
label is written into label entry 9 (`Apocalypse`), which no script uses.

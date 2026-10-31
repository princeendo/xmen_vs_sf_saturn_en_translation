# Coverage Exceptions

What the M5 win-quote build deliberately leaves untouched, and why. The
roster is `data/text/m5_roster.json`: all 18 characters of arcade slots 0-17
(user decision 2026-10-29, `RE-008`: "All 18, with Apocalypse"). Every build
must leave the items below byte-identical to the source image. What the M8
ending build covers and leaves is in the last section.

## Files and slots outside the roster

| Item | Reason | Evidence | Taken up by |
| --- | --- | --- | --- |
| `MCED.SHP` | Holds no arcade Japanese win-quote or ending record of any slot. It is the ending overlay: the scene scripts and speaker labels (`EXP-0038`, D-033). M7 and M8 change only its script header words (below). | `EXP-0029`, D-024, D-033 | M7, M8 |
| Arcade slot 18 | Has no file of its own: its Japanese and English pointers both equal slot 11's (Chun-Li). Which character uses it, if any, is unknown. Slot 11's table is localized in `MC0B.SHP`; if slot 18 reads that file, it shows the same English. | `EXP-0029`, D-024 | `SPECIAL-001` |

## Parts of roster files outside M5

| Item | Reason | Evidence | Taken up by |
| --- | --- | --- | --- |
| Records after the 16 quotes in every `MCxx` (4-12 per file) | Japanese ending records; endings waited until win quotes were proven and generalized (rule 23). | `EXP-0025`, `EXP-0029` | **Taken up by M8** for slots 0-7 and 9-17 (below); slot 8's stay Japanese |
| Everything else in each `MCxx` outside the first 800 bytes of its quote table | Not win-quote text. The English records (8 × 100 bytes) are written over the start of the 1,216-byte Japanese table; the rest of the table and of the file stays as decoded. | `EXP-0024`, `EXP-0028` | — |
| Arcade English record 8 of each slot (none in slot 8) | Never chosen by the win-quote selector (`r mod 8`). | `EXP-0022`, `EXP-0026` | before claiming full English coverage (`docs/known_unknowns.md`) |

## Special characters in the roster

Rule 24 keeps secret characters and bosses out until a task permits them.
`RE-008` permits two, for their ordinary win quotes only:

- **Gouki** (slot 15, `MC0F`): not one of the 16 grid portraits. His cell
  above the grid appears only in some states (`EXP-0025`, `EXP-0032`).
- **Apocalypse** (slot 8, `MC08`): the boss, not on the grid; 8 English
  records, which cover every draw under `r mod 8`. His quote shows only when
  he beats the player.

Their other text (boss pre-fight exchanges, unlock conditions, endings)
stays with `SPECIAL-001` and the ending tasks. Apocalypse's pre-fight line,
a Japanese box at the top of the screen, was seen in the `EXP-0032` play
check and is unchanged (`docs/text_surfaces.md`).

## M8 endings (`END-011`, 2026-10-30)

Roster: `data/text/m8_ending_roster.json`. The user was given the
`END-010` census (`EXP-0043`) and answered three questions:

| Question | Answer (verbatim) |
| --- | --- |
| Which characters' endings should M8 put into English? | "All 17 playable (Recommended)" |
| Ryu's ending script is shared with Apocalypse's slot. How should that be handled? | "Switch shared layout (Rec.)" |
| Should M8 also cover endings when the character is picked second? | "Yes, include (Recommended)" |

So M8 covers the endings of slots 0-7 and 9-17, Gouki and Cammy included,
with the character picked first or second.

| Item | Treatment | Evidence |
| --- | --- | --- |
| Slot 8 (Apocalypse) | **No English ending of his own.** He is the boss, not selectable. His `MCED` script is Ryu's, and his arcade English pointer equals Ryu's. Switching Ryu's shared script to English switches slot 8's too, but slot 8 is not marked in the fixed table, and `MC08` gets no English ending records. If Apocalypse's ending could ever play, it would show `MC08`'s Japanese records under Ryu's English script. That it never plays is a HYPOTHESIS, to be recorded by `END-016`. | `EXP-0043`, D-038 |
| Slot 18 (name list: Bison) | No file. It shares Chun-Li's script and pointers, and Chun-Li's switch changes it too. Which character uses it stays with `SPECIAL-001`. | `EXP-0029`, `EXP-0043` |
| `mced_english_scripts` | It refuses a slot whose script is shared with an unlisted slot. The M8 build must allow slot 9 with slot 8, and slot 11 with slot 18, explicitly (`END-014`). | `tools/disc/english_mode.py` |

## M8 coverage register (`END-016`, 2026-10-30)

The M8 build is `build/m8_roster_endings` (`EXP-0046`, D-041; reference
`roster_endings_v4`). It covers:

- the ordinary win quotes of slots 0-17 (M5);
- the endings of slots 0-7 and 9-17 in the official arcade English.

Every page of those endings was shown on screen with the character picked
first (`EXP-0047`, D-042). With the character picked second, Ryu's ending
was shown in play.

### Ending text left Japanese, or not shown

| Item | Status | Why | Evidence | Taken up by |
| --- | --- | --- | --- | --- |
| Slot 8 (Apocalypse): `MC08`'s 4 Japanese ending records (decoded `0xF60` + 76k) | Japanese, unchanged | He is the boss, not a roster pick, so slot 8 is not marked and gets no English records (`END-011`). His `MCED` script is Ryu's, so it is now the English script. That his ending never plays is a **HYPOTHESIS**: in 17 routes, 2 plays and `EXP-0045`'s routes, every ending was a team member's. If it ever played, it would show these Japanese records under Ryu's English script. | `EXP-0043`, `EXP-0045`, `EXP-0047` | `SPECIAL-001` |
| Slot 18 (name list: Bison) | No file of its own | It shares Chun-Li's script and pointers, so Chun-Li's switch covers it. Which character uses it, if any, is unknown. | `EXP-0029`, `EXP-0043` | `SPECIAL-001` |
| The tail of each roster file's old Japanese ending | Japanese bytes, not shown | The English bytes (800 + 100n from the quote table) are shorter than the Japanese records they replace. The rest stays as decoded: 348 bytes (slot 0), 48 (1), 348 (2), 424 (3), 372 (4), 120 (5), 500 (6), 20 (7), 172 (9), 396 (10), 348 (11), 120 (12), 220 (13), 220 (14), 120 (15), 272 (16), 28 (17). The English script reads only the n English records. The renderer read once past the last record in M7 (`EXP-0041`), and every page matches the arcade. | `EXP-0041`, `EXP-0046`, `EXP-0047` | — |
| The Japanese ending scripts in `MCED.SHP` | Japanese, unchanged, not run | Each roster script's language-0 header word now points to its English script (17 words), so the Japanese scripts are no longer reached for roster slots. | `EXP-0046` | — |
| Second-pick endings other than Ryu's | English on disc, not shown | Every roster file loads into the second buffer unchanged (`EXP-0046`). Ryu's second-pick ending used version 4's second-buffer rule (`EXP-0047`). The others use the same rule and are **SUPPORTED**, not shown. A route cannot reach them, because the route's tag did not take effect (`EXP-0045`). | `EXP-0045`, `EXP-0046`, `EXP-0047` | — |
| Gouki's ending in an ordinary save | English on disc; reachable only if his cell is open | His cell above Juggernaut's is open in the route's select state. Whether it is open in a fresh save (an unlock) is unknown. | `EXP-0046` | — |

### Other text around the endings, unchanged

| Item | Status | Taken up by |
| --- | --- | --- |
| Apocalypse's pre-fight exchange: two Japanese boxes at the top of the boss stage (the "target confirmed" line, then Apocalypse's) | Japanese, seen in every play check | `SPECIAL-001` |
| The `⚠乱入禁止` ("no challengers") warning in the boss and partner fights | Japanese | `UI-001` |
| The staff roll, `GAME OVER`, initials entry and score screens | Already English on the Japanese disc (`EXP-0034`) | — |

The win quote after Apocalypse and in the partner fight is the winner's
ordinary win quote, in English since M5. It was seen in English in every
play check.

## Name variants (`LOC-007`, 2026-10-30)

Both variants are built from the M8 build's specs with `--names us`
(`EXP-0051`) or `--names saturn` (`EXP-0052`). What either leaves unchanged:

| Item | Variant | Status | Why | Evidence | Taken up by |
| --- | --- | --- | --- | --- | --- |
| Apocalypse's pre-fight boxes on the boss stage | both | Japanese; they name the player's character in katakana (ナッシュ, ゴウキ, ベガ) | Special-case text, outside both variants (`LOC-004`) | `EXP-0048`, `EXP-0051` run B | `SPECIAL-001` |
| Quote and ending text, ending labels | American | As the arcade wrote them ("Bison", "Akuma", "Charlie"; Magneto's page 3 `Vega`) | Already American (`LOC-004`) | `EXP-0047` | — |
| Art and voice | Saturn names | The Saturn's own (VEGA, GOUKI, NASH) | That is the variant; its code equals M8's | `EXP-0048`, `EXP-0052` | — |
| Label entry 9 (`Apocalypse`) | Saturn names | Replaced by `Balrog` | No script in any language uses it; it holds Magneto's page 3 label | `EXP-0052`, D-048 | — |
| Region-dependent sound request (`0x0604FD02`: `0x9E` or `0x9F`) | both | As the Saturn has it (`0x9E`) | Not a per-character list; what it plays was not identified | `EXP-0051` | — |
| Table B (`MMPACK.PCA`, after table A) | both | Unchanged | Its role is unknown; it changed neither name call | `EXP-0050` | `docs/known_unknowns.md` |
| The VS screen's clip from the cart (`0x0240FBD7`) | both | Unchanged | Not identified; not from the name-call table | `EXP-0050` | `docs/known_unknowns.md` |
| CPU-side BISON and CHARLIE (life bar, VS screen) | American | In the build, not seen in play | No CPU team held them in the routes or plays; the CPU-side AKUMA came from the same list | `EXP-0051` | — |
| Second player's side, Versus Mode | both | Not played | The same routines draw both sides | `EXP-0051` | — |

## Boot warnings (`BOOT-005`, 2026-10-30)

`--boot-warnings` replaces all five warning pictures, `ERR1`-`ERR5.BIN`
(`EXP-0056`). No boot message is left in Japanese. What is not shown, or not
the game's:

| Item | Status | Why | Evidence |
| --- | --- | --- | --- |
| `ERR5.BIN` ("not inserted") | English on disc; shown only by forcing its branch | The cart test chooses it for an unsteady cart ID or a 1 MB cart that fails its RAM test; Mednafen's carts produce neither | `EXP-0053`, `EXP-0054`, `EXP-0056` |
| "16" in the no-free-space warning | Kept as the original says | The game warns at 18 free blocks or fewer (of Mednafen's 64-byte blocks); the text was translated as written (`BOOT-003`) | `EXP-0053`, `EXP-0055` |
| Disc-error text in file `0` ("FILE LOAD ERROR", "READ ERROR"…) and exception text in `MMPACK.PCA` ("CPU ADDRESS ERROR"…) | Already English, not triggered | Developer text; needs a disc read failure or a crash | `EXP-0053` |
| `ERRBKUPJ.FHD` and three more names in file `0` | Unused | No such files on the disc, and no code refers to them | `EXP-0053` |
| The Saturn's own screens after warnings A and B (the CD-player menu, Memory Manager) | The BIOS's, not the game's | Already labelled in English by the BIOS | `EXP-0055` |
| The 16 MiB CS1 RAM cart | No message; the game hangs on "NOW LOADING" | It passes the cart test | `EXP-0053` |

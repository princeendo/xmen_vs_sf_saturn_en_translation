# Coverage Exceptions

What the M5 win-quote build deliberately leaves untouched, and why. The
roster is `data/text/m5_roster.json`: all 18 characters of arcade slots 0-17
(user decision 2026-10-29, `RE-008`: "All 18, with Apocalypse"). Every build
must leave the items below byte-identical to the source image.

## Files and slots outside the roster

| Item | Reason | Evidence | Taken up by |
| --- | --- | --- | --- |
| `MCED.SHP` | Holds no arcade Japanese win-quote or ending record of any slot; its role and its loader are unknown. | `EXP-0029`, D-024 | a later task, if it turns out to hold text (`docs/known_unknowns.md`) |
| Arcade slot 18 | Has no file of its own: its Japanese and English pointers both equal slot 11's (Chun-Li). Which character uses it, if any, is unknown. Slot 11's table is localized in `MC0B.SHP`; if slot 18 reads that file, it shows the same English. | `EXP-0029`, D-024 | `SPECIAL-001` |

## Parts of roster files outside M5

| Item | Reason | Evidence | Taken up by |
| --- | --- | --- | --- |
| Records after the 16 quotes in every `MCxx` (4-12 per file) | Japanese ending records; endings wait until win quotes are proven and generalized (rule 23). | `EXP-0025`, `EXP-0029` | `END-001` and later |
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

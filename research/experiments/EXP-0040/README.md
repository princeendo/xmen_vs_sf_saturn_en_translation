# EXP-0040 (M7): Version 4, English Endings Per Slot

Task: END-006
Status: DONE
Confidence: CONFIRMED (RAM trials); the disc build is `END-008`

## Observation

`EXP-0038` (D-033) turned on Nash's English ending in RAM. It switched
eight code reads to English, which made the renderer English for every
caller, and it put the records in scratch RAM behind a hand-made list.
`LAYOUT-002` chose that layout (option (a)). `END-006` needs a same-size
patch that does this for chosen slots only.

## Hypothesis

A same-size rewrite of the type-4 selector in `MMPACK.PCA` can turn on the
English ending per slot, together with one bit per slot in the fixed-index
table and a 2-byte header change in `MCED.SHP`:

- **The rewrite:** the selector always uses the language-0 list. For
  marked slots it moves the pointer back `0x1A0` bytes, to quote table +
  800, and sets the task's English flag.
- **The header change:** the slot's language-0 entry selects its English
  script.

Unmarked slots, and all win quotes, are unchanged.

## Design (rule 12)

All addresses are WRAM-H, in decoded `MMPACK.PCA` loaded at `0x06014BA0`,
except `MCED`.

| Address | Original | New | Purpose |
| --- | --- | --- | --- |
| `0x060668C2`-`0x060668EF` (23 words) | `90D7 00BD C101 C501 300C C101 D10F C501 021D 70FE 011D 6029 201D 6703 C503 300C C103 C503 017D 7002 027D 6029 201D` | `D712 D112 C503 021C 300C 007E 4211 8905 911F 301C E15C 316C E202 2120` + 9 × `0009` | Type-4 selector: language-0 list always; for marked slots, pointer − `0x1A0` and task + `0x5C` = 2 (disassembly in `tools/disc/english_mode.py`) |
| `0x0606690C`-`0x06066917` | `06066912 060854F8 06085544` | `060854F8 060666E1 FE600000` | Literals: list, `FIXED_TABLE` + 1, −`0x1A0`. These held the old literal and the start of the language table, which only this selector read (a search of all PC-relative loads and absolute longs in the decoded code). |
| `0x060668C4` (version 2 and 3: `00BD` → `E000`) | — | replaced by the row above | — |
| `0x060666E0` + 2·slot + 1 (fixed-table low byte) | the fixed index (0-7; slot 16: `00`) | `| 0x80` | Marks the slot for an English ending |
| `MCED.SHP` decoded `0x2CF0` (Nash's script header, RAM `0x060D4CF0`) | `0008` | `0038` | Language 0 runs Nash's English script |

The rest of version 3 (the win selector, the renderer's task-flag reads and
the slot table's high bytes) is unchanged.

**Why the records go at quote table + 800.** For a slot with English win
quotes, the table's first 800 bytes hold its 8 English quotes. The next 416
bytes (the rest of the Japanese table) and the 456 bytes of Japanese ending
records after them are not read once both are English. That makes 872
bytes, for 600 bytes of English records. So:

- English pointer = language-0 pointer (quote table + `0x4C0`) − `0x1A0`;
- a slot gets an English ending only together with English win quotes.

`patches_v4` refuses anything else. `END-007` must confirm, with a read log,
that those bytes are unread.

**The bit** shares the low byte with the fixed index. Only the fixed-index
path reads that byte, and for English win-quote slots it uses `index & 7`
(version 3), which drops the bit.

## Prediction

- **v4_off** (version 4 code, no slot marked): Nash's ending is
  pixel-identical to the untouched game at every frame.
- **v4_on** (slot 16 marked, `MCED` header changed, records at table +
  800): every frame equals `EXP-0038`'s English trial.
- **Win quotes:** Ryu's 8 English draws are identical under version 3,
  version 4, and version 4 with his own slot marked.
- **Fit:** `MMPACK.PCA` and `MCED.SHP` still fit their sectors.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | Track 01 `c904a386…`; `MMPACK.PCA;1`; `MCED.SHP;1` `aa10db67…` |
| Checkpoints | `local/checkpoints/end001/f00220064.mcs` `7c5a7257…`; Ryu `pre_ko` `local/checkpoints/dbg003/f00009769.mcs` (`EXP-0013`) |
| Roster build files | `local/re010/b1/MC09.SHP` (Ryu's English table, `EXP-0032`) |
| Program image | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` |

## Tools

| Tool | Use |
| --- | --- |
| [`v4_trial.py`](v4_trial.py) | control, v4_off and v4_on on Nash's ending (91 screenshots each, every 30 frames from 220,500) |
| [`win_regression.py`](win_regression.py) | Ryu's draws 0-7 under v3, v4 and v4 with his own slot marked |
| [`fit_check.py`](fit_check.py) | Re-encodes `MMPACK.PCA` (version 4 plus slot 16's bit) and `MCED.SHP` (the header) to their sizes |
| `tools/disc/english_mode.py` | Now holds version 4: `patches_v4`, `ending_slot_patches`, `mced_english_scripts`, with unit tests |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0040/v4_trial.py local/end006/trial1
./invenv.sh python research/experiments/EXP-0040/win_regression.py local/end006/win1
./invenv.sh python research/experiments/EXP-0040/fit_check.py
./invenv.sh pytest tests/unit/test_english_mode.py
```

## Actual Result

- **Encoding:** the new selector, applied to the decoded code and
  disassembled, reads as designed.
- **Nash's ending** (`v4_trial.py`, 91 frames each):
  - v4_off equals control at **all 91** frames.
  - v4_on equals `EXP-0038`'s English trial at **90 of 91** frames. Frame
    222,120 differs in 14,516 pixels, all inside the picture window (x
    96-255, y 40-135), as page 5's Guile picture fades in. Its text, label
    and box are identical, and the next sample (222,150) is identical
    again. This is attributed to a one-frame shift in the fade; it was not
    examined further.
  - v4_on's pointer stepped through `0x0024FD20` + 100k (quote table +
    800).
- **Win quotes** (`win_regression.py`): for draws 0-7, v4 and v4_bit
  match v3 in pointer, 100 bytes and screenshot. v3 read record r at
  `0x0024F5D8` + 100r each time.
- **Fit** (`fit_check.py`):

  | File | Size | Rebuilt | Margin | Rebuilt SHA-256 |
  | --- | --- | --- | --- | --- |
  | `MMPACK.PCA` | 258,319 | 258,319 | (lazy, as before) | `276d534c…` |
  | `MCED.SHP` | 21,203 | 21,203 | 204 bytes (natural lazy 20,999) | `cca9332d…` |

  Both round-trip.
- **Tools:**
  - `patches_v4(range(18), [16])` equals the trial's code plus slot 16's
    bit.
  - `mced_english_scripts(MCED, [16])` gives the trial's edit (`0x2CF0`:
    `0008` → `0038`) and refuses slot 9 (its script is shared with slot 8).
  - 10 new unit tests; 177 pass.

## Conclusion

**CONFIRMED in RAM:** version 4 turns on the English ending for marked
slots only. Unmarked endings and win quotes are unchanged. For Nash it
reproduces the `LAYOUT-002` layout. The code is same-size, and both changed
files fit their sectors.

## Uncertainty and Alternatives

- **Nash as the second pick:** the language-0 list also holds the second
  member's base (Ryu `0x060B2A98`, WRAM-H), so the same rule applies to his
  copy: second-member table + 800. That copy holds the English quotes too
  (D-027). But the second member's ending was never reached; it stays
  untested (`END-013`).
- **The bytes after the English win quotes** are assumed unread. `END-007`
  must show it with a read log.
- **A task-identity assumption.** The flag is set on the selector's r6 task,
  and the renderer reads it from its r12 task. That they are the same
  object is shown only by the result.

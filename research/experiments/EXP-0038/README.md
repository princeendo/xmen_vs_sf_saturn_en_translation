# EXP-0038 (M7): The Saturn's English Ending Script

Task: END-005
Status: DONE
Confidence: CONFIRMED

## Observation

- **Arcade** (`EXP-0037`, D-032): the English ending shows the same six
  records as the Japanese, but with its own scene breaks (pages 1, 2, 4,
  5), pictures and labels (`Charlie`, `Charlie's friend`).
- **Saturn** (`EXP-0035`): with the global size and language words set to
  2, the ending showed a `Charlie` label and a picture change. But the
  type-4 selector's language-2 list holds no addresses, and the size word
  has other readers.

## Hypothesis

The Saturn holds an English scene script for Nash's ending. If only the
ending's own language reads return 2, and the selector gets a valid
pointer to the six arcade English records, the Saturn shows the arcade's
English ending: same scene breaks, pictures, labels, text and page timing.

## Controlled Change

All in RAM, from `local/checkpoints/end001/f00220064.mcs` (untouched image,
no input). The global words `0x060F5478`/`0x060F547A` stay 0.

| Address | Original | Trial | Purpose |
| --- | --- | --- | --- |
| `0x060D4738` (`MCED` scene-script reader) | `00BD` | `E002` | language read → 2 |
| `0x060668C4` (type-4 selector) | `00BD` | `E002` | language read → 2 |
| `0x0606696A`, `0x0606699E`, `0x060669CC`, `0x060669F6`, `0x06066A10`, `0x06066A3A` (renderer) | `00BD` each | `E002` each | the renderer's size and language reads → 2 (the sites version 3 patches for win quotes) |
| `0x06066914` (selector's language-2 list address) | `06085544` | `00259100` | point language 2 at a new list |
| `0x00259100` (76 bytes, was zero) | zeros | 19 longs; slot 16 = `0x00259200` | the list |
| `0x00259200` (600 bytes, was zero) | zeros | arcade English slot 16 records 0-5 (`0x18D0AE`-`0x18D305`) | the records |

`0x00259050`-`0x0025E3DF` (just after `MC10`'s buffer) is zero at the
checkpoint, at page 1 and after the credits. It was read back after the
run and only the written bytes had changed.

The label test is separate: from `f00220917.mcs` (page 2), the first letter
of label entry `0x11` changed from `N` to `X` (`0x060D5FC8`, `004E` →
`0058`).

## Prediction

- The trial pages read `0x00259200` + 100k, one per page, at the arcade's
  English pace.
- They show black, captive, captive, black, Guile, Guile, with `Charlie` on
  page 4 and `Charlie's friend` on page 5.
- The text is drawn in the 2 × 25 grid with the `FIX.PRS` glyphs.
- The label edit changes one letter only.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | Track 01 `c904a386…`; `MCED.SHP;1` `aa10db67…` (decoded 39,064 bytes, `1cba5403…`) |
| Checkpoints | `f00220064.mcs` `7c5a7257…`, `f00220917.mcs` `11f2cf90…` (`EXP-0034`) |
| Program image | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` (English records) |
| Arcade comparison | `EXP-0037` English snapshots (`en_cyclops`) |

## Tools

| Tool | Use |
| --- | --- |
| [`word_reads.py`](word_reads.py) | Read log on the two words over the ending, by PC per page interval |
| [`dump_ram.py`](dump_ram.py) | WRAM-L and WRAM-H through the debugger, at a checkpoint plus N frames |
| `tools.sh2.disasm` | Readers and the scene-script routine |
| [`english_trial.py`](english_trial.py) | control and english runs; screenshots every 30 frames; quote pointer |
| `research/experiments/EXP-0023/cell_check_en.py` | Drawn cells against `FIX.PRS` |
| [`label_write.py`](label_write.py) | One-letter label edit |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0038/word_reads.py local/end005/reads1
./invenv.sh python research/experiments/EXP-0038/dump_ram.py local/end005/ram_ko local/checkpoints/end001/f00220064.mcs 0
./invenv.sh python research/experiments/EXP-0038/dump_ram.py local/end005/ram_p1 local/checkpoints/end001/f00220064.mcs 590
./invenv.sh python research/experiments/EXP-0038/dump_ram.py local/end005/ram_end local/checkpoints/end001/f00220064.mcs 2980
./invenv.sh python -m tools.sh2.disasm local/end005/ram_p1/wram-h.bin --base 0x06000000 \
  --start 0x060D4710 --end 0x060D47A0
./invenv.sh python research/experiments/EXP-0038/english_trial.py local/end005/trial1
# cell check: local/end005/cells/result.json = the trial's six first page frames
# (pointer, arcade record bytes), plus their VDP1 dumps
./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/end005/cells local/ref007/saturn_files/FIX.PRS
./invenv.sh python research/experiments/EXP-0038/label_write.py local/end005/label1
```

## Actual Result

### Who reads the words during the ending

From `word_reads.py`, frames 220,064-223,044.

The log does not give the address read, so each PC was identified by its
code:

| PC | Word | When | What it is |
| --- | --- | --- | --- |
| `0x06054226`, `0x06054232`, `0x060610EE`, `0x060610FA` | size (`0xD478`) | every frame | compare with 10 and 4 (mode checks); 0 and 2 both fail them |
| `0x060D4738` | language (`0xD47A`) | once per scene (pages 1, 3, 5, 6) | the `MCED` scene-script routine (below) |
| `0x060668C4` | language | once per scene | the type-4 selector (`EXP-0035`) |
| `0x0606696A`-`0x06066A3A` (6 sites) | size and language | once per page (2 hits at two of them) | the renderer's grid choice |
| `0x06062402` (506 hits), and 9 others with 1-2 hits | not identified | before page 1 only (and `0x06055F76`/`F82` in the credits) | outside the page path |

### The scene script is in `MCED.SHP`

- **The file:** `MCED.SHP` is the ending overlay. In RAM at `0x060D2000`
  it equals the decoded file plus 317 relocated longs (`+0x060D2040`);
  18 bytes differ, run-time variables at 4 places. Its loader was not
  caught.
- **The routine** at `0x060D4710` (disassembly):
  1. It reads the ending slot byte (R11 + `0xD11A`, 16 here).
  2. It takes the slot's script base from the table at `0x060D46C4`
     (19 longs).
  3. It reads the language word and adds the header word at base +
     language. That gives the Japanese script at language 0 and the
     English one at languages 2, 4 and 6.
  4. It indexes by scene (×2) to the scene entry, and stores it at
     R11 + `0xA4D0`.
  5. It reads the entry: duration word → R11 + `0xA4CE`, record byte, label
     byte. Then it continues at `0x060D5C90`.
- **Slot table:**
  - Slots 8 and 9 share one script (`0x060D4AD4`), and slots 11 and 18
    share another. This mirrors the arcade's English pointer equalities
    (`EXP-0008`).
  - In the file, the table holds `0x2CB0` for slot 16, which plus
    `0x060D2040` is `0x060D4CF0`.
- **Nash's script** (`0x060D4CF0`, decoded `MCED` `0x2CF0`, equal to RAM):

  | | Japanese (base + 8) | English (base + `0x38`) |
  | --- | --- | --- |
  | Scenes | 4: records 0-1, 2-3, 4, 5 | 4: records 0, 1-2, 3, 4-5 |
  | Page lengths | `0x100`, `0x100`, `0x100`, `0x100`, `0x140`, `0x300` | `0x180` × 5, then `0x300` |
  | Label bytes, pages 1-6 | `00 00 11 23 11 24` | `00 00 00 15 27 00` |

  Pictures follow the scene number: black, captive, black, Guile.
- **Labels:** the label byte indexes a list at `0x060D5DA8` (decoded
  `MCED` `0x3DA8`). It has 40 entries of 32 bytes, in 16-bit ASCII, equal
  to RAM. Entries:
  - `0x01`-`0x12`: the 18 roster names in slot order (`Vega` at `0x0F`,
    `Gouki` `0x10`, `Nash` `0x11`, `Cammy` `0x12`);
  - `0x13` `Bison`, `0x14` `Akuma`, `0x15` `Charlie`;
  - then other speakers, including `0x23` `Nazo no koe`, `0x24` `Nash's
    friend` and `0x27` `Charlie's friend`.

### English trial

The quote pointer at each page change:

| Run | Page 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| control | `0x0024FEC0` (220,560) | `…FF0C` (220,830) | `…FF58` (221,070) | `…FFA4` (221,340) | `…FFF0` (221,610) | `0x0025003C` (221,940) |
| english | `0x00259200` (220,560) | `…9264` (220,950) | `…92C8` (221,340) | `…932C` (221,730) | `…9390` (222,120) | `…93F4` (222,510) |

- **Records:** the English run read records 0-5 of the arcade English
  block, one per page.
- **Timing:** about 390 frames between pages. The arcade's English pages
  are about 383 frames apart, and the script says `0x180` (384).
- **The global words** were still 0 at the end of both runs. The scratch
  region held only the written bytes.

**Screens** (agent-reviewed; English run, mid-page):

| Page | Frame | SHA-256 | Picture | Label | Text |
| --- | --- | --- | --- | --- | --- |
| 1 | 220,680 | `65ae6f95…` | black | none | English record 0, 1 line |
| 2 | 221,070 | `456fee1d…` | captive | none | record 1, 2 lines |
| 3 | 221,460 | `a5661877…` | captive | none | record 2, 2 lines |
| 4 | 221,850 | `fc8fe0c5…` | black | `Charlie` | record 3, 1 line |
| 5 | 222,240 | `bdfbd8b7…` | Guile | `Charlie's friend` | record 4, 2 lines |
| 6 | 222,630 | `55a9d2cd…` | Guile | none | record 5, 2 lines |

Page for page, these match `EXP-0037`'s arcade English snapshots: the
pictures, the labels, the line counts and the text.

**Cells:** on all six pages, every sprite matches its `FIX.PRS` glyph,
with none missing. The grid is rows 176 and 192 at a 12 px pitch, 50 or
100 sprites (100 where two commands share a cell, as in `EXP-0035`).

### Label edit

From `f00220917`, `N` → `X` in entry `0x11`:

- At page 3, 27 pixels differed from control, all in x 32-40, y 172-179,
  the label's first letter.
- At zoom, `Nash` became `Xash`.
- Control equals the session's page 3 screenshot (`4c3ef8e4…`). The written
  screenshot is `1551cf2e…`.

## Conclusion

**CONFIRMED:** the Saturn holds the arcade's English ending script for
Nash in `MCED.SHP`. It has its own scene breaks, page lengths, label
indices (`Charlie`, `Charlie's friend`) and, through the scene numbers,
pictures. When the ending's own language reads return 2, and the selector
gets a pointer to the six arcade English records, the Saturn shows the
arcade English ending, page for page. The global words and the size word's
other readers are not needed.

**What M7 needs:**

1. **Code:** the three reads that pick the script, the records and the
   grid return English for slot 16's ending only. The renderer already
   reads a per-task flag in version 3, and the selector's language read is
   a constant 0 there.
2. **A pointer source** for the English records, because the language-2
   list at `0x06085544` is not filled.
3. **The records** (600 bytes), placed where they load with the ending.

The labels need no change: `Charlie` and `Charlie's friend` are already in
`MCED` and already used by the English script.

## Uncertainty and Alternatives

- **One ending:** only Nash's script was read and run. The slot table
  suggests every roster slot has both scripts; checking that is M8.
- **The trial's renderer change** made the renderer English for every
  caller. During the ending only the ending uses it. A real patch must
  limit it, as version 3 does for win quotes.
- **`MCED`'s loader and timing** (when it is loaded, and whether it is
  reloaded) were not caught. `END-007` needs it only if records go into
  `MCED`.
- **Readers not identified:** 10 PCs read one of the words before page 1.
  They are outside the page path, but they were not examined.

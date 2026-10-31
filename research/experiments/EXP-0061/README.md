# EXP-0061 (Special): The Special Cases, Built

Task: SPEC-004
Status: DONE
Confidence: CONFIRMED (a RAM change against a control, then every box
routed on the built images and read against the approved lines)

## Observation

The user's plan (`SPEC-003`, `EXP-0060`) has two parts:

- **Boss boxes:** the approved English for Apocalypse's boxes
  (`data/translations/boss_boxes.json`), in the win quotes' 2 × 25 layout.
- **Alpha Chun-Li:** Chun-Li's official English for slot 18, with table
  word `0x0285` (`EXP-0059`).

The boxes draw 2 × 19 wide cells, and the 2 × 25 layout needs a code change.

## How the boxes are chosen and drawn

These facts were read on the untouched image from `walk2/p0`, with write
logs and dumps (`local/spec004/`).

- **Renderer:** the boxes use the win-quote renderer. The pointer write is
  at `0x0606698C`, for task `0x060F9CC0`.
- **Record address:** the renderer reads the record base from task + 52
  and the index from task + 38. The address is base + index × (76, or
  100 when the size test is non-zero).
- **Layout:** five language tests choose the layout: 19 or 25 cells, and
  the line-2 address. In the English builds, those six reads take the
  task byte + `0x5C` (`D-022`, `english_mode`).
- **Box setup** (`0x060667C4`):
  - It takes the slot as the player's character word >> 1.
  - The start index comes from the byte table `0x0606684C` (decoded
    `MMPACK.PCA` `0x51CAC`).
  - The base comes from a two-entry table chosen by the global language
    word. Entry 0 holds `0x060C2090`, `MC08` + `0x1090`. The other entry
    is a placeholder, `0x060854F8`.
  - The setup never sets task + `0x5C`.
  - Each later box adds 1 to the index (`0x060665DE`), so a slot's three
    boxes are consecutive records.

## The Change

Set task + `0x5C` = 2 in the box setup and give it an English base.

**Room:** 17 distinct triples (slot 8 repeats slot 7) need 5,100 bytes.
The free space in decoded `MC08.SHP` is:

- `0xDC0`-`0x2098` (4,824 bytes). This is Apocalypse's unused Japanese
  quotes 8-15, slot 8's never-shown Japanese ending records and the
  Japanese box table.
- A run of 1,792 zero bytes at `0x4A3C`.

In the American build, RAM at the boss stage held exactly the file's bytes
in both ranges (no relocations).

**Zero run checked:** read and write logs found **no access** at
`0x060C5A3C`-`0x060C613B`:

- 2,400 frames from `p0`: boxes, transformation, fight;
- 2,400 frames from `p9` with the boss knocked out, through the post-boss
  quote and into the partner fight (`zero_read`, `zero_write`,
  `zero_read_ko`).

So 16 triples start at `0xDC0`. The 17th, Cammy's, is at index 155
(`0x4A4C`).

`tools/disc/boss_boxes.py` holds the layout. Each change is listed below
(rule 12):

| Address (WRAM-H) | Original | New | Purpose |
| --- | --- | --- | --- |
| `0x06066804` (decoded `MMPACK` `0x51C64`, 26 bytes) | `9014 00BD C101 C501 300C C101 D109 C501 021D 70FE 011D 6029 201D` | `E15C 316C E002 2100 D002 A006 0009 0009 0009 0009 060C 1DC0 0009` | Task + `0x5C` = 2; base = literal `0x060C1DC0`; rejoins the original store at `0x0606681E` |
| `0x0606684C` (20 bytes, index by slot 0-19) | `00 03 06 09 0C 0F 12 15 18 1B 1E 21 24 27 2A 2D 30 33 21 21` | `00 03 06 09 0C 0F 12 15 15 18 1B 1E 21 24 27 2A 2D 9B 1E 1E` | Slot 8 → slot 7's triple; 9-16 shift by one triple; 17 → 155; 18 and 19 → Chun-Li's |
| `0x06066704` (slot 18's fixed-table word) | `0005` | `0285` | Alpha Chun-Li: English flag and ending bit (`EXP-0059`) |
| `MC08.SHP` decoded `0xDC0`-`0x2080` and `0x4A4C`-`0x4B78` | Japanese records and zeros | 51 English records (100 bytes each) | The approved lines |

## RAM Test (one controlled change)

The test ran on the American build (`build/boot004_us`) from `walk_us/p0`
(`7cddb36f…`, frame 18,840, before the box setup). That walk picked
Cyclops; a key was missed, so not Ryu as planned.
[`ram_items.py`](ram_items.py) writes the setup, index-table and record
changes into RAM. Each original was checked against a dump of `p0`
(`dump_us_p0`).

```bash
B="build/boot004_us/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0061/ram_items.py local/spec004/dump_us_p0/p0/wram_h.bin us \
  > local/spec004/ram_items_us.txt
for f in 150 240 400; do
  ./invenv.sh python research/experiments/EXP-0049/patch_run.py "$B" local/spec004/ram_$f \
    local/spec004/walk_us/p0.mcs $f $(cat local/spec004/ram_items_us.txt)
done
```

| Frames | Control (Japanese) | Patched |
| --- | --- | --- |
| 150 | 追いつめたぞ… (`4d1e1655…`) | "I've got you, Apocalypse! / Your schemes end here!!" (`65c99613…`) |
| 240 | それで我が輩を… (`eeda1bd3…`) | "Think you've cornered me? / Cyclops, you all lose!" (`4357dc61…`) |
| 400 | 見るがよい… (`74515bfd…`) | "Behold my true form! / Now offer up your life!!" (`32774c3c…`) |

Every write held to the end.

## The Builds

```bash
SPECS=$(python3 -c "import json;r=[x for x in json.load(open('data/regression/references.json'))['references'] if x['name']=='roster_endings_v4'][0];print(' '.join(r['specs']))")
for v in us saturn; do
  ./invenv.sh python -m tools.disc.build_english ${=SPECS} local/spec004/files_$v \
    --patch-version 4 --names $v --boot-warnings --special --image build/spec004_$v
  ./invenv.sh python -m tools.disc.sector "build/spec004_$v/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
done
```

`build_english --special` writes the boxes into `MC08.SHP`, after
Apocalypse's English quotes. It refuses an overlap with them or a record
outside the free ranges. It also adds the `MMPACK.PCA` changes above.

| | American names | Saturn names |
| --- | --- | --- |
| Track 01 | `5d1f76e4…b49b` | `a4e3e98e…1a38` |
| Sectors | 71,908, 0 invalid | 71,908, 0 invalid |
| `MC08.SHP` / `MMPACK.PCA` | `c3538551…` / `af4c3704…` | `86fba33a…` / `1c8476e4…` |
| Other changed files | equal to `boot004_us`'s | equal to `boot004_saturn`'s |

**No other change**, against the `BOOT-004` builds, decoded:

- **`MC08.SHP`:** same length, and every changed byte lies inside the two
  free ranges.
- **`MMPACK.PCA`:** changes only at `0x51B64` (slot 18's word),
  `0x51C64`-`0x51C7E` (the setup) and `0x51CB4`-`0x51CC0` (index entries
  8-19).
- **Between the two variants:** `MC08.SHP` differs only inside the second
  box of slots 14-16.

The M8 quotes, endings and every other file are those of the registered
references.

## Screens

[`run_boxes.py`](run_boxes.py) routes each roster slot to the boxes. It is
`EXP-0047`'s ending runner with a screenshot every 40 frames. The route
tool gained `--shot-every`, and `--stop-on-bad-load`, which ends a run when
its pick loaded the wrong character. The user pointed out that failed
picks ran to the end.

[`check_boxes.py`](check_boxes.py) compares the last three quote pointers
inside `MC08` with the planned records. It also crops each box's last
screenshot for the agent to read.

```bash
for v in us saturn; do
  N="build/spec004_$v/X-Men vs. Street Fighter (Japan) (3M).cue"
  ./invenv.sh python research/experiments/EXP-0061/run_boxes.py "$N" local/spec004/files_$v/MMPACK.PCA \
    local/spec004/boxes_$v
  ./invenv.sh python research/experiments/EXP-0061/check_boxes.py local/spec004/boxes_$v local/spec004/check_$v
done
```

- **American image:** all 17 slots loaded correctly (6 needed a second or
  third attempt, after lost keys). Every slot's three pointers equal the
  planned records, Cammy's far triple included.
  - The agent read all 51 boxes against the approved lines: each matches,
    with version A or B of the third box as planned, and "Bison", "Akuma"
    and "Charlie".
  - Earlier pointers in the same WRAM-H range were the partner's ordinary
    win quotes, from the second team buffer.
- **Saturn-names image:** 16 slots matched; Rogue's pick failed all three
  attempts.
  - The second box of slots 14-16 reads "Vega, lower than trash,",
    "Gouki, however strong," and "Pitiful, Nash.", and the other boxes
    read as on the American image.
  - Rogue's records are byte-identical to the American image's, which
    were read on screen.
  - The user chose to rely on that identity rather than wait for more
    runs (asked mid-task; the full run had already finished).
- **Alpha Chun-Li** (`alpha_us`, cold boot of `build/spec004_us`, Start
  held over Chun-Li): character word `0024`; her table word read `0285`.
  - **Win quote:** "I expected better. / Why do I expect so much?", the
    arcade's line (`EXP-0059`).
  - **Boxes:** "So you're Apocalypse? / Freeze! You're arrested!!",
    "Arrest me? Ha ha ha ha! / Chun-Li, don't be absurd.", "Behold my
    true form! / Now offer up your life!!".
  - **Post-boss quote:** "I am the strongest woman / in this or any
    world!" (the arcade's).
  - **Ending:** six English pages, from "Chun-Li..." to "You're as cute
    as Jean!", then the credits.
  - Her slot-18 bytes are the same in the Saturn-names image, which was
    not walked.

## Conclusion

**CONFIRMED:**

- Both name variants build with the approved English boss boxes in the
  2 × 25 layout, and with Alpha Chun-Li in Chun-Li's official English.
- Every box of the 17 roster slots shows its approved line on the
  American image, and the variant boxes on the Saturn-names image.
- Nothing else changed.

## Uncertainty

- **Slot 8's ending** is now English box text instead of its Japanese
  records, if it could ever play (HYPOTHESIS that it never does,
  `docs/coverage_exceptions.md`).
- **The zero run** at `MC08` `0x4A3C` was not accessed over the boss stage
  and the start of the partner fight. Its use elsewhere is unknown; that
  `MC08` (Apocalypse, not selectable) is loaded only for the boss stage is
  a HYPOTHESIS.
- **The user's play check** is `SPEC-005`'s.

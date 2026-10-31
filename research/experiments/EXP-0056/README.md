# EXP-0056 (Boot): The English Boot Warnings, Built and Shown

Task: BOOT-004
Status: DONE
Confidence: CONFIRMED (every warning shown from a cold boot of each built
image equals its built picture pixel for pixel)

## Observation

`BOOT-003` (`EXP-0055`): the user approved the English for `ERR1`-`ERR5.BIN`
and the style (the quote font in the original palette),
`data/translations/boot_warnings.json`. `EXP-0054` measured the format.

## Hypothesis

Built from the untouched source with `build_english --boot-warnings`, each
picture keeps its format, every warning shows its English exactly as built,
and nothing else changes: the normal boot and every other built file stay
as in the name-variant references.

## Tools

| Tool | Use |
| --- | --- |
| `tools/disc/boot_warnings.py` | The generator, promoted from `EXP-0055`'s `render_samples.py`: layout and style from the data file, format checks, `shown` (the screen as the game shows a picture) |
| `tools.disc.build_english --boot-warnings` | Writes the five pictures; lists each file's changed span with its original and new bytes (rule 12) |
| [`check_screens.py`](check_screens.py) | A screenshot against a built picture, pixel for pixel |
| `research/experiments/EXP-0053/census.py`, `boot_dump.py` | Cold boots under each condition; the forced `ERR5` |

## Procedure

```bash
SPECS=$(python3 -c "import json;r=[x for x in json.load(open('data/regression/references.json'))['references'] if x['name']=='roster_endings_v4'][0];print(' '.join(r['specs']))")
./invenv.sh python -m tools.disc.build_english ${=SPECS} local/boot004/files_us \
  --patch-version 4 --names us --boot-warnings --image build/boot004_us
./invenv.sh python -m tools.disc.build_english ${=SPECS} local/boot004/files_saturn \
  --patch-version 4 --names saturn --boot-warnings --image build/boot004_saturn
for v in us saturn; do
  ./invenv.sh python -m tools.disc.sector "build/boot004_$v/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
  N="build/boot004_$v/X-Men vs. Street Fighter (Japan) (3M).cue"
  ./invenv.sh python research/experiments/EXP-0053/census.py "$N" local/boot004/r_$v \
    extram4_valid none_valid backup_valid extram4_zero extram4_corrupt extram4_free18
  ./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$N" local/boot001/c2/homes/none_valid \
    local/boot004/r5_$v 1500 pc:060228D4:060228D4 onhit:060228D4:060228FA:8905
  C=local/boot004/r_$v
  ./invenv.sh python research/experiments/EXP-0056/check_screens.py local/boot004/files_$v \
    $C/none_valid/f00003600.png:ERR4.BIN $C/backup_valid/f00003600.png:ERR4.BIN \
    $C/extram4_zero/f00003600.png:ERR1.BIN $C/extram4_corrupt/f00003600.png:ERR2.BIN \
    $C/extram4_free18/f00003600.png:ERR3.BIN local/boot004/r5_$v/screen.png:ERR5.BIN
done
# baselines: the name-variant images without the warnings
./invenv.sh python research/experiments/EXP-0053/census.py \
  "build/loc005_names_us/X-Men vs. Street Fighter (Japan) (3M).cue" local/boot004/base_loc005_names_us extram4_valid
./invenv.sh python research/experiments/EXP-0053/census.py \
  "build/loc006_names_saturn/X-Men vs. Street Fighter (Japan) (3M).cue" local/boot004/base_loc006_names_saturn extram4_valid
```

## Actual Result

### The first build, and a correction to `EXP-0054`

The first build (kept as `build/boot004_us_v1`, `_saturn_v1`) passed every
check except one: on the no-free-space warning, 64 pixels on screen row 232
were black where `ERR3`'s last line has its drop shadow (dark grey).

- **Why:** every screenshot in this project, game screens included, has
  content only on screen rows 8-231. The display is 224 lines; Mednafen's
  352 × 240 screenshots pad 8 black rows above and below. So the visible
  picture rows are **0-223**, not 0-231 as `EXP-0054` concluded (its
  comparisons had black on both sides there). `EXP-0054`, D-050 and the
  generator (`LAST_ROW` 223) were corrected.
- **Fix:** `ERR3`'s block starts 2 rows higher (`"top": 50` in the data
  file), so its last shadow row is picture row 222. Its wording and look are
  unchanged; the other four pictures are byte-identical to the first build
  and to the samples the user approved.

### The builds

| | American names | Saturn names |
| --- | --- | --- |
| Image | `build/boot004_us` | `build/boot004_saturn` |
| Track 01 | `e8c9cc4f…3ef4` | `f53d2378…2280` |
| Sectors | 71,908, 0 invalid | 71,908, 0 invalid |
| Other 20 changed files | equal to `names_us_v4`'s | equal to `names_saturn_v4`'s |

Pictures (both images): `ERR1` `72fbff0a…`, `ERR2` `5cee7adb…`, `ERR3`
`017b7a5e…`, `ERR4` `970f953a…`, `ERR5` `7c918f31…`. Each keeps its size
(42,358 bytes) and its first 118 bytes (header and palette); every change
starts after the header (`changes.json`: one span per file, original and new
bytes).

### The screens (frame 3,600; forced `ERR5` at frame 1,500)

| Condition | Picture | American: pixels that differ | Saturn names |
| --- | --- | --- | --- |
| no cart | `ERR4` | 0 of 84,480 | 0 |
| backup cart | `ERR4` | 0 | 0 |
| unformatted | `ERR1` | 0 | 0 |
| damaged save | `ERR2` | 0 | 0 |
| 18 blocks free | `ERR3` | 0 | 0 |
| forced −1 branch (`0x060228FA` read back `8905`) | `ERR5` | 0 | 0 |
| control (4 MB, a save) | none | `d92881d1…`, equal to `loc005_names_us`'s | `6d6e4b7d…`, equal to `loc006_names_saturn`'s |

The agent read all six English screens against the approved text: every
line, colour and highlight as approved.

## Conclusion

**CONFIRMED:** both name variants build with the English boot warnings
from the untouched source. Every warning the census could trigger, and
`ERR5` by its forced branch, shows its English picture exactly; the normal
boot and every other file are unchanged.

## Uncertainty

- **Real hardware:** not tried; the pictures keep the original format and
  palette, so they should show as the Japanese ones did.
- **The user's play check** is `BOOT-005`'s.

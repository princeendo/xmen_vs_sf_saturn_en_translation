# EXP-0063 (UI): The "No Challengers" Sign: Storage, and the Arcade's English Path

Task: NOCH-001
Status: DONE
Confidence: CONFIRMED (storage, and the English path, each by a controlled
RAM change against a control; the build shown by route on both images and
in the user's play)

## Observation

After Apocalypse is beaten, a `⚠乱入禁止` ("no challengers") sign shows at the
top right, from the black splash screen through the partner fight and its
continue screen (`docs/text_surfaces.md`, `EXP-0034`). The US arcade shows
`NO CHALLENGERS` there (`EXP-0037`).

MSHvSF (a HYPOTHESIS for XvSF, rule 13): its similar labels were quote-font
art cells, and its font held the arcade's English UI art, "NO CHALLENGERS"
included (MSHvSF `EXP-0053`).

## Inputs

- Untouched image (`references/saturn_jp/README.md`; Track 01 `c904a386…`).
- Checkpoints: `local/checkpoints/end001/f00216311.mcs` (Nash and Ryu,
  about 470 frames before the sign; `EXP-0034`), `f00219894.mcs` (the
  partner fight, sign shown), and `local/spec001/walk2/p0.mcs` (the boss
  stage, before the boxes; `EXP-0058`).
- The data-track files, extracted to `local/noch001/disc/` with
  `tools.disc.iso9660 --extract`.
- The arcade screenshot `local/end004/final/en_ryu/snap/xmvsfu_f13860.png`
  (`EXP-0037`).

Tools: `EXP-0049`'s `dump_screen.py`, `write_log.py` and `patch_run.py`;
`tools.memory.vdp1_sprites`; `tools.text.font`; `tools.sh2.disasm`.

## Where the sign is

1. **Cells** (dump of `f00219894`, `local/noch001/dump_fight/`): five VDP1
   16 × 16 4 bpp sprites, colour word `0x7000`, at y = 1 and x = 256-320,
   character data `0x1AA00`-`0x1AC00`. The rendered cells are the sign.
2. **Font codes:** the five cells equal `FIX.PRS` (the quote font, D-014)
   codes `0x28B`-`0x28F`, decoded with `tools.text.font`. Each glyph is
   unique in the font. The raw cells are on no disc file and in no work
   RAM: the game decodes them at run time (`0x06024CF0`, D-045).
3. **Controlled change 1** (`empty_28f`): from `f00216311`, 650 frames, the
   size byte of code `0x28F` in the RAM font (WRAM-L `0x002C44BF`, `41` →
   `00`, an empty glyph; the last code of its block, so no other glyph
   moves). Control: ⚠乱入禁止 (`1eadb11b…`). Patched: ⚠乱入禁, with 止 gone
   (`a5bf6380…`).
4. **The request:** the decoder is called for `0x28B`-`0x28F` once, when
   the sign appears (`decoder_pc`). Each frame the sprite-list processor
   (`0x06024800`; 0x389 eight-byte entries at `0x060E3020`) draws an entry
   `E150 2011 568B 0400`:
   - word 0: flags `0xE000`, x `0x150`; y `0x011`;
   - word 1: `0x5400` + code `0x28B`; cells across − 1 = 4 (bits 8-11).
5. **The definition:** a sprite-script interpreter in the overlay code
   (`0x0607B9xx`-`0x0607BCxx`) reads the code and width once, from
   `0x0607C5BE`: `1234 0480 0400 568B` (`def_read`). The definition before
   it, at `0x0607C5B6`, is `1234 0480 0700 5880`: code `0x480`, 8 cells.

## English art in the font

`FIX.PRS` holds the arcade's English UI art (`local/noch001/sheets/`):

- `0x460`-`0x46F`: PRESS START, FREE PLAY, ©;
- `0x470`-`0x47F`: INSERT COIN, JOIN IN, GAME OVER;
- **`0x480`-`0x487`: NO CHALLENGERS** (128 px), then INSERT ADDITIONAL COIN,
  INSERT 1 MORE COIN, PLEASE WAIT;
- `0x200`: an italic CHALLENGER!; `0x220`: NEW HERO; WINS, 1P, 2P.

The arcade's `NO CHALLENGERS` (MAME `xmvsfu`, frame 13,860) is drawn at the
top right, about 128 px wide, in the same letters.

## The arcade's English path

The x is set before the script runs, at `0x0605F82E`-`0x0605F868`
(`x_write`, writes to the interpreter's x word `0x06001FCA`):

- the sign takes variant `0x020E` and offset −16 when the word at R11 +
  `0xD478` (**`0x060F5478`**, the region word of D-047) is non-zero;
- otherwise variant `0x020F` and offset +32; x = `0x130` + offset.

The Saturn keeps the word at 0, so the sign is variant `0x020F`, x
`0x150` (screen x 256), 5 cells, ending at 336. Variant `0x020E` gives x
`0x120` (screen x 208): 8 cells would end at the same 336.

**Controlled change 2** (`site_d`, one change): from `f00216311`, the region
read at **`0x0605F838`** (`00BD`, `mov.w @(r0,r11),r0`) replaced by
`E002` (`mov #2,r0`), the change `--names us` makes at its 10 sites
(D-047); this read is not one of them.

| Run | Frames | Control | Patched |
| --- | --- | --- | --- |
| `site_d` (splash) | 650 | ⚠乱入禁止 (`1eadb11b…`) | **NO CHALLENGERS**, 8 cells, x 208-335 (`bee65d13…`); 1,344 pixels differ, all in x 209-334, y 9-23 |
| `site_d_fight` | 3,600 | ⚠乱入禁止 on the continue screen (`91885d79…`) | NO CHALLENGERS on the continue screen (`fc6414bd…`) |
| `site_d_boss` (from `walk2/p0`) | 900 | the boss fight, PRESS START at the top right (`f17f1484…`) | identical (`f17f1484…`) |

The run to the partner fight lost it with no input, so it ended on the
continue screen; the sign is one object from the splash to there.

Earlier RAM runs on the definition itself, recorded so they are not
retried:

- `def_a` (code word `568B` → `5880` only): "NO CHALLE", the first 5 cells.
- `def_b` (also the word after the code, `0x0607C5CA`, `0400` → `0700`): the
  same as `def_a`; that word belongs to the next definition.
- `def_c` (`0x0607C5C2` `0400` → `0700` and `568B` → `5880`): all 8 cells
  from x 256, running off the right edge. The position comes from the
  region read, not from the definition.

**Build location:** decoded `MMPACK.PCA` offset `0x4AC98` (`0x0605F838` −
`0x06014BA0`) holds `00BD` in the untouched image.

## The User's Choice

Shown a before-and-after sample (`local/noch001/sample/noch_sample.png`:
the splash and continue screens, control and `site_d`, and the arcade's
sign), the user chose (verbatim): "Use the arcade's own NO CHALLENGERS, as
in the sample (the one region-word change)." The other option offered was
to remove the sign. Recorded in `docs/localization_policy.md`.

## The Build

`build_english --no-challengers` adds the one patch (`NO_CHALLENGERS`,
`no_challengers_patches`), refusing an overlap with any other `MMPACK.PCA`
patch (`with_extra`). `tools.disc.regression` passes the flag for a
reference with `"no_challengers": true`. Unit tests:
`tests/unit/test_no_challengers.py`.

```bash
SPECS=$(python3 -c "import json;r=[x for x in json.load(open('data/regression/references.json'))['references'] if x['name']=='special_us_v4'][0];print(' '.join(r['specs']))")
for v in us saturn; do
  ./invenv.sh python -m tools.disc.build_english ${=SPECS} local/noch001/files_$v \
    --patch-version 4 --names $v --boot-warnings --special --no-challengers --image build/noch001_$v
  ./invenv.sh python -m tools.disc.sector "build/noch001_$v/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
done
```

| | American names | Saturn names |
| --- | --- | --- |
| Track 01 | `6820f12d…90cf` | `57c397ea…915a` |
| Sectors | 71,908, 0 invalid | 71,908, 0 invalid |
| `MMPACK.PCA` | `32c1772a…` | `42524835…` |

Against the `SPEC-004` builds (`build/spec004_*`), only `MMPACK.PCA`
differs; decoded, the same length, and only bytes `0x4AC98`-`0x4AC99`
(`00BD` → `E002`), in both variants.

## Route Check on the Built Images

[`run_sign.py`](run_sign.py) is `EXP-0061/run_boxes.py` with 13,500 frames:
Ryu first, Cyclops second, policy `first`, a screenshot every 40 frames.

```bash
C="X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0063/run_sign.py "build/noch001_us/$C" \
  local/noch001/files_us/MMPACK.PCA local/noch001/route_us
./invenv.sh python research/experiments/EXP-0063/run_sign.py "build/noch001_saturn/$C" \
  local/noch001/files_saturn/MMPACK.PCA local/noch001/route_saturn
```

- Both picks loaded on the first attempt; both runs reached the boss and
  the partner fight (route events).
- **Both images:** NO CHALLENGERS at the top right from the post-boss
  splash through the post-boss quote and the partner fight, until its
  knockout; no Japanese sign in any screenshot. Frame 11,840: the American
  image in the partner fight (`d9de4601…`), the Saturn-names image on the
  post-boss quote (`158c6730…`). On the fight screen the sign sits right of
  the timer without touching it.
- **Timing unchanged:** the `EXP-0047` route on the M8 image (Ryu,
  `local/end015/r1/s09_a1`, the Japanese sign) shows the sign over the same
  stretch, gone by the knockout.

## The User's Play Check

[`play_check.py`](play_check.py) is `EXP-0062/play_check.py` with the
`--no-challengers` builds. The user chose to play the American-names image
only ("Open the play check on the American-names image only.").

```bash
./invenv.sh python research/experiments/EXP-0063/play_check.py local/noch001/play us
```

- **Boot:** `build/noch001_us`, 4 MB cart, a valid save (`c1fa3ecd…`; the
  silent home's save, which later runs update, so it differs from
  `EXP-0062`'s), 944 s, 1,823 screenshots.
- **Play:** Ryu and Akuma; one continue at Apocalypse; Apocalypse beaten;
  the partner fight against Cyclops.
- **The sign:** NO CHALLENGERS at the top right from the VS screen of the
  partner fight. The state `f00053698` (partner fight), dumped with
  `EXP-0049/dump_screen.py` on the same image, draws eight cells at y = 1,
  x 208-320, colour word `0x7000`, which decode as `FIX.PRS` `0x480`-`0x487`.
  None of `0x28B`-`0x28F` is drawn (`screen.png` `0b645617…`).

## The Regression References

`data/regression/references.json` gained `no_challengers_us_v4` (Track 01
`6820f12d…90cf`) and `no_challengers_saturn_v4` (`57c397ea…915a`), each with
`"no_challengers": true`; against `special_*_v4` only `MMPACK.PCA` differs.
`build_english.py` changed, so every reference was rebuilt (the user's rule,
`tools.disc.regression`):

```bash
./invenv.sh python -m tools.disc.regression --report docs/regression_report.md
```

All thirteen match (`docs/regression_report.md`).

## Conclusion

**CONFIRMED:**

- The sign is `FIX.PRS` codes `0x28B`-`0x28F`, drawn by a sprite definition
  in the overlay code.
- The user chose the arcade's own sign; `build_english --no-challengers`
  builds it into both name variants, and it showed by route on both images
  and in the user's play.
- The game keeps the arcade's English sign: one region read chooses it,
  with its own art (`0x480`-`0x487`), width and position. Reading the
  region as US at `0x0605F838` alone shows the arcade's NO CHALLENGERS,
  right-aligned where the sign was, and changes nothing else on screen.

## Uncertainty

- Whether anything else reads the region at `0x0605F838`'s branch: the
  variants `0x020C`/`0x020D` (offsets 0, 24) were not reached here.
- The second similar block at `0x0605F894` (x = 96) was not traced; it may
  be the other side's sign (a second player).
- D-047's static scan found 45 region-word readers in `MMPACK.PCA`; the
  others' effects are unknown.

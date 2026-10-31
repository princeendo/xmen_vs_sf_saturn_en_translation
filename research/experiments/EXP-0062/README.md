# EXP-0062 (Special): The User's Play Check, and the Registered Builds

Task: SPEC-005
Status: DONE
Confidence: CONFIRMED (the user's cold-boot plays recorded and the boxes
matched, glyph for glyph, to the forced runs; every regression reference
rebuilt)

## Observation

`EXP-0061` (D-054): both name variants build with Apocalypse's boxes in the
approved English and with Alpha Chun-Li in Chun-Li's English. Every box was
shown by forced routes; the user had not played the builds.

## Hypothesis

A user who plays to the boss stage from a cold boot sees the same English
boxes as the forced routes, on each name variant, with no unlock.

## The Play Check

[`play_check.py`](play_check.py) opened two cold boots in turn, each in a
fresh copy of the interactive home `local/mednafen` (the user's pad and
sound; their own home untouched), with the 4 MB cart and a valid save
(SHA-256 `9a9b6189…6c4d`). It kept a screenshot every half second and a
state every minute (`local/spec005/play/<boot>/`).

```bash
./invenv.sh python research/experiments/EXP-0062/play_check.py local/spec005/play
```

The agent suggested Alpha Chun-Li on the American image and Vega on the
Saturn-names image, so that the play would show slot 18 and a variant box.

| Boot | Image | Time | Team (character byte, from a state) | Reached |
| --- | --- | --- | --- | --- |
| `us` | `build/spec004_us` | 850 s | Ryu (`0x12`) and Alpha Chun-Li (`0x24`); table word 18 `0285` | Boss beaten; post-boss quote |
| `saturn` | `build/spec004_saturn` | 715 s | Ryu (`0x12`) and Vega (`0x1C`) | The boss fight |

The teams were read from WRAM-H dumps of the states `f00035694` (`us`) and
`f00035787` (`saturn`), taken with `EXP-0049/dump_screen.py`: player blocks
`0x060F4200` and `0x060F4A00`, byte + `0x23` (`tools.mednafen.route`).

## Comparison With the Forced Runs

The boxes were compared with `EXP-0061`'s forced screenshots of the same
slot: slot 11's (`boxes_us/s11_a1`, whose boxes slot 18 shares) and slot
14's (`boxes_saturn/s14_a1`). Whole screens cannot match, because the
score, timer, life bars and portrait differ. So the comparison takes the
box area (x 8-343, y 12-63) and its light-grey glyph pixels (every channel
≥ 150, spread ≤ 24), and counts the pixels where the two masks differ.

| Boot | Box | User's screenshots (frames) | Forced | Differing pixels | Where |
| --- | --- | --- | --- | --- | --- |
| `us` | 1 "So you're Apocalypse? / Freeze! You're arrested!!" | 36,512-36,574 | `r009920` | 11 | portrait corner (x 8-12, y 57-62), outside the box |
| `us` | 2 "Arrest me? Ha ha ha ha! / Chun-Li, don't be absurd." | 36,604-36,696 | `r010040` | 62 | the same 11, and "PRESS START", blinked off in the forced shot |
| `us` | 3 "Behold my true form! / Now offer up your life!!" | 36,791-36,852 | `r010160` | 11 | portrait corner |
| `saturn` | 1 "So you came, Apocalypse! / Your era ended long ago!!" | 41,392-41,453 | `r009800` | 29 | portrait corner (x 8-28, y 52-62) |
| `saturn` | 2 "Vega, lower than trash, / you think you'll beat me?" | 41,483-41,575 | `r009920` | 29 | portrait corner |
| `saturn` | 3 "Behold my true form! / Now offer up your life!!" | 41,668-41,730 | `r010080` | 29 | portrait corner |

So every glyph of the six boxes equals the forced run's. The agent also
read each box on screen against `data/translations/boss_boxes.json`.

Also seen in the American play, read on screen (not pixel-matched; the
forced walk's screenshots have another size):

- Alpha Chun-Li's win quote "I expected better. / Why do I expect so
  much?" (Ryu's "So many I have fought..." showed after his wins);
- her post-boss quote "I am the strongest woman / in this or any world!",
  the last screen of the recording.

The scripts were scratch work (glyph masks with ffmpeg); the method above
is complete enough to repeat.

## The Regression References

`data/regression/references.json` gained `special_us_v4` (Track 01
`5d1f76e4…b49b`) and `special_saturn_v4` (`a4e3e98e…1a38`), each with
`"special": true`, `EXP-0061`'s specs and its 25 changed files. Against the
boot-warning references they differ only in `MC08.SHP` and `MMPACK.PCA`.

```bash
./invenv.sh python -m tools.disc.regression --report docs/regression_report.md
```

## Actual Result

- **Play check:** the tables above.
- **Regression:** all eleven references match: the nine of `EXP-0061`
  and `special_us_v4`, `special_saturn_v4` (`docs/regression_report.md`).
  No build code had changed since `EXP-0061`'s full run, so rebuilding the
  two new references alone would have been enough; the user then decided
  that the full run is for build-tool changes only (`tools.disc.regression`).
- **Coverage:** `docs/coverage_exceptions.md`, "Special cases".
- **README:** both build commands with `--special`; Apocalypse's boxes
  removed from "Still Japanese".

## Conclusion

**CONFIRMED:** from a cold boot with no unlock, the user reached the boss
stage on both name variants and saw the English boxes, glyph for glyph as
built: Alpha Chun-Li's on the American image and Vega's, with the Saturn
name, on the Saturn-names image. Alpha Chun-Li's English quotes and
post-boss quote showed in play.

## Uncertainty and Alternatives

- **Not played:** Alpha Chun-Li's ending in this check (shown in
  `EXP-0061`), Alpha Chun-Li on the Saturn-names image, and the boxes of
  other characters in play (all shown by routes in `EXP-0061`).
- The rest is listed in `docs/coverage_exceptions.md`, "Special cases".

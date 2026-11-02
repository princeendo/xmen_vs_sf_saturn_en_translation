# EXP-0072 (UI): A Survey of the Remaining Screens

Task: UI-005
Status: DONE (2026-11-01)
Confidence: CONFIRMED for the screens below (seen on the toggle build)

## Observation

`docs/text_surfaces.md` listed versus mode, the Options sub-screens, the
QSound screen and rare text as not yet inventoried. The user chose to
survey them, then decide ("Survey, then decide (Recommended)").

## Method

Cold boots of `build/loc010_toggle` walked with `EXP-0068/opt_walk.py` (a
copy of `local/loc008/home_opt1` with a good save), and the screenshots of
`EXP-0069`'s routes to the credits (`ram2_v0`). Each screen read by eye.

## Result

| Screen | Seen | Japanese or romanised text? |
| --- | --- | --- |
| Versus mode select (1P/2P cursors, names, win counters) | `vs2` `vs1.png`-`vs5.png` | None |
| Versus mode beyond the select screen | not reached: the second player's picks need a second controller, which the walker does not drive | (the fights use the arcade screens, already English) |
| OPTION MODE, every row and value list | `EXP-0069`, `EXP-0070`; the rows' strings are ASCII in `MMPACK.PCA` | None |
| BUTTON CONFIG. | `opt2` `bc1.png` | None |
| Credits | `ram2_v0` frames 16,000-18,700 | Staff names in Latin letters only |
| "Presented by CAPCOM" with the QSound notice | `ram2_v0` `r018960.png` (`fc75088a…`, the same picture as `text_surfaces.md`'s) | **One line**: a Japanese trademark sentence below five English lines that say the same |
| GAME OVER, name entry ("1st _"), SCORE RANKING, VS RANKING | `ram2_v0` frames 19,000-21,600 and 26,000+ | None |
| Attract legal text | `ram2_v0` `r028800.png` | None |
| Nash's ending labels | D-033 | `Nazo no koe` is in the Japanese script only; the English shows `Charlie`, `Charlie's friend` |

The 21 non-ASCII bytes in the menu string area are the row lists' offset
words, not text.

## Conclusion

On every screen reached, the only Japanese left is the QSound notice's
last line (part of a picture). Put to the user with its cost.

**The user's decision** (verbatim): "Leave it (Recommended)". Recorded in
`docs/localization_policy.md` and `docs/coverage_exceptions.md`.

# EXP-0057 (Boot): The User's Play Check, and the Registered Builds

Task: BOOT-005
Status: DONE
Confidence: CONFIRMED (the user's boots recorded and matched to the built
pictures; every regression reference rebuilt)

## Observation

`EXP-0056` (D-051): both name variants build with the English boot
warnings, and every warning matched its picture in scripted cold boots.

## The Play Check

[`play_check.py`](play_check.py) opened six cold boots in turn, each in a
fresh copy of the interactive home `local/mednafen` (the user's pad and
sound; their own home untouched) with the case's cart and backup memory,
and recorded a screenshot every second (`local/boot005/play/<boot>/`).

```bash
./invenv.sh python research/experiments/EXP-0057/play_check.py local/boot005/play
```

| Boot | Image | Cart | Backup memory | Screenshots matching a built picture exactly | Last screen |
| --- | --- | --- | --- | --- | --- |
| `us_no_cart` | `build/boot004_us` | none | valid save | `ERR4`: 13 (frames 875-1,616) | the English no-cart warning |
| `us_damaged_save` | `build/boot004_us` | 4 MB | damaged save | `ERR2`: 7 (1,435-1,805) | the English damaged-save warning |
| `us_normal` | `build/boot004_us` | 4 MB | valid save | none | attract ("PRESS START BUTTON"), past the title |
| `saturn_no_cart` | `build/boot004_saturn` | none | valid save | `ERR4`: 10 (820-1,381) | the English no-cart warning |
| `saturn_no_space` | `build/boot004_saturn` | 4 MB | 18 blocks free | `ERR3`: 10 (1,434-1,996) | the English no-free-space warning |
| `saturn_normal` | `build/boot004_saturn` | 4 MB | valid save | none | the CAPCOM logo (window closed before the title) |

"Matching exactly" means equal, pixel for pixel, to the built picture as the
game shows it (`tools.disc.boot_warnings.shown`). The user's report:
"done", with nothing wrong.

- **After a button:** the damaged-save and no-free-space recordings end on
  the warning, so the game going on after a button was not recorded in this
  check; it was in `EXP-0053` (the same code, Japanese pictures).
- **The Saturn-names normal boot** passed the boot check (the CAPCOM logo
  follows it) but was closed before the title; `EXP-0056`'s scripted cold
  boot of the same image reached the attract fight, equal to the image
  without the warnings.

## The Regression References

`data/regression/references.json` gained `boot_warnings_us_v4` (Track 01
`e8c9cc4f…3ef4`) and `boot_warnings_saturn_v4` (`f53d2378…2280`), each
with `"boot_warnings": true` and its 25 changed files.

```bash
./invenv.sh python -m tools.disc.regression --report docs/regression_report.md
```

The result is in "Actual Result" below.

## Actual Result

- **Play check:** the table above.
- **Regression:** all nine references match: `ryu_v2`, `ryu_ken_v3`,
  `roster_v3`, `nash_ending_v4`, `roster_endings_v4`, `names_us_v4`,
  `names_saturn_v4`, `boot_warnings_us_v4`, `boot_warnings_saturn_v4`
  (`docs/regression_report.md`).
- **Coverage:** `docs/coverage_exceptions.md`, "Boot warnings".
- **README:** both build commands with `--boot-warnings`, American first;
  the boot warnings removed from "Still Japanese".

## Conclusion

**CONFIRMED:** the user saw the English no-cart warning on both images, the
damaged-save warning on the American image and the no-free-space warning on
the Saturn-names image, each exactly as built, and both normal boots passed
the boot check without a warning.

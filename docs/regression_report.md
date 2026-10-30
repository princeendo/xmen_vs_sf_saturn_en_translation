# Regression Report

Every confirmed English build is rebuilt from the untouched source by
`tools.disc.regression`, and its hashes are compared with
`data/regression/references.json` (`RE-011`). This file is written by
the script with `--report`; the last run is below.

## References

| Name | Experiment | Task | Specs | Patch version | Files | Track 01 |
| --- | --- | --- | --- | --- | --- | --- |
| `ryu_v2` | `EXP-0024` | `RE-003` | 1 | 2 | 2 | `1034b8d7…` |
| `ryu_ken_v3` | `EXP-0028` | `RE-007` | 2 | 3 | 3 | `b5dd07c2…` |
| `roster_v3` | `EXP-0032` | `RE-010` | 18 | 3 | 19 | `36672c5d…` |
| `nash_ending_v4` | `EXP-0041` | `END-008` | 19 | 4 | 20 | `2abe9771…` |
| `roster_endings_v4` | `EXP-0046` | `END-014` | 35 | 4 | 20 | `7bb8ab82…` |
| `names_us_v4` | `EXP-0051` | `LOC-005` | 35 | 4 | 20 | `441c9cfc…` |
| `names_saturn_v4` | `EXP-0052` | `LOC-006` | 35 | 4 | 20 | `b11c8cd9…` |

## Last Run

- Date: 2026-10-30T22:24:57+00:00
- Commit: `0772a90`
- Python: 3.13.13
- Source Track 01: `c904a386…` (matches)
- Program image: `1b1a5a26…` (matches)

| Reference | File | Expected | Built | Match |
| --- | --- | --- | --- | --- |
| `ryu_v2` | `MC09.SHP;1` | `507b1f46…` | `507b1f46…` | yes |
| `ryu_v2` | `MMPACK.PCA;1` | `9a7ab3e7…` | `9a7ab3e7…` | yes |
| `ryu_v2` | `Track 01` | `1034b8d7…` | `1034b8d7…` | yes |
| `ryu_ken_v3` | `MC09.SHP;1` | `507b1f46…` | `507b1f46…` | yes |
| `ryu_ken_v3` | `MC0A.SHP;1` | `585f9e99…` | `585f9e99…` | yes |
| `ryu_ken_v3` | `MMPACK.PCA;1` | `6d7e50a0…` | `6d7e50a0…` | yes |
| `ryu_ken_v3` | `Track 01` | `b5dd07c2…` | `b5dd07c2…` | yes |
| `roster_v3` | `MC00.SHP;1` | `4310e357…` | `4310e357…` | yes |
| `roster_v3` | `MC01.SHP;1` | `0a9f633b…` | `0a9f633b…` | yes |
| `roster_v3` | `MC02.SHP;1` | `b08caf80…` | `b08caf80…` | yes |
| `roster_v3` | `MC03.SHP;1` | `7142fd5f…` | `7142fd5f…` | yes |
| `roster_v3` | `MC04.SHP;1` | `55c1f8ce…` | `55c1f8ce…` | yes |
| `roster_v3` | `MC05.SHP;1` | `1ca63d0a…` | `1ca63d0a…` | yes |
| `roster_v3` | `MC06.SHP;1` | `df72d759…` | `df72d759…` | yes |
| `roster_v3` | `MC07.SHP;1` | `093bdd6f…` | `093bdd6f…` | yes |
| `roster_v3` | `MC08.SHP;1` | `7bb06fec…` | `7bb06fec…` | yes |
| `roster_v3` | `MC09.SHP;1` | `507b1f46…` | `507b1f46…` | yes |
| `roster_v3` | `MC0A.SHP;1` | `585f9e99…` | `585f9e99…` | yes |
| `roster_v3` | `MC0B.SHP;1` | `82dd72d1…` | `82dd72d1…` | yes |
| `roster_v3` | `MC0C.SHP;1` | `c8ba22eb…` | `c8ba22eb…` | yes |
| `roster_v3` | `MC0D.SHP;1` | `3c2b90a9…` | `3c2b90a9…` | yes |
| `roster_v3` | `MC0E.SHP;1` | `1f0037f9…` | `1f0037f9…` | yes |
| `roster_v3` | `MC0F.SHP;1` | `68ab8736…` | `68ab8736…` | yes |
| `roster_v3` | `MC10.SHP;1` | `26c448cb…` | `26c448cb…` | yes |
| `roster_v3` | `MC11.SHP;1` | `e6d4cc64…` | `e6d4cc64…` | yes |
| `roster_v3` | `MMPACK.PCA;1` | `4e81b64f…` | `4e81b64f…` | yes |
| `roster_v3` | `Track 01` | `36672c5d…` | `36672c5d…` | yes |
| `nash_ending_v4` | `MC00.SHP;1` | `4310e357…` | `4310e357…` | yes |
| `nash_ending_v4` | `MC01.SHP;1` | `0a9f633b…` | `0a9f633b…` | yes |
| `nash_ending_v4` | `MC02.SHP;1` | `b08caf80…` | `b08caf80…` | yes |
| `nash_ending_v4` | `MC03.SHP;1` | `7142fd5f…` | `7142fd5f…` | yes |
| `nash_ending_v4` | `MC04.SHP;1` | `55c1f8ce…` | `55c1f8ce…` | yes |
| `nash_ending_v4` | `MC05.SHP;1` | `1ca63d0a…` | `1ca63d0a…` | yes |
| `nash_ending_v4` | `MC06.SHP;1` | `df72d759…` | `df72d759…` | yes |
| `nash_ending_v4` | `MC07.SHP;1` | `093bdd6f…` | `093bdd6f…` | yes |
| `nash_ending_v4` | `MC08.SHP;1` | `7bb06fec…` | `7bb06fec…` | yes |
| `nash_ending_v4` | `MC09.SHP;1` | `507b1f46…` | `507b1f46…` | yes |
| `nash_ending_v4` | `MC0A.SHP;1` | `585f9e99…` | `585f9e99…` | yes |
| `nash_ending_v4` | `MC0B.SHP;1` | `82dd72d1…` | `82dd72d1…` | yes |
| `nash_ending_v4` | `MC0C.SHP;1` | `c8ba22eb…` | `c8ba22eb…` | yes |
| `nash_ending_v4` | `MC0D.SHP;1` | `3c2b90a9…` | `3c2b90a9…` | yes |
| `nash_ending_v4` | `MC0E.SHP;1` | `1f0037f9…` | `1f0037f9…` | yes |
| `nash_ending_v4` | `MC0F.SHP;1` | `68ab8736…` | `68ab8736…` | yes |
| `nash_ending_v4` | `MC10.SHP;1` | `d97633a6…` | `d97633a6…` | yes |
| `nash_ending_v4` | `MC11.SHP;1` | `e6d4cc64…` | `e6d4cc64…` | yes |
| `nash_ending_v4` | `MMPACK.PCA;1` | `276d534c…` | `276d534c…` | yes |
| `nash_ending_v4` | `MCED.SHP;1` | `cca9332d…` | `cca9332d…` | yes |
| `nash_ending_v4` | `Track 01` | `2abe9771…` | `2abe9771…` | yes |
| `roster_endings_v4` | `MC00.SHP;1` | `12367af4…` | `12367af4…` | yes |
| `roster_endings_v4` | `MC01.SHP;1` | `3f5e7ab4…` | `3f5e7ab4…` | yes |
| `roster_endings_v4` | `MC02.SHP;1` | `a608e360…` | `a608e360…` | yes |
| `roster_endings_v4` | `MC03.SHP;1` | `fe4b9d82…` | `fe4b9d82…` | yes |
| `roster_endings_v4` | `MC04.SHP;1` | `49233397…` | `49233397…` | yes |
| `roster_endings_v4` | `MC05.SHP;1` | `02179ea7…` | `02179ea7…` | yes |
| `roster_endings_v4` | `MC06.SHP;1` | `89fa13f2…` | `89fa13f2…` | yes |
| `roster_endings_v4` | `MC07.SHP;1` | `b2776f78…` | `b2776f78…` | yes |
| `roster_endings_v4` | `MC08.SHP;1` | `7bb06fec…` | `7bb06fec…` | yes |
| `roster_endings_v4` | `MC09.SHP;1` | `f9c524a5…` | `f9c524a5…` | yes |
| `roster_endings_v4` | `MC0A.SHP;1` | `4a8aafea…` | `4a8aafea…` | yes |
| `roster_endings_v4` | `MC0B.SHP;1` | `76c6c033…` | `76c6c033…` | yes |
| `roster_endings_v4` | `MC0C.SHP;1` | `284c9667…` | `284c9667…` | yes |
| `roster_endings_v4` | `MC0D.SHP;1` | `2a3ae96e…` | `2a3ae96e…` | yes |
| `roster_endings_v4` | `MC0E.SHP;1` | `35daca66…` | `35daca66…` | yes |
| `roster_endings_v4` | `MC0F.SHP;1` | `983aca7b…` | `983aca7b…` | yes |
| `roster_endings_v4` | `MC10.SHP;1` | `d97633a6…` | `d97633a6…` | yes |
| `roster_endings_v4` | `MC11.SHP;1` | `736aab3d…` | `736aab3d…` | yes |
| `roster_endings_v4` | `MCED.SHP;1` | `b37c3a64…` | `b37c3a64…` | yes |
| `roster_endings_v4` | `MMPACK.PCA;1` | `36179171…` | `36179171…` | yes |
| `roster_endings_v4` | `Track 01` | `7bb8ab82…` | `7bb8ab82…` | yes |
| `names_us_v4` | `MC00.SHP;1` | `12367af4…` | `12367af4…` | yes |
| `names_us_v4` | `MC01.SHP;1` | `3f5e7ab4…` | `3f5e7ab4…` | yes |
| `names_us_v4` | `MC02.SHP;1` | `a608e360…` | `a608e360…` | yes |
| `names_us_v4` | `MC03.SHP;1` | `fe4b9d82…` | `fe4b9d82…` | yes |
| `names_us_v4` | `MC04.SHP;1` | `49233397…` | `49233397…` | yes |
| `names_us_v4` | `MC05.SHP;1` | `02179ea7…` | `02179ea7…` | yes |
| `names_us_v4` | `MC06.SHP;1` | `89fa13f2…` | `89fa13f2…` | yes |
| `names_us_v4` | `MC07.SHP;1` | `b2776f78…` | `b2776f78…` | yes |
| `names_us_v4` | `MC08.SHP;1` | `7bb06fec…` | `7bb06fec…` | yes |
| `names_us_v4` | `MC09.SHP;1` | `f9c524a5…` | `f9c524a5…` | yes |
| `names_us_v4` | `MC0A.SHP;1` | `4a8aafea…` | `4a8aafea…` | yes |
| `names_us_v4` | `MC0B.SHP;1` | `76c6c033…` | `76c6c033…` | yes |
| `names_us_v4` | `MC0C.SHP;1` | `284c9667…` | `284c9667…` | yes |
| `names_us_v4` | `MC0D.SHP;1` | `2a3ae96e…` | `2a3ae96e…` | yes |
| `names_us_v4` | `MC0E.SHP;1` | `35daca66…` | `35daca66…` | yes |
| `names_us_v4` | `MC0F.SHP;1` | `983aca7b…` | `983aca7b…` | yes |
| `names_us_v4` | `MC10.SHP;1` | `d97633a6…` | `d97633a6…` | yes |
| `names_us_v4` | `MC11.SHP;1` | `736aab3d…` | `736aab3d…` | yes |
| `names_us_v4` | `MCED.SHP;1` | `b37c3a64…` | `b37c3a64…` | yes |
| `names_us_v4` | `MMPACK.PCA;1` | `b5b7927c…` | `b5b7927c…` | yes |
| `names_us_v4` | `Track 01` | `441c9cfc…` | `441c9cfc…` | yes |
| `names_saturn_v4` | `MC00.SHP;1` | `12367af4…` | `12367af4…` | yes |
| `names_saturn_v4` | `MC01.SHP;1` | `3f5e7ab4…` | `3f5e7ab4…` | yes |
| `names_saturn_v4` | `MC02.SHP;1` | `a608e360…` | `a608e360…` | yes |
| `names_saturn_v4` | `MC03.SHP;1` | `fe4b9d82…` | `fe4b9d82…` | yes |
| `names_saturn_v4` | `MC04.SHP;1` | `49233397…` | `49233397…` | yes |
| `names_saturn_v4` | `MC05.SHP;1` | `02179ea7…` | `02179ea7…` | yes |
| `names_saturn_v4` | `MC06.SHP;1` | `89fa13f2…` | `89fa13f2…` | yes |
| `names_saturn_v4` | `MC07.SHP;1` | `b2776f78…` | `b2776f78…` | yes |
| `names_saturn_v4` | `MC08.SHP;1` | `7bb06fec…` | `7bb06fec…` | yes |
| `names_saturn_v4` | `MC09.SHP;1` | `f9c524a5…` | `f9c524a5…` | yes |
| `names_saturn_v4` | `MC0A.SHP;1` | `4a8aafea…` | `4a8aafea…` | yes |
| `names_saturn_v4` | `MC0B.SHP;1` | `76c6c033…` | `76c6c033…` | yes |
| `names_saturn_v4` | `MC0C.SHP;1` | `284c9667…` | `284c9667…` | yes |
| `names_saturn_v4` | `MC0D.SHP;1` | `2a3ae96e…` | `2a3ae96e…` | yes |
| `names_saturn_v4` | `MC0E.SHP;1` | `8ac63fff…` | `8ac63fff…` | yes |
| `names_saturn_v4` | `MC0F.SHP;1` | `983aca7b…` | `983aca7b…` | yes |
| `names_saturn_v4` | `MC10.SHP;1` | `15143957…` | `15143957…` | yes |
| `names_saturn_v4` | `MC11.SHP;1` | `b07c60ba…` | `b07c60ba…` | yes |
| `names_saturn_v4` | `MCED.SHP;1` | `6184f150…` | `6184f150…` | yes |
| `names_saturn_v4` | `MMPACK.PCA;1` | `36179171…` | `36179171…` | yes |
| `names_saturn_v4` | `Track 01` | `b11c8cd9…` | `b11c8cd9…` | yes |

Result: all references match.

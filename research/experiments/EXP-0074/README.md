# EXP-0074 (Release): The Disc Header RetroAchievements Hashes

Task: RA-001
Status: DONE (2026-11-02)
Confidence: CONFIRMED for the 0.1.0 image and the rcheevos revision read;
whether RetroAchievements lists this hash, and whether its achievements
still work with the patch, is not tested

## Observation

The user asked what it would take for the translation to be detected by
RetroAchievements. The rcheevos library (`RetroAchievements/rcheevos`,
branch `develop`, commit `0aea57b03b822cd7982fc31e92df6913cc909c01`,
2026-10-30), `src/hash/rc_hash_disc.c`, function `rc_hash_sega_cd`, hashes a
Saturn disc as the MD5 of the first 512 bytes of track 1, sector 0 (user
data), after checking that they start `SEGA SEGASATURN `. Nothing else on
the disc is hashed.

## Hypothesis

The English builds never write sector 0 of track 01, so the 0.1.0 image has
the untouched image's RetroAchievements hash.

## Controlled Change

None to the image. The release tools `tools.disc.make_patch` and
`tools.disc.make_ssp` gained a check: they refuse a built track 01 whose
first 512 bytes of sector 0 differ from the source (`ra_header`).

## Prediction

Equal 512-byte headers and MD5s for the source and the 0.1.0 image.

## Inputs and Provenance

- Source track 01: `local/disc_images/xmvsf_saturn_jp_3m/`, SHA-256
  `c904a38644964e91e6dc0ee93ea41e921ca673efe708a8e2658207c736bfda70`
  (`references/saturn_jp/README.md`).
- 0.1.0 image: `build/regression/name_toggle_v4/image/`, track 01 SHA-256
  `68813e93108f433a9b64e4b2e420baebbabb136634c2b927b938f56addf9ad1a`
  (regression reference `name_toggle_v4`, `release/name_toggle.json`).

## Tools and Environment

Python 3.13.13 through `./invenv.sh`; macOS `dd`, `md5`, `cmp`; `gh api`
to read the rcheevos source.

## Procedure

```bash
./invenv.sh python -c "
from pathlib import Path
from tools.disc.make_patch import TRACK01, ra_hash, ra_header
s = Path('local/disc_images/xmvsf_saturn_jp_3m')/TRACK01
b = Path('build/regression/name_toggle_v4/image')/TRACK01
print(ra_hash(s), ra_hash(b), ra_header(s) == ra_header(b))"
```

Independently, with system tools: `dd bs=1 skip=16 count=512 | md5` on each
track 01 (Mode 1/2352, so user data starts at byte 16), and `cmp` of the
first 16 raw sectors (the 32 KiB system area).

## Actual Result

- Both headers: MD5 `5bfb1a925a03cc5bd6a7c04a38d31727`, equal bytes. The
  header reads `SEGA SEGASATURN`, maker `SEGA TP T-12`, product
  `T-1226G`, version `V1.002`, date `19970925`, `CD-1/1`, area `J`, title
  `X-MEN VS STREET FIGHTER`.
- The first 16 raw sectors of the two track 01 files are identical.
- `tests/unit/test_disc_make_patch.py`: both tools exit with the
  RetroAchievements error on a synthetic image whose header differs, and
  `ra_header` ignores everything past byte 512 of sector 0.

## Conclusion

Prediction met. RetroAchievements cannot tell the 0.1.0 image from the
untouched disc. The xdelta and SSP patches give that image, so they keep
the hash too, and the check stops a later build from changing it unnoticed.

## Uncertainty and Alternatives

- The RetroAchievements site (game 14567, the Saturn X-Men vs. Street
  Fighter) showed a bot check to the browser and was not read. Whether
  `5bfb1a92…` is linked to that game is unknown.
- Achievements test RAM addresses. Where the patch changes code or data in
  RAM (fonts, records, the toggle's code), an achievement reading those
  addresses could behave differently. Not tested.
- A later rcheevos revision could hash differently.

## Reproduction

The Procedure above, and
`./invenv.sh python -m pytest -q tests/unit/test_disc_make_patch.py`.

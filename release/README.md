# Release Patch: X-Men vs. Street Fighter (Saturn) in English

This folder describes the English patch for the Japanese Sega Saturn release of
**X-Men vs. Street Fighter**: what it changes, how to apply it, and how to
rebuild it from this repository.

**The patch files are not in the repository.** Their bytes include
game-derived data, which this project never commits (`AGENTS.md` rule 21).
They are published as GitHub Release assets.

[`name_toggle.json`](name_toggle.json) and
[`name_toggle.ssp.json`](name_toggle.ssp.json) are the release records:
hashes, sizes, tool versions and flags (metadata only).

## What the Patch Changes

One image, built with `build_english --names toggle` (regression reference
`name_toggle_v4`):

- **Win quotes and endings:** every character's, in the official US arcade
  English, shown in the game's own English layout.
- **Apocalypse's boss boxes and Alpha Chun-Li:** in English (the boxes are a
  new translation; the US arcade skips them).
- **Attract captions, continue hints, the "no challengers" sign:** the US
  arcade's English.
- **Boot warnings** (cart and save messages): new English pictures.
- **Character names:** a NAMES row in Options switches between the American
  names (U.S., the default: BISON, AKUMA, CHARLIE) and the Saturn's (SATURN:
  VEGA, GOUKI, NASH) on the select screen, VS screen, life bars, win banners,
  name calls, text and ending labels. The choice is kept with BACK UP: SAVE,
  like the game's other settings.
- **COMBO GAUGE:** the game's hidden COMBO GAGE row stays, as an eleventh
  row spelled COMBO GAUGE; it shows only when the game unlocks it.

Known limits are listed in [`docs/coverage_exceptions.md`](../docs/coverage_exceptions.md).
The main ones: the QSound notice after the credits keeps one Japanese
trademark line; versus mode beyond its select screen was not surveyed.

## Apply the Patch

### You need

1. **The original disc image**, as BIN/CUE with 41 tracks: Redump disc 62395
   (T-1227G, version 1.002). Only track 01 is patched, and it must be the
   original:

   | Component | Size (bytes) | SHA-256 |
   | --- | ---: | --- |
   | `X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin` | 169127616 | `c904a38644964e91e6dc0ee93ea41e921ca673efe708a8e2658207c736bfda70` |
   | `X-Men vs. Street Fighter (Japan) (3M).cue` | 5417 | `4b063eed002a5dfe2f634b22ff745870ede0ab694a39402db46e5413e13531e3` |

   Tracks 02-41 are listed in `references/saturn_jp/README.md`. Redump's two
   cart-bundle discs (1745, 62394) have the same track 01 and different audio
   tracks, so the patch applies to them too; keep your own audio tracks.
2. **The 4 MB RAM cartridge** (in Mednafen, `ss.cart auto`).
3. **A patcher:** xdelta3, or a Sega Saturn Patcher (`.ssp`) program.

### xdelta

```bash
xdelta3 -d -s "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin" \
  xmvsf_saturn_en_toggle.Track01.xdelta "Track 01 patched.bin"
```

1. Run it in the folder with the original image (xdelta3 3.2.2 is tested;
   the patch is plain VCDIFF, no secondary compression, 16 MiB window).
2. The result's SHA-256 is given in the zip's `README.txt` (the "patched
   track 01" line) and in [`name_toggle.json`](name_toggle.json).
3. Replace track 01 with it under its original filename, so the CUE still
   finds it. Keep tracks 02-41 and the CUE.

### Sega Saturn Patcher (.ssp)

- **Tested: [saturn-patcher-egui](https://github.com/ralfguth/saturn-patcher-egui)**
  (commit `20837e06`). It patches a copy of track 01 in place and checks
  each original file's MD5 first:

  ```bash
  cp "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin" "Track 01 patched.bin"
  saturn-patcher xmvsf_saturn_en_toggle.ssp "Track 01 patched.bin"
  ```

  The result equals the xdelta result. Continue from step 3 above.
- **The official Sega Saturn Patcher:** not tried for this game. For MSHvSF
  its rebuilt disc differed from the xdelta result in the disc-length field
  and the audio layout, so its track 01 will not match the hashes.

## Rebuild the Patch from This Repository

You supply the original image (`local/disc_images/xmvsf_saturn_jp_3m/`), the
US arcade program (`local/ref003/xmvsfu-68k.bin`) and the arcade caption art
(`local/cap002/art`); see the top-level [`README.md`](../README.md). Then:

```bash
# 1. Rebuild every reference and check its hashes (all must match).
./invenv.sh python -m tools.disc.regression --keep --only name_toggle_v4
# 2. The patches, checked against the reference.
./invenv.sh python -m tools.disc.make_patch --built-dir build/regression/name_toggle_v4/image \
  --reference name_toggle_v4 --stem xmvsf_saturn_en_toggle --out-dir build/release/toggle \
  --record release/name_toggle.json
./invenv.sh python -m tools.disc.make_ssp --built-dir build/regression/name_toggle_v4/image \
  --reference name_toggle_v4 --stem xmvsf_saturn_en_toggle --release-version 0.1.0 \
  --description "English win quotes, endings, captions, hints and UI; American or Saturn names, chosen in Options (NAMES)." \
  --out-dir build/release/toggle --record release/name_toggle.ssp.json
# 3. The zips, and a check that applies every patch from them.
./invenv.sh python research/experiments/EXP-0071/make_zips.py 0.1.0 build/release/v0.1.0
bash research/experiments/EXP-0071/check_zips.sh 0.1.0 build/release/v0.1.0 local/rel/v0.1.0-check
```

Every step refuses a source or build whose hashes differ from the records.
The full procedure for publishing is [`RELEASING.md`](RELEASING.md).

# EXP-0031 (M5): Every Roster File Fits Its Sectors

Task: RE-009
Status: DONE
Confidence: CONFIRMED

## Observation

The build writes a character's 8 English records (800 bytes) over the start
of its 1,216-byte Japanese table and re-encodes the MC file at its original
size. Its stream must end in the file's last sector (`tools.disc.build_english`,
`EXP-0024`). This fitted Ryu's `MC09` and Ken's `MC0A` (`EXP-0024`,
`EXP-0028`). The open question "Will longer (English) quote files fit 11
sectors?" (`docs/known_unknowns.md`) was unanswered for the other 16 roster
files.

## Hypothesis

For every roster file, the English-edited content re-encodes, with the
build's encoder, to no more than the original size. The rebuilt file then
keeps its size and sector count and changes nothing outside the English
area.

## Controlled Change

Per file, in memory only, one change: the slot's English records 0-7 are
written over the start of the table found by the census (`EXP-0029`). The
file is rebuilt by the build's own function (`build_mc`). No image is built.

## Prediction

- Each file's natural re-encoded size is at most its original size.
- `build_mc` succeeds and gives a file of the original size whose stream
  ends in the last sector.
- The rebuilt file decodes to the original decoded file outside the 800
  English bytes, and to the English bytes inside.
- For Ryu and Ken, the rebuilt files equal `EXP-0028`'s (`507b1f46…`,
  `585f9e99…`).

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| MC files | Untouched Track 01 (`c904a386…`), each checked against `references/saturn_jp/iso_listing.json` |
| English | US program `local/ref003/xmvsfu-68k.bin` (`EXP-0008`), table `0x17E1E8`, records 0-7 of each slot |
| Roster and offsets | `data/text/m5_roster.json` (`RE-008`), from `data/text/slot_census.json` (`EXP-0029`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`fit_sectors.py`](fit_sectors.py) | Per file: English bytes (recompile-checked), natural sizes, `build_mc` rebuild, decode comparison; writes `data/text/m5_sector_fit.json` |
| `tools/disc/build_english.py` (`build_mc`), `tools/disc/prs.py` | The build's re-encode (lazy matching; leading literals when the stream would end before the last sector) |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0031/fit_sectors.py data/text/m5_sector_fit.json
```

It runs in about 2.5 minutes. A second run must be byte-identical.

## Actual Result

All 18 files fit (exit 0).

| Slot | Character | File | Size | Sectors | English, re-encoded | Margin | Original, re-encoded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Wolverine | `MC00.SHP` | 31,838 | 16 | 31,054 | 784 | 31,147 |
| 1 | Cyclops | `MC01.SHP` | 35,411 | 18 | 34,925 | 486 | 34,897 |
| 2 | Storm | `MC02.SHP` | 28,822 | 15 | 28,117 | 705 | 28,192 |
| 3 | Rogue | `MC03.SHP` | 33,591 | 17 | 32,880 | 711 | 32,927 |
| 4 | Gambit | `MC04.SHP` | 29,086 | 15 | 28,453 | 633 | 28,536 |
| 5 | Sabretooth | `MC05.SHP` | 28,746 | 15 | 28,159 | 587 | 28,186 |
| 6 | Juggernaut | `MC06.SHP` | 28,820 | 15 | 28,282 | 538 | 28,303 |
| 7 | Magneto | `MC07.SHP` | 34,961 | 18 | 34,179 | 782 | 34,224 |
| 8 | Apocalypse | `MC08.SHP` | 29,667 | 15 | 29,492 | 175 | 29,453 |
| 9 | Ryu | `MC09.SHP` | 20,686 | 11 | 20,267 | 419 | 20,197 |
| 10 | Ken | `MC0A.SHP` | 23,258 | 12 | 22,663 | 595 | 22,753 |
| 11 | Chun-Li | `MC0B.SHP` | 33,270 | 17 | 32,094 | 1,176 | 32,054 |
| 12 | Dhalsim | `MC0C.SHP` | 27,001 | 14 | 26,422 | 579 | 26,432 |
| 13 | Zangief | `MC0D.SHP` | 28,016 | 14 | 27,390 | 626 | 27,477 |
| 14 | Vega | `MC0E.SHP` | 24,759 | 13 | 24,415 | 344 | 24,371 |
| 15 | Gouki | `MC0F.SHP` | 25,139 | 13 | 24,592 | 547 | 24,512 |
| 16 | Nash | `MC10.SHP` | 23,913 | 12 | 23,242 | 671 | 23,438 |
| 17 | Cammy | `MC11.SHP` | 28,494 | 14 | 28,006 | 488 | 27,924 |

- **Margins:** 175 bytes (Apocalypse) to 1,176 bytes (Chun-Li). Sizes are
  in bytes, with the 4-byte header and no padding. The margin is the
  original size minus the English re-encoded size.
- **Rebuilt files:** all 18 keep their original size, and their streams
  end in the last sector. Each decodes to the English bytes in place and
  to the original decoded file everywhere else.
- **Encoder:** it re-encodes every original file smaller than the original
  (by 0.7-3.7 %). The English edit grows the stream for 7 files (by 28-82
  bytes) and shrinks it for 11.
- **Ryu and Ken:** the rebuilt `MC09` (`507b1f46…`) and `MC0A`
  (`585f9e99…`) equal `EXP-0028`'s, and their English bytes equal its
  `english_sha256` values. So this check runs the build's own path.
- **Reproduction:** a second run was byte-identical.

## Conclusion

**CONFIRMED.** Every M5 roster file, with its 8 official English records in
place, re-encodes within its original size, with its stream in its last
sector. Outside the English area the file is unchanged. No option needs
choosing before `RE-010`. Apocalypse's `MC08` has the least room, 175 bytes.

## Uncertainty and Alternatives

- **Grammar fixes:** these margins are for the official English as
  written. An opt-in grammar fix (none is planned) would need a recheck.
- **Real hardware:** not tested. The streams decode with the project's
  decoder and, for Ryu and Ken, in the game.

## Reproduction

Run the procedure. Expect exit 0, the table above, and
`data/text/m5_sector_fit.json` byte for byte.

# EXP-0029 (M5): Census of the Quote Files Against the Arcade Slots

Task: RE-005
Status: DONE
Confidence: CONFIRMED (file contents and one more load trace); details below

## Observation

The data track holds 19 quote files: `MC00`-`MC11` and `MCED`. "`MCxx` holds
arcade slot `xx`" is CONFIRMED for slots 9 and 10 by load traces (`EXP-0017`,
`EXP-0025`). It is SUPPORTED for 3, 0x0B, 0x0F and 0x11, whose tables were
found in RAM (`EXP-0025`). The arcade has 19 win-quote slots
(`EXP-0008`).

## Hypothesis

Each `MCxx` (xx = 0x00-0x11) holds arcade slot `xx`'s 16 Japanese win-quote
records byte for byte, and the game loads it when that character is picked.
`MCED` and arcade slot 18 do not fit this pattern.

## Controlled Change

None to the game. The static census reads every quote file from the
untouched track and the arcade program. The live check picks one untraced
character (Cyclops, `MC01`) from a session state, with a write breakpoint
on where his table should load. The control is the same state with no
input.

## Prediction

- **Static:** each of `MC00`-`MC11` contains exactly one 16-record table,
  equal to the arcade Japanese records of slot `xx`. `MCED` contains none.
- **Live:** picking Cyclops as the second member halts in the loader
  (`0x0600D124`, as in `EXP-0025`). The halt has R5 = 35,411 (`0x8A53`,
  `MC01`'s size), base `0x060B0000` and R12 = `0x060B3C60` (base + table
  offset `0x3C60`). The control does not halt.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Quote files | Untouched Track 01 (`c904a386…`), each checked against `references/saturn_jp/iso_listing.json` |
| Arcade program | `local/ref003/xmvsfu-68k.bin` (`EXP-0008`), SHA-256 `1b1a5a26…`. Japanese quotes `0x17E19C`, English `0x17E1E8`, Japanese endings `0x17E2CC`, name list `0x503E4` |
| Pick state | `local/re004/session/states/f00003193.mcs` (`EXP-0025` user session; Ken picked, partner cursor on Cyclops in screenshots 3083-3193), SHA-256 `87f1de8b…` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`census.py`](census.py) | Static census of slots and files; writes `data/text/slot_census.json` |
| [`catch_pick.py`](catch_pick.py) | Halt on the first write to a table range at a pick (generalized from `EXP-0025`'s `catch_loader.py`) |

Mednafen: the patched agent build (`EMU-021`), scratch home
`local/mednafen_keys` (pad A on K).

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0029/census.py data/text/slot_census.json
S=local/re004/session/states/f00003193.mcs
R=060B3C60-060B4333   # Cyclops: 16 quote + 7 ending records at base 0x060B0000 + 0x3C60
./invenv.sh python research/experiments/EXP-0029/catch_pick.py $S $R local/re005/catch_control --control
./invenv.sh python research/experiments/EXP-0029/catch_pick.py $S $R local/re005/catch_trial --wait 90
./invenv.sh python research/experiments/EXP-0029/catch_pick.py $S $R local/re005/catch_trial2 --wait 90
```

The checks of the file in RAM after each halt are in
`research_log.md` (`SESSION-0042`).

## Actual Result

### Files and slots

Every quote stream decodes, and every stream ends in its file's last sector.

| Slot | Name list | File | Size | Sectors | Table offset | Ending records after | English records |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Wolverine | `MC00.SHP` | 31,838 | 16 | `0x393c` | 7 | 9 |
| 1 | Cyclops | `MC01.SHP` | 35,411 | 18 | `0x3c60` | 7 | 9 |
| 2 | Storm | `MC02.SHP` | 28,822 | 15 | `0x40d4` | 7 | 9 |
| 3 | Rogue | `MC03.SHP` | 33,591 | 17 | `0x3f94` | 8 | 9 |
| 4 | Gambit | `MC04.SHP` | 29,086 | 15 | `0x34b4` | 6 | 9 |
| 5 | Sabretooth | `MC05.SHP` | 28,746 | 15 | `0x3460` | 4 | 9 |
| 6 | Juggernaut | `MC06.SHP` | 28,820 | 15 | `0x3438` | 9 | 9 |
| 7 | Magneto | `MC07.SHP` | 34,961 | 18 | `0x447c` | 4 | 9 |
| 8 | Apocalypse | `MC08.SHP` | 29,667 | 15 | `0xaa0` | 4 | 8 |
| 9 | Ryu | `MC09.SHP` | 20,686 | 11 | `0x25d8` | 6 | 9 |
| 10 | Ken | `MC0A.SHP` | 23,258 | 12 | `0x2a4c` | 5 | 9 |
| 11 | Chun-Li | `MC0B.SHP` | 33,270 | 17 | `0x349c` | 7 | 9 |
| 12 | Dhalsim | `MC0C.SHP` | 27,001 | 14 | `0x3048` | 4 | 9 |
| 13 | Zangief | `MC0D.SHP` | 28,016 | 14 | `0x2d68` | 4 | 9 |
| 14 | Vega | `MC0E.SHP` | 24,759 | 13 | `0x221c` | 4 | 9 |
| 15 | Gouki | `MC0F.SHP` | 25,139 | 13 | `0x2e0c` | 4 | 9 |
| 16 | Nash | `MC10.SHP` | 23,913 | 12 | `0x2a00` | 6 | 9 |
| 17 | Cammy | `MC11.SHP` | 28,494 | 14 | `0x2f1c` | 12 | 9 |
| 18 | (list: Bison) | none of its own | | | slot 11's table (alias) | | 9 (slot 11's, alias) |
| — | — | `MCED.SHP` | 21,203 | 11 | none | — | — |

- **Name list:** its first entry is blank, so slot `s` is entry `s + 1`.
  Names agree with every slot established by other evidence: 0 and 12
  (Dhalsim's CPU win, `EXP-0009`), 1 (this experiment), and 3, 9, 10, 11,
  15 and 17 (`EXP-0013`, `EXP-0025`).
- **Ending records after** counts the Saturn records after the 16 quotes
  that equal the arcade's Japanese ending records for that slot. They were
  counted only, not read (rule 23).
- **Japanese pointer order:** slot 15's records lie after slot 16's in the
  arcade program (`0x182FFC` and `0x182B3C`). The files and the English
  table keep slot order.

### Irregular cases

| Case | Evidence |
| --- | --- |
| `MCED.SHP` | It decodes (39,064 bytes). It holds no arcade Japanese quote record and no Japanese ending record of any slot. Three short runs of text-like codes sit at decoded `0x654E` (42 codes), `0x65CC` (40) and `0x663E` (50); they were not decoded. Its role and its loader are UNKNOWN. |
| Slot 18 | Its Japanese and English pointers both equal slot 11's (Chun-Li). No `MC12` exists. Name-list entry 19 is "Bison", but entries after Cammy run Bison, Akuma, Charlie, Jubilee, …, which are not slots. Which character, if any, uses slot 18 is UNKNOWN. |
| Slot 8 (Apocalypse) | 8 English records instead of 9. Records 0-7 exist, so `k mod 8` has a record for every draw. The table is unusually early in its file (`0xAA0`). |

### Live load (Cyclops, `MC01`)

| Run | Result |
| --- | --- |
| Control (no input, 120 frames) | No event |
| Trial | Halt at `0x0600D124` (frame 308). R5 = R9 = `0x8A53`, R6 = R10 = `0x060B0000`, R12 = `0x060B3C60`, PR = `0x0600D11A` |
| Repeat | Halt at frame 315, with identical registers |

- **Size:** `0x8A53` (35,411) is the size of `MC01.SHP` only, among all
  files on the track.
- **RAM:** in both trials, WRAM-H `0x060B0000`-`0x060B3C5F` equals decoded
  `MC01` up to the table, byte for byte.
- **The two trials' dumps** differ in 6,252 WRAM-H bytes, none inside the
  file region. This comes from the 7-frame difference in when the key took
  effect.

## Conclusion

**CONFIRMED.**

- Each of the 18 files `MC00`-`MC11` holds exactly one 16-record table,
  equal byte for byte to arcade Japanese slot `xx`'s win quotes, followed by
  4-12 of that slot's Japanese ending records.
- The game loads `MCxx` for the character in slot `xx`. This is now traced
  for slots 1 (second member), 9 and 10.
- Slots 0-17 have their own English records: 9 each, but 8 for slot 8.
- Two cases are irregular: `MCED` (no quote records; role unknown) and
  slot 18 (an alias of slot 11 with no file of its own).

## Uncertainty and Alternatives

- **Loads not traced:** 15 of the 18 files are matched by content but not
  by a load trace. The census rules out any other file holding their
  tables.
- **CPU opponents:** whether a CPU opponent's file is the same `MCxx` was
  seen for Rogue, Chun-Li and Cammy (`EXP-0025`, RAM contents), not traced.
- **Slot 18 and `MCED`:** see above. Neither blocks an ordinary-character
  roster, but both are listed for `RE-008`.
- **Name list:** the names are labels from the arcade list. Slots not
  seen in play are named by list position only.

## Reproduction

Run the procedure. Expect `data/text/slot_census.json` to reproduce byte
for byte, a control with no event, and two trials halting at `0x0600D124`
with R5 = `0x8A53`.

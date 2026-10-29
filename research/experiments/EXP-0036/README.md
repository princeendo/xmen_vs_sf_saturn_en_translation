# EXP-0036 (M6): Where Nash's Ending Text Lives

Task: END-003
Status: IN_PROGRESS (the marker play check is pending)
Confidence: CONFIRMED for RAM, writer and file; the on-screen marker from
disc is not yet observed

## Observation

`EXP-0035` found that Nash's six ending pages are read from WRAM-L
`0x0024FEC0` + 76k. Those bytes equal decoded `MC10.SHP` records 16-21. That
match is static. It does not show which code put them there, or that a disc
edit reaches the screen.

## Hypothesis

`MC10.SHP` is loaded once, when Nash is picked, by the file loader that
loads the win quotes (`0x0600D124`, D-024), into the first-member buffer
`0x0024D000`. Nothing rewrites the ending records afterwards. So a same-size
edit of records 16-21 in `MC10.SHP` reaches the ending pages.

## Controlled Changes

| Run | Single change |
| --- | --- |
| `write_log.py` (`wlog1`) | None; write breakpoints (log) on the six records from `f00210163` (pre-boss) to frame 222,100 |
| `write_log.py` (`wlog_marker`) | Same, booting the marker image |
| `ram_write.py` | Record 18's first code `0x0AF4` → `0x09F2` in RAM, from `f00220917` (page 2) |
| `make_marker.py` | Decoded `MC10.SHP` offset `0x2EC0` (record 16, page 1), 8 bytes: `0bc30d760a0d0c66` → `09f20a2b0a0e0a92` (record 21's first four codes) |
| `pick_writer.py` | Nash picked from the select state `local/checkpoints/re004/f00002973.mcs`, booting the untouched image, then the marker image |

## Predictions

- No write to the records between the pre-boss checkpoint and the ending.
- The RAM write changes exactly page 3's first cell to the glyph for
  `0x09F2`.
- At the pick, every write to the records comes from `0x0600D124`, with
  R5 = MC10's size. The buffer equals the file plus the `EXP-0025`
  fix-ups, and on the marker image it holds the marker.
- In play on the marker image, page 1's first four cells show page 6's
  first four glyphs, and nothing else in the ending changes.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | Track 01 `c904a386…`; `MC10.SHP;1` `07bbfb41…cee6` (23,913 bytes, LSN 53,813, 12 sectors) |
| Marker file | `local/end003/marker/MC10.SHP` `026ab640…6df3`, same size; `changes.json` holds the 8 original and modified bytes |
| Marker image | `build/end003_marker/`, Track 01 `547359de…a27c`. All 12 `MC10` sectors (LSN 53,813-53,824) changed, nothing else. 71,908 sectors pass EDC/ECC (`tools.disc.sector`). |
| Checkpoints | `local/checkpoints/end001/` (`EXP-0034`); select state `local/checkpoints/re004/f00002973.mcs` (`EXP-0032`) |
| Arcade program | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` (census) |

## Tools

| Tool | Use |
| --- | --- |
| [`write_log.py`](write_log.py) | Write log on the records over a frame span, on any image |
| [`ram_write.py`](ram_write.py) | One-code RAM write before page 3; pixel diff and glyph check |
| [`make_marker.py`](make_marker.py) | The same-size marker `MC10.SHP` |
| `tools.disc.patch_image` | The marker image |
| [`pick_writer.py`](pick_writer.py) | Pick Nash (keys, as `EXP-0032`) with a write log on the records; buffer against the file plus fix-ups |
| [`census_endings.py`](census_endings.py) | Every roster file's ending records against the arcade's (`data/text/ending_census.json`) |

## Procedure

```bash
SRC=local/disc_images/xmvsf_saturn_jp_3m; T="X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
CUE="X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0036/write_log.py local/end003/wlog1 \
  local/checkpoints/end001/f00210163.mcs 222100
./invenv.sh python research/experiments/EXP-0036/ram_write.py local/end003/ramw1 local/ref007/saturn_files/FIX.PRS
./invenv.sh python research/experiments/EXP-0036/make_marker.py local/end003/marker
./invenv.sh python -m tools.disc.patch_image --source-dir $SRC --manifest references/saturn_jp/README.md \
  --track "$T" --file "MC10.SHP;1" --data local/end003/marker/MC10.SHP --out-dir build/end003_marker
./invenv.sh python -m tools.disc.sector "build/end003_marker/$T"
./invenv.sh python research/experiments/EXP-0036/write_log.py local/end003/wlog_marker \
  local/checkpoints/end001/f00210163.mcs 220700 "build/end003_marker/$CUE"
./invenv.sh python research/experiments/EXP-0036/pick_writer.py "$SRC/$CUE" \
  local/ref007/saturn_files/MC10.SHP local/end003/pick_orig2
./invenv.sh python research/experiments/EXP-0036/pick_writer.py "build/end003_marker/$CUE" \
  local/end003/marker/MC10.SHP local/end003/pick_marker
./invenv.sh python research/experiments/EXP-0036/census_endings.py data/text/ending_census.json
```

`pick_writer.py` brings Mednafen to the front to send keys. Its first run
(`pick_orig`) stopped because another window had the focus, and the key was
not sent. The script now retries.

## Actual Result

### No rewrite before the ending

- **`wlog1`** (untouched image, frames 210,163-222,100): 0 writes to the
  records, and they were unchanged at the end. That span covers the boss
  stage's loads, the partner fight and all six pages.
- **`wlog_marker`** (marker image, frames 210,163-220,700): 0 writes. The
  records still held the original bytes (`0bc30d76…`), so the game does not
  reload `MC10` from disc in that span.

### RAM write

From `f00220917`, record 18's first code was changed to `0x09F2`.

- **Screenshot:** 139 pixels differed from control at page 3 (frame
  221,112), all inside x 27-40, y 187-200, the first cell of the top row.
  At zoom, 何 became こ; the rest was unchanged.
- **VDP1:** the cell's character data equals the `FIX.PRS` glyph for
  `0x09F2`; in control it equals the glyph for `0x0AF4`.

### Writer and file

| Run | Writes to the records | Writer | Records after the pick | Buffer equals file plus fix-ups |
| --- | --- | --- | --- | --- |
| untouched image | 114 (longwords, 456 bytes) | all `0x0600D124`, R5 = `0x5D69` (23,913, MC10's size), R6 = `0x0024D000`, PR = `0x0600D11A` | `0bc30d76…` (= MC10) | yes, 263 fix-ups (109 at 2-byte alignment) |
| marker image | 114 | all `0x0600D124` | `09f20a2b0a0e0a92…` (= marker) | yes, against the marker file |

### Census (`data/text/ending_census.json`)

The ending offset is the quote table + `0x4C0` in every roster file.

| Slot | File | Saturn records | Arcade JP block | Arcade English |
| --- | --- | --- | --- | --- |
| 0 | `MC00` | 7 | 7 | 6 |
| 1 | `MC01` | 7 | 7 | 9 |
| 2 | `MC02` | 7 | 7 | 6 |
| 3 | `MC03` | 8 | 8 | 6 |
| 4 | `MC04` | 6 | 6 | 5 |
| 5 | `MC05` | 4 | 4 | 6 |
| 6 | `MC06` | 9 | 9 | 6 |
| 7 | `MC07` | 4 | 4 | 7 |
| 8 | `MC08` | 4 | 4 | 7 |
| 9 | `MC09` | 6 | 6 | 7 |
| 10 | `MC0A` | 5 | 5 | 4 |
| 11 | `MC0B` | 7 | 7 | 6 |
| 12 | `MC0C` | 4 | 4 | 6 |
| 13 | `MC0D` | 4 | 4 | 5 |
| 14 | `MC0E` | 4 | 4 | 5 |
| 15 | `MC0F` | 4 | 4 | 6 |
| 16 | `MC10` | 6 | 6 | 6 |
| 17 | `MC11` | 12 | ≤ 70 (no later pointer bounds it) | 13 |

- **Slots 0-16:** each file holds its slot's whole arcade Japanese ending
  block, in order, at table + `0x4C0`.
- **Slot 17 (Cammy):** 12 records match. The arcade block's end is not
  bounded by a pointer, so whether the arcade has more is open.
- **Slot 8 (Apocalypse):** the record after his 4 is still text-like (the
  heuristic in the script); no other file's is.
- **English counts:** they differ from the Japanese in 14 of 18 slots. That
  is `END-004`'s question.
- **Run-time lists:** the `EXP-0035` language-0 list pointed at table +
  `0x4C0` for all three loaded characters:
  - Nash `0x0024FEC0` = `0x0024D000` + `0x2A00` + `0x4C0`;
  - Ryu `0x060B2A98` = `0x060B0000` + `0x25D8` + `0x4C0`;
  - Apocalypse `0x060C1F60` = `0x060C1000` + `0xAA0` + `0x4C0`.

### Marker on screen

Pending: a user play session on the marker image, Nash first, to his
ending.

## Conclusion (so far)

**CONFIRMED:**

- Nash's ending records are loaded once, at the pick, by the file loader
  `0x0600D124`, from `MC10.SHP` into `0x0024D000` (records at `+0x2EC0`).
- Nothing writes them again before or during the ending.
- A RAM edit of a record changes exactly the predicted cell.
- A same-size disc edit reaches RAM through the same loader.

Every roster file keeps its slot's arcade Japanese ending block at table +
`0x4C0`. For slots 0-16 the whole block is there.

**Open:** the marker shown on screen from disc (the play check), and
Cammy's block end.

## Uncertainty and Alternatives

- **Pick to boss:** stages 1-7 were not watched with a write log. The play
  check on the marker image covers that span.
- **Second members and CPU:** they load into other buffers (WRAM-H
  `0x060B0000`, opponents `0x060C1000`). Only Nash first was tested for the
  ending.
- **The text-like heuristic** is a range test on codes, not a reading.

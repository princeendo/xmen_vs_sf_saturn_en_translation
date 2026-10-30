# EXP-0041 (M7): Nash's English Ending Records on Disc

Task: END-007
Status: DONE
Confidence: CONFIRMED

## Observation

Version 4 (`EXP-0040`, D-034) reads the English ending records at quote table
+ 800, after the 8 English win quotes. That space held Japanese quote
records 10.5-15 and the Japanese ending records. `END-007` must:

- show that nothing else reads those bytes once both parts are English;
- write the records with a spec;
- show that the file fits and loads.

## Hypothesis

`MC10.SHP` holds the 800 English win-quote bytes followed by the 600
English ending bytes at decoded `0x2A00`, and fits its 12 sectors. After a
pick, its RAM copy equals the file plus fix-ups. In a run from select to the
ending with the build's code, the bytes after the win quotes are read only
while the ending shows them.

## Changes

- **Spec:** `data/translations/nash_ending.json` (`make_spec.py`) holds the
  six English records' source addresses, SHA-256 and line lengths, taken
  from `nash_ending_pairing.json`. No text.
- **Build tool:** `tools.disc.build_english` takes ending specs
  (`"kind": "ending"`). They need `--patch-version 4` and a win-quote spec
  for the same slot, file and table. The tool then:
  - compiles the records like win quotes;
  - writes them right after the win quotes;
  - applies `patches_v4` to `MMPACK.PCA`;
  - re-encodes `MCED.SHP` with `mced_english_scripts`.

  6 new unit tests. Earlier builds (versions 2 and 3) are unchanged.
- **Image:** `build/m7_nash_ending`, from the untouched source:

  | File | Rebuilt SHA-256 | Change |
  | --- | --- | --- |
  | 18 `MCxx` (roster win quotes) | as `EXP-0032`, except `MC10` | — |
  | `MC10.SHP` | `d97633a6…` | 1,400 bytes at decoded `0x2A00` (English bytes `fcdcaf45…`; ending part `69f1a137…`) |
  | `MCED.SHP` | `cca9332d…` | `0x2CF0`: `0008` → `0038` |
  | `MMPACK.PCA` | `276d534c…` | version 4, slots 0-17, ending slot 16 |

  Track 01 is `2abe9771…`. All 71,908 sectors pass EDC/ECC.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | Track 01 `c904a386…` |
| Program image | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` |
| Select state | `local/checkpoints/re004/f00002973.mcs` (`EXP-0025`; cursor on Ken, original image, after Start) |
| Specs | the 18 roster win-quote specs and `data/translations/nash_ending.json` |

## Tools

| Tool | Use |
| --- | --- |
| [`make_spec.py`](make_spec.py) | The ending spec |
| `tools.disc.build_english` | The build (`--patch-version 4 --image`) |
| [`saturn_route.py`](saturn_route.py) | No-play route: pick Nash from the select state, then set the CPU side's vitality (`0x060F4610`, `0x060F4E10`) to 0 every 20 frames; load check; read log on an area; quote pointer log; screenshots every 120 frames. `--mmpack` writes the build's code bytes into RAM first. |
| [`area_reads.py`](area_reads.py) | First attempt (invalid, below) |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0041/make_spec.py data/translations/nash_ending.json
./invenv.sh python -m tools.disc.build_english \
  data/translations/{wolverine,cyclops,storm,rogue,gambit,sabretooth,juggernaut,magneto,apocalypse,ryu,ken,chun_li,dhalsim,zangief,vega,gouki,nash,cammy}_win_quotes.json \
  data/translations/nash_ending.json local/end007/b1 --patch-version 4 --image build/m7_nash_ending
./invenv.sh python -m tools.disc.sector "build/m7_nash_ending/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
C="build/m7_nash_ending/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0041/saturn_route.py "$C" local/end007/b1/MC10.SHP \
  local/end007/route_after2 --area 0024FD20:00250087 --frames 26000 --mmpack local/end007/b1/MMPACK.PCA
./invenv.sh python research/experiments/EXP-0041/saturn_route.py "$C" local/end007/b1/MC10.SHP \
  local/end007/route_rest3 --area 0024FF78:00250087 --frames 26000 --mmpack local/end007/b1/MMPACK.PCA
```

`saturn_route.py` brings Mednafen to the front for the pick. A run whose key
could not be sent stops with an error (`route_rest2`), and was rerun.

## Actual Result

### Invalid attempts (recorded)

1. **`area_reads.py`** ran from `f00210163` with no input and RAM edits.
   - **The `MCED` edit failed** at first: `MCED` is not in RAM yet at that
     checkpoint. It is there by the Apocalypse fight (`f00216311`), so it
     loads with the boss stage.
   - **Nash then lost the boss fight** (continue screen, title), so the
     runs never reached the ending. This also invalidated `EXP-0036`'s
     write logs, which are now withdrawn there.
2. **`route_after` and `route_rest`** (route on the build without
   `--mmpack`).
   - **Original code:** the select state already held the original
     `MMPACK.PCA` code, so the runs used it. The pointers show 76-byte
     Japanese records: Nash's win quotes at table + 76r, his ending at
     table + `0x4C0` + 76k.
   - **The reads are therefore invalid.** It was caught from the pointer
     log.
3. **`route_rest2`:** stopped at the pick (Mednafen not frontmost).

### Valid runs (`--mmpack`: 33 code ranges written, all inside the patch areas)

| Run | Area (WRAM-L) | Load check | Reads while the quote pointer is on an ending record | Other reads |
| --- | --- | --- | --- | --- |
| `route_after2` | `0x0024FD20`-`0x00250087` (table + 800 to the old Japanese ending's end) | buffer = built `MC10` + 263 fix-ups | 306, all by `0x06066A84` | **0** |
| `route_rest3` | `0x0024FF78`-`0x00250087` (after the English ending) | same | 0 | 1, by `0x06066A84` at frame 15,020, the 20 frames in which page 6 began |

**Pointer log (`route_after2`, frames after the pick):**

- **Win quotes:** Nash's English win quotes at table + 100r: 540, 2,200,
  3,800, 5,540, 8,860, 11,240.
- **Apocalypse's pre-fight line:** at 9,620-9,880, from his buffer
  (`0x060C2ED0` + 76k).
- **The ending:** `0x0024FD20` + 100k at 12,720-14,660.
- **The credits** follow.

**The single read past page 6's record:**

- During page 6, the renderer read once just past the record's 100
  bytes. In the build those bytes are left-over Japanese ending data; in
  `EXP-0038`'s trial they were zeros.
- The page-6 screenshots are identical in both, so the value read does not
  change the page.

**Screens (agent-reviewed; `route_after2` contact sheets):**

- **Stages:** every stage's win quote is English. The win quote after
  Apocalypse is English too: "You don't have the mettle…", Nash's record 0,
  the record the arcade shows there (`EXP-0037`).
- **Apocalypse's pre-fight line** is Japanese (`SPECIAL-001`).
- **The ending's six pages** (frames 12,840, 13,200, 13,560, 13,920,
  14,400, 14,760) hash `65ae6f95…`, `456fee1d…`, `a5661877…`, `fc8fe0c5…`,
  `bdfbd8b7…`, `55a9d2cd…`. These are byte-identical to `EXP-0038`'s
  English trial pages, the layout the user chose (`LAYOUT-002`).

**Fit:** `MC10.SHP` with both English parts compresses lazily to 23,099
bytes, against its 23,913-byte size: **814 bytes** to spare. The stream
ends in the file's last sector. In decoded `MC10`, 1,227 bytes differ from
the original, all within `0x2A00`-`0x2F77`.

## Conclusion

**CONFIRMED:**

- Nash's six English ending records go at `MC10.SHP` decoded `0x2D20`
  (quote table + 800), after his English win quotes, and the file fits with
  814 bytes to spare.
- After the pick, the file loads exactly.
- From select to the credits, with the build's code, the bytes from table
  + 800 to the end of the old Japanese ending are read only by the ending
  renderer while it shows those pages. The one exception is a single read
  just past page 6's record, which does not change the screen.
- The build shows the chosen English ending page for page.

## Uncertainty and Alternatives

- **The code came from RAM writes,** not from a cold boot of the build.
  The 33 written ranges equal the build's decoded `MMPACK.PCA` there, and
  the rest of the code is the same file. `END-008`'s play check boots the
  build from cold.
- **One team:** the route ran Nash and Cyclops, picked with the default
  partner, and won every fight by vitality forcing. Other partners, or
  fights won in play, were not run.
- **The read address past page 6** is not known: the hit lines give no
  address.

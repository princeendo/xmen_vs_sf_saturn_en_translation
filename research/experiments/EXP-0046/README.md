# EXP-0046 (M8): Build Every Roster Ending

Task: END-014
Status: DONE
Confidence: CONFIRMED (build, files, load check); CONFIRMED (the second
cursor's skip rule and Rogue's run-time words, from screenshots and an
untouched-image control)

## Observation

- **Gate:** `GATE-TRANSLATION` covers all 17 `END-011` roster endings
  (2026-10-30, `SESSION-0069`). Page k shows the arcade English ending
  record k, with no rewording and the arcade names.
- **Method:** version 4 (`EXP-0040`, D-034), proven for Nash (`EXP-0041`,
  D-035, D-036). The census (`EXP-0043`, D-038) says every roster file can
  hold its English ending, and every slot has an English script.
- **Tooling gaps:**
  - `EXP-0041` `make_spec.py` writes Nash's spec only;
  - `mced_english_scripts` refuses Ryu's and Chun-Li's scripts, which are
    shared with slots 8 and 18.

## Hypothesis

With the 18 roster win-quote specs, an ending spec for each of the 17
roster slots, and Ryu's and Chun-Li's shared scripts switched by explicit
permission, `tools.disc.build_english` version 4 builds one image from the
untouched source that:

- changes only each MC file's English range, `MCED`'s header words and
  `MMPACK`'s version-4 patches;
- re-encodes every changed file within its original sectors;
- passes EDC/ECC;
- loads each roster character's built file into either team buffer.

## Changes

- **Specs:** `make_specs.py` (generalizes `EXP-0041` `make_spec.py`) wrote
  `data/translations/<name>_ending.json` for the 17 roster slots from their
  pairing files. Each holds addresses, hashes and line lengths only. It
  checks that every page is CONFIRMED and that the hashes match. It also
  checks that 800 + 100n bytes fit in the Japanese records they replace.
  Nash's regenerated records equal the M7 spec's. Only the description and
  two size fields are new.
- **Shared scripts:** `mced_english_scripts(decoded, slots, shared)`. A
  slot in `shared` may switch with an ending slot whose script it shares.
  It must share one, and it must not be an ending slot itself. An ending
  spec's `mced_shared_with` passes it: Ryu's lists 8 and Chun-Li's lists 18.
  2 new tests.
- **Route tool** (`tools.mednafen.route`):
  - both buffers are saved to OUT;
  - a screenshot of each cursor is taken before its A press;
  - second-pick moves are planned with the skip rule (below).

  2 new tests.

## Prediction

- **Build:** the file check passes for all 17 MC files, `MCED` and
  `MMPACK`, and every compressed margin is ≥ 0.
- **Sectors:** all 71,908 sectors pass EDC/ECC.
- **Reproducibility:** a second build gives identical files.
- **Load:** every roster character's buffer equals its built file plus
  fix-ups, picked first and picked second.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | Track 01 `c904a386…` (untouched) |
| Program image | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` |
| Specs | 18 `<name>_win_quotes.json` (M5) and 17 `<name>_ending.json` |
| Select state | `local/checkpoints/re004/f00002973.mcs` (route `STATE`) |
| Gouki state | `local/re004/session/states/f00009348.mcs` (`GOUKI_STATE`) |

## Tools

| Tool | Use |
| --- | --- |
| [`make_specs.py`](make_specs.py) | The 17 ending specs |
| `tools.disc.build_english` | The build (`--patch-version 4 --image`) |
| [`check_build.py`](check_build.py) | MC bytes and margins, `MCED` edits against the script census, `MMPACK` against `patches_v4` |
| [`load_check.py`](load_check.py) | Picks every team; judges each buffer; retries wrong picks |
| [`identify_buffers.py`](identify_buffers.py) | Which MC file a saved buffer holds |
| [`gouki_cell.py`](gouki_cell.py) | Picks with given moves from the select state, then saves both buffers |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0046/make_specs.py local/end014/specs
cp local/end014/specs/*_ending.json data/translations/
W=""; E=""
for n in wolverine cyclops storm rogue gambit sabretooth juggernaut magneto apocalypse \
         ryu ken chun_li dhalsim zangief vega gouki nash cammy; do
  W="$W data/translations/${n}_win_quotes.json"
  [ $n != apocalypse ] && E="$E data/translations/${n}_ending.json"
done
# zsh: ${=W} splits the lists; in bash use $W
./invenv.sh python -m tools.disc.build_english ${=W} ${=E} local/end014/b1 \
  --patch-version 4 --image build/m8_roster_endings
./invenv.sh python -m tools.disc.sector "build/m8_roster_endings/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
./invenv.sh python research/experiments/EXP-0046/check_build.py local/end014/b1 local/end014/check.json
./invenv.sh python -m tools.disc.build_english ${=W} ${=E} local/end014/b2 --patch-version 4
B="build/m8_roster_endings/X-Men vs. Street Fighter (Japan) (3M).cue"
O="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0046/load_check.py "$O" local/end014/control3 3:4 1:2
./invenv.sh python research/experiments/EXP-0046/identify_buffers.py "$O" local/end014/control3/t*
./invenv.sh python research/experiments/EXP-0046/load_check.py "$B" local/end014/load6
./invenv.sh python research/experiments/EXP-0046/gouki_cell.py "$B" local/end014/gouki1 uuullu "" 15 1
./invenv.sh python research/experiments/EXP-0046/gouki_cell.py "$B" local/end014/gouki2 "" uuuu 10 15
./invenv.sh python research/experiments/EXP-0046/identify_buffers.py "$B" local/end014/gouki1 local/end014/gouki2
```

(`gouki1` was run before the probe took slot arguments; its intended slots
were then fixed in the script as 15 and 1.)

(`control3` was run with the earlier driver, before retries and judging
were added; its buffers were judged with `identify_buffers.py`.)

## Actual Result

### Build

`build/m8_roster_endings`, from the untouched source. All 71,908 sectors
of Track 01 pass EDC/ECC. A second build (`local/end014/b2`) gave 21
byte-identical files.

| File | Rebuilt SHA-256 | Change |
| --- | --- | --- |
| 17 roster `MCxx` | `local/end014/b1/changes.json` | the 800 English win-quote bytes plus 100n ending bytes at the quote table; all other decoded bytes unchanged |
| `MC08.SHP` | `7bb06fec…` (as M5 and M7) | win quotes only |
| `MC10.SHP` | `d97633a6…` (as M7) | unchanged from M7 |
| `MCED.SHP` | `b37c3a64…` | 17 header words, below |
| `MMPACK.PCA` | `36179171…` | version 4, slots 0-17, ending slots 0-7 and 9-17: 48 patches, each equal to `patches_v4` |
| Track 01 | `7bb8ab82…` | |

**`check_build.py`:**

- Every roster MC file holds exactly its English bytes. These are the
  8 win quotes, then the n ending records from the program image.
- Every other decoded byte equals the original.
- The `MCED` edits are exactly the 17 distinct roster scripts' header
  words, each `0008` → its language-2 word, as `ending_script_census.json`
  gives.
- `MMPACK` equals `patches_v4`.

| Slot | File | English bytes | Japanese space | Compressed margin |
| --- | --- | --- | --- | --- |
| 0 | `MC00` | 1,400 | 1,748 | 808 |
| 1 | `MC01` | 1,700 | 1,748 | 633 |
| 2 | `MC02` | 1,400 | 1,748 | 782 |
| 3 | `MC03` | 1,400 | 1,824 | 862 |
| 4 | `MC04` | 1,300 | 1,672 | 726 |
| 5 | `MC05` | 1,400 | 1,520 | 716 |
| 6 | `MC06` | 1,400 | 1,900 | 637 |
| 7 | `MC07` | 1,500 | 1,520 | 914 |
| 9 | `MC09` | 1,500 | 1,672 | 606 |
| 10 | `MC0A` | 1,200 | 1,596 | 607 |
| 11 | `MC0B` | 1,400 | 1,748 | 1,293 |
| 12 | `MC0C` | 1,400 | 1,520 | 631 |
| 13 | `MC0D` | 1,300 | 1,520 | 784 |
| 14 | `MC0E` | 1,300 | 1,520 | 494 |
| 15 | `MC0F` | 1,400 | 1,520 | 561 |
| 16 | `MC10` | 1,400 | 1,672 | 814 |
| 17 | `MC11` | 2,100 | 2,128 | 659 |

"Japanese space" is the 16 win quotes plus the ending records, 76 bytes
each. "Compressed margin" is the file size minus the natural lazy PRS
length. Every stream ends in its file's last sector (`build_english`).

`MCED.SHP` header words (decoded offset, `0008` → new):

`0x2814` `0030`, `0x2868` `0036`, `0x28d4` `0036`, `0x2934` `0034`,
`0x298c` `002c`, `0x29d8` `0024`, `0x2a20` `0038`, `0x2a7c` `002a`
(Ryu and Apocalypse), `0x2ad4` `0032`, `0x2b34` `0028` (Chun-Li and slot
18), `0x2b78` `0030`, `0x2bcc` `002a`, `0x2c20` `0024`, `0x2c64` `0024`,
`0x2ca8` `0024`, `0x2cf0` `0038` (Nash, as M7), `0x2d58` `0062`.

### Load check

`load_check.py` on the build (`local/end014/load6`, with the corrected
route): 17 teams. Every grid character was picked once first and once
second, and Gouki was picked first from `GOUKI_STATE`.

| Team (first, second) | Attempts | First buffer | Second buffer |
| --- | --- | --- | --- |
| Wolverine, Cyclops | 1 | pass | pass |
| Cyclops, Storm | 1 | pass | pass |
| Storm, Rogue | 2 (a lost key in attempt 1) | pass | pass (Rogue's words) |
| Rogue, Gambit | 1 | pass (Rogue's words) | pass |
| Gambit, Sabretooth | 1 | pass | pass |
| Sabretooth, Juggernaut | 1 | pass | pass |
| Juggernaut, Magneto | 1 | pass | pass |
| Magneto, Ryu | 1 | pass | pass |
| Ryu, Ken | 1 | pass | pass |
| Ken, Chun-Li | 1 | pass | pass |
| Chun-Li, Dhalsim | 1 | pass | pass |
| Dhalsim, Zangief | 1 | pass | pass |
| Zangief, Vega | 1 | pass | pass |
| Vega, Nash | 1 | pass | pass |
| Nash, Cammy | 1 | pass | pass |
| Cammy, Wolverine | 1 | pass | pass |
| Gouki (state), Cyclops | 1 | pass | pass |

**Gouki from the disc** (`gouki_cell.py`, build image):

| Run | First moves | Second moves | First buffer | Second buffer |
| --- | --- | --- | --- | --- |
| `gouki1` | `uuullu` (Ken to Juggernaut, then up) | none (Cyclops) | `MC0F`, 0 differing bytes | `MC01`, 0 |
| `gouki2` | none (Ken) | `uuuu` (Cyclops to Juggernaut, then up) | `MC0A`, 0 | `MC0F`, 0 |

Gouki's cell is above Juggernaut's (screenshot `gouki1/first_cursor.png`
shows his portrait in the cell above the grid). From the route's select
state he can be picked first or second, and the build's `MC0F` then loads
from the disc into either buffer with no differences.

Earlier runs (`load1` to `load5`, `control1` to `control3`) failed on wrong
picks and on Rogue. They led to the findings below; none of them showed a
build file loading wrongly.

### Found on the way

1. **The second cursor skips the first pick's cell.** Seen in screenshots
   taken before the second A press (`control2`, `control3`; untouched
   image):
   - With Rogue picked first, the second cursor started on Cyclops. "u"
     went to Storm, so "ul" ended on Sabretooth, not Gambit.
   - With Cyclops picked first, the second cursor started on Wolverine.
   - With Juggernaut picked first, "uuul" from Cyclops ended on Gouki's
     cell above the grid.

   The route's second-pick moves now plan with this rule.
   `EXP-0045`'s second picks never crossed the first pick's cell.
2. **Keys are sometimes lost.** Two first picks went wrong with
   correctly planned moves (`load5`):
   - one "l" was lost (Rogue instead of Gambit);
   - one A press was lost (Cyclops's cursor then moved on to Chun-Li with
     the partner's moves).

   A lost key always gives a buffer holding another character's file
   exactly, so the driver retries those teams.
3. **Rogue's run-time words.** `MC03.SHP` holds four `9999 9999` longs at
   decoded `0x9332`, `0xA446`, `0xB018` and `0xBDE4`. After loading, the
   game writes into them: `0x9333`-`0x9334` = `00 13`, `0xA447`-`0xA448` =
   `00 10`, `0xB019`-`0xB01A` = `00 16`, `0xBDE5`-`0xBDE6` = `00 1E`
   (`control2`, `control3`). That happens on the untouched image too, so
   it is the game's doing, not the build's. One build run also changed
   `0x9332`. The load check allows differences inside those four longs for
   Rogue only.

## Conclusion

**CONFIRMED:**

- `build/m8_roster_endings` (Track 01 `7bb8ab82…`) is built from the
  untouched source with every roster character's English win quotes and
  English ending. It is reproducible, and all its sectors pass EDC/ECC.
- Its changes are exactly:
  - each MC file's English range;
  - 17 `MCED` header words;
  - the 48 version-4 code patches.

  Every changed file fits its sectors with at least 494 bytes of
  compressed margin.
- Every roster character's built MC file loads from the disc into the
  first and the second team buffer, equal to the file plus fix-ups. Gouki
  is included, picked from his cell above Juggernaut's. Rogue's four
  game-written longs are the one exception, and they differ the same way on
  the untouched image.
- **The second cursor skips the first pick's cell.** It starts on Cyclops,
  or on Wolverine when Cyclops is taken.
- **Gouki's cell** is reached by "u" from Juggernaut, from the route's
  select state.

`END-014`'s criteria are met. `END-015` can use Gouki's cell instead of
`GOUKI_STATE` for a route with no RAM patching (not changed here).

## Uncertainty and Alternatives

- **Rogue's words:** what the game writes there, and why, is UNKNOWN.
  Possibly per-match state for her power copy. The values vary slightly
  between runs.
- **Skip rule:** seen for three first picks. It is a HYPOTHESIS for edge
  cells not tried (for example a taken cell at the grid's edge).
- **Gouki in `load_check.py`** is picked from `GOUKI_STATE`, whose RAM
  holds the untouched `MC0F` patched by the route. That team checks the
  patching, not a disc load. The disc loads are `gouki1` and `gouki2`. The
  route tool still uses `GOUKI_STATE`.
- **Gouki's cell:** whether it is open in every save (an unlock) is not
  known. The route's select state has it open.
- **Screens:** nothing here shows an English ending on screen; that is
  `END-015`.

## Reproduction

The procedure above. Outputs are under `local/end014/` (ignored).

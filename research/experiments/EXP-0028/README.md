# EXP-0028 (M4): Ryu and Ken in English from the Source Image

Task: RE-007
Status: DONE
Confidence: CONFIRMED

## Observation

Two things are now known:

- **Version 3** of the English-mode patch makes English a per-slot data byte
  (`EXP-0027`, D-022).
- **Ken's records** pair with English slot 10 as `k mod 8` (`EXP-0026`, D-021).
  The user passed `GATE-TRANSLATION` for them (`SESSION-0038`).

The build tool (`tools.disc.build_english`, `EXP-0024`) still takes one
spec and applies version 2, which tests only Ryu's slot.

## Hypothesis

A build tool that takes several specs and applies version 3 with every
spec's slot gives one image in which both Ryu and Ken speak English. Both
use the same mechanism, and every other speaker stays unchanged.

## Controlled Change

`tools.disc.build_english` now does the following:

- It takes `SPEC [SPEC ...] OUT`.
- It applies `patches_v3` with the slots of the specs (version 3, the
  default).
- It rejects a repeated slot or MC file.
- `--patch-version 2` keeps the old Ryu-only build.
- `--image DIR` also runs `tools.disc.patch_image` on the files it wrote.

The new spec `data/translations/ken_win_quotes.json` is written by
[`make_spec.py`](make_spec.py), which is generalized from `EXP-0024`. The
image changes only `MMPACK.PCA`, `MC09.SHP` and `MC0A.SHP`.

## Prediction

- **Build:**
  - Only the three files change, each at its own size.
  - Every sector passes EDC/ECC, and the ISO layout is unchanged.
  - Two builds are identical, and the source is unchanged.
  - Ryu's version-2 build still gives `EXP-0024`'s files.
- **Ken:** each of his 16 draws, steered by seed, shows English record
  `draw & 7` as compiled (50/50 cells).
- **Ryu:** his 16 draws are byte-identical to `EXP-0024`.
- **Disc and cold boot:**
  - Picking either character loads the built file.
  - A cold boot has the version-3 code, with only slots 9 and 10 marked.
- **Play:** a cold-boot play check shows English for Ryu and Ken. It also
  shows another character's quote and a continue hint in Japanese.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | `local/disc_images/xmvsf_saturn_jp_3m` (`references/saturn_jp/README.md`); Track 01 `c904a386…`, unchanged after every build |
| Specs | `data/translations/ryu_win_quotes.json`, `data/translations/ken_win_quotes.json` (addresses and hashes, no text) |
| English | US program `local/ref003/xmvsfu-68k.bin` (`EXP-0008`); Ryu `0x188DE2`, Ken `0x189166` |
| Ken `pre_ko` | `local/checkpoints/re004/f00007684.mcs` (`EXP-0025`); paused seed 9501 |
| Ryu `pre_ko` | `local/checkpoints/dbg003/f00009769.mcs` (`EXP-0013`); paused seed 8520 |
| Pick states | Ryu `local/dbg003/session/states/f00005696.mcs` (`EXP-0013`), Ken `local/checkpoints/re004/f00002973.mcs` (`EXP-0025`) |
| Regression reference | `local/re003/draws_a`, `draws_b` (`EXP-0024`) |
| Play session | `local/re007/session2/` (168 screenshots, 58 states) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/disc/build_english.py` | Several specs, version 3, `--image` |
| [`make_spec.py`](make_spec.py) | Writes a character's spec from the arcade program and the pairing |
| [`seed_scan.py`](seed_scan.py) | Finds a seed for each draw (CASE `ryu` or `ken`) |
| [`force_draws.py`](force_draws.py) | Shows each draw with the built code and records |
| [`pick_load.py`](pick_load.py) | Picks a character with the built image mounted and compares RAM with the built file |
| [`play_pointers.py`](play_pointers.py) | Reads the quote pointer from play states and names the record |
| `research/experiments/EXP-0023/cell_check_en.py` | Cell check |
| `research/experiments/EXP-0019/cold_font.py`, `EXP-0025/dump_states.py` | Cold boot plus Start, then WRAM-H dump |
| `tools/mednafen/session_recorder.py` | Play-session recording |
| `tests/unit/test_english_build.py` | Slot list, version 2, repeated slot or file, unknown version |

Mednafen: the patched agent build (`EMU-021`).

## Procedure

```bash
# specs (Ryu's arguments reproduce ryu_win_quotes.json except the description)
./invenv.sh python research/experiments/EXP-0028/make_spec.py local/re007/ryu_check.json \
  Ryu 9 "MC09.SHP;1" 0x25D8 data/translations/ryu_pairing.json x
./invenv.sh python research/experiments/EXP-0028/make_spec.py data/translations/ken_win_quotes.json \
  Ken 10 "MC0A.SHP;1" 0x2A4C data/translations/ken_pairing.json \
  "user decision 2026-10-29, SESSION-0038"
# version-2 regression, then two version-3 builds
./invenv.sh python -m tools.disc.build_english data/translations/ryu_win_quotes.json \
  local/re007/v2_ryu --patch-version 2
for b in b1 b2; do
  ./invenv.sh python -m tools.disc.build_english data/translations/ryu_win_quotes.json \
    data/translations/ken_win_quotes.json local/re007/$b > local/re007/$b.json
done
# the image (one command)
./invenv.sh python -m tools.disc.build_english data/translations/ryu_win_quotes.json \
  data/translations/ken_win_quotes.json local/re007/b3 --image build/re007_ryu_ken_english
B="build/re007_ryu_ken_english/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
./invenv.sh python -m tools.disc.sector "$B"
./invenv.sh python -m tools.disc.iso9660 --check "$B" > local/re007/built_listing.json
# Ken's seeds, then every draw for both characters
./invenv.sh python research/experiments/EXP-0028/seed_scan.py ken local/re007/scan1 $(seq 1 60)
./invenv.sh python research/experiments/EXP-0028/seed_scan.py ken local/re007/scan2 \
  15 20 25 2 35 24 4 9 7 12 1 3 8 13 5 10
for c in ken ryu; do
  ./invenv.sh python research/experiments/EXP-0028/force_draws.py $c local/re007/b1 local/re007/draws_$c
  ./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/re007/draws_$c \
    local/ref007/saturn_files/FIX.PRS > local/re007/cells_$c.json
done
# disc loads and cold boot
CUE="build/re007_ryu_ken_english/X-Men vs. Street Fighter (Japan) (3M).cue"
for c in ryu ken; do
  ./invenv.sh python research/experiments/EXP-0028/pick_load.py $c "$CUE" local/re007/b1 local/re007/pick_$c
done
./invenv.sh python research/experiments/EXP-0019/cold_font.py "$CUE" local/re007/cold
./invenv.sh python research/experiments/EXP-0025/dump_states.py local/re007/cold_dump \
  local/re007/cold/after_start.mcs
# play check: the user plays the built image (interactive home); the recorder runs
./invenv.sh python -m tools.mednafen.session_recorder local/re007/session2 \
  --agent-dir local/re007/session/agent --state-interval 3 --keep-states 120
S=local/re007/session2/states
./invenv.sh python research/experiments/EXP-0028/play_pointers.py "$CUE" local/re007/b1 \
  local/re007/play_pointers $S/f00216805.mcs $S/f00222185.mcs $S/f00222642.mcs $S/f00232497.mcs
./invenv.sh python research/experiments/EXP-0028/play_pointers.py "$CUE" local/re007/b1 \
  local/re007/play_pointers_ken $S/f00232935.mcs
```

Use the MYPYPATH setting `MYPYPATH=research/experiments/EXP-0025` for
`mypy --strict` on `pick_load.py`, which imports two `EXP-0025` helpers.

## Actual Result

### Build

| File | Size | Original SHA-256 | Built SHA-256 |
| --- | --- | --- | --- |
| `MC09.SHP` | 20,686 | `e9a5605b…` | `507b1f46…` (same as `EXP-0024`) |
| `MC0A.SHP` | 23,258 | `d85edd6a…` | `585f9e99…` |
| `MMPACK.PCA` | 258,319 | `60dddde3…` | `6d7e50a0…` |

- **Builds:** `b1`, `b2` and `b3` are identical. The version-2 Ryu build
  still gives `EXP-0024`'s `MC09` (`507b1f46…`).
- **Code:** the decoded `MMPACK.PCA` differs from the original in 42
  bytes, all inside `patches_v3([9, 10])`. So the code is the code that
  left Storm byte-identical in `EXP-0027`.
- **Image:** only Track 01 differs (`b5dd07c2…`). All 71,908 sectors pass
  EDC/ECC, the ISO paths and layout are unchanged, and only the three
  files differ.
- **One command:** the `--image` build gave a Track 01 identical to the
  two-step build (`build_english`, then `patch_image`).
- **Source:** the source Track 01 is still `c904a386…`.

### Live checks

**Seeds.** For Ken's 16 draws, seeds 1-60 cover every draw, and each run
paused at seed 9501. A repeat with the chosen seed for each draw gave the
same draws.

**Forced draws.** These used the built code and records (`force_draws.py`).

| Case | Runs | Pointer and bytes as predicted | Cells |
| --- | --- | --- | --- |
| Ken | control, 0-15 | 17/17 | control 38/38 (16 px); draws 50/50 (12 px) |
| Ryu | control, 0-15 | 17/17 | control 38/38; draws 50/50 |

- **Ken's pointers:** draw `d` points to `0x0024FA4C + 100 × (d & 7)`. The
  control (natural draw 14, Japanese) points to `0x0024FE74`.
- **Ryu:** the 17 screenshots and VDP1 VRAM dumps are byte-identical to
  `EXP-0024` (17 of 17).

**Pick from disc** (built image mounted):

| Character | Fix-ups (2-byte aligned) | RAM = built file + fix-ups | English table loaded |
| --- | --- | --- | --- |
| Ryu | 259 (106) | yes | yes |
| Ken | 302 (123) | yes | yes |

**Cold boot plus Start.** Every new byte of `patches_v3([9, 10])` is in
WRAM-H. The fixed-index words have high byte 2 only at slot 9 (`0x0201`)
and slot 10 (`0x0207`). Every other slot's high byte is 0.

### Play check (user, cold boot of the built image)

The first recording stopped at frame 4,685, when the agent went 10 s
without a reply (see Uncertainty). Recording restarted at frame 207,906
and ran through the route below.

| Screen | Screenshot | Speaker | Shown | Pointer (state) |
| --- | --- | --- | --- | --- |
| Player win | `f00216915` | Ryu (team Ryu and Cammy) | English, 12-px grid | `0x0024F704` = `MC09` English record 3 (`f00216805`) |
| CPU win | `f00222446` | Rogue (team Rogue and Chun-Li) | Japanese, 16-px grid, as the unpatched game | no state during the quote |
| Continue | `f00222613` | hint | Japanese | `0x0608583C`, in neither English table (`f00222642`) |
| Player win | `f00232749` | Ken (team Ken and Gouki) | English, 12-px grid | `0x0024FD08` = `MC0A` English record 7 (`f00232935`, saved just after the quote) |

Both English quotes came from the first member's copy in WRAM-L.

**Tests:** 162 pass.

## Conclusion

**CONFIRMED.** One command builds an image from the untouched source in
which Ryu's and Ken's win quotes are their official arcade English. Saturn
record `k` shows English record `k mod 8`, through version 3 of the
English mode.

- All 16 draws of each character show the compiled English cell for cell.
- Ryu is byte-identical to `EXP-0024`.
- Unmarked speakers keep their Japanese quotes (Rogue in play, Storm in
  `EXP-0027` with the same code), and hints stay Japanese.
- M4 is reached.

## Uncertainty and Alternatives

- **Second member and CPU speakers:** both play-check quotes were spoken
  by the first member of the player's team. A win finished by the second
  member (WRAM-H copy) and a CPU win by Ryu or Ken were not observed. The
  build changes the MC file wherever it loads, so both are expected to be
  English, but this is not observed.
- **Recorder stall:** in the first play session the agent stopped
  answering at frame 4,685 (attract demo) for an unknown time. Mednafen kept
  running and later answered at frame 206,743. The user was away from the
  computer. Cause unknown.
- **Paths not reached:** the fixed-index path, the type-6 selector and the
  endings were not reached in play (`EXP-0023`, `EXP-0027`).
- **Real hardware:** not tested.

## Reproduction

Run the procedure. Expect the hashes above, 17/17 forced runs for each
character at 50/50 cells, 17 byte-identical Ryu runs, both pick loads
equal, the slot table with only slots 9 and 10 marked, and the play-check
pointers above when the same states are loaded.

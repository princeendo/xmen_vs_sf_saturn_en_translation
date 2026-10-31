# EXP-0064 (UI): The Attract Captions: Census, Storage and Official English

Task: CAP-001
Status: DONE
Confidence: CONFIRMED (census from cold-boot captures; storage by a
one-byte disc change predicted by the decoder and seen in RAM and on
screen; official English from the US arcade and PS1 captures)

## Observation

`docs/text_surfaces.md` (`REF-005`): four full-screen Japanese captions in
the attract loop, with English captions in the same slots of the US arcade,
paired by order (HYPOTHESIS). MSHvSF (a HYPOTHESIS for XvSF, rule 13): its
captions were VDP2 tiles from `.ST2` attract streams, with their own LZ.

## Inputs

- Untouched image (`references/saturn_jp/README.md`). The `OPENING0`-`7.ST2`
  files, extracted with `tools.disc.iso9660 --extract` (`local/noch001/disc/`),
  SHA-256 `5b9d1f0f…`, `9aa3aaa6…`, `5a4b7acf…`, `00d24c84…`, `3a6571bc…`,
  `bbbf09eb…`, `7c63c249…`, `e82a1239…`.
- US arcade `xmvsfu` (MAME 0.289, `local/arcade_roms/xmvsf_mame0289`).
- US PS1 disc (`references/ps1/README.md`: Track `13e66a3e…`, CUE
  `dc10746e…`, both checked) and the BIOS `scph1001.bin` (SHA-256
  `71af94d1…`), which the user supplied for MSHvSF's `EXP-0072` on
  2026-10-26; copied into the ignored `local/cap001/psx_home/firmware/` and
  never committed.

## Census (Saturn, cold boot, no input)

```bash
./invenv.sh python -m tools.mednafen.frame_capture \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/cap001/cold1 --first 60 --last 24000 --step 20
```

1,198 screenshots, frames 60-24,000: **eight attract cycles** of about
2,860 frames, each with the same four captions in the same order. Every
caption has the line `PRESS START BUTTON` under it.

| # | Caption (transcription) | Cycle 1 frames | Screenshot | Shown after / before |
| --- | --- | --- | --- | --- |
| 1 | 日米ヒーロー / 夢の競演!! | 2,880-2,920 | `f00002900.png` `8df6be82…` | Ken and Rogue's intro / a demo scene |
| 2 | 2つの心を / 1つに合わせ | 3,220-3,260 | `f00003240.png` `5de20c87…` | Rogue's demo / a demo scene |
| 3 | 友情の / 合体技!! | 3,480-3,520 | `f00003500.png` `4a20498e…` | a white flash / a demo scene |
| 4 | ヴァリアブル ヒーローバトル!! (scrolls right to left) | 3,720-3,880 | `f00003740.png` `51c6bfbc…`, `f00003800.png` `333ecbe6…`, `f00003860.png` `f0858bda…` | a white flash / the title (Ryu and Cyclops) |

Captions 1-3 each have exactly two screenshot variants over the eight
cycles (1: `8df6be82…`, `af0da1b6…`; 2: `5de20c87…`, `f084289e…`; 3:
`4a20498e…`, `b2df1dde…`); the `REF-005` samples are among them. The text
is the same; the variants are probably the blinking prompt (not checked).

## Storage

### Layer

States on each caption ([`caption_states.py`](caption_states.py): cold
boot, then run-save-halt at chosen frames; disc timing shifts each boot by
a few hundred frames, so frames differ between runs):

```bash
C="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0064/caption_states.py "$C" local/cap001/states1 2600 2640 2980 3240 3520
./invenv.sh python research/experiments/EXP-0064/caption_states.py "$C" local/cap001/states2 2900 3500 3760 3800 3840
```

- No VDP1 sprite is drawn on a caption screen (`dump_c2`, from
  `EXP-0049/dump_screen.py`).
- VDP2 registers (from the states): all four NBG layers on; **NBG1**:
  16 colours, 2 × 2-cell characters, 2-word pattern names (`CHCTLA`
  `0x0100`, `PNCN1` 0), plane 2 × 2 pages (`PLSZ` `0x3C`), map
  `MPOFN` `0x110`, `MPABN1` `0x2C2C`: page **`0x6C000`** in VDP2 VRAM, the
  same for all four captions.
- `tools.memory.vdp2_plane` (copied from MSHvSF with provenance; page given
  explicitly) renders NBG1's pages:
  - captions 1 and 2: the top of page `0x6C000`;
  - caption 3: rows 16-31 of the same page, brought into view by the
    vertical scroll (`SCYIN1` `0x110`);
  - caption 4: the top rows of pages `0x6C000` and `0x6D000`, scrolled
    horizontally (`SCXIN1` `0x2A8` → `0x528` over 80 frames).
- **決めろ!** ("Decide it!") sits in the same page's top right while
  caption 3 shows, outside the visible area. It was never on screen in the
  eight cycles.

### File, container and codec

- **Container:** `OPENING*.ST2`, as MSHvSF's: a header sector with three
  section sizes (`OPENING0`: `0x28800`, `0x14800`, `0x19800`), then
  0x800-byte stream sectors; those tagged `MISS` (581 in `OPENING0`) carry
  0x7FC bytes each of a stream of graphics blocks (u32 compressed size, u32
  decompressed size, data), with zero words between some blocks.
- **The copied decoder failed:** MSHvSF's LZ (copy field = distance back
  from the output end) raised on every XvSF block. A zero-filled window let
  each block decode to its stated size, but its output held none of the
  caption's characters. Both are recorded as rejected.
- **Tracing:** caption 2's characters were only in VDP2 VRAM at the caption
  (`0x30980`-`0x34E7F`). [`find_decode.py`](find_decode.py) stepped 10
  frames at a time from a state 260 frames before it: they appear in WRAM-H
  **`0x060809C0`-`0x06084E80`** 16-26 frames in and in VRAM 10-20 frames
  later; no CPU write reaches that VRAM (`write_log`), so a DMA copies them.
  A write log on the WRAM-H buffer found the decoder: `0x06021B26` (literal)
  and `0x06021B6A` (copy), with R3 = the block's size, `0x3E620`.
- **The codec** (`0x06021AF6`-`0x06021B8C`): flags most significant bit
  first; 0 = literal; 1 = a big-endian word `w` copying `(w & 0xF) + 3`
  bytes from **ring position** `w >> 4` of a 0x1000-byte ring at WRAM-H
  `0x06021BF8`; every output byte is also written to the ring (index from
  0). The routine yields between flag bytes, so it spans frames. After
  decoding, it stores the block's size at output + 0x10.
- **Decoder trusted:** `tools.disc.st2_stream.lz_decode` (rewritten; unit
  tests `tests/unit/test_st2_stream.py`) decodes `OPENING6.ST2` stream block
  3 (`b75b94bd…`, 255,520 bytes; `OPENING7` block 2 is identical) equal to
  WRAM-H `0x06080000` after the game's decode, except the 3 non-zero bytes
  of the size field the game writes (`compare_ram.py`, `cmp6b`).

```bash
./invenv.sh python research/experiments/EXP-0064/compare_ram.py "$C" local/cap001/states1/t00002980.mcs \
  local/cap001/cmp6b local/cap001/blocks/OPENING6_b3.bin 06080000 10 5
```

### Where each caption is

Searching the decoded blocks of all eight files for each caption's own 8 × 8
cells (only the rows the caption occupies):

| Caption | Cells | Found complete in |
| --- | --- | --- |
| 1 | 72 | section C of every `OPENING` file |
| 2 | 351 | one stream block of every file (`OPENING0` 3, `1` 2, `2` 3, `3` 2, `4` 2, `5` 2, `6` 3, `7` 2) |
| 3 (and 決めろ!) | 239 (144) | stream block 6 (`OPENING0`, `2`, `6`) or 5 (the others) |
| 4 | 100 | a late stream block of six files (`OPENING0` 10, `1` 9, `4` 9, `5` 8, `6` 9, `7` 8); split over two consecutive blocks in `OPENING2` (9, 10) and `OPENING3` (8, 9) |

The blocks around them hold the demo scenes; the eight files differ there.

### Controlled change (disc)

[`pick_literal.py`](pick_literal.py) picked one literal byte of caption 2's
block whose change alters only two decoded bytes, both inside caption 2's
characters, and predicted the decoded block (`expected.bin`).

| File | Offset | Original | New | Decoded bytes changed |
| --- | --- | --- | --- | --- |
| `OPENING6.ST2` | `0xB5E6A` | `12` | `FF` | `0x2039`, `0x2074` |
| `OPENING7.ST2` | `0x8666A` | `12` | `FF` | `0x2039`, `0x2074` |

```bash
./invenv.sh python -m tools.disc.patch_image --source-dir local/disc_images/xmvsf_saturn_jp_3m \
  --manifest references/saturn_jp/README.md --track "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin" \
  --file "OPENING6.ST2;1" --data local/cap001/change1/OPENING6.ST2 \
  --file "OPENING7.ST2;1" --data local/cap001/change1b/OPENING7.ST2 --out-dir build/cap001_probe
./invenv.sh python research/experiments/EXP-0064/compare_ram.py \
  "build/cap001_probe/X-Men vs. Street Fighter (Japan) (3M).cue" - \
  local/cap001/probe_cold local/cap001/change1/expected.bin 06080000 20 30 2700
```

(The test image's Track 01 is `cecf7554…`. The control is the same command
on the untouched CUE, out `local/cap001/ctrl_cold`.)

- **RAM:** on the test image, WRAM-H `0x06080000` equals the predicted block
  from frame 3,024 to 3,184, except the 3-byte size field; on the untouched
  image the same buffer differs from the prediction in exactly those 3 bytes
  and the 2 predicted ones.
- **Screen** (caption 2, frames 3,224-3,264): the two cold boots differ in 3
  pixels, (185, 78), (186, 78) and (184, 85): new white pixels beside a
  stroke of 心 (`f00003244.png`: control `5de20c87…`, test `5174c394…`).
- **Rejected first tries:** a replay of a state from frame 2,600 on the test
  image showed no change: the stream was already read into memory. The
  first test image changed only `OPENING6`; its cold boot streamed the
  identical block from `OPENING7`, and showed no change either.

## Official English

### US arcade (MAME)

```bash
D=local/cap001/mame_us; mkdir -p $D && cp -R local/mame_arcade/ref005/cfg local/mame_arcade/ref005/nvram $D/
SNAP_FRAMES="$(seq 30 15 15000 | tr '\n' ' ')" mame xmvsfu -rompath local/arcade_roms/xmvsf_mame0289 \
  -video none -sound none -nothrottle -skip_gameinfo -nomouse -cfg_directory $D/cfg \
  -nvram_directory $D/nvram -snapshot_directory $D/snap -homepath $D \
  -autoboot_script tools/reference/mame_snap_frames.lua
```

999 snapshots; the cycle is about 3,700 frames, with four captions in the
same slots, equal to the `REF-005` samples (`d51aac57…`, `3028bcc1…`,
`d79e03e1…`):

| # | Arcade caption (as written) | Frame | Screenshot |
| --- | --- | --- | --- |
| 1 | THE WILDEST / CROSSOVER / YOU HAVE / NEVER DREAMT! | 1,440 | `d51aac57…` |
| 2 | COMBINE / YOUR POWERS | 1,800 | `3028bcc1…` |
| 3 | THE MARVELOUS / TEAM-UP MOVE! | 2,055 | `d79e03e1…` |
| 4 | PREPARE FOR THE UNCCANY TAG BATTLE MODE!! (scrolls; "UNCCANY" as written) | 2,265-2,415 | `f02325` `702fd83c…` |

Yellow-to-orange outlined capitals on black, with `INSERT COINS` below.

### US PlayStation

A separate silent home (`local/cap001/psx_home`, a copy of the silent
Saturn home with `psx.bios_na scph1001.bin` and its own `firmware/`):

```bash
./invenv.sh python -m tools.mednafen.frame_capture \
  "local/disc_images/xmvsf_ps1_us/X-Men vs. Street Fighter (USA).cue" local/cap001/ps1_us \
  --first 60 --last 10000 --step 20 --home local/cap001/psx_home --agent-dir local/cap001/psx_agent
```

497 screenshots: two attract cycles of about 4,120 frames, each with the
arcade's four captions in the same slots, between the same screens, and
`PRESS START BUTTON` below (the arcade has `INSERT COINS`). Each still
caption's screenshot is identical in both cycles.

| # | PS1 caption | Cycle 1 frames | Screenshot (cycle 2 frame) |
| --- | --- | --- | --- |
| 1 | THE WILDEST / CROSSOVER / YOU HAVE / NEVER DREAMT! | 3,780-3,820 | `f00003800.png` `adb4ee7f…` (7,920: the same) |
| 2 | COMBINE / YOUR POWERS | 4,120-4,160 | `f00004140.png` `64a59260…` (8,260: the same) |
| 3 | THE MARVELOUS / TEAM-UP MOVE! | 4,360-4,400 | `f00004380.png` `6ef4d473…` (8,500: the same) |
| 4 | PREPARE FOR THE UNCCANY TAG BATTLE MODE!! (scrolls; "UNCCANY" as in the arcade) | 4,540-4,720 | `f00004620.png` `c4055ecb…` |

The wording, line breaks and colours equal the arcade's.

## Pairing

By sequence position and neighbouring screens, not frame numbers. Both
versions run: the CAPCOM logo, Ken and Rogue's intro, caption 1, a demo
scene, Rogue, caption 2, a demo scene, a white flash, caption 3, a demo
scene, a white flash, the scrolling caption 4, then the title with Ryu and
Cyclops.

| # | Saturn | US arcade | US PS1 |
| --- | --- | --- | --- |
| 1 | 日米ヒーロー / 夢の競演!! | THE WILDEST / CROSSOVER / YOU HAVE / NEVER DREAMT! | THE WILDEST / CROSSOVER / YOU HAVE / NEVER DREAMT! |
| 2 | 2つの心を / 1つに合わせ | COMBINE / YOUR POWERS | COMBINE / YOUR POWERS |
| 3 | 友情の / 合体技!! | THE MARVELOUS / TEAM-UP MOVE! | THE MARVELOUS / TEAM-UP MOVE! |
| 4 | ヴァリアブル ヒーローバトル!! | PREPARE FOR THE UNCCANY TAG BATTLE MODE!! | the same ("UNCCANY") |

## Conclusion

**CONFIRMED:**

- Four captions, the same in all eight attract cycles watched.
- They are NBG1 tiles, decoded from `OPENING*.ST2` (section C and the
  `MISS` stream blocks) by XvSF's ring-buffer LZ, which the rewritten
  `tools.disc.st2_stream` reproduces; a one-byte disc change appears in RAM
  and on screen exactly as predicted.
- The official English is the US arcade's four captions, paired by order and
  neighbouring screens. The US PS1 shows the same four, word for word, "UNCCANY" included.

## Uncertainty

- **The maps:** where NBG1's caption maps come from (MSHvSF: section A's
  script) was not traced; `CAP-002` needs it for English layouts.
- **決めろ!** is decoded with caption 3 and placed in the plane but was never
  shown; when (or whether) it shows is unknown.
- **Which file plays:** each cycle streams one `OPENING` file; which, and in
  what order, was not traced. The captions' characters are in all eight, so
  an English build must change all eight.
- **The ring's starting contents:** the routine does not clear the ring; the
  verified block decodes equal with a zero ring, but whether every block
  starts from a zero ring is not shown.

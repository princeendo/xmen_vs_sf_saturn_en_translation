# EXP-0053 (Boot): Census of the Boot-Time Messages

Task: BOOT-001
Status: DONE
Confidence:

- CONFIRMED: the four messages triggered, their conditions, and the file
  each loads (bitmap in RAM equal to the disc file);
- CONFIRMED (code): the boot check's structure and the fifth message's
  condition;
- HYPOTHESIS: that the fifth message (`ERR5.BIN`) can show on real
  hardware (an unsteady cart ID, or a 1 MB cart that fails its RAM test).

## Observation

- `EXP-0002` (D-002): with no cart the game stops on one Japanese warning.
- The disc holds `ERR1.BIN`-`ERR5.BIN`, each 42,358 bytes with a 352 × 240,
  4-bit BMP header.
- MSHvSF's census of its own `ERR` files (its `UI-008`) gave a mapping that
  is only a HYPOTHESIS here (rule 13).

## Questions

Which messages can the game show while it loads, under which conditions,
and from which data?

## Tools

| Tool | Use |
| --- | --- |
| [`census.py`](census.py) | One fresh home per case (the silent home's settings, firmware and clock file; `ss.cart` set; a backup-RAM fixture under the image's save name); cold boot, screenshots, no input |
| `tools/mednafen/frame_capture.py` | The cold boot with screenshots. Copied unchanged from MSHvSF at `d95a62a` |
| `tools/mednafen/backup_ram.py` | The fixtures. Copied from MSHvSF at `447e573`; corrupted byte made a parameter; the one-block case fixed (it computed a negative size) |
| [`boot_dump.py`](boot_dump.py) | Cold boot in a case home, then WRAM-L/H dumps and optional breakpoint logs |
| `research/experiments/EXP-0051/cold_walk.py` | Key presses on each warning (it gained a `COLD_WALK_HOME` override) |
| [`render_bmp.py`](render_bmp.py) | Draws a 4-bit BMP as a PNG, for the screen no case could trigger |
| `tools.sh2.disasm` | The boot check |

## Inputs and Provenance

- Untouched image, Track 01 `c904a386…da70`. `CPK.PCA` `8d24cb95…`,
  `CPK.EMM` (= `EMM.BIN`) `f534297e…`; `ERR1`-`ERR5.BIN` `4b0ffd3e…`,
  `0d891367…`, `4e4f9424…`, `d2c36a03…`, `d7905109…`.
- Save name for this image (every built image uses the same):
  `X-Men vs. Street Fighter (Japan) (3M).cead02d9d3cc1b97c82dbf063fba19bf`.
  No case created a file under another name.
- Fixtures (SHA-256 of the `.bkr` written): `valid` `7263ccd8…` (a copy of
  the silent home's save: one file, `XMEN_VS_SF_`, 992 bytes, from block 2,
  the layout `backup_ram.py` assumes), `zero` `c3502047…`, `corrupt`
  `973d2e71…` (`valid`, block 5 byte 20 inverted, inside the game's file),
  `free509` `df2b92f2…`, `free19` `3442edc9…`, `free18` `9740050e…`,
  `free17` `6ec49670…`, `free0` `4eca3e35…`.

## Procedure

```bash
C="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0053/census.py "$C" local/boot001/c2
./invenv.sh python research/experiments/EXP-0053/census.py "$C" local/boot001/c3 \
  cs1ram16_valid extram1_valid --first 600 --last 12000 --step 600 --parallel 2
H=local/boot001/c2/homes
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$C" $H/none_valid local/boot001/d_none 1200
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$C" $H/backup_valid local/boot001/d_backup 1200
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$C" $H/extram4_zero local/boot001/d_zero 1500
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$C" $H/extram4_corrupt local/boot001/d_corrupt 2400
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$C" $H/extram4_free18 local/boot001/d_free18 2400
# key presses: each case home with the route's key map (local/boot001/press_homes/<case>)
COLD_WALK_HOME=$PWD/local/boot001/press_homes/extram4_zero ./invenv.sh python \
  research/experiments/EXP-0051/cold_walk.py "$C" local/boot001/press_extram4_zero \
  wait:1800 shot:warn keys:a wait:300 shot:a300 wait:900 shot:a1200
for n in 1 2 3 4 5; do ./invenv.sh python research/experiments/EXP-0053/render_bmp.py \
  local/ref007/saturn_files/ERR$n.BIN local/boot001/err$n.png; done
```

The first census run (`c1`) stopped on the one-block fixture bug before
`free509`; its other eleven cases match `c2`.

## Actual Result

### The cases (`c2`, frame 3,600 unless noted)

| Case | Cart | Backup RAM | Screen | Screen SHA-256 | File in RAM at `0x06080000` |
| --- | --- | --- | --- | --- | --- |
| control | 4 MB | `valid` | normal boot (attract fight) | `d92881d1…` | — |
| no cart | none | `valid` | **warning A** | `fdd6ce8d…` | `ERR4.BIN` |
| backup cart | Backup Memory | `valid` | warning A (identical) | `fdd6ce8d…` | `ERR4.BIN` |
| 1 MB cart | 1 MB | `valid` | normal boot; attract with demo fights to frame 12,000 (`c3`) | `9626afd9…` | — |
| CS1 RAM | 16 MiB CS1 | `valid` | CAPCOM, then "NOW LOADING" to frame 12,000, no message (`c3`) | `ea9dd074…` | — |
| unformatted | 4 MB | `zero` | **warning B** | `26815f5e…` | `ERR1.BIN` |
| damaged save | 4 MB | `corrupt` | **warning C** | `8a03df41…` | `ERR2.BIN` |
| empty, formatted | 4 MB | `free509` | normal boot; the game writes its save | `1dec747b…` | — |
| 19 blocks free | 4 MB | `free19` | normal boot; save written | `d7b2ca09…` | — |
| 18, 17, 0 blocks free | 4 MB | `free18`, `free17`, `free0` | **warning D** | `eb804399…` | `ERR3.BIN` (`free18`) |

The file column compares the 42,358 bytes at `0x06080000` in each dump with
the five disc files: each equals exactly one.

### What a button does (`press_*`, A pressed at frame 1,800)

| Warning | After A |
| --- | --- |
| A (no cart) | The Saturn's own multiplayer (CD player) screen, "Start Application" |
| B (unformatted) | The same BIOS screen |
| C (damaged save) | The game goes on (CAPCOM logo) |
| D (no space) | The game goes on (CAPCOM logo) |

### The messages (the agent's transcription and translation)

| | File | Japanese | Agent's translation |
| --- | --- | --- | --- |
| A | `ERR4.BIN` | 警告 / 拡張ラムカートリッジ4MBが正しく差し込まれていません。 / 電源を切り、拡張ラムカートリッジ4MBを差し直してください。 | "Warning. The 4MB extended RAM cartridge is not inserted correctly. Turn off the power and reinsert the 4MB extended RAM cartridge." |
| B | `ERR1.BIN` | 警告 / 本体RAM（カートリッジRAM）のバックアップの準備がまだできていません（初期化されていません）。 / セガサターン本体の保存データ管理画面で全ての記録を消してください（初期化してください）。 / このまま何かボタンを押すと、マルチプレイヤー画面へ進みます。 | "Warning. The system RAM (cartridge RAM) backup is not ready yet (it has not been initialized). Erase all records on the Sega Saturn's save-data management screen (initialize it). If you press any button now, you will go to the multiplayer screen." |
| C | `ERR2.BIN` | 警告 / 記録を正しく読み込むことができませんでした。 / このままゲームをスタートした場合、以前のデータは使用されません。 / 何かボタンを押すと、ゲームがスタートします。 | "Warning. The record could not be read correctly. If you start the game now, the earlier data will not be used. Press any button to start the game." |
| D | `ERR3.BIN` | 警告 / 新しい記録を保存するための空き容量がありません。 / このままゲームをスタートした場合、セガサターン本体の保存データ管理画面で他の記録を消さない限り、新しい記録を保存することはできません。 / 新しい記録を保存するためには、16の空き容量が必要です。 / このまま何かボタンを押すと、ゲームがスタートします。 | "Warning. There is no free space to save a new record. If you start the game now, you cannot save a new record unless you erase other records on the Sega Saturn's save-data management screen. A new record needs 16 [blocks] of free space. Press any button now to start the game." |
| E (not triggered) | `ERR5.BIN` | 警告 / 拡張ラムカートリッジ4MBが差し込まれていません。 / 電源を切り、拡張ラムカートリッジ4MBを差し直してください。 | "Warning. The 4MB extended RAM cartridge is not inserted. Turn off the power and reinsert the 4MB extended RAM cartridge." |

A-D were read from the screenshots, E from the file drawn as a PNG
(`render_bmp.py`). The "16" in D is part of the picture (red); the game
warns at 18 free blocks and not at 19 (counted in 64-byte `.bkr` blocks).

### The boot check (code)

`CPK.PCA` is decoded into WRAM-H at `0x06022000`; its file table at
`0x06023D54` names `CPK.EMM`, `CPK.MAP`, `CPK.TSK`, `CPK.CPK` and, at
`0x06023D74`, `ERR1.BIN`-`ERR5.BIN` (16 bytes each).

- **`0x060228D4`** loads `CPK.EMM` into `0x06080000` and runs two tests:
  - the cart test (`0x06022042`, which calls `CPK.EMM`'s entry): −1 shows
    index 4 (`ERR5`), −2 shows index 3 (`ERR4`); both then wait for a
    button and leave the game (`0x060220D0`);
  - the backup-memory test (`0x06022760`): −1 shows index 0 (`ERR1`),
    then leaves; −2 shows index 2 (`ERR3`) and −3 index 1 (`ERR2`), and the
    game goes on after a button.
- **`0x060221E0`** shows `ERR` index r4: it loads `0x06023D74` + 16 × r4
  into `0x06080000` (`0xA576` bytes) and draws it; r5 = 1 means "leave
  afterwards".
- **`CPK.EMM`** reads the cart ID at `0x24FFFFFF` four times:
  - unequal reads: −1;
  - `0x5A` (1 MB): a RAM test at `0x22400000`/`0x22600000`; failure gives −1;
  - `0x5C` (4 MB): a 4 MB test, then a 1 MB test (treated as 1 MB), then
    the CS1 test;
  - any other ID, or the 4 MB fallback: a RAM test at
    `0x24400000`/`0x24600000` (A-bus CS1). Failure returns −2 straight to
    the caller (its `pr` pop skips the −1 mapping).

  So no cart (steady ID, no RAM) and the backup cart give −2 (`ERR4`, "not
  inserted correctly"); the 1 MB cart passes; the 16 MiB CS1 RAM passes
  the CS1 test.

### Other messages in the data, not triggered

| Where | Text | Status |
| --- | --- | --- |
| File `0` (loaded at `0x06008000`), string table `0x06008328`-`0x0600837C` | "FILE LOAD ERROR", "FILE STATUS:", "READ ERROR", "ILLIGAL FILENAME", "FILE NOT FOUND", "BAD RECORD", "NO DISK SPCAE", "WRITE PROTECT", "NAZO ERROR" and others | Already English (developer text, a disc file-system error). Needs a disc read failure, which Mednafen does not produce from a good image |
| File `0`, `0x060138D0` | `ERRBKUPJ.FHD`, `ERRINITJ.FHD`, `ERRLOADJ.FHD`, `ERRERAMJ.FHD` | File names only; no such files on the disc, and no code address refers to them (literal search of WRAM-H). Likely unused library data |
| `MMPACK.PCA` (decoded) | "CPU ADDRESS ERROR", "DMA ADDRESS ERROR", "0 DIV ERROR"; "EEPROM ERROR", "RAM ERROR"; an arcade rating notice | Already English; exception and arcade test text. Not boot messages; not triggered |

The Saturn BIOS's screens (the multiplayer screen after warnings A and B)
are not the game's and are left out.

## Conclusion

**CONFIRMED:**

- The game shows four boot-time warnings in Mednafen: no cart or a backup
  cart (A, `ERR4.BIN`), unformatted backup memory (B, `ERR1.BIN`), a
  damaged save (C, `ERR2.BIN`), and too little free space, at 18 blocks or
  fewer (D, `ERR3.BIN`). A and B leave to the BIOS after a button; C and D
  continue.
- A fifth, E (`ERR5.BIN`, "not inserted"), is chosen by the code when the
  cart ID reads unsteadily or a 1 MB cart fails its RAM test. Mednafen's
  carts produce neither.
- The 1 MB cart and the 16 MiB CS1 RAM pass the check (the latter then
  hangs on "NOW LOADING" with no message).

**DISPROVEN for XvSF** (MSHvSF's mapping): no cart shows `ERR4`, not
`ERR5`; a 1 MB cart shows no warning, not `ERR4`.

## Uncertainty and Alternatives

- **E on real hardware:** HYPOTHESIS. It could be shown in Mednafen only by
  a code or RAM change (`BOOT-002`'s controlled change).
- **"16" in D:** the picture's number and the observed threshold (19
  blocks of 64 bytes) differ; the game or BIOS may count blocks another
  way. Not needed for a translation of the text as written.
- **Drawn as it is:** that the screen is the file drawn as it is (not
  re-coloured or cropped) is `BOOT-002`'s.
- **Developer English messages** were not triggered.

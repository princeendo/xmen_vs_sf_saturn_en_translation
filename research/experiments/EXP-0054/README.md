# EXP-0054 (Boot): Where the Boot Warnings Are Stored and How They Are Drawn

Task: BOOT-002
Status: DONE
Confidence: CONFIRMED (each claim below by a controlled change or an exact
pixel comparison, unless marked)

## Observation

`EXP-0053` (D-049): the boot check loads `ERRn.BIN` into WRAM-H `0x06080000`
and shows it; four warnings appeared in Mednafen (`ERR1`-`ERR4`), and the
code chooses a fifth (`ERR5`) for conditions Mednafen cannot make. Whether
each screen is its file drawn as it is was open.

## Hypothesis

Each warning screen is its `ERRn.BIN` picture drawn unchanged, so changing a
file's pixels changes that screen there and nowhere else.

## Controlled Changes

1. **A test build** (`build/boot002_markers`, from the untouched source):
   `ERR1`-`ERR5.BIN` replaced by copies with a band of colour index 14 in
   picture rows 40n to 40n + 3, columns 8-343 (`markers.py`). Nothing else on
   the disc changes.
2. **`ERR5` by a code change in RAM:** with no cart (cart test −2), a `pc`
   breakpoint at the boot check's entry `0x060228D4` writes `8905` over
   `8908` at `0x060228FA` (decoded `CPK.PCA` `0x8FA`, checked), so the −2 branch
   goes to the −1 branch, which shows index 4 (`ERR5.BIN`).

## Prediction

1. On the test image each warning differs from the untouched image's only in
   its band's screen rows, in index 14's colour; the normal boot is unchanged.
2. The forced branch loads and shows `ERR5.BIN` (the marked one on the test
   image).

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Untouched Track 01 | `c904a386…da70` |
| `ERR1`-`ERR5.BIN` | `4b0ffd3e…`, `0d891367…`, `4e4f9424…`, `d2c36a03…`, `d7905109…` |
| Case homes | `local/boot001/c2/homes/<case>` (`EXP-0053`) |
| Untouched screens | `local/boot001/c2/<case>/f00003600.png`, `local/boot001/press_<case>/shots/warn.png` |

## Tools

| Tool | Use |
| --- | --- |
| [`compare_screen.py`](compare_screen.py) | A screenshot against a BMP, with the row shift and the game's colour rule |
| [`markers.py`](markers.py) | The marked `ERR` files and their change list |
| `tools.disc.patch_image`, `tools.disc.sector` | The test image; EDC/ECC |
| `research/experiments/EXP-0053/census.py`, `boot_dump.py` | Boots and dumps (`boot_dump.py` gained VDP dumps and `onhit:` writes) |
| `tools.sh2.disasm` | The display code |

## Procedure

```bash
U="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$U" \
  local/boot001/c2/homes/none_valid local/boot002/v_none 1500
./invenv.sh python research/experiments/EXP-0054/compare_screen.py \
  local/boot001/press_none_valid/shots/warn.png local/ref007/saturn_files/ERR4.BIN
./invenv.sh python research/experiments/EXP-0054/markers.py local/boot002/markers
M=local/boot002/markers; T="X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
./invenv.sh python -m tools.disc.patch_image --source-dir local/disc_images/xmvsf_saturn_jp_3m \
  --manifest references/saturn_jp/README.md --track "$T" \
  --file "ERR1.BIN;1" --data $M/ERR1.BIN --file "ERR2.BIN;1" --data $M/ERR2.BIN \
  --file "ERR3.BIN;1" --data $M/ERR3.BIN --file "ERR4.BIN;1" --data $M/ERR4.BIN \
  --file "ERR5.BIN;1" --data $M/ERR5.BIN --out-dir build/boot002_markers
./invenv.sh python -m tools.disc.sector "build/boot002_markers/$T"
N="build/boot002_markers/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0053/census.py "$N" local/boot002/m1 \
  extram4_valid none_valid backup_valid extram4_zero extram4_corrupt extram4_free18
H=local/boot001/c2/homes/none_valid
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$U" $H local/boot002/e5_untouched 1500 \
  pc:060228D4:060228D4 onhit:060228D4:060228FA:8905
./invenv.sh python research/experiments/EXP-0053/boot_dump.py "$N" $H local/boot002/e5_marker 1500 \
  pc:060228D4:060228D4 onhit:060228D4:060228FA:8905
```

## Actual Result

### The drawing path (code and VRAM)

- **Load:** `0x060221E0` loads `ERRn.BIN` (raw, `0xA576` = 42,358 bytes)
  into `0x06080000`, then `0x060220FC` draws it.
- **Palette** (`0x060220FC`-`0x06022154`): from file offset 54 (after a
  40-byte info header) it reads 256 four-byte entries (B, G, R, x) and
  writes one word each to colour RAM `0x25F00000`. Only entries 0-15 are the
  file's palette; 16-255 come from the pixel data and are never shown.
- **Colour conversion** (`0x060220DC`): `(B & 31) << 10 | (G & 31) << 5 |
  (R & 31)`, the **low** five bits of each 8-bit channel, not the high five.
  So `f8` shows as `c0`, `78` as `c0`, `40` as `00`, `28` as `40`. The
  screens are darker and differently coloured than the pictures were drawn:
  an original bug, faithfully emulated.
- **Pixels:** the routine at `0x06022156` unpacks the 4-bit rows (pixel
  offset from the little-endian long at file offset 10; bottom row first,
  width 352, stride 176) into an 8-bit bitmap in VDP2 VRAM from `0x0`, 512
  bytes per row. In the no-cart dump all 240 rows equal the file's, row y at
  `y × 0x200`, and nothing else is written there (`v_none/vdp2vram.bin`).
- **Position:** screen row y shows picture row y − 8. Screen rows 0-7 are
  black. **Corrected by `EXP-0056`:** the display is 224 lines (screen rows
  8-231; the screenshots pad 8 rows above and below), so picture rows
  224-239 are never shown, not only 232-239.

### Every pixel

`compare_screen.py` (screen against file, row shift −8, the game's colour
rule; 352 × 240 = 84,480 pixels each):

| Screen | File | Differing pixels |
| --- | --- | --- |
| no cart (`press_none_valid/warn.png`) | `ERR4.BIN` | 0 |
| unformatted (`press_extram4_zero`) | `ERR1.BIN` | 0 |
| damaged save (`press_extram4_corrupt`) | `ERR2.BIN` | 0 |
| 18 blocks free (`press_extram4_free18`) | `ERR3.BIN` | 0 |
| forced −1 branch, untouched image (`e5_untouched/screen.png`, `c33ad8bf…`) | `ERR5.BIN` | 0 |
| forced −1 branch, test image (`e5_marker/screen.png`, `c7a47d6f…`) | marked `ERR5.BIN` | 0 |

### The test build

- `build/boot002_markers`: the five files replaced (same sizes); 71,908
  sectors, 0 invalid. Marked file hashes and every changed row (offset,
  length, original and new SHA-256) are in `local/boot002/markers/changes.json`.
- Frame 3,600 of each case, test image against untouched:

  | Case | File | Rows that differ | Columns | New colour |
  | --- | --- | --- | --- | --- |
  | no cart | `ERR4` | 168-171 | 8-343 | `c00000` |
  | backup cart | `ERR4` | 168-171 | 8-343 | `c00000` |
  | unformatted | `ERR1` | 48-51 | 8-343 | `c00000` |
  | damaged save | `ERR2` | 88-91 | 8-343 | `c00000` |
  | 18 blocks free | `ERR3` | 128-131 | 8-343 | `c00000` |
  | control (4 MB, save) | — | none: `d92881d1…`, as the untouched image | — | — |

  Each band is exactly at picture row 40n + 8 on screen, as predicted.
- **`ERR5`:** with the forced branch the bytes at `0x060228FA` read `8905`
  at the end of both runs; the bitmap at `0x06080000` equals `ERR5.BIN` on
  the untouched image and the marked `ERR5.BIN` on the test image, whose
  screen shows the band at rows 208-211.

### The room for English

| | Value |
| --- | --- |
| File | raw, exactly 42,358 bytes (read as `0xA576`); BMP header 14 + 40 bytes, palette at 54, pixels at 118 (the game reads the offset at 10 and assumes the palette at 54) |
| Picture | 352 × 240, 4 bits per pixel, bottom-up, 176 bytes per row |
| Visible | all 352 columns; picture rows 0-223 (corrected by `EXP-0056`; this record first said 0-231) |
| Colours | 16 indices. The five files share one palette. As shown: 0 `000000`, 1 `404040`, 2 `000000`, 3 `000040`, 4 `000040`, 5 `c0c0c0`, 6 `c0c0c0`, 7 `000040`, 8 `000000`, 9 `008080`, 10 `00c0c0`, 11 `c0c000`, 12 `c0c000`, 13 `000000`, 14 `c00000`, 15 `00c000` (15 is unused) |
| Text area now | `ERR1` x 32-321, rows 26-207; `ERR2` x 47-308, rows 26-191; `ERR3` x 32-319, rows 26-207; `ERR4` x 70-284, rows 26-160; `ERR5` x 70-281, rows 26-160 (picture rows) |

The palette could be changed in an English file, since each file carries its
own: entries chosen for their low five bits would show the colours the
artist meant. Whether to keep the Japanese look or correct it is the user's
choice (`BOOT-003`, style).

## Conclusion

**CONFIRMED:**

- Each boot warning is its `ERRn.BIN` drawn unchanged into a VDP2 bitmap,
  shown 8 rows down; changing a file's pixels changes only that screen's
  matching pixels, and the normal boot is unchanged.
- `ERR5.BIN` is shown by the code's −1 branch; forcing that branch in RAM
  showed it, pixel for pixel.
- The game converts the palette from the low five bits of each channel.

## Uncertainty and Alternatives

- **Real hardware:** the colour rule is in the game's code, so the screens
  should look the same on a Saturn (HYPOTHESIS until seen).
- **Colour RAM** cannot be read through the agent; the rule comes from the
  code and the pixel comparisons, which match for 15 of the 16 indices
  (index 15 is used by no picture).

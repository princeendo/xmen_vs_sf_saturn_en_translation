# EXP-0019: Find the Quote Font and Prove Its Format

Task: FONT-001
Status: DONE
Confidence: CONFIRMED

## Observation

The quote is drawn by VDP1 from one 128-byte 4bpp cell per distinct glyph,
starting at `0x4A800` (`EXP-0015`). MSHvSF drew such cells from a compressed
font through a staging cell, and repacked its font byte-identically (MSHvSF
`EXP-0020`, `EXP-0023`). That is a HYPOTHESIS for XvSF.

## Hypothesis

A routine builds each glyph cell from a font image in RAM, and that image
comes from one disc file whose layout can be unpacked and repacked exactly.

## Controlled Changes

1. **Renderer.** A log-mode write breakpoint from `pre_quote`, on the VDP1
   cell and then on a candidate staging cell. Only reads, no change.
2. **Disc source.** A one-byte change to the candidate file, `FIX.PRS`, at
   the same size, against the original image as control. Both are cold-booted
   the same way: 60 s with no input, Start held 0.2 s, 6 s more, then the font
   region is read.

   | Field | Value |
   | --- | --- |
   | File offset | `0x1E0B7` in `FIX.PRS` (LSN 46,775) |
   | Original byte | `07` |
   | Modified byte | `F8` |
   | Purpose | The first pixel-value byte of glyph `0x09E1` (あ), compressed size 92 |
   | Expected | RAM font = the mounted image's `FIX.PRS` |
   | Observed | As expected |

## Prediction

- The writer of the staging cell decodes the font format reimplemented from
  its code, and the decoded cells equal the drawn ones.
- After a cold boot, the RAM font equals the mounted image's `FIX.PRS`, so
  the probe run differs from the control only at the changed byte.
- `font_pack` repacks `FIX.PRS` byte for byte.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Checkpoints | `pre_quote` `f00010285.mcs` and `quote_visible` `f00010336.mcs` (`EXP-0014`) |
| Session states | `f00005116.mcs` and the bisection range (`EXP-0013`) |
| Source image | Hashes match `references/saturn_jp/README.md` before and after (`local/logs/font001-source-after.json`) |
| Probe image | `build/font001_probe/`; probe `FIX.PRS` `c331883d…2948`, Track 01 `709627eb…` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/font.py`, `tools/text/font_pack.py` | Copied from MSHvSF `69c666c`. Only the docstrings and CLIs changed (no MSHvSF defaults left); the format code is unchanged. |
| `tools/sh2/disasm.py` | Disassembly |
| `tools/memory/vdp1_sprites.py` | VDP1 sprite list |
| `tools/disc/patch_image.py` | Probe image build |
| [`cell_check.py`](cell_check.py) | Compares decoded glyphs with the drawn cells |
| [`load_trace.py`](load_trace.py) | Cold-boot write log and bus reads |
| [`catch_font.py`](catch_font.py) | Halts on a write, after an injected Start |
| [`font_load.py`](font_load.py) | Start from a saved state, then read the font |
| [`cold_font.py`](cold_font.py) | Cold boot and Start, then read the font |
| [`build_font_probe.py`](build_font_probe.py) | Builds the one-byte probe `FIX.PRS` |

The key-press scripts use the scratch home `local/mednafen_keys_start`, with
pad Start bound to K. The user's homes are unchanged.

## Procedure

```bash
CUE="X-Men vs. Street Fighter (Japan) (3M).cue"; SRC=local/disc_images/xmvsf_saturn_jp_3m
./invenv.sh python -m tools.mednafen.replay_state "$SRC/$CUE" \
  local/checkpoints/dbg003/f00010285.mcs local/font001/stage_bp --steps 2 \
  --step-frames 60 --bp "write:06024DDC-06024E5B,26024DDC-26024E5B"
./invenv.sh python -m tools.sh2.disasm local/font001/s10336/wram_h.bin \
  --base 0x06000000 --start 0x06024CF0 --end 0x06024DDC
./invenv.sh python research/experiments/EXP-0019/cell_check.py local/font001/s10336
./invenv.sh python -m tools.text.font_pack local/ref007/saturn_files/FIX.PRS
./invenv.sh python research/experiments/EXP-0019/build_font_probe.py local/font001/probe
./invenv.sh python -m tools.disc.patch_image --source-dir $SRC \
  --manifest references/saturn_jp/README.md \
  --track "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin" \
  --file "FIX.PRS;1" --data local/font001/probe/FIX.PRS --out-dir build/font001_probe
./invenv.sh python research/experiments/EXP-0019/cold_font.py "$SRC/$CUE" local/font001/cold_orig
./invenv.sh python research/experiments/EXP-0019/cold_font.py "build/font001_probe/$CUE" local/font001/cold_probe2
```

## Actual Result

**The cell writer is not a CPU write.**

- From `pre_quote`, 120 frames: 0 CPU writes to cell `0x4A800`, although
  the cell changes by `quote_visible`.
- The glyph cell exists nowhere else, in any layout tried: the 4bpp cell,
  1bpp, nibble-swapped, single rows, and 8×8 quadrants.
- But the *last* glyph's cell (`0x4B200`) is also at WRAM-H `0x06024DDC`, a
  staging cell. The copy to VDP1 is presumably DMA (HYPOTHESIS).

**Glyph routine.** The staging cell's writes (2,719 logged) come from
`0x06024CF0` (code in R3). It takes the font base from the longword at
`0x0602586C` (`0x002C3EA0`, WRAM-L):

- **Location:** block table at base+16, one long per 16 codes; size table at
  base+16+`0x380`, one byte per code; the sizes of earlier codes in the block
  are summed.
- **Size byte:** negative = raw 128 bytes, 0 = empty (cleared), positive =
  compressed.
- **Compressed glyphs:** a 16-bit mask, LSB first, selects bytes that give
  32 nibble masks (staging at `0x06024E5C`). Then 8 byte-columns are filled
  top to bottom, where bit 1 reads a new byte and bit 0 repeats the last.

**Code-to-glyph mapping** (`cell_check.py`, `quote_visible`): all **22 of
22** distinct codes in record 10 decode, through the WRAM-L font, to the
drawn VDP1 cells byte for byte. That is 21 compressed glyphs (with
anti-aliasing and the `F` shadow) plus `0x0020`, which is empty.

**Font image.**

- 209,285 bytes, with code count `0x0E00` (all 224 blocks) and a 16-byte
  header of zeros plus the count.
- 3,458 compressed, 21 raw and 105 empty codes.
- It equals the file **`FIX.PRS`** (LSN 46,715, SHA-256 `68032831…0bab`) from
  offset 0 to its end. The file is stored uncompressed despite the extension.
- **Repack:** `font_pack` unpacks and repacks it **byte-identically**.
- The `0x09E0`-`0x0A7F` atlas shows the hiragana and katakana in Unicode order.

**When it loads.**

- Bisection of the `EXP-0013` states: absent at 5116 (attract), present at
  5169, after the user pressed Start.
- At 5116, a full copy is already in cart RAM at extracted offset
  `0x346490`. Cart extraction is HYPOTHESIS (`EXP-0005`).
- Replaying a Start press from 5116 fills `0x002C3EA0` with the font. With the
  probe image mounted, it still loaded the *original* font: run 1's Start
  didn't register, and run 2 loaded the original. The copy comes from memory
  held in the state, not from the disc.
- A halt on the first write to the font header, from 5116 with Start, caught
  the CD-port copy loop at `0x06013120` (source `0x25818000`). But it was
  writing other data (`DD680315…`), not the font. The region is a shared
  buffer.
- 30 s of cold boot: only the BIOS clear writes the header word.

**Disc source (controlled).** Cold boot and Start, reading `0x002C3EA0`:

| Image | Runs | RAM font |
| --- | --- | --- |
| Original | 1 | = original `FIX.PRS` |
| Probe | 2 valid (a third could not focus the window; no key was sent) | = probe `FIX.PRS` (`c331883d…`); differs from the original only at `0x1E0B7` |

In the states saved after Start, the cart copy at `0x346490` equals each
image's file only up to offset `0xB2C0`. Beyond that, other data had
replaced it by then.

## Conclusion

**CONFIRMED:**

- The win-quote font is the file **`FIX.PRS`**, loaded unchanged to WRAM-L
  `0x002C3EA0` (font pointer at WRAM-H `0x0602586C`).
- Glyphs are built by `0x06024CF0` into the staging cell `0x06024DDC`, in the
  format above.
- The format model is proven by a byte-identical repack.
- The code-to-glyph mapping matches 22 of 22 drawn cells.
- A one-byte disc change appears in the loaded font from a cold boot.

## Uncertainty and Alternatives

- **Cart route:** the font passes through cart RAM, but when it is read from
  disc into the cart, and what copies it to WRAM-L, are not traced
  (cart extraction is unvalidated).
- **Copy to VDP1:** from the staging cell to the VDP1 cells, not traced
  (DMA or slave CPU).
- **Visible effect:** the probe's change was checked in RAM, not on screen.
  The decoder predicts it (`change.json` holds the cells before and after).
- **Other fonts:** whether `FIX.PRS` serves surfaces other than win quotes is
  not tested.
- **Latin glyphs:** `FONT-002`.

## Reproduction

Run the procedure. Expect:

- staging writes from `0x06024D28`-`0x06024DC0`;
- 22/22 exact in `cell_check.py`;
- `"identical": true` from `font_pack`;
- RAM font = each image's `FIX.PRS`.

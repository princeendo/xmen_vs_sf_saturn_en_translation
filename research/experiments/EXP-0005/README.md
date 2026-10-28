# EXP-0005: Validate the Save-State Extractor on XvSF

Task: DBG-001
Status: DONE
Confidence: CONFIRMED (WRAM-L, WRAM-H, VDP1 VRAM, VDP2 VRAM); HYPOTHESIS (cart RAM)

## Observation

`AGENTS.md` allows extracted state data as evidence only for regions matched
byte for byte against a stock debugger dump of the same paused instant on
XvSF. MSHvSF validated `tools/memory/mcs_extract.py` on MSHvSF (MSHvSF
`DBG-012`, `EXP-0008`) and found each stored 16-bit element byte-swapped;
here that is a hypothesis.

## Hypothesis

For a state saved during a frame-advance freeze, `mcs_extract` (default
`saturn` byte order) reproduces the stock debugger's dumps of the same freeze
exactly for WRAM-L, WRAM-H, VDP1 VRAM and VDP2 VRAM.

## Controlled Change

None to the emulator, image or configuration. The extractor was copied
unchanged from MSHvSF `69c666c` with a provenance note. Its region table
(variables, element width, sizes, bus bases) was re-checked against this
repository's Mednafen 1.32.1 source: `ss/ss.cpp` `WorkRAML`/`WorkRAMH`
(`uint16`, section `MAIN`), `ss/cart/extram.cpp` `ExtRAM` `LO`/`HI`
(`CART_EXTRAM`), `ss/vdp1.cpp` and `ss/vdp2.cpp` `VRAM` (`VDP1`, `VDP2`).

## Prediction

Byte-identical output for all four regions; the `state` byte order equals the
dumps only after swapping each 16-bit pair.

## Inputs and Provenance

- Instant A: `EXP-0004` run A (title, 2026-10-28 20:36 UTC). State
  `local/emu007/run-a-state/…mc0`, 3,499,031 bytes, `62837cf2…fc3f`; dumps
  `research/memory_dumps/emu007/wraml-1.bin` (`e55529cf…bf94`) and
  `wramh-1.bin` (`a384c0ef…6702`).
- Instant G: run G below (20:56 UTC). State `local/dbg001/run-g-state/…mc0`,
  3,499,398 bytes,
  `95ac6a10a7c55fc9a7717d3fc1bff2da4874b534fbc61465a781cd898ec4699f`.
- Emulator, BIOS, home and source as `EXP-0004`.

## Tools and Environment

`tools/memory/mcs_extract.py` (copied), `tools/mednafen/hotkeys.py`.

## Procedure

Run G ([`steps/run-g.steps`](steps/run-g.steps)): freeze at 70 s, `F5`, open
the memory editor, and dump each space with a window capture confirming its
name (one `period` = Low Work RAM, two = High Work RAM, nine = VDP1 VRAM,
twelve = VDP2 VRAM):

```bash
find local/mednafen_quiet/sav -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/dbg001/run-g.log --script research/experiments/EXP-0005/steps/run-g.steps --keep-focus
./invenv.sh python -m tools.memory.mcs_extract STATE --out-dir research/memory_dumps/dbg001/run-g-saturn
./invenv.sh python -m tools.memory.mcs_extract STATE --byte-order state --out-dir research/memory_dumps/dbg001/run-a-state
cmp research/memory_dumps/dbg001/run-g-saturn/wram_l.bin research/memory_dumps/dbg001/g-wraml.bin   # and the others
```

## Actual Result

| Instant | Region | Debugger dump SHA-256 | Extracted (`saturn`) |
| --- | --- | --- | --- |
| A | WRAM-L | `e55529cf…bf94` | identical |
| A | WRAM-H | `a384c0ef…6702` | identical |
| G | WRAM-L | `e55529cf143e3424c2f5600bb8ce08a7b5c3c7d9013b46d2090e2e0c6276bf94` | identical |
| G | WRAM-H | `33ef8e04df206cab6865926a41e8caad173f88f8789de2c2bf555d83918b9a98` | identical |
| G | VDP1 VRAM | `29e5a4d08bb80562ea2481a62878788a4c7a531d23a8c46fede11d861f04799c` | identical |
| G | VDP2 VRAM | `d18de893a33b2c8378e84df71bf82f1563811deecc848cf2d6e4a04b54f23ad8` | identical |

- Instant A's `state`-order WRAM-L and WRAM-H differ from the dumps
  (749,332 and 550,662 bytes) and equal them after swapping every 16-bit
  pair: the state stores each element byte-swapped, as MSHvSF found.
- WRAM-H differs between instants A and G (3,990 bytes); WRAM-L is the same
  at both. The two instants are independent checks for WRAM-H.
- Captures confirmed the editor showed "Low Work RAM", "High Work RAM",
  "VDP1 VRAM" and "VDP2 VRAM" before each dump.
- Cart RAM was extracted (4 MiB, `c2dddda2…3b1b`, same at A and G, 2,109,318
  non-zero bytes) but cannot be validated: the stock memory editor has no
  cart space (MSHvSF `EXP-0007`; not re-listed here).
- Run G exited 0; source manifests identical before and after.

## Conclusion

**CONFIRMED** for XvSF: `mcs_extract` reproduces stock debugger dumps exactly
for WRAM-L and WRAM-H (two instants) and VDP1 and VDP2 VRAM (one instant).
These regions from states may be used as evidence. Cart RAM stays
**HYPOTHESIS**.

## Uncertainty and Alternatives

- VDP1 and VDP2 VRAM were validated at one instant only (the title screen).
- Both instants are on the title screen; other scenes were not tested.

## Reproduction

Run the procedure. Each `cmp` must report no difference.

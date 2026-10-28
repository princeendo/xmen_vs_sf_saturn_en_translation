# EXP-0002: Forced 4 MiB Cart and a No-Cart Control

Task: EMU-004
Status: DONE
Confidence: CONFIRMED

## Observation

In `EXP-0001`, `ss.cart auto` selected `Cart: 4MiB Extended RAM` and the game
reached its title screen. Mednafen 1.32.1's `src/ss/db.cpp` lists `T-1226G` as
`CART_EXTRAM_4M`, "Game requirement". The user states the game needs the 4 MB
cart (2026-10-27).

## Hypothesis

The game runs with an explicitly forced 4 MiB extended-RAM cart, and does not
run normally without a cart.

## Controlled Change

Only the command-line setting `-ss.cart`: `extram4` (three boots) or `none`
(one control boot). Binary, BIOS, home, source image, run length (90 s) and
the absence of input are the same as `EXP-0001`. The home's `sav/` was emptied
before each boot. Mednafen saved each value into
`local/mednafen_quiet/mednafen.cfg` on exit; `./invenv.sh python -m
tools.mednafen.home` restored `ss.cart auto` after every boot, and the file's
SHA-256 returned to `ef897288…5019` each time.

## Prediction

- `extram4`: the log shows `Cart: 4MiB Extended RAM`, and the frames equal
  `EXP-0001`'s, since `auto` already chose the same cart.
- `none`: the log shows no cart, and the game stops or shows an error before
  the title.

## Inputs and Provenance

As `EXP-0001`: source `local/disc_images/xmvsf_saturn_jp_3m/` (42
components), BIOS `sega_101.bin` (`dcfef4b9…deac`), stock 1.32.1 binary
(`892bb60a…29dd`), home `local/mednafen_quiet/`.

## Tools and Environment

`tools/mednafen/cold_boot.py` with its new `--setting KEY=VALUE` option, which
passes `-KEY VALUE` to Mednafen. Otherwise as `EXP-0001`.

## Procedure

```bash
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python -m tools.disc.hash_source --json \
  local/disc_images/xmvsf_saturn_jp_3m/* > local/emu004/source-before.json
for run in extram4_1:extram4 extram4_2:extram4 extram4_3:extram4 none_1:none; do
  rm -f local/mednafen_quiet/sav/*
  ./invenv.sh python -m tools.mednafen.cold_boot "$CUE" local/emu004/${run%%:*} \
    --seconds 90 --setting ss.cart=${run##*:}
  ./invenv.sh python -m tools.mednafen.home
  shasum -a 256 local/mednafen_quiet/mednafen.cfg
done
./invenv.sh python -m tools.disc.hash_source --json \
  local/disc_images/xmvsf_saturn_jp_3m/* > local/emu004/source-after.json
cmp local/emu004/source-before.json local/emu004/source-after.json
```

## Actual Result

| Run | Start (UTC) | Exit | Log cart line | Log SHA-256 | Frames equal to `EXP-0001` |
| --- | --- | ---: | --- | --- | ---: |
| `extram4_1` | 2026-10-28 19:37:09 | 0 | `Cart: 4MiB Extended RAM` | `e6581b03…9ea5` | 89 of 89 |
| `extram4_2` | 2026-10-28 19:38:50 | 0 | `Cart: 4MiB Extended RAM` | `0ae18a85…1b3a` | 89 of 89 |
| `extram4_3` | 2026-10-28 19:40:32 | 0 | `Cart: 4MiB Extended RAM` | `64fd7aea…cd41` | 89 of 89 |
| `none_1` | 2026-10-28 19:42:14 | 0 | `Cart: None` | `ec90dc6b…4152` | 14 of 89 |

- All four logs show `SGID: T-1226G`, `SGAREA: J`. Apart from the output-path
  and cart lines, the `extram4_1` and `none_1` logs are identical.
- Forced cart: every per-second frame equals `EXP-0001` boot 1, including the
  title (frame 070, `ebfbb7da…e662`) and the attract fight after it.
- No cart: frames 001-014 (BIOS and SEGA licence) equal `EXP-0001`. From
  frame 015 to 089 the screen is one static image (one distinct hash,
  `frames/015.png` `5af68833…f2c7`): a Japanese warning, reviewed by the
  agent. Transcription and the agent's translation:

  > 警　告 / 拡張ラムカートリッジ4MBが正しく差し込まれていません。 /
  > 電源を切り、拡張ラムカートリッジ4MBを差し直してください。
  >
  > "Warning. The 4MB extended RAM cartridge is not inserted correctly.
  > Turn off the power and reinsert the 4MB extended RAM cartridge."

- Source manifests identical before and after; the config hash was restored
  after each run.

## Conclusion

**CONFIRMED.** With `ss.cart extram4` the game logs the 4 MiB cart and runs
to the title and attract fight exactly as with `auto`. Without a cart it
stops at about 14 s on a cart-missing warning and does not reach the title.
The 4 MB cart is required, and `ss.cart auto` already provides it.

## Uncertainty and Alternatives

- Only `none` was tested as a control; other carts (`backup`, `extram1`)
  were not.
- The warning screen is a Saturn-only text surface with no arcade
  counterpart. Translating it is outside current scope; it belongs to the
  `REF-005` inventory.

## Reproduction

Run the procedure above. Evidence stays in the ignored `local/emu004/`
(`*/run.json`, `mednafen.log`, `frames/`, `sheet-*.png`; source manifests).
Expect `extram4_*` frame 070 to hash `ebfbb7da…e662` and `none_1` frame 015
to hash `5af68833…f2c7`.

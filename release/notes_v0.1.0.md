# X-Men vs. Street Fighter (Saturn) English 0.1.0

An English patch for the Japanese Sega Saturn release of X-Men vs. Street
Fighter (Redump disc 62395, T-1227G, version 1.002; the cart-bundle discs
1745 and 62394 share its track 01).

## What's in English

- Every character's win quotes and ending, in the official US arcade English.
- Apocalypse's boss boxes (a new translation) and Alpha Chun-Li.
- The attract captions, the continue hints and the "no challengers" sign, as
  in the US arcade.
- The boot warnings about the RAM cart and the save memory.
- **Names, your choice:** Options has a NAMES row: U.S. (default) for BISON,
  AKUMA and CHARLIE, or SATURN for VEGA, GOUKI and NASH, everywhere they
  appear (art, voice, text). Save it with BACK UP: SAVE.

The hidden COMBO GAGE option is kept, as COMBO GAUGE.

## Downloads

| File | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `xmvsf_saturn_en_0.1.0_xdelta.zip` | 3,852,177 | `8de3a7e6255d7cdcd4b14cef148e8ca25782102d2215fac2b4d7c564fb2c2ff4` |
| `xmvsf_saturn_en_0.1.0_ssp.zip` | 4,872,893 | `7347d30ed91c8ae367e703cdc66789c22cdf279b4c16e9a7acb810590360d7d0` |

Each zip holds the patch and a `README.txt` with the source and target
hashes. Only track 01 changes.

## Apply

See [`release/README.md`](https://github.com/princeendo/xmen_vs_sf_saturn_en_translation/blob/main/release/README.md):
xdelta3, or saturn-patcher-egui for the `.ssp`. Needs the 4 MB RAM cart.

## Known Limits

- The QSound notice after the credits keeps one Japanese trademark line
  (its English is on the same screen).
- Versus mode beyond its select screen was not surveyed.
- Full list: [`docs/coverage_exceptions.md`](https://github.com/princeendo/xmen_vs_sf_saturn_en_translation/blob/main/docs/coverage_exceptions.md).

# XvSF PlayStation: Secondary References

Secondary references only (`REF-006` decides whether the US English is a second
oracle). Do not assume PlayStation and Saturn structures are equivalent
(`AGENTS.md` rule 14). Never commit the images or anything extracted from them.

## Intake (`REF-002`, 2026-10-28)

Each user-supplied archive was listed with `bsdtar -tvf`, then extracted
unchanged with `bsdtar -xf` into its own new, empty, ignored folder.

| Archive | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `X-Men vs. Street Fighter (USA)-PS1.7z` | 212931976 | `42daa9e8b53740a7cf9c6eda57521fbac79bedd6535dc405eb66c5d87ab1a21e` |
| `X-Men vs. Street Fighter - EX Edition (Japan).7z` | 213045606 | `991f3ee79d4c2ec0d77853d124fe4a433d87025c0258053bca4f7d03fbf88f62` |

Components, hashed with `./invenv.sh python -m tools.disc.hash_source --json`;
CRC-32 and SHA-1 were computed separately for the catalog comparison:

| Folder | File | Size | SHA-256 | CRC-32 | SHA-1 |
| --- | --- | ---: | --- | --- | --- |
| `local/disc_images/xmvsf_ps1_us/` | `X-Men vs. Street Fighter (USA).bin` | 392393568 | `13e66a3e739cfdfca3801264b1aa7bc90136635becd71caa150056fa80d8b519` | `02cdbe88` | `c04bf74422c7e1cbb3b961528c38cd67b656856a` |
| `local/disc_images/xmvsf_ps1_us/` | `X-Men vs. Street Fighter (USA).cue` | 96 | `dc10746e19cbf5f6546b848c31b6c24f3f5ab95fe3e7179bd97364d30422f233` | `eb9e926c` | `a8cf841b80b1c6b9545eea0dffd94a6c039365ab` |
| `local/disc_images/xmvsf_ps1_jp_ex/` | `X-Men vs. Street Fighter - EX Edition (Japan).bin` | 392762832 | `b1f0049f844e51b927c0c0e33ad9e09d9f8da3b9946481cc4c7367fce868b107` | `7e7d62f4` | `3a5d5503a9a92a01fddb7be55b8e3aee0b636692` |
| `local/disc_images/xmvsf_ps1_jp_ex/` | `X-Men vs. Street Fighter - EX Edition (Japan).cue` | 111 | `99e5825b36803a519daae15b3a75c0ed7c626639d51038a87c98b0ca3d170935` | `3668cb90` | `d2ae2e0de7887cde91135dee02a21e56f174068e` |

Both images are one `MODE2/2352` track.

## Identity

Catalog: MAME 0.289 `hash/psx.xml` (`/opt/homebrew/share/mame/hash/psx.xml`,
SHA-256 `d5c9acd791513686a6e94061f2efb49f0c46d13260aa0465ade8ebe84a0fbc1f`).

- **US: CONFIRMED.** Software `xmvsf`, "X-Men vs. Street Fighter (USA)", serial
  `SLUS-00627`. The `.bin` and the `.cue` both match by size, CRC-32 and SHA-1.
  A text search of the image finds `BOOT = cdrom:\SLUS_006.27`.
- **JP EX Edition: UNKNOWN.** No file in MAME 0.289's `hash/` folder lists its
  CRC-32 or SHA-1, or an XvSF EX Edition entry. A text search of the image finds
  `BOOT = cdrom:\SLPS_012.84`. Identity is as named by the archive only.

These results equal what MSHvSF recorded for the same files on 2026-10-24.

## English Text (`REF-006`, `EXP-0010`)

`P/P4/SELECT.BIN` (LSN 142996, 167,108 bytes, SHA-256
`3fd5810b8f0cf6011a68b10478e407ed9597213008702932b0976d609d61e53c`) holds 293
of the arcade's 294 English records (`EXP-0008`), little-endian and
byte-identical: all win quotes and endings in arcade order, the arcade hints
less one record, and a second hint set with 7 PS1-only records. The arcade's
"coming soon" line and its Spanish, Portuguese and Japanese tables are not on
the disc.

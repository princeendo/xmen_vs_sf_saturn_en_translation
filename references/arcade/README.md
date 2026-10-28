# XvSF Arcade (CPS-II): Reference Sets

The arcade release is the translation oracle (`docs/localization_policy.md`). It
is evidence, never a template for Saturn structures (`AGENTS.md` rules 14-15).
Permitted provenance and factual metadata only; never commit ROMs or keys.

## Intake (`REF-001`, 2026-10-28)

The user supplied 11 zips and 6 keys in `~/Downloads/xmvsf/`. They were copied
unchanged (`cp -p`, then `cmp` against the originals) to the ignored
`local/arcade_roms/xmvsf/` and `local/arcade_roms/xmvsf/keys/`. Per-file size,
SHA-256 and per-member SHA-1 are in [`manifest.json`](manifest.json).

Pinned catalog: MAME 0.289 (Homebrew `/opt/homebrew/bin/mame`). The set
definitions are `mame -listxml 'xmvsf*'`, saved as the ignored
`local/logs/ref001-listxml.xml`, SHA-256
`af77657f205dce52dbcaca12e873474677441bf66157b367307e13af92f28f32`.

Matching is by SHA-1 only (`tools/reference/listxml_match.py`), so older set
names and relabelled members are still identified:

| Held zip | MAME 0.289 set | Title |
| --- | --- | --- |
| `xmvsf.zip` | `xmvsf` | X-Men Vs. Street Fighter (Europe 961004) |
| `xmvsfa.zip` | `xmvsfa` | (Asia 961023) |
| `xmvsfar1.zip` | `xmvsfar2` | (Asia 960919) |
| `xmvsfb.zip` | `xmvsfb` | (Brazil 961023) |
| `xmvsfh.zip` | `xmvsfh` | (Hispanic 961004) |
| `xmvsfj.zip` | `xmvsfjr2` | (Japan 961004) |
| `xmvsfjr1.zip` | `xmvsfjr3` | (Japan 960910) |
| `xmvsfjr2.zip` | `xmvsfjr4` | (Japan 960909) |
| `xmvsfr1.zip` | `xmvsfr1` | (Europe 960910) |
| `xmvsfu.zip` | `xmvsfu` | (USA 961023) |
| `xmvsfur1.zip` | `xmvsfur1` | (USA 961004) |

- Every member of every zip matches a MAME 0.289 ROM entry; none is unmatched.
- Relabelled members: `xmvsfar1.zip` (`xvsa.03e`/`04e`), `xmvsfj.zip`
  (`xvsj.03i`/`04i`), `xmvsfjr1.zip` (`xvsj.03d`/`04d`), `xmvsfjr2.zip`
  (`xvsj.03c`/`04c`, `xvs.05`/`06`), and `xmvsfur1.zip` (`xvsu.03h`/`04h`)
  carry older names; their SHA-1 values match the 0.289 entries.
- MAME 0.289 sets not held: `xmvsfj` (Japan, current), `xmvsfjr1`,
  `xmvsfar1`, `xmvsfar3`, `xmvsfur2`, and the bootleg `xmvsfu1d`.

Keys, by SHA-1 against the same catalog:

| Key | Used by (MAME 0.289) |
| --- | --- |
| `xmvsf.key` | `xmvsf`, `xmvsfr1` |
| `xmvsfa.key` | `xmvsfa`, `xmvsfar1`, `xmvsfar2`, `xmvsfar3` |
| `xmvsfh.key` | `xmvsfh` |
| `xmvsfj.key` | `xmvsfj`, `xmvsfjr1`-`xmvsfjr4` |
| `xmvsfu.key` | `xmvsfu`, `xmvsfur1`, `xmvsfur2` |
| `phoenix.key` | `xmvsfu1d` (bootleg); not needed |

`xmvsfb.key` (Brazil) is not held.

## MAME Use

MAME finds sets by name, so the ignored `local/arcade_roms/xmvsf_mame0289/`
holds copies of the zips under their 0.289 names, each key in a folder named
after every held set that uses it, and `qsound.zip`. `qsound.zip` (2,676 bytes,
SHA-256 `55feb9b70dacb7364f0310ed16cc9281b5b0a31318b9e2e0587ae06d15f95356`) was
copied from the MSHvSF ignored `local/arcade_roms/mshvsf/`.

```bash
mame -rompath local/arcade_roms/xmvsf_mame0289 -verifyroms 'xmvsf*'
```

Result: **10 of 11 romsets OK**. `xmvsfb` fails only for `xmvsfb.key - NOT FOUND`.

Headless boot (`tools/reference/mame_snap_frames.lua`, copied from MSHvSF):

```bash
SNAP_FRAMES="1200 3000" mame xmvsfu -rompath local/arcade_roms/xmvsf_mame0289 \
  -video none -sound none -nothrottle -skip_gameinfo -nomouse \
  -cfg_directory local/mame_arcade/ref001/cfg \
  -nvram_directory local/mame_arcade/ref001/nvram \
  -snapshot_directory local/mame_arcade/ref001/snap \
  -homepath local/mame_arcade/ref001 \
  -autoboot_script tools/reference/mame_snap_frames.lua
```

| Set | Frame | Screen (agent-reviewed) | 384x224 PNG SHA-256 |
| --- | ---: | --- | --- |
| `xmvsfu` | 1200 | Capcom logo | `381fd6597c06181623921a0f6891798003ef3bee446c199176823eba8c7a3577` |
| `xmvsfu` | 3000 | Title, `INSERT COINS` | `e8a8ab8ec057ee6659348d5c2c869c0f84752c0b99b6f1a360314d092bfb9ba3` |
| `xmvsfjr2` | 1200 | Attract fight (Ken, Gambit) | `2be9853241e5ff5aeb1737ada0dd0bf0158e0f30df906ed54572329381428db9` |
| `xmvsfjr2` | 3000 | Attract, copyright notice (English) | `e19f6bae78b185c906788124abcc6a1be0f8c77b8b3fdfec60759f08ae81f1fb` |

Both runs exited 0. Both frame-3000 hashes equal the values MSHvSF recorded on
2026-10-24 for the same sets, so the headless boot is reproducible across the
two checkouts.

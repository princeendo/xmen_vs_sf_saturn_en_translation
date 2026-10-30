# EXP-0052 (Names): The Saturn-Names Variant

Task: LOC-006
Status: DONE
Confidence: see "Conclusion"

## Observation

- **`LOC-004`:** the user approved, under `GATE-TRANSLATION`, six name
  edits to the official English and four label switches for this variant,
  plus a new `Balrog` label for Magneto's page 3, written into a label
  entry that no script uses. The art and voice keep the Saturn's names.
- **`LOC-005`** (`EXP-0051`): the name variants are a build switch,
  `build_english --names`. The American variant's code patches are the
  only code difference between the variants.
- **The label list** (`EXP-0038`, `EXP-0043`): 40 entries of 16 cells in
  16-bit ASCII at decoded `MCED.SHP` `0x3DA8`, indexed by a byte in each
  script page word.

## Hypothesis

The variant needs no code change. Recompiling the six official records
with the name edits, switching the label bytes in the five English ending
scripts, and writing `Balrog` into an unused entry shows the Saturn names
in the English text and labels, with everything else as in the American
variant apart from its 10 name-site patches.

## The Unused Label Entry

- **Readers:** in the ending overlay (`MCED.SHP` at `0x060D2000`, RAM dump
  `local/end005/ram_p1`), the list's address (`0x060D5DA8`) is loaded at a
  single site, `0x060D5CF8`. It indexes the list with the byte at task +
  38, which `0x060D5CE4` stores from the script's page word. So a label is
  read only when a script page names it.
- **Scan:** every script of all 19 slots, in all four language headers
  (0, 2, 4, 6), parsed as in `EXP-0043`: 39 of the 40 entries are used.
  **Entry 9 (`Apocalypse`) is used by none.** The list is followed directly
  by code, so there is no free entry after it.
- **Choice:** `Balrog` is written into entry 9.

## Controlled Change

`data/translations/saturn_names.json` lists every edit; `tools/disc/names.py`
applies them under `build_english --names saturn`:

| Kind | Where | Edit |
| --- | --- | --- |
| Win quote | `MC11.SHP` (Cammy), English record 0, line 1 | Bison → Vega |
| Win quote | `MC11.SHP`, English record 4, line 1 | Bison → Vega |
| Ending | `MC0E.SHP` (Vega), English record 1, line 1 | Bison → Vega |
| Ending | `MC0E.SHP`, English record 4, line 1 | Bison → Vega |
| Ending | `MC10.SHP` (Nash), English record 1, line 1 | Charlie → Nash |
| Ending | `MC10.SHP`, English record 4, line 2 | Charlie → Nash |
| Label | slot 3 (Rogue) English script, page 1 | `0x13` Bison → `0x0F` Vega |
| Label | slot 7 (Magneto), page 3 | `0x0F` Vega → `0x09` (Balrog) |
| Label | slot 15 (Gouki), page 5 | `0x14` Akuma → `0x10` Gouki |
| Label | slot 16 (Nash), page 4 | `0x15` Charlie → `0x11` Nash (and the scene's end word) |
| Label | slot 16, page 5 | `0x27` Charlie's friend → `0x24` Nash's friend |
| Label entry | entry 9 (decoded `0x3EC8`) | `Apocalypse` → `Balrog` |

Each text edit replaces the one occurrence of the name in that line; the
build refuses a line that holds it zero or several times. Each label edit
must be found on exactly the listed pages.

## Prediction

- The six records compile to the approved lines and fit the 25-cell line.
- Cammy's forced quotes 0 and 4 read "Vega"; Vega's ending pages 2 and 5
  read "Vega"; Nash's pages 2 and 5 read "Nash"; the labels read `Vega`
  (Rogue p1), `Balrog` (Magneto p3), `Gouki` (Gouki p5), `Nash` and
  `Nash's friend` (Nash p4, p5).
- Against the American build, only `MMPACK.PCA` (its 10 name sites),
  `MC0E`, `MC10`, `MC11` (the edited records) and `MCED.SHP` (the label
  bytes and entry 9) differ.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source Track 01 | `c904a386…da70` (untouched) |
| Official English | `local/ref003/xmvsfu-68k.bin` (`1b1a5a26…2dd1`) |
| Specs | `roster_endings_v4`'s 35 specs (`data/regression/references.json`) |
| American build | `build/loc005_names_us` (`EXP-0051`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/disc/names.py`, `data/translations/saturn_names.json` | the edits |
| `tools.disc.build_english --names saturn` | the build |
| `research/experiments/EXP-0051/cold_walk.py` | cold boot to Cammy's first fight, with `save:` |
| [`quote_seeds.py`](quote_seeds.py) | Cammy's quote draws forced by seed, on the built image |
| `research/experiments/EXP-0047/run_endings.py`, `compare_pages.py` | the route to the edited endings |

## Actual Result

### The build

```bash
SPECS=$(python3 -c "import json;r=[x for x in json.load(open('data/regression/references.json'))['references'] if x['name']=='roster_endings_v4'][0];print(' '.join(r['specs']))")
./invenv.sh python -m tools.disc.build_english ${=SPECS} local/loc006/files_saturn \
  --patch-version 4 --names saturn --image build/loc006_names_saturn
./invenv.sh python -m tools.disc.sector "build/loc006_names_saturn/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
```

- **Image:** `build/loc006_names_saturn`, Track 01 `b11c8cd9…e26e`; 71,908
  sectors, 0 invalid.
- **Edited records** (`changes.json`, `saturn_name_records`):

  | File | English record | Source SHA-256 | Edit |
  | --- | --- | --- | --- |
  | `MC11.SHP` | 0 | `ef65f207…` | line 1 Bison → Vega |
  | `MC11.SHP` | 4 | `20a82ded…` | line 1 Bison → Vega |
  | `MC0E.SHP` | 1 | `cbb06028…` | line 1 Bison → Vega |
  | `MC0E.SHP` | 4 | `3b348951…` | line 1 Bison → Vega |
  | `MC10.SHP` | 1 | `6030a4ad…` | line 1 Charlie → Nash |
  | `MC10.SHP` | 4 | `bef07159…` | line 2 Charlie → Nash |

  Decoded from the built files, the six records read exactly as approved
  in `LOC-004`.
- **Files:** `MMPACK.PCA` equals the M8 build's byte for byte (no code
  change). `MC0E` `8ac63fff…`, `MC10` `15143957…`, `MC11` `b07c60ba…`,
  `MCED` `6184f150…`; every other file equals M8's and the American
  build's.
- **Against the American build, decoded:** the MC files differ only
  inside the six edited records; `MCED.SHP` only at the six label bytes
  (`0x296F`, `0x2ABB`, `0x2CE3`, `0x2D47`, `0x2D4B`, `0x2D4F`) and in
  entry 9 (`0x3EC9`-`0x3EDB`); `MMPACK.PCA` only at the 10 American name
  sites.

### Cammy's quotes, forced on the built image

```bash
N="build/loc006_names_saturn/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$N" local/loc006/cammy \
  wait:1800 await:local/loc005/title_ref.png:6000 wait:150 press:s:local/loc005/select_ref.png:15 \
  wait:60 keys:ur wait:60 shot:hover_cammy keys:a wait:120 keys:r wait:60 shot:hover2_ryu \
  keys:a wait:120 keys:a wait:150 shot:vs1 wait:450 shot:fight save:fight
./invenv.sh python research/experiments/EXP-0052/quote_seeds.py "$N" local/loc006/seeds1 \
  local/loc006/cammy/fight.mcs 0024FF1C 1300 1 2 3 4 5 6 7 8 9 10 11 12
./invenv.sh python research/experiments/EXP-0052/quote_seeds.py "$N" local/loc006/seeds_800 \
  local/loc006/cammy/fight.mcs 0024FF1C 800 1 9
```

- **Seed scan** (state seed 4387; Cammy and Ryu against Rogue and
  Chun-Li): the pointer gave English record 0 for seeds 1-3, 1 for 7-8,
  2 for 10, 3 for 4, **4 for 9**, 6 for 5, 7 for 6 and 11-12. At 1,300
  frames the screen had already moved to the next stage, so the screens
  were taken again at 800 frames.
- **Screens** (`seeds_800/s1.png`, `s9.png`, viewed by the agent): "Lord
  Vega must / be protected!" and "Vega and I will laugh / about this
  tonight...", in the English grid. The other records drawn are unedited
  (the decoded `MC11.SHP` differs from the American build's only in
  records 0 and 4).

### The edited endings, by the route on the built image

```bash
N="build/loc006_names_saturn/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0047/run_endings.py "$N" local/loc006/files_saturn/MMPACK.PCA \
  local/loc006/endings 3 7 14 15 16
./invenv.sh python research/experiments/EXP-0047/compare_pages.py local/loc006/endings \
  local/end012/compare.json local/end012/runs local/loc006/pages
```

All five runs passed their load checks on the first attempt. The sheets
`local/loc006/pages/s03`, `s07`, `s14`, `s15`, `s16.png` were viewed by the
agent, and each edited label row enlarged 3 ×:

| Ending | Page | Saturn-names build | US arcade (right of the sheet) |
| --- | --- | --- | --- |
| Rogue | 1 | label `Vega` | `Bison` |
| Magneto | 3 | label `Balrog` | `Vega` |
| Vega | 2 | "But Vega's Psycho Power / eventually overwhelmed" | "Bison's" |
| Vega | 5 | "Vega turns his attention / to taking the universe." | "Bison" |
| Gouki | 5 | label `Gouki` | `Akuma` |
| Nash | 2 | "Nash is taken hostage / by Shadaloo." | "Charlie" |
| Nash | 4 | label `Nash` | `Charlie` |
| Nash | 5 | label `Nash's friend`; "It must have been / Nash, his dog tags..." | `Charlie's friend`, "Charlie" |

Each matches the line or label approved in `LOC-004`.

**Unedited pages:** of the 19 unedited pages of these five endings, 18
are byte-identical to the American build's (`EXP-0051`, `local/loc005/pages`).
Rogue's page 3 started 120 frames later; viewed side by side, its text
and label are the same and only the picture's moment differs.

## Conclusion

**CONFIRMED:**

- **Unused entry:** the label list has one reader (`0x060D5CF8`), indexed
  by the script's label byte, and entry 9 is used by no script in any
  language. `Balrog` written there shows on Magneto's page 3.
- **The variant:** `build_english --names saturn` builds it from the
  untouched source with no code change. The six edited records read as
  approved on Cammy's forced quotes and on the routed endings, and the
  five label switches show `Vega`, `Balrog`, `Gouki`, `Nash` and `Nash's
  friend`.
- **Nothing else:** against the American build, the decoded files differ
  only in the edited records, the label bytes, entry 9 and the American
  build's 10 name sites. `MMPACK.PCA` equals the M8 build's, so the art
  and voice are the Saturn's own (VEGA, GOUKI, NASH; `EXP-0048`, D-044).

## Uncertainty and Alternatives

- **Art and voice** were not shown again on this image: its code equals
  the M8 build's byte for byte, where `EXP-0048` observed them.
- **The other win quotes and endings** were not run on this image; their
  files are byte-identical to the American build's, which `EXP-0051` ran.
- **Entry 9** keeps no `Apocalypse` label. No script uses it now; a
  future script that wanted it would need another entry.
- **The boss stage's Japanese boxes** are `SPECIAL-001`'s, as in the
  American variant.

## Reproduction

The commands are in "The build", "Cammy's quotes, forced on the built
image" and "The edited endings" above. The unused-entry scan:

```bash
./invenv.sh python - <<'PY'
import sys; sys.path.insert(0, "research/experiments/EXP-0043")
from census_scripts import parse, word, labels
from tools.disc.build_english import read_file
from tools.disc.english_mode import MCED_SCRIPTS, MCED_RELOCATION
from tools.disc.prs import decompress_file
m, _ = decompress_file(read_file("MCED.SHP;1"))
used = set()
for s in range(19):
    base = int.from_bytes(m[MCED_SCRIPTS + 4 * s:MCED_SCRIPTS + 4 * s + 4], "big") + MCED_RELOCATION
    for lang in range(4):
        for scene in parse(m, base + word(m, base + 2 * lang))["scenes"]:
            used |= {p["label"] for p in scene}
print([i for i in range(40) if i not in used])
PY
```

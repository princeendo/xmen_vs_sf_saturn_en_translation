# Character Names Across Releases (`REF-007`)

Which names the Saturn shows, which the arcade English uses, and where they
differ. Evidence: `EXP-0011`. Policy (`docs/localization_policy.md`): American
names by default, both variants built.

## Names That Differ

| Character | Saturn (observed) | Arcade JP set | Arcade US set (art) | Arcade English text | Status |
| --- | --- | --- | --- | --- | --- |
| Akuma / Gouki | **GOUKI**: select label (`f00007661.png` `132c3d60…1d03`), VS screen and win banner (`f00011244.png` session) | **GOUKI** select label (`xmvsfjr2` frame 2650, `0b34de80…91d5`) | **AKUMA** select label (`xmvsfu` frame 2650, `79b2962c…d3f9`) | not named in any quote, ending or hint | **Differs, observed** |
| Charlie / Nash | **NASH**: select label (`f00018389.png` `12e4796c…5695`) | not observed | not observed | **Charlie** (2 mentions) | **Differs** (Saturn art vs arcade English text) |
| M. Bison / Vega (Shadaloo's leader) | not observed | not observed | not observed | **Bison** (4 mentions) | Expected to differ; Saturn side **UNKNOWN** |
| Shadaloo (organization) | Japanese text only | — | — | **Shadaloo** (2) | Same romanization in the English; Saturn not checked |

The arcade's region ROMs also hold a 16-bit name list that contains both
conventions side by side (`Vega`, `Gouki`, `Nash`, `Bison`, `Akuma`, `Charlie`)
plus speaker labels. It is identical in every region, so it does not show which
name a region displays.

## Names That Match Where Observed

Saturn and US arcade art agree on CYCLOPS, WOLVERINE, STORM, SABRETOOTH,
GAMBIT, MAGNETO, RYU and KEN (select labels). The Saturn session also showed
ROGUE and CHUN-LI (VS screen, win banner) as in the arcade name lists. Not yet
observed on any screen: Juggernaut, Dhalsim's label, Zangief, Cammy and
Apocalypse. Dhalsim and Sabretooth appear in the US win banner (`EXP-0009`).

## Latin Names Found In Game Data

- **Ending speaker labels** (`EXP-0034`, `EXP-0035`): Nash's ending shows
  Latin labels above the text box: `Nash`, `Nazo no koe` (romanized
  Japanese) and `Nash's friend`. With the global language word set to 2 in
  RAM, a `Charlie` label appeared on one page. So the Saturn game holds at
  least one American-name label, chosen by language. Where those labels
  are stored, and whether `Akuma` and `Bison` labels exist too, is not yet
  traced (`END-003`, `LOC-001`).

## Not Examined

- **Voice.** Whether the Saturn announcer or victory voices speak these names,
  and in which convention, was not checked (no audio analysis yet). MSHvSF's
  disc held both conventions' voice clips; for XvSF that is a hypothesis
  (`LOC-001`).
- **Assets on the Saturn disc.** The disc holds no name as plain text in any
  tested encoding (8-bit or 16-bit ASCII). The names are art. Whether
  American-name art is also on the disc is `LOC-001`.

## Options and Costs (for the American-default policy)

The default is already decided (American names, both variants). The open
question is cost, which depends on `LOC-001`.

| Variant | What changes | Cost if the American art and voice are already on the disc | Cost if they are not |
| --- | --- | --- | --- |
| American (default) | Gouki→Akuma, Nash→Charlie, Vega→Bison on select labels, VS screen, win banners, life bars and any spoken name; the English text is already American | Point the game at the existing assets (MSHvSF did this for its game) | New art drawn in the existing font style for three names on four surfaces; voice either left Japanese-convention or re-recorded |
| Saturn names (alternative) | Art unchanged; the English text's 6 American mentions (Charlie ×2, Bison ×4) edited to Nash and Vega | Small text edits per record (within the 25-code lines) | Same |

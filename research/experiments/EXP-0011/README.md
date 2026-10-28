# EXP-0011: Character Names Across Releases

Task: REF-007
Status: DONE
Confidence: CONFIRMED (Gouki/Akuma art by region; Saturn GOUKI and NASH; English text names); UNKNOWN (Bison/Vega on the Saturn, arcade art for Charlie and Bison, voice)

## Observation

The policy sets American names as the default (`docs/localization_policy.md`).
Which names differ between the Saturn and the US arcade, and on which surfaces,
was unknown. MSHvSF's differences (Vega/Bison, Gouki/Akuma) are a hypothesis
here.

## Hypothesis

The Saturn shows the Japanese-convention names (Gouki, Nash, Vega) where the
US arcade shows Akuma, Charlie and Bison.

## Controlled Change

None; observation of recorded screens, MAME runs and data.

## Prediction

Saturn select labels read GOUKI and NASH; the US arcade select label reads
AKUMA, the JP arcade GOUKI; the arcade English text uses Charlie and Bison.

## Inputs and Provenance

The `EXP-0007` Saturn session screenshots. MAME 0.289 runs of `xmvsfu` and
`xmvsfjr2`. The decoded arcade English (`EXP-0008`). The Saturn data-track
files, extracted with `tools/disc/iso9660.py` (236 files) to the ignored
`local/ref007/saturn_files/`.

## Tools and Environment

ffmpeg crops of the select-screen label area; `tools/reference/mame_timeline.lua`
select-screen routes (timelines in ignored `local/ref007/sweep*/`).

## Procedure

1. Crop the name label (bottom-left of the select screen) from all 31
   select-screen frames of the Saturn session.
2. MAME, both sets: four coins, Start, then cursor moves with a snapshot
   after each; crop the labels.
3. Count name variants in the decoded English (win quotes, endings, hints)
   and in the Spanish and Portuguese text.
4. Search every Saturn file for each variant as 8-bit and 16-bit
   big-endian text.
5. Decode the arcade region-ROM name lists (8-bit near `0x1CC2D`, 16-bit at
   `0x503E4`) in the US, EU and JP sets.

## Actual Result

- **Saturn labels** (agent-read): STORM, GOUKI, CYCLOPS, **NASH**,
  SABRETOOTH, WOLVERINE (frames listed in `docs/names.md`).
- **MAME:** labels appeared only during the partner-select phase of run 1,
  frames 2560-2650. US: GAMBIT, SABRETOOTH, MAGNETO, **AKUMA**. JP: GAMBIT,
  SABRETOOTH, MAGNETO, **GOUKI**. Both: CYCLOPS, WOLVERINE. A second sweep
  (down-first) showed no labels during cursor moves.
- **English text:** Bison 4, Charlie 2, Shadaloo 2; Akuma, Gouki, Vega and
  Nash 0. Spanish and Portuguese: Bison 8, Charlie 4, Shadaloo 4.
- **Saturn files:** no name variant as text in any file.
- **Arcade name lists:** identical in US, EU and JP. The 16-bit list holds
  both conventions and speaker labels.

## Conclusion

**CONFIRMED:**
- Gouki (Saturn, JP arcade) and Akuma (US arcade) differ in on-screen art.
- The Saturn shows NASH where the arcade English text says Charlie.
- The arcade English uses Bison.

The Saturn's name for Bison/Vega and the US arcade's art for Charlie and
Bison are UNKNOWN. So is voice.

## Uncertainty and Alternatives

- The label crops read only the select screen; VS screens and life bars for
  Charlie and Bison were not captured on either platform.
- Whether Bison/Vega is selectable or appears only as an opponent was not
  established here.
- Names may also appear in endings' speaker labels; not inventoried.

## Reproduction

Re-crop the listed Saturn frames; rerun the MAME select route (run 1 of
`research/experiments/EXP-0011/timelines/select-sweep.txt`) and crop frame 2650.

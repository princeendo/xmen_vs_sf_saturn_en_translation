# EXP-0055 (Boot): Official English for the Boot Warnings, and the User's Wording

Task: BOOT-003
Status: DONE
Confidence: CONFIRMED (no official English found in the sources searched;
the user's decisions recorded verbatim)

## Observation

`EXP-0053`/`EXP-0054` (D-049, D-050): five boot warnings, `ERR1`-`ERR5.BIN`,
each a 352 × 240 4-bit picture drawn unchanged, 8 rows down, through a
palette conversion that keeps each channel's low five bits. The policy
asks for official English where it exists, otherwise a recorded new
translation approved by the user.

## Official English: the searches

| Source | What was searched | Result |
| --- | --- | --- |
| US arcade (`local/ref003/xmvsfu-68k.bin`) | ASCII runs with WARN, ERROR, MEMORY, INSERT, CARD, SAVE | Only coin prompts ("INSERT COIN"…) and test-mode text ("MEMORY CHECK", "RAM ERROR", "EEPROM ERROR", "WARNING/"). The arcade has no cart or save memory, so it has no such message; no wording is shared. |
| US PlayStation release (`SLUS-00627`, `local/disc_images/xmvsf_ps1_us/`, `13e66a3e…b519`) | ASCII runs with memory card, format, block, save, load | Capcom's own English for the nearest messages in this game: "MEMORY CARD IS UNFORMATTED.", "YOU CAN NOT SAVE THE GAME DATA." / "UNLESS YOU FORMAT THE MEMORY CARD.", "AN ADDITIONAL 1 BLOCK OF FREE" / "MEMORY IS REQUIRED TO SAVE", "THE FILE COULD NOT BE LOADED", "MEMORY CARD IS NOT INSERTED!" (image offsets `0x140836e4`-`0x14083784`). Not the same messages; the terms "saved data", "free" and "loaded/read" were taken as Capcom's register. |
| Saturn BIOS, Japanese (`sega_101.bin`, `dcfef4b9…deac`) and US (`mpr-17933.bin`, `96e106f7…266f`) | ASCII runs | Both hold English menu labels: "Start Application", "Manage Memory", "Memory Manager", "Cartridge", "Clear", "Settings"; the US BIOS also "Not Formatted", "available". |
| The screens a player reaches (Mednafen, untouched image, unformatted-memory case, `local/boot003/bios1`, `bios2`) | After warning B: A, then the "Manage Memory" icon | The CD-player menu ("Start Application", "Manage Memory", "Hide Controls"), then **Memory Manager** with **System Memory**, "Remove Item", "Clear", "Exit", "System Settings". |
| MSHvSF's approved English (`data/ui008/error_screens.json` there, read only) | Its five screens | Offered to the user as an option, labelled as MSHvSF's. |

No official English exists for these warnings: XvSF had no US Saturn
release, and no other release has these messages.

## The Proposal

`draft.json`: a new translation by the agent, 27 characters a line at most,
with the BIOS's labels ("Memory Manager", "System Memory") and Capcom's
PlayStation register. `render_samples.py` drew it with the `FIX.PRS` quote
font (12-pixel pitch, the game's English quote pitch; 14-pixel lines) in two
looks: the Japanese palette kept, and the palette corrected for the game's
colour rule. Each screen was checked to fit (no line wider than 336 pixels,
nothing below picture row 231) and shown beside the Japanese original as the
game shows it (the redrawn originals equal the real screenshots pixel for
pixel). The sheets (`local/boot003/sheet_s_jp.png`, `sheet_s_fix.png`) were
sent to the user.

```bash
./invenv.sh python research/experiments/EXP-0055/render_samples.py research/experiments/EXP-0055/draft.json local/boot003/s_jp
./invenv.sh python research/experiments/EXP-0055/render_samples.py research/experiments/EXP-0055/draft.json local/boot003/s_fix --palette corrected
```

## The User's Decisions (2026-10-30)

| Question (short) | Answer (verbatim) |
| --- | --- |
| Approve the proposed English as a new translation (by Claude, with each Japanese screen's hash), with the BIOS labels and Capcom's PlayStation wording, "16" kept? | "Approve (Recommended)" |
| Which look: match the Japanese (palette kept, as dim as the originals) or corrected colours? | "Match Japanese (Recommended)" |
| What should the English call the "multiplayer screen" the unformatted warning leads to? | "control panel (Recommended)" |
| `ERR5`: "insert" or the literal "reinsert"? | `"insert" (Recommended)` |

The approved lines are `data/translations/boot_warnings.json` (the draft
unchanged, with the full source hashes and the style).

## Conclusion

**CONFIRMED:** no official English exists for the five boot warnings in the
sources searched. The user approved the agent's translation and the
Japanese look, recorded under `GATE-TRANSLATION` (boot-warnings extension)
and in `docs/localization_policy.md`.

## Uncertainty

- **The "16" blocks** stays as the original says, though the game warns
  below 19 of Mednafen's 64-byte blocks (`EXP-0053`).
- **The font** is the win-quote font; its full stop is a small low mark, as
  in the game's own English quotes.

# XvSF Saturn Text Surfaces (`REF-005`)

From one recorded user play session (`EXP-0007`, 2026-10-28 21:13-21:22 UTC,
frames 142-30380): boot, attract, arcade mode with one fight won, one lost with
a continue, a second loss to game over, and the options screen. All 514
screenshots (414 unique) were reviewed by the agent. Screenshot paths are
under the ignored `local/ref005/session1/shots/`. Game text is not copied
into this repository; short descriptions only.

## Surfaces With Japanese Text

| Surface | Screen | When shown | Sample (frame, SHA-256) | Arcade English? |
| --- | --- | --- | --- | --- |
| Attract captions | Full-screen white captions on black, 4 of them, with `PRESS START BUTTON` | Attract loop, between demo scenes, before the title | `f00002911.png` `8df6be82…54ca`; `f00003266.png` `f084289e…19ed`; `f00003507.png` `4a20498e…3c34`; `f00003740.png` (a scrolling caption) `062412e4…4e0a` | **Yes, observed.** The US set `xmvsfu` (MAME 0.289, headless attract) shows English captions in the same attract slots: frames 1800, 4950, 5550 and a scrolling one at 2400/5850 (`3028bcc1…114d`, `d51aac57…5495`, `d79e03e1…3a5c`, `7576c6d8…f8eb`, `cd5818b2…e521`). The JP set `xmvsfjr2` shows Japanese captions there. Caption-by-caption pairing is by order: **HYPOTHESIS**. |
| Win quotes | Winners' portraits over a comic-page background; two lines of Japanese in a speech bubble at the bottom | After a won match (player or CPU), before the next stage or the continue screen | Player win (Ryu/Gouki team) `f00011244.png` `8428bf99…11a6`; CPU wins (Chun-Li/Rogue) `f00016690.png` `a47e1671…a687`, `f00023880.png` `380c0656…7358` | **Yes, observed.** 161 English win-quote records in the arcade ROM (`EXP-0008`); the US arcade draws them exactly (`EXP-0009`). |
| Continue hints | `CONTINUE?` countdown (English art) with a boxed two-line Japanese gameplay tip below; tips include inline arrow icons | Continue screen after a lost match; the tip differed between the two continues | `f00016985.png` `a62c0cb9…19f0`; `f00024184.png` `3acb5a7f…1ad8` | **Yes, observed.** 23 English hint records (`EXP-0008`); the US arcade draws them as two-line pages (`EXP-0009`). Two match the Saturn hints seen here in content. |
| Boss pre-fight line (Apocalypse) | Two-line Japanese box at the top of the screen, over the stage, before Apocalypse transforms | Start of the final stage, before the fight (`EXP-0032` play session) | `f00058252.png` `5a42fbbf…2fa8` (frames 58,191-58,366, `local/re010/session`) | **UNKNOWN**; not yet looked for (`SPECIAL-001`) |

## Nash's Ending and the Run-Up to It (`END-001`, `EXP-0034`)

From the `END-001` session (2026-10-29 18:30-19:38 UTC, untouched image,
Nash and Ryu, `local/end001/session/shots/`). After Apocalypse, the two team
members fight each other; Nash's ending follows the player's win in that
fight. Every screenshot was checked by the agent.

| Surface | Screen | Frames | Sample (frame, SHA-256) | Japanese? |
| --- | --- | --- | --- | --- |
| Pre-boss story line | Win-quote layout (team portraits, bubble), two lines | ~210,184 | `f00210184.png` `4cfcc72e…68cd` | Yes |
| Post-Apocalypse win quote | Win-quote layout, two lines | ~217,028-217,265 | `f00217153.png` `f18a8c3c…919b` | Yes |
| "No challengers" warning | `⚠乱入禁止` sprite at top right, from the black pre-fight screen through the partner fight and its continue screen | ~216,914 to the end of the partner fight | `f00216914.png` `67335bfd…a64f`; in the fight `f00219310.png` `2f7e6207…8da8` | Yes |
| **Ending pages** | Six timed pages: picture window at top centre (black on pages 1, 2, 5), purple box at the bottom with 1-2 lines; full-width Japanese font | 220,539-222,930 | Page 1 `f00220654.png` `9d66b488…ddbd`; 2 `f00220887.png` `361438a2…48f6`; 3 `f00221112.png` `4c3ef8e4…3d8e`; 4 `f00221342.png` `388c0716…8dcc`; 5 `f00221690.png` `78a2207a…91df`; 6 `f00222037.png` `ab2f6006…fa94` | Yes |
| Ending speaker labels | Small Latin label above the box on pages 3-6: `Nash`, `Nazo no koe`, `Nash`, `Nash's friend` | 221,112-222,930 | as pages 3-6 | Latin letters; `Nazo no koe` is romanized Japanese ("mysterious voice") |
| QSound notice | Under `Presented by CAPCOM`: English notice plus one Japanese trademark line | ~226,838-226,953 | `f00226838.png` `fc75088a…b047` | One line |

Already English here: the staff roll (~222,981-226,589), `THANK YOU FOR
PLAYING / PRESENTED BY CAPCOM`, `GAME OVER`, initials entry and score
ranking. Pages and line counts: 1, 2, 1, 2, 1, 2 lines. Arcade English for
these surfaces is `END-004`.

## Surfaces Already In English (no Japanese seen)

Saturn BIOS and SEGA licence screens; Capcom logo; `NOW LOADING`; attract demo
fights with the copyright notice; title with `PRESS START BUTTON`; menu
(`ARCADE MODE`, `VERSUS MODE`, `OPTION MODE`); character select; mode select
(`NORMAL`/`AUTO`/`TURBO`); stage cards (number and name); versus screen with
names; fight HUD and callouts (`FIGHT!`, `FIRST ATTACK`, hit counts, `K.O.`,
`WIN`, `PERFECT`, bonus tally); `GAME OVER`; initials entry; score ranking;
`OPTION MODE` screen (every line was visited).

## Not Reached In This Session

Endings other than Nash's (reached in `EXP-0034`, above); boss and secret-character text;
versus mode screens; options sub-screens (button config, sound test, other
values); save/backup messages; the cart-missing warning (Japanese, seen in
`EXP-0002`); rare or region-gated text. Each needs its own capture before it
can be inventoried.

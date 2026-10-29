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

## Surfaces Already In English (no Japanese seen)

Saturn BIOS and SEGA licence screens; Capcom logo; `NOW LOADING`; attract demo
fights with the copyright notice; title with `PRESS START BUTTON`; menu
(`ARCADE MODE`, `VERSUS MODE`, `OPTION MODE`); character select; mode select
(`NORMAL`/`AUTO`/`TURBO`); stage cards (number and name); versus screen with
names; fight HUD and callouts (`FIGHT!`, `FIRST ATTACK`, hit counts, `K.O.`,
`WIN`, `PERFECT`, bonus tally); `GAME OVER`; initials entry; score ranking;
`OPTION MODE` screen (every line was visited).

## Not Reached In This Session

Endings and any story or pre-fight text; boss and secret-character text;
versus mode screens; options sub-screens (button config, sound test, other
values); save/backup messages; the cart-missing warning (Japanese, seen in
`EXP-0002`); rare or region-gated text. Each needs its own capture before it
can be inventoried.

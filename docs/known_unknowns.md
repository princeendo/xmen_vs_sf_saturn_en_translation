# Known Unknowns

Open questions about XvSF, each with its current evidence and the smallest
experiment that would answer it. Close an entry by linking the task or
experiment that answered it.

| Question | Current evidence | Smallest discriminating experiment | Task |
| --- | --- | --- | --- |
| ~~Does stock Mednafen boot this image, and with which cartridge setting?~~ | Answered: boots with `ss.cart auto` (4 MiB); without a cart it stops on a warning. | — | `EXP-0001`, `EXP-0002` (D-001, D-002) |
| Is this image a verified Redump dump? | Header, names and layout agree; the data track equals the earlier rip. No database hash compared. | Compare the track hashes with a Redump entry, or build a CHD and compare with MAME's `xmvssf`/`xmvssfdou`. | `ENV-007` |
| Where is the arcade's English text, and how is it encoded? | None for XvSF. MSHvSF's arcade text was unencrypted 16-bit codes in a program ROM (a hypothesis here only). | Locate known English strings in the decrypted program ROMs of the US set. | `REF-003` |
| Which text surfaces exist (win quotes, endings, story, attract, UI)? | Seen so far: Japanese attract captions (`EXP-0001`) and a cart-missing warning screen (`EXP-0002`). | One recorded play session from boot through one fight and a continue screen. | `REF-005` |
| Does XvSF use the same engine or text formats as MSHvSF? | No `.PAC` or `MEMFIX` file names on the data track (MSHvSF intake observation). | Answer each format question separately from runtime evidence; never by analogy. | various |

# RISKS (ranked; first register, Stage 00)

Ranked by how much each could block or mislead the project. Labels: VERIFIED, SUSPECTED, UNKNOWN.

| Rank | ID | Risk | Consequence | Label | Mitigation / next step |
|---:|---|---|---|---|---|
| 1 | R-01 | No real Android device and no attached computer | No on-device frame time, touch feel or thermal data can exist. The spec's 60 FPS claim can only be "BLOCKED/UNVERIFIED" | VERIFIED | You supply the phone model, or attach a machine; otherwise performance stays an explicit release blocker (spec stage 16) |
| 2 | R-02 | Godot, Unity and `adb` are not installed here; versions are unverified | Stage 06 comparison and any export test cannot run in this container | VERIFIED | Run engine work on your computer, or accept a Godot-only spike with the limitation recorded |
| 3 | R-03 | Outbound web is allowlisted. After the 2026-11-22 approval, 15 hosts work; TouchArcade (bot check), the Met (HTTP 429) and the content of the Apple developer pages (JavaScript) did not return text. Godot, Unity and Android developer hosts are not yet allowed | Stage 06 dated-docs checks cannot run until those hosts are added | VERIFIED | Request the Stage 06 hosts at Stage 06; label anything unread UNVERIFIED |
| 4 | R-04 | Citizens may be unreadable at real phone size in motion | The three behaviour profiles are the mechanic. If players cannot tell them apart, the game loses its "why" | SUSPECTED | In-engine test at 390×844 and 320×568 (Stage 10). Mockups only show them static |
| 5 | R-05 | Art direction converges too early | Three rounds were drawn before Stage 05; the last round was written to match a critique, so it may over-fit that critique | SUSPECTED | Keep D2 provisional; Stage 05 compares it with at least one genuinely different alternative |
| 6 | R-06 | Font and asset licences unchecked | A mockup font may not be distributable in a shipped game; Georgian glyph support untested | UNKNOWN | Source licensed fonts at Stage 05, check Georgian coverage before localisation |
| 7 | R-07 | The "ink wobble", paper tooth and halftone in the mockups are browser SVG filters | They are not proof that the look is cheap on a mid-range phone GPU | SUSPECTED | Treat as a Stage 10 performance item; reduce grain before gameplay information (spec E4) |
| 8 | R-08 | Spec ambiguities (Plaza vs Market in the camera path; 30 s deadline vs 32 s limit) | Wrong copy or a wrong camera anchor gets baked in | VERIFIED | Resolve in Stage 03 rules and Stage 04 copy |
| 9 | R-09 | Mock numbers in pictures (14/20, "78%", "5 waiting") look like results | They can be mistaken for simulation output | VERIFIED | Every sheet says "mock data"; real values only after Stage 08 |
| 10 | R-10 | Scope creep from the art rounds (a win screen, a replay, a system board) | Features appear that no stage has approved | SUSPECTED | They are pictures only; their gameplay equivalents wait for the stage that owns them |
| 11 | R-11 | Single-reviewer process | Approval gates rely on one person; no playtester data until Stage 17 | UNKNOWN | Do not call anything proven; label judgements as expert opinion |
| 12 | R-12 | Touch-target rule sources disagree: WCAG 2.2 AA is 24 CSS px (2.5.8), AAA is 44 (2.5.5); Android says 48dp; Apple's 44pt could not be read | A rule quoted as "required by WCAG" would be wrong; the 44pt/48dp floor is our own stricter design choice | VERIFIED | State it as a design rule at Stage 04, not as a WCAG requirement; read Apple's page at Stage 04 |
| 13 | R-13 | Visual overlap with Mini Metro and Mini Motorways (bold lines, flat minimalism) | The atlas view could read as a copy of a well-known look | SUSPECTED | See docs/DIFFERENTIATION.md section 4; compare at Stage 05 |

## Verified vs suspected code issues

There is no code, so there are no code issues. VERIFIED: nothing to audit. Do not read this as "the codebase is clean"; it means "there is no codebase yet".

## Manual checks I could not do (reproducible later)

- On-device frame time: needs an Android phone, a debug build and a capture tool. Test at Stage 06 and Stage 16.
- Source dates for Godot 4.7 and Unity 6.3 LTS: open the two release pages listed in the spec, section I, items 1, 2, 8, 9, and record the "date shown / date accessed" in `docs/SOURCES.md` at Stage 01 or 06.

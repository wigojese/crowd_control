# ART BIBLE (Stage 05: art direction competition)

Three complete visual systems, drawn on the same level (R1, goal 18 of 20) and the same five moments: menu, quiet planning, dense crowd, zoomed-out ribbons, result. Pictures: `docs/stage05-art/` (`d5-A.png`, `d5-B.png`, `d5-C.png`, `d5-compare.png`). Generators: `docs/stage05-art/*.js`. Status: **PROPOSED**. You choose one direction (CC-D-012). Everything is a **static mockup** with made-up numbers; nothing has been tested in motion, in an engine or on a phone.

Rules all three obey: no blue in the standard palette (the rule comes from your review documents; you have not confirmed it to me, AS-08); vermilion belongs to the sign; meaning never rides on colour alone; system insets are drawn in; every figure was drawn for this project (no copied assets).

## 1. The three systems

| | **A. Print atlas** (Civic Press) | **B. Fold-out paper theater** | **C. Transit score** |
|---|---|---|---|
| One line | Inked lines on warm map paper that briefly come alive | A pop-up book: flat paper street plan, standing landmarks, a signpost | A city read as a score at night: streets are staves, walkers are notes |
| Ground | Warm paper with world-anchored grain | Cream plate on a dark curtain | Warm black with static staff lines |
| Roads | Ink double stroke | Cut channel with a cream surface | One bright line plus two thin side lines |
| Walkers | Stamped figures: hat and briefcase; bobble hat with a trailing friend; leaning with a pack | Paper pawns: tall hat; round with a small friend; leaning with a pack | Notes: single; beamed pair; flagged with a dot |
| Sign | Heavy enamel arrow in a charcoal double-outline head with a foot tab | A standing signpost with a raised arrow board | A vermilion disc with a parchment arrow, a conductor's mark |
| Queues | Oxblood halftone mat | Oxblood hatched mat | Plum hatched ring |
| Zoomed out | Counted ink ribbons with arrows | Folded paper ribbons with fold lines | Beamed staff ribbons in amber and sage |
| Result | A printed proof slip with a stamp | A pulled-out ticket with a stamp | Arrivals as bars per 4-second measure |

### 1A. Print atlas

| Token | Value |
|---|---|
| Palette | Paper `#EDE1CC`, panel paper `#F7F0E3`, ink `#1E1A17`, vermilion (sign only) `#D6522F`, rust (route history) `#A86135`, oxblood (queues) `#7D3B42`, olive (Plaza, success) `#7A7B55`, mustard (School, goal) `#C39B34`, shadow paper `#DDCFB8`, stone `#A49A8B` |
| Road weight | Ink 11 px outer, paper 7.4 px inner; narrow 8 and 4.4 px; outlines 1.2–1.4 px |
| Grain | World-anchored dots, 5 px pitch, 7–9 % opacity, plus a static paper tooth. UI stays crisp |
| Silhouette size | 26 px street, 20 px district, none in the atlas (ribbons at least 3 px) |
| Label density | At most 6 in district view, 4 in the atlas |
| Shadow | Only a contact ellipse under the sign (12×3.4 px, 28 %) |
| Arrow | Vermilion arrow, charcoal circular head with a bright inner ring, foot tab, rim notch |
| State transitions | Lift 90–120 ms; snap 120–190 ms; turn 140–180 ms; ink tick at a changed decision at most 250 ms; retry fade 320 + 120 ms |
| Type | Display: editorial serif. UI: Inter. Numerals: JetBrains Mono, tabular |

### 1B. Fold-out paper theater

| Token | Value |
|---|---|
| Palette | Curtain `#4A2B2F`, plate `#F2E8D5`, cut channel `#DCC9A4`, ink `#231A17`, vermilion (sign) `#D6522F`, gold (landmarks, score) `#E0A21B`, sage (followers, Plaza) `#8E9A6B`, clay (independents) `#C48A73`, oxblood (queues) `#7D3B42`, moss (canal) `#4E4A33` |
| Road weight | Cut channel 11.4 px with a cream surface 8 px; 2 px shadow beneath |
| Grain | None; paper edges and soft shadows carry the material |
| Silhouette size | 24 px pawns with a drop shadow |
| Label density | Paper tags, at most 5 in district view |
| Shadow | Drop shadow dy 4 px, blur 2.6 px, 50 % on the plate and standing blocks (a real GPU cost) |
| Arrow | Raised vermilion board 3.6 px thick on a pole and base |
| State transitions | Plate unfolds on a hinge 550 ms; sign lifts 100 ms; snap 120–190 ms |
| Type | Display: heavy grotesk. UI: Inter. Numerals: JetBrains Mono |

### 1C. Transit score

| Token | Value |
|---|---|
| Palette | Night `#17120F`, panel `#100C0A`, stave (parchment) `#EFE3C8`, dim parchment `#B7A98F`, amber (School route) `#E6A532`, sage (Plaza route) `#A8B56A`, coral (market) `#E8765A`, vermilion (sign) `#E04E2D`, plum (queues) `#B8566F` |
| Road weight | Centre line 1.6 px, two side lines 1 px at ±3.2 px, halo 13 px at 10 % |
| Grain | None; static staff lines every 12 px |
| Silhouette size | Notes 18 px: single, beamed pair, flagged |
| Label density | Plain text with a dark halo, at most 6 |
| Shadow | None; a soft glow ring when the sign is lifted |
| Arrow | Vermilion disc, parchment arrow, rim notch |
| State transitions | A timeline playhead tracks the clock; sign lift 100 ms; snap 120–190 ms |
| Type | Display: very light grotesk (200) for numerals, 800 for the title. UI: Inter 600+. Data: JetBrains Mono |

### Typeface licences (what I could check)

| Font | Result |
|---|---|
| Inter and Inter Display | **VERIFIED from the installed font files**: "SIL Open Font License, Version 1.1" |
| JetBrains Mono | **VERIFIED from the installed font file**: SIL OFL 1.1 |
| Bitstream Charter (stand-in for A's serif) | **UNVERIFIED.** The file's licence field could not be read. Do not ship it unchecked |
| Replacement serif for A, display grotesk for B, light grotesk for C | **Candidates only, not checked.** An open-licence serif and an open-licence heavy grotesk must be sourced and checked at adoption. Georgian glyph coverage must also be checked (R-06) |

## 2. Scoring against the spec's rubric (B5)

These are **my judgements from static pictures**, not test results. Weights are the spec's: distinctiveness 30, causality readability 25, tactile satisfaction 15, production feasibility 15, contrast and accessibility 10, performance 5.

| Criterion (weight) | A | B | C | Why |
|---|---:|---:|---:|---|
| Distinctiveness (30) | 7.0 | 7.5 | 8.5 | C is the least like anything else I compared; B is distinctive but near the "cozy diorama" cliché; A is the most tasteful and the most familiar (paper map, transit-map overlap, R-13) |
| Causality readability (25) | 8.0 | 6.0 | 7.5 | In B the big gold School and the black works block are louder than the queue or the sign. C reads well but notes are small. A's ribbons, hatching and counts carry it |
| Tactile satisfaction (15) | 7.0 | 9.0 | 5.5 | B's signpost is the most "pick-up-able"; C is a diagram you watch |
| Production feasibility (15) | 8.5 | 5.0 | 7.0 | B needs pop-up art for every landmark and depth sorting; A and C are vector lines |
| Contrast and accessibility (10) | 7.5 | 6.0 | 5.5 | See the numbers in section 3 |
| Performance (5) | 8.0 | 5.0 | 8.5 | B's shadows; A's grain and ink wobble must be baked into textures |
| **Weighted total** | **7.58** | **6.70** | **7.28** | |

**Sensitivity:** A beats C by 0.30. If you weight distinctiveness more than 30 %, C overtakes A. If you value tactility more, B gains.

## 3. Tests run on the mockups

**Contrast** (WCAG relative-luminance formula, computed):

| Pair | Ratio |
|---|---:|
| A: ink on paper / soft black on paper | 13.36 / 8.50 |
| B: ink on cream / ink on gold / cream on curtain | 15.43 / 7.59 / 11.32 |
| C: parchment on night / dim parchment / amber / plum / faint grey | 14.60 / 8.04 / 8.67 / 4.07 / 3.15 |
| Vermilion sign against its ground: A paper / B cream / C night | 3.18 / 3.38 / 4.69 |
| C: parchment arrow on the vermilion disc | 3.11 |

C's plum is below 4.5 for small text, so it is for hatched fills only. C's sign arrow sits just above the 3:1 non-text floor; A's sign has a charcoal head and does not rely on the arrow-to-disc contrast.

**Grayscale and one-second look** (`d5-compare.png`, small grayscale mid-round): the sign was findable in all three. In A it is the dark disc, in B a mid-grey raised arrow, in C a mid-grey disc on black. The queue was visible as hatching in all three. The three walker types are not distinguishable at that size in any of them, which is the expected cost of semantic zoom.

**320×568** (`d5-*.png`, "Small phone"): all three fit the map and a one-line HUD, buttons stay at least 44 high. B's and C's labels get crowded near Canal Turn; A's "Canal Turn" label collides with a block outline at this size (fix at Stage 10).

**Identifiable without branding:** each sheet is recognisable as a different game with the title hidden. A and B share a warm paper look, which is closest to the problem R-13 describes.

**Copying check:** all shapes, glyphs and layouts were drawn for this project. The only third-party items are the installed stand-in fonts.

**Not tested** (needs motion, an engine or a phone): world-anchored grain stability, filter and shadow cost, daylight legibility of C, touch feel, real fonts.

## 4. Recommendation (judgement, not decided)

**Choose A as the base.** It scores highest under your own weights, is the cheapest to build and animate, reads best, and carries the most work already (the Stage 04 pictures are drawn in it). Its weakness is distinctiveness: it needs one memorable device. Two details worth borrowing, both separate from A's identity:
- **From C:** the timeline in the dock (a playhead and 4-second ticks) as the clock and lock indicator. It makes the 4 s lock legible at a glance.
- **From B:** nothing structural; if anything, only the idea of a deeper shadow under the sign while it is held.

Keep **C** as an optional dark theme later if daylight tests allow. It is the strongest "only this game" look, but it is the weakest in sunlight and for touch feel.

## 5. Provisional DO / DO NOT / objective tests (for A; confirmed only if you choose A)

| DO | DO NOT |
|---|---|
| Keep vermilion exclusive to the sign | Use vermilion for any other control or text |
| Draw roads as ink double strokes; keep static buildings subordinate | Put a building over a decision node (North Gate, Canal Turn) |
| Distinguish walker types by shape and grouping | Rely on colour to separate walker types or queues |
| Aggregate to counted ribbons in the atlas | Show tiny bodies on top of ribbons |
| Anchor grain to the world; keep the UI crisp | Put grain on text, the HUD or the dock |
| Keep misregistration on static fills only | Offset the sign, walkers or counters |
| Draw the system insets in every picture | Put a control in the top or bottom inset |

| Objective test | Pass condition |
|---|---|
| Grayscale | The sign, a queue and the two destinations can be identified in the grayscale mid-round at 390×844 |
| Small phone | At 320×568 every required control is at least 44 px and no label overlaps a decision node |
| Contrast | Body text at least 4.5:1; sign against its ground at least 3:1 |
| Palette audit | No blue, teal, cyan or navy anywhere, including charts and icons |
| Grain | No shimmer while panning at 60 FPS in the engine (Stage 10) |
| Silent view | In a 6-second muted recording, a stranger can point to the sign and to a rerouted walker |

## 6. Decision for you (CC-D-012)

Approve **one** direction, optionally with one named detail from another:
- **A**, with or without the timeline from C;
- **B**;
- **C**.

If none, say what to change; I will revise Stage 05 and not move on.

## 7. CHOSEN: Direction C, transit score (dark theme). DO, DO NOT and objective tests

Chosen by the user on 2026-11-23 (CC-D-012). The five moments, palette and tokens in section 1C are the working definition. Changes required before it is realised in the engine, from the tests in section 3:

| Change | Reason |
|---|---|
| Use plum `#B8566F` for hatched fills only, never for small text | 4.07:1 on night |
| Raise disabled-control text to at least 4.5:1 | the faint grey is 3.15:1 |
| Draw the sign arrow dark (`#17120F`) on the vermilion disc, keep the parchment ring | parchment on vermilion is 3.11:1; dark on vermilion is 4.69:1 |
| Add a high-contrast variant with thicker lines (staff lines off, 2.4 px centre line) | spec accessibility requirement and daylight risk R-21 |
| Make the notes at least 18 px and keep beamed pairs for followers | notes were the smallest marks in the mockups |

| DO | DO NOT |
|---|---|
| Keep vermilion exclusive to the sign | Use vermilion for any other control or text |
| Draw streets as one bright centre line with two thin side lines | Add glow or blur to roads |
| Separate walker types by note shape (single, beamed pair, flagged), not by colour | Colour-code walker types |
| Use amber for School-bound routes and sage for Plaza-bound routes, always with a shape cue | Use amber or sage as the only way to tell destinations apart |
| Show the clock as a timeline with 4-second ticks in the dock | Hide the lock timer |
| Keep staff lines static and anchored to the screen's map area | Animate or scroll the staff lines with the camera (shimmer risk) |
| Use Inter, Inter Display and JetBrains Mono (all verified SIL OFL) | Ship a font whose licence has not been read |
| Keep text at least 12.5 px and 4.5:1 | Put thin text (weight under 400) at body sizes |

| Objective test | Pass condition |
|---|---|
| Grayscale | The sign, a queue and both destinations are identifiable in the grayscale mid-round at 390×844 |
| Sunlight | On a real phone outdoors, a tester finds the sign and the queue within 3 seconds. **Not yet testable (R-01, R-21)** |
| Contrast | Body text at least 4.5:1; sign against its ground at least 3:1; plum never used for text |
| Small phone | At 320×568 every required control is at least 44 px and no label overlaps a decision node |
| Palette audit | No blue, teal, cyan or navy anywhere, including charts and icons |
| Silent view | In a 6-second muted recording, a stranger can point to the sign and to a rerouted walker |
| Fonts | Licence files for Inter, Inter Display and JetBrains Mono are in the repository; Georgian fallback chosen before localisation (R-22) |

# VISUAL IMPLEMENTATION (Stage 10)

Direction C (transit score, dark theme, CC-D-012) put into code. **No Godot has run, so there are no engine screenshots.** The pictures in `docs/stage10/` are drawn by `scripts/stage10_preview.py` from real runs of the Python reference model on level CC-L01-R1, and every one carries the line "PREVIEW FROM MODEL DATA, NOT ENGINE". They show the visual language on real data. They are not proof that the engine draws it.

## 1. Where each rule is implemented

| Rule (ART_BIBLE section 1C and 7) | Engine code (not run) | Picture reference (run) |
|---|---|---|
| Colours only from tokens, dark theme, high-contrast variant | `data/art_tokens.json`, `CcMapView._c()`; `H` key in `graybox.gd` | `v_highcontrast_t120.png`, `v_result_AE_highcontrast.png` |
| Streets as three-line staves (1.6 px centre, 1 px sides at 3.2 px) | `CcMapView._draw_streets` | all |
| Walkers as notes: single (commuter), beamed pair (follower), flagged (independent) | `CcMapView._draw_note` | `s2_run_AE_t120.png` |
| Queues as plum hatched bands; plum for fills only | `CcMapView._draw_queue` | `s3_run_nosign_t240.png` |
| Ribbons from counted flow; zero flow draws nothing; solid School, dashed Plaza | `CcRibbonModel.width`, `CcMapView._draw_ribbons` | `s4_result_AE.png`, `s5_result_nosign.png` |
| Sign: vermilion disc, dark arrow, rim notch; vermilion only for the sign | `CcMapView._draw_sign`; token `sign_arrow` | all |
| Labels as plain text with a dark halo | `CcMapView._label` | all |
| World-anchored texture: staff lines every 24 px of world space (C has no grain) | `CcMapView._draw_stave_grid` | faint lines in all |
| HUD type: Inter, JetBrains Mono numerals | **not implemented** (the engine's fallback font is used until font files are added, Stage 10b) | preview uses Inter and JetBrains Mono |
| No engine-default buttons | **not implemented**: the Restart, Pause and Try again buttons exist only in the pictures | pictures |
| Destination emblems (School, Plaza) | **not implemented in the engine** | drawn in pictures |

## 2. Five states shown (model data)

1 Placement (`s1_placement.png`); 2 Running with sign A/E at 0:06 (`s2_run_AE_t120.png`); 3 Running with no sign at 0:12, queues forming (`s3_run_nosign_t240.png`); 4 Result A/E, 20 of 20 (`s4_result_AE.png`); 5 Result no sign, 17 of 20, 1 short (`s5_result_nosign.png`). Side by side: `contact_five_states.png`.

## 3. What the checks found

| Check | Result |
|---|---|
| Contrast, standard and high-contrast themes: text 4.5:1, graphics 3:1, arrow on sign disc (`scripts/check_contrast.py`) | RAN, all 20 pass. Lowest: plum queue 4.07:1, vermilion sign on night 4.69:1 |
| **Colour-off separation** | The checker found amber (School) and sage (Plaza) differ by only **1.03:1** in luminance, so colour alone cannot tell the two routes apart. The pictures therefore draw School solid and Plaza dashed. `v_nocolor_*.png` use a grayscale filter (an approximation of "colour off") and the routes are still separable. Coral and amber are 1.37:1, so queue meaning rests on the hatch, which is a pattern |
| Ribbons never misrepresent flow | RAN: `scripts/ref_ribbon.py` 7 checks pass (zero flow draws nothing, width never falls as flow grows, counts only from `EDGE_ENTERED`). In the pictures the number on each ribbon is the counted flow |
| 320 px narrow check | The whole screen **scaled** to 320 px wide (`v_narrow320_*.png`), not a re-laid-out 320×568 screen. At that scale a note is about 15 px, **below the 18 px rule**, and queued notes at Canal Turn overlap. Failed the legibility target as drawn; needs a lower note count per node or a larger note at narrow widths |
| 15 s in-game capture, draw-order and performance delta against the graybox | **BLOCKED**: needs a runnable Godot, a display and a phone |

## 4. Draw order and LOD notes (proposed, untested)

Back to front: background; staff grid; street glow (10% stave); street lines; queue hatching; ribbons (zoomed-out view only, in place of walkers); node rings and emblems; walkers as notes; sign; labels; HUD in a separate layer. Level of detail: notes in the street and district views, ribbons only in the atlas view (Stage 11 decides the switch). The engine draws every item with `_draw` calls each frame, which is a **known cost risk**: the plan for Stage 16 is to cache static layers and batch walkers.

## 5. Asset licence list

| Asset | Source | Licence |
|---|---|---|
| All map drawing | Code, `CcMapView`; no image files | Project's own |
| Preview pictures and generator | `scripts/stage10_preview.py`, `docs/stage10/shot10.js` | Project's own |
| Inter, Inter Display, JetBrains Mono | System packages, used only in the preview pictures; **no font file is in the repo yet** | SIL OFL 1.1 (texts in `assets/fonts/licenses/`); Inter's file also lists Apache-2.0, unchecked (R-29) |

## 6. Departures from the master prompt

- The prompt asks for an "art-paper texture" and "world-anchored grain". Direction C was chosen with static staff lines instead of grain, so the texture is the staff grid.
- "Five real engine screenshot states" and "one 15 s in-game capture" are not met; the picture set is a preview from model data.

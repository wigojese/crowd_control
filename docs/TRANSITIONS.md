# TRANSITIONS (Stage 12)

Six transitions from master prompt matrix C4, as data (`data/transitions.json`) driven by one cancellable state machine. GDScript (**not run**): `src/camera/transition.gd`. Python reference (**run**): `scripts/ref_transitions.py`. Pictures and quarter-speed videos: `docs/stage12/` (model data, not engine; frame times are the reference driver's timeline at 30 fps, **not an on-device capture**).

## 1. Design rules (enforced by tests)

- **All game-state callbacks fire at START** (`on_start`): `level_ready`, `result_shown`, `reset_run`. Cancelling or skipping at any point cannot change a run, lose a result or send it twice. The result is on screen at 0 ms and watching the pullback is optional.
- **`on_end` is cosmetic and fires exactly once**, with a reason: completed, skipped, or cancelled (touch, app_background, app_interrupt).
- **A touch freezes the camera exactly where it is**; skip settles to the end over 100 ms. No transition blocks input, so control is back at 0 ms on skip (the 100 ms is only the picture settling). Limit is 150 ms.
- **Reduced motion** ends at once and is shown as a 150 ms crossfade.
- No black overlay track exists, and no per-millisecond jump appears in any track.
- **Animations cannot consume the action budget**: `CcTransition` has no command interface and no handle to the simulation (lint rule L10 keeps the camera package away from simulation classes).
- Auto-camera speed: average at most 1.2 viewport widths per second (468 px/s at 390 px). **Provisional, as the prompt says.** Averages: paper unfolds 356, consequence follows ink 412, outcome pullback 391 px/s. Peak speed is not limited (R-39).

## 2. Animation token table

| Transition | Trigger | Duration | Tracks (easing) | Game-state callback at start | Hooks | Skip | Reduced motion |
|---|---|---:|---|---|---|---|---|
| paper_unfolds | level_enter | 550 ms | cam_center cubic_out; cam_zoom cubic_out; streets_alpha cubic_out; labels_alpha cubic_out +250ms | level_ready | sound.paper_unfold, haptic.none | settle_to_end | crossfade |
| sign_drops | sign_release_on_socket | 170 ms | sign_scale spring; socket_glow cubic_out | none | haptic.sign_drop, sound.sign_drop | settle_to_end | crossfade |
| consequence_follows_ink | sign_changed | 800 ms | edge_highlight cubic_out; cam_path ease_in_out; cam_zoom linear | none | sound.ink_follow, haptic.tick | settle_to_end | crossfade |
| district_to_diagram | enter_atlas_band | 210 ms | agents_alpha cubic_out; ribbons_alpha cubic_out | none | sound.coalesce | settle_to_end | crossfade |
| outcome_pullback | level_end | 650 ms | cam_center ease_in_out; cam_zoom ease_in_out; ribbons_alpha ease_in_out +300ms | result_shown | sound.result, haptic.result | settle_to_end | crossfade |
| ghosted_rewind | retry | 440 ms | ghost_alpha cubic_out; settle cubic_out +320ms | reset_run | sound.rewind | settle_to_end | crossfade |

Global tokens: skip settle 100 ms, reduced motion 150 ms, speed limit 1.2 viewport widths per second.

## 3. Engineering asset per transition

| Transition | Before to after | Anchor ids | Cancel semantics | Focus order | Sound and haptic |
|---|---|---|---|---|---|
| paper_unfolds | zoom 0.72 to 1.15, centre (181, 262) to (136, 98); streets fade in over 200 ms, labels 250 to 450 ms | A, B | tap skips; a touch freezes | sign, then dock | paper sound, no haptic |
| sign_drops | sign scale 1.08 to 1.0 with a damped spring, minimum 0.991; no camera movement | socket | skip settles; the sign is already placed at t=0 | the sign | haptic and sound at the first frame |
| consequence_follows_ink | highlight edge A to C, camera along A, C, E at zoom 1.15 over 800 ms | A, C, E | pan or tap cancels; the sign disc stays visible (8 px minimum margin to the HUD) | changed edge, then reroute | tick and ink sound |
| district_to_diagram | agents and ribbons crossfade over 210 ms, total opacity always 1 | none | skip settles | none | coalesce sound |
| outcome_pullback | zoom 1.15 to 0.78, from the school to (181, 262) over 650 ms; ribbons fade in from 300 ms | F, the whole map | skip settles; result shown at t=0 | result, then map | result sound and haptic |
| ghosted_rewind | the old run's ink fades from 100% to 25% over 320 ms, then 120 ms settle; run reset at t=0 | whole map | skip settles | none | rewind sound |

## 4. Test results

`python3 -I scripts/ref_transitions.py`: 60 checks pass in the Python reference, including cancel, skip and app interruption at 0, 25, 50, 75 and 99% for every transition (four ways times five points, six transitions) and a mock-run check over those 120 combinations. The same rules are written as 8 GDScript tests in `tests/test_transitions.gd`; **they have not run.**

## 5. Not done

- No on-device capture or timing; the pictures are reference renderings. Real timings: BLOCKED (needs Godot, a display and a phone).
- Sound and haptic hooks are ids only; nothing plays them.
- Nothing in the engine starts these transitions yet; they are not wired to the game state machine.
- Reduced-motion crossfade is a rule, not a drawn effect.

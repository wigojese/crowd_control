# CAMERA AND SEMANTIC ZOOM (Stage 11)

Code (GDScript, **not run**): `src/camera/camera_transform.gd`, `camera_path.gd`, `zoom_bands.gd`, `camera_director.gd`. Python reference (**run**): `scripts/ref_camera.py`. Golden file: `tests/fixtures/camera_golden.json`. Pictures and video: `docs/stage11/`, all drawn from model data and marked "PREVIEW FROM MODEL DATA, NOT ENGINE". The `camera` layer sits below the simulation in `scripts/lint.py`, and rule L10 fails the build if simulation and camera reference each other, so the camera cannot change a run.

## 1. What exists

| Piece | Rule | Where |
|---|---|---|
| Transform | `screen = (world - center) * zoom + viewport_center + safe_offset`, plus the inverse; zoom limits 0.65 to 2.80; `zoom_about` keeps the pinch anchor fixed | `CcCameraTransform` |
| Safe composition | A focused junction is put in the free band between HUD and dock, never under the thumb | `compose_focus` |
| Camera path | Catmull-Rom spline through A, B, D, F, G (the real junctions of CC-L01-R1), arc-length table at 4 units spacing | `CcCameraPath` |
| Scrub | `delta_arc = -dy / zoom * 0.85`; inertia `v0 * exp(-6 t)`, capped at 1.6 viewport heights per second | `CcCameraPath.scrub_delta`, `inertia_velocity` |
| Zoom bands | CITY 0.65 to 0.92, DISTRICT 0.92 to 1.65, STREET 1.65 to 2.80; hysteresis: STREET in at 1.75 and out at 1.55, CITY in at 0.85 and out at 1.00 | `CcZoomBands.update` |
| Honest flux | Ribbons use the EDGE_ENTERED events of the last 20 ticks (1 s) only | `CcZoomBands.flux_window` |
| Level-of-detail plan | CITY: ribbons and congestion knots, no agents. DISTRICT: every active agent once, queue badges. STREET: agent detail. People count is always the number of active walkers. Every street stays visible | `CcZoomBands.lod_plan` |
| Director | Nine states from the master prompt; priorities TOUCH 3 > USER 2 > CRITICAL 1 > DECORATIVE 0; touch freezes the camera where it is; reduced motion jumps at once | `CcCameraDirector` |
| Narrow-phone rule (Stage 10 option B) | Notes stay 18 logical px; a queue of 4 (3 below 360 px wide) becomes one note plus a count badge | `CcZoomBands.cluster_badges`, `art_tokens.json` |
| Return to sign | `request_focus("SIGN_FOCUS", "USER", ...)`; accepted only when no finger is down | `CcCameraDirector` |

## 2. Test results (Python reference, RAN)

`python3 -I scripts/ref_camera.py`: 44 checks, all pass. Highlights: the anchor error over 200 random pinches is 3.6e-13 px (limit 2 px); path spacing 4.0 (limit 5); equal arc-length steps give equal movement (ratio 1.01); jitter of 0.02 around 1.75 or 0.85 changes the band at most once; people represented is 16 of 16 active in all three bands; no duplicated agent; no street hidden; cancel at 0, 25, 50, 75 and 99% leaves the camera exactly where it was.

The same checks exist as GDScript tests in `tests/test_camera.gd` (9 tests). **They have not run.**

## 3. Pictures and walkthrough (model data)

- `contact_three_zooms.png`: the same simulation tick (120) at zoom 0.78 (CITY), 1.20 (DISTRICT) and 2.20 (STREET). People are 20 in each; CITY shows only counted ribbons and one knot, DISTRICT shows each agent, STREET shows the larger sign and a local queue.
- `narrow320.png`: a re-laid-out 320 by 568 screen with the badge rule: the 3-walker queue at Canal Turn is one note and "x3". The long stacks of walkers already moving on the two other streets are still tight; not fixed.
- `walkthrough_20s_preview.mp4`: 200 frames at 10 per second. 0 to 2 s fly-in (zoom 0.72 to 1.15), 2 to 14 s follow the path A, B, D, F, G (zoom 1.15 to 1.9), 14 to 20 s pullback to the atlas (zoom 0.78). The band changed exactly 4 times, once per threshold, so no flicker in this path. It is a render of the reference camera over model data, **not** an in-engine capture.

## 4. Not done

- No engine capture, no 3× engine screenshots, no device pinch test, no real label-flicker test on a screen (all BLOCKED, see `docs/TEST_LOG.md`).
- The camera is not yet wired into the graybox scene or the input router: nothing drives pinch, pan or the Return to sign button in the engine yet.
- Map tilt along the path is off (default zero rotation, as the prompt says).
- Reduced motion substitutes a jump; the 150 ms cross-fade is not drawn.

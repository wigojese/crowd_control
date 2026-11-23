# TEST LOG

Evidence labels: **VERIFIED/RAN** = executed in this session with the output shown; **BLOCKED** = needs a tool or device that is not available here, with the exact missing piece and a reproducible manual test.
Run date: 2026-11-23. Machine: this cloud container (Linux, Python 3 at `/usr/local/bin/python3`, **no `godot`**). Commit under test: see `git log` (Stage 07 commit).

## Stage 07

| ID | Test | Result | Evidence |
|---|---|---|---|
| T07-01 | Lint rules L1 to L9 on the repo | RAN, PASS | `python3 -I scripts/lint.py` prints `LINT RESULT: OK` |
| T07-02 | Each lint rule fires on a deliberately bad copy | RAN, PASS (11 cases) | `python3 -I scripts/test_lint.py` prints `SELF-TEST RESULT: OK`. The first real run of the lint found two over-long lines in my own tests, which I fixed |
| T07-03 | Scenario validator verdicts on 5 fixtures (1 valid, 4 invalid) | RAN, PASS | `python3 -I scripts/validate_scenarios.py --fixtures` |
| T07-04 | Golden files equal the reference model's output | RAN, PASS | `python3 -I scripts/check_golden.py` |
| T07-05 | Clean clone: `git clone` into an empty directory, then `scripts/check_all.sh` | RAN, PASS | working tree clean after clone; `CHECK_ALL: OK`; no ignored or hidden local file needed. Engine steps skipped there (no Godot) |
| T07-06 | GDScript unit tests (`tests/test_*.gd`, 16 tests: RNG 3, state machine 5, event log 4, tick fixture 3, scenario validator 1; the test runner counts only what it finds) | **BLOCKED** | Missing: Godot 4.7.2 executable. Running the downloaded binary was denied by the session's security classifier (Stage 06). Manual test: `godot --headless --path . --script res://tools/test_runner.gd`; expect `RESULT: ALL PASS` and exit code 0 |
| T07-07 | Tick fixture reproduces the reference hash `1029034432` (157 spawns, 158 events) | **BLOCKED** | Same missing tool. The number comes from `scripts/ref_model.py`, not from the engine. Matching it is what T07-06 `test_fixture_matches_golden` checks |
| T07-08 | Duplicate / invalid state transition caught at run time | **BLOCKED** in engine. The same rule on the data table is RAN, PASS in lint L6 (`test_lint.py`, duplicate-transition case) | Manual test: T07-06, tests `test_invalid_transition_is_rejected_and_state_kept`, `test_duplicate_transition_in_table_is_caught`, `test_double_fire_is_rejected` |
| T07-09 | Boot scene shows one verified boot state | **BLOCKED** | Manual test: `godot --headless --path . --quit-after 2`; expect the line `BOOT_STATE=READY`. Visual check needs the editor or a display |
| T07-10 | Headless scenario runner | **BLOCKED** | Manual test: `godot --headless --path . --script res://tools/scenario_runner.gd -- res://tests/fixtures/scenario_ok.json`; expect `VALID seed=1007 spawned=157 events=158 hash=1029034432` |
| T07-11 | GDScript and Python scenario validators agree | **BLOCKED** (GDScript half) | Python half RAN (T07-03). GDScript half is test `test_fixture_verdicts` in T07-06 |
| T07-12 | GDScript syntax and type correctness of all `src`, `tests`, `tools` files | **BLOCKED / UNVERIFIED** | Nothing here parses GDScript. The Stage 06 spike has the same gap. Expect small fixes on the first real run |
| T07-13 | CI workflow `.github/workflows/ci.yml` | **UNVERIFIED** | Never executed; no run was triggered. Manual test: push, open the Actions tab |
| T07-14 | `project.godot` and `boot.tscn` load in the editor 4.7.2 | **BLOCKED** | Hand-written, not produced by the editor. The input-map key objects follow the 4.x text format from memory, **UNVERIFIED** |

## What these results do and do not show

- The Python side (lint, scenario rules, golden values) is checked and behaves as described.
- No GDScript has been executed. Every claim that the **engine code** works is **unproven** until T07-06 to T07-10 run. The golden numbers prove only that the Python reference is self-consistent.

## Reproduce

```bash
scripts/check_all.sh
```

## Stage 08 (graybox CC-L01-R1)

Level data: `data/levels/cc_l01_r1.json` (passes both scenario validators). Engine code: `src/simulation/sim_world.gd`, `src/app/graybox.gd`, `tools/run_level.gd`. Tests: `tests/test_sim_l01.gd` (6 tests).

| ID | Test | Result | Evidence |
|---|---|---|---|
| T08-01 | Lint on all new files | RAN, PASS | `python3 -I scripts/lint.py` |
| T08-02 | Level file valid | RAN, PASS | `python3 -I scripts/validate_scenarios.py data/levels/cc_l01_r1.json` prints `VALID` |
| T08-03 | Reference numbers for 9 scenarios on R1 (**Python model, not the engine**) | RAN | `python3 -I scripts/stage08_reference_runs.py`; output in `docs/stage08/scenarios.csv` |
| T08-04 | At least one pass and one failure achievable and provable (**Python model**) | RAN | NO_SIGN 17 of 20 FAIL; A/E 20 of 20 PASS (pass mark 18) |
| T08-05 | Sign input changes at least 2 downstream route choices (**Python model**) | RAN | 8 of 20 walkers choose a different first edge with A/E than with no sign (`docs/stage08/first_decisions.csv`) |
| T08-06 | Engine simulation reproduces the reference numbers (`test_sim_l01.gd`) | **BLOCKED** | Missing: runnable Godot 4.7.2. Manual: `godot --headless --path . --script res://tools/test_runner.gd` |
| T08-07 | Restart reproduces (same event hash twice) | **BLOCKED** | Same. Test `test_replay_is_deterministic`. The Python model reproduces its numbers (they match the Stage 06 JSON) |
| T08-08 | No deadlock, no routing through walls | Partly: in the Python model every walker arrives or is still en route at tick 640; routes can only use graph edges. **Engine: BLOCKED** | The 17 of 20 failure cases are slow queues, not deadlock: the last arrival is tick 581, before the end |
| T08-09 | Headless run with CSV event log and replay JSON from the engine | **BLOCKED** | Manual: `godot --headless --path . --script res://tools/run_level.gd -- res://data/levels/cc_l01_r1.json A E docs/stage08/engine` |
| T08-10 | Phone APK, video of 3 runs, benchmark of the real simulation | **BLOCKED** | Missing: Godot export templates and Android SDK (not reachable), a phone, a screen recorder. The Stage 06 bench (`spikes/godot-sim/bench.gd`) is also not run |
| T08-11 | Graybox scene (`graybox.tscn`) is readable: queues, dots, sign, score | **BLOCKED / UNVERIFIED** | Never rendered or seen. Manual: open `src/app/graybox.tscn` in the editor and press F6; space runs |

Finding from T08-03 (Python model): `B/E then MOVE A at tick 100` scores 17 (fail), the same as no sign, and `A/E then ROTATE N at tick 200` still scores 20. Everything that decides the result happens before about tick 100; later actions barely matter (risk R-15 again, now with numbers).

## Stage 09 (input and gesture arbitration)

Code: `src/input/gesture_router.gd`, `data/input_tokens.json`; reference `scripts/ref_input.py`; cases `tests/fixtures/input_cases.json` (21 cases: G-01 to G-15, G-08b, X-01 to X-05); GDScript tests `tests/test_input_router.gd` (3 tests).

| ID | Test | Result | Evidence |
|---|---|---|---|
| T09-01 | Lint with the new `input` layer | RAN, PASS | `scripts/lint.py`, `scripts/test_lint.py` |
| T09-02 | 21 gesture cases on the Python reference | RAN, PASS (after fixing one wrong test coordinate, IB-01) | `python3 -I scripts/ref_input.py` ends `INPUT RESULT: ALL PASS` |
| T09-03 | Same cases on the GDScript router | **BLOCKED** | Missing: runnable Godot. Manual: `godot --headless --path . --script res://tools/test_runner.gd` |
| T09-04 | Pan never spends a sign action; cancel neither duplicates nor loses the sign (G-05, G-10, every pickup has one resolution) | RAN, PASS in the Python reference. Engine: BLOCKED | `test_every_pickup_has_exactly_one_resolution` in the GDScript tests |
| T09-05 | Finger starts on sign, map, dock, notification edge, two simultaneous touches | RAN in the reference (G-03, G-05, G-08, G-09, G-07, G-13). Engine and real touchscreen: BLOCKED | |
| T09-06 | Real touchscreen feel, 390×844 and 320×568 recordings, alternative control comparison | **BLOCKED** | Missing: phone, screen recorder |
| T09-07 | Measured first-acknowledgement latency | **BLOCKED** | Missing: phone and a high-speed or on-device capture. The router's own `first_ack` is not this number |
| T09-08 | Input thresholds live in tokens, not scattered | RAN | Router reads only `tok[...]`; no number literal for a threshold in `gesture_router.gd` (checked by reading; there is no lint rule for it yet) |

## Stage 08 experiment, user option B (spawn window first)

`python3 -I docs/analysis/stage08_r2_experiment.py` (Python model). A third walker group at tick 200, 300 or 360 from gates A, B, C or E: the best case adds **2 of 27** arrivals over the best fixed placement (group from Canal Turn to School at tick 200: 23 fixed, 25 with one running action). Most variants add 0 or 1. **A second wave alone does not make running play decisive.** The level file is unchanged (still R1).

## Stage 10 (visual identity)

| ID | Test | Result | Evidence |
|---|---|---|---|
| T10-01 | Lint with the new `rendering` layer | RAN, PASS | `scripts/lint.py`, `scripts/test_lint.py` |
| T10-02 | Contrast of all token pairs, both themes | RAN, PASS (20 checks) | `python3 -I scripts/check_contrast.py` |
| T10-03 | Colour-off separation of routes and queues | RAN: amber vs sage 1.03:1, so a dash pattern is required and used | same script, INFO lines |
| T10-04 | Ribbon rule (zero flow draws nothing, monotone, capped, counts from `EDGE_ENTERED` only) | RAN, PASS 7 of 7 | `python3 -I scripts/ref_ribbon.py` |
| T10-05 | Ribbon model in GDScript | **BLOCKED** | `tests/test_ribbon_model.gd`, run with the test runner |
| T10-06 | Preview pictures: five states, high contrast, no-colour (grayscale filter), 320 px scaled | RAN (pictures read by me) | `docs/stage10/*.png`. Found and fixed two preview bugs: a caption overlapping the buttons, and a "sign locked" claim shown before any action (it would have misreported the rules) |
| T10-07 | 320 px legibility | FAILED as drawn (notes about 15 px, queued notes overlap) | `v_narrow320_t120.png`; see docs/VISUAL_IMPLEMENTATION.md |
| T10-08 | Five real engine screenshots, 15 s capture, narrow capture, draw-order and performance delta | **BLOCKED** | Missing: runnable Godot, display, phone. Manual: open `src/app/graybox.tscn`, F6, space to run, H toggles high contrast |
| T10-09 | `map_view.gd` parses and draws | **BLOCKED / UNVERIFIED** | Never loaded |
| T10-10 | No engine-default buttons in main gameplay | **NOT MET**: the styled buttons exist only in the pictures | |

## Stage 11 (camera and semantic zoom)

| ID | Test | Result | Evidence |
|---|---|---|---|
| T11-01 | Lint with `camera` layer and rule L10 (simulation and camera must not reference each other) | RAN, PASS, rule fires on a bad copy | `scripts/lint.py`, `scripts/test_lint.py` |
| T11-02 | 44 camera checks on the Python reference | RAN, PASS | `python3 -I scripts/ref_camera.py`. I tightened two weak checks of my own (a flux check with an `or`, and a jitter test that could not fail) before accepting the result |
| T11-03 | One world anchor survives pinch within 2 px | RAN, PASS in the reference (3.6e-13 px). Engine: BLOCKED | |
| T11-04 | No label flicker at thresholds | RAN in the reference (band changes at most once per threshold under jitter; the walkthrough changes band exactly 4 times). Real screen: BLOCKED | |
| T11-05 | No hidden edge, no duplicated agent, exact counts at every band | RAN, PASS in the reference | |
| T11-06 | GDScript camera tests (9) | **BLOCKED** | Missing: runnable Godot. Manual: the test runner |
| T11-07 | No input conflict with the sign | RAN only as a rule: a finger down outranks every camera request and freezes the camera. The router and the camera are not wired together. **BLOCKED** in the engine | |
| T11-08 | 3× zoom screenshots at one tick, 20 s walkthrough, narrow capture | RAN as model-data previews (not engine). Engine captures: **BLOCKED** | `docs/stage11/` |
| T11-09 | Reduced motion and RETURN TO SIGN | Logic RAN in the reference; no button exists in the engine | |

## Stage 12 (six transitions)

| ID | Test | Result | Evidence |
|---|---|---|---|
| T12-01 | 60 transition checks on the Python reference | RAN, PASS | `python3 -I scripts/ref_transitions.py` |
| T12-02 | Cancel, skip and app interruption at 0, 25, 50, 75, 99% for all six transitions | RAN, PASS in the reference (frozen values stay frozen, one on_end, identical game-state events) | same |
| T12-03 | Replay state unchanged | RAN in a mock run: identical tick log in all 120 combinations. The real guarantee is structural (no simulation handle, lint L10). Engine replay hash: BLOCKED | |
| T12-04 | No double result callback; skip returns control within 150 ms | RAN, PASS in the reference (callbacks only at start; settle 100 ms; no input lock) | |
| T12-05 | Sign stays visible during consequence_follows_ink | RAN, PASS, but the margin is only 8 px to the HUD (added after I noticed the rule was only a data field, not a test) | |
| T12-06 | GDScript transition tests (8) | **BLOCKED** | Missing: runnable Godot |
| T12-07 | Timings from an actual capture, one MP4 per transition from the engine | **BLOCKED**. Substitute: six reference-driven sheets and quarter-speed videos from model data, clearly labelled | `docs/stage12/` |
| T12-08 | Grain shimmer, black flashes, mandatory waits | No black overlay track exists; no mandatory wait (skip at any time); grain: none in direction C. Not seen on a screen | |
| T12-09 | Transitions wired to game states | **NOT DONE** | |

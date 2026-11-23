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

# RELEASE CANDIDATE FREEZE AND HANDOFF (Stage 18)

**Status: NOT A RELEASE CANDIDATE YET. This is a design-and-reference freeze.** No build exists: Godot has never run in this project, there is no APK, no signing, no device test, no real playtest. Nothing was submitted or published, and nothing will be without your explicit authorisation. Everything below is labelled VERIFIED, RAN (Python reference only), DESIGNED or BLOCKED.

## 1. What is frozen (changes now need a new decision record and your approval)

Mechanics `CC-RULESET-01C` (one sign, fixed 0.05 s tick, next-junction effect, token-bucket queues); levels L01 R1, L02 Ferry Landing, L03 Two Narrow Roads (L04 to L08 specified only); art direction C (transit score, dark theme, CC-D-012) with tokens in `data/art_tokens.json`; input thresholds `data/input_tokens.json`; camera, six transitions, causal explainer, audio and settings as approved in CC-D-016 to CC-D-022. Frozen at the commit that contains this file (see `git log -1 -- docs/RELEASE.md`). The Stage 17 playtest protocol is approved but **has no data**, so the freeze rests on reference-model evidence only.

## 2. Reproduce what exists (another developer, supported machine: Linux with Python 3)

```bash
python3 --version
```

```bash
scripts/check_all.sh
```

Expected: `CHECK_ALL: OK` (16 Python checks, 283 Stage 16 checks in quick mode; engine checks print SKIPPED without `godot`). With Godot 4.7.2 stable on `PATH` the same script also runs the GDScript tests: **never done; expect first-run failures** in the unrun GDScript (it is a port of the Python reference, `docs/ARCHITECTURE.md`). Pins: `docs/VERSION_MANIFEST.md`.

## 3. Release checklist

| # | Item | Status |
|---|---|---|
| 1 | Reference-model tests (rules, levels, explainer, camera, audio, settings, transitions, contrast, layout, fuzz) | RAN, PASS |
| 2 | GDScript tests, headless boot, scenario runner | **BLOCKED** (no Godot run) |
| 3 | Engine port reproduces replay hashes (`data/replays/*`) | **BLOCKED** |
| 4 | Android export, target API 36, signing, install | **BLOCKED** (no SDK, device or keystore) |
| 5 | 60 FPS on a real mid-range phone, 10-minute thermal run | **BLOCKED** (R-51) |
| 6 | Real players understand the sign and why they lost | **UNTESTED** (`docs/PLAYTEST.md`, empty grid) |
| 7 | Sounds heard and judged | **UNVERIFIED** (I cannot hear; mixes in `docs/stage15/`) |
| 8 | Haptics on a device, screen reader | **BLOCKED** |
| 9 | Asset and licence audit | RAN: 293 tracked files, no third-party binaries; no font file shipped (`docs/stage16/license_audit.json`) |
| 10 | Fonts: add files and check Inter's Apache-2.0 part | **OPEN** (R-29) |
| 11 | Store policy at launch time: Google Play target API (sources said API 36 from 31 Aug 2026), data-safety form, age rating, privacy | **NOT RE-VERIFIED today.** Must be read again when a build exists. The game collects no data and has no ads, accounts or purchases (design fact, not a legal opinion) |
| 12 | iOS export | **NOT ATTEMPTED** (needs macOS and Xcode) |
| 13 | CI | Written, **never run** (`.github/workflows/ci.yml`) |
| 14 | Store stills from real engine imagery | **BLOCKED** (no engine screenshot exists; the model-data pictures are not store art) |

## 4. Unresolved issues (ranked)

1. No build, so every performance, touch and platform claim is unproven (R-01, R-51).
2. GDScript never executed (R-37 and others); first engine run will find bugs.
3. Running play barely changes the outcome in L01 (R-30, R-31): the core fantasy may not hold. Candidate fix in `docs/PLAYTEST.md` section 6.
4. At 320 wide the whole map opens in the atlas band (R-50).
5. Three of six muted-play cues exist only as designs (R-49).
6. Crowd density on narrow phones (R-34, R-38).
7. Sound tone unconfirmed; the mix peaks near -2 dBFS and may need a limiter.
8. Rule note: the ruleset has no randomness, so "seed" does nothing yet (R-46).
Full list: `docs/RISKS.md`.

## 5. Level and editor guide (how to add or diagnose a level)

A level is one JSON file in `data/levels/` (nodes with x,y; edges with service rate; sockets; spawn schedule with profile mix C/F/I; pass mark; solutions with commands). There is no editor. To add one: copy `cc_l02_ferry.json`, edit, add its file name to `LEVELS` in `scripts/check_levels.py`, then run `python3 -I scripts/check_levels.py`. It rejects invalid files, requires that no sign fails, every listed solution passes, passing placements are few, the graph fits at 390x844 and 320x568, and sockets are far enough apart. Diagnose a run with `docs/stage13/trace_*.csv` style traces (`scripts/stage13_evidence.py`) and the explainer (`docs/CAUSAL_EXPLANATION.md`). Specs for L04 to L08: `docs/LEVELS_L04_L08_SPEC.md`.

## 6. Design bible

Versioned set, all at the freeze commit: `docs/BRIEF.md`, `RULES.md`, `ART_BIBLE.md` and `VISUAL_IMPLEMENTATION.md` (art C), `INPUT_SPEC.md`, `CAMERA.md`, `TRANSITIONS.md`, `CAUSAL_EXPLANATION.md`, `AUDIO.md`, `ACCESSIBILITY.md`, `LEVELS.md`. Version label: **Design Bible v0.18-unbuilt**.

## 7. Trailer

60 s storyboard: `docs/TRAILER_STORYBOARD.md`. It lists shots to capture; **none exists**, and it must use real in-engine capture only.

## 8. Archive of stage approvals

| Stage | Your words | Date |
|---|---|---|
| 00 | "Approve Stage 00, Confirm the baseline: Web access approved" | 2026-11-22 |
| 01 | "approve stage 1" | 2026-11-22 |
| 02 | "Approve Stage 02, choose C" | 2026-11-22 |
| 03 | "approve and continue" | 2026-11-23 |
| 04 | "Approve Stage 04, choose A" | 2026-11-23 |
| 05 | "Approve Stage 05 … continue with C, dark theme" | 2026-11-23 |
| 06 | "Approve Stage 06, option C" (accepted without engine evidence) | 2026-11-23 |
| 07 | "Approve Stage 07, option A. split app at Stage 09 or 10" | 2026-11-23 |
| 08 | option B (recorded in commit 6b8a8b3; spawn-window experiment) | 2026-11-23 |
| 09 to 14 | "Approve Stage NN, option A/B" as recorded in CC-D-016 to CC-D-021 | 2026-11-23 |
| 15 | "Approve Stage 15, option A" | 2026-11-23 |
| 16 | "Approve Stage 16, option A" | 2026-11-23 |
| 17 | "Approve Stage 17, option A" | 2026-11-23 |

Decision records: `docs/DECISIONS.md` (CC-D-001 to CC-D-025). CC-D-005, CC-D-006 and CC-D-007 are still marked PROPOSED there: please confirm or close them.

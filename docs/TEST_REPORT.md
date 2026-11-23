# TEST REPORT (Stage 16)

**Scope, stated plainly.** Everything below ran on the **Python reference of the rules**, not the engine and not a phone. Godot has never run in this project, no Android device exists, and no build, APK or export was made. So the Stage 16 core items (10-minute device profile, FPS p50/p95/p99, thermal, memory, release APK, real safe-area and 3 engine camera sessions) are **BLOCKED and are release blockers**, not met.

## Results

| ID | Test | Command | Result |
|---|---|---|---|
| T16-01 | All earlier Python checks (15 scripts) | `scripts/check_all.sh` | RAN, PASS |
| T16-02 | Property/fuzz: 200 random scenarios per level x 3 levels: deterministic, command-order independent, each arrival counted once and never above spawned, one-sign pick/drop pairing, no decision while on an edge (next-junction rule), only real edges, token-bucket rate bound, no softlock (run 3x long, every walker arrives; latest arrival tick 765 / 1100 / 958) | `python3 -I scripts/stage16_checks.py` | RAN, PASS (30 properties) |
| T16-03 | Frame-rate independence: fixed 0.05 s tick driven at 30/60/90/120/144 Hz with +-30% jitter gives the identical event hash; 400 ms hitches drop backlog (19 times) and slow the run but the hash is unchanged | same | RAN, PASS |
| T16-04 | Camera lifecycle fuzz: 3 levels x 3 viewports x reduced motion on/off, 3000 random focus/touch/pinch/update steps each: finite, inside zoom limits, pinch anchor within 2 px, frozen under a finger, sign focus lands between HUD and dock | same | RAN, PASS (reference, not engine) |
| T16-05 | Layout sweep: 10 viewports (320x568 to 1024x1366, insets), both hands, larger targets: no overlap, inside edge reserve and safe area, controls at least 44x44, whole graph fits at zoom of at least 0.65, sockets at least 56 px apart | same | RAN, PASS after fixing a bug (below) |
| T16-06 | Licence audit of 293 tracked files: no font, music or image binary of unknown origin; no font file shipped | `python3 -I scripts/stage16_evidence.py` | RAN, PASS (by extension, see caveat in `docs/stage16/license_audit.json`) |
| T16-07 | Engine tests (all `tests/*.gd`), export smoke, headless boot | `scripts/check_all.sh` with `godot` | **BLOCKED** |
| T16-08 | 10-minute device profile, FPS percentiles, thermal, memory, bottlenecks | none | **BLOCKED: no device** |
| T16-09 | Release APK, small/tall/tablet engine screenshots, platform interruption on a phone | none | **BLOCKED** |
| T16-10 | Real 3-level camera stress session in engine | none | **BLOCKED** |

## Bugs found and fixed

| ID | Repro | Fix |
|---|---|---|
| BUG-16-01 | `ref_settings.dock_layout(False, True, (360, 640))`: pause button ends 20 px from the edge, inside the 24 px reserve (larger targets at 360 wide) | Button width is capped so three controls and two gaps always fit |
| BUG-16-02 | `dock_layout(False, False, (768, 1024))`: controls spread across 712 px, out of thumb reach | Tablet row is 480 px, anchored on the thumb side |
| (test bug) | First rate check ignored the bucket's burst allowance and reported 332 false violations | Bound is now cap + refill (spec A5) |

The GDScript `src/input/dock_layout.gd` got the same fix but is **not run**. Shared fixtures (`tests/fixtures/settings_cases.json`) are unchanged because they cover only 320 and 390 wide.

## Not tested, and why it matters

- Performance targets (60 FPS, 16.67 ms, input latency): UNKNOWN. No number in this report is a device number.
- At 320 wide the whole map fits only at zoom 0.74, which is the atlas band (below 0.85). A small phone may start in the ribbon view (new risk R-50).
- Tablet and tall renderings are layout diagrams from model data, not engine screenshots (`docs/stage16/layout_contact_sheet.png`).
- Property tests prove the reference model; the engine port must reproduce its hashes (T14-04, still blocked).

# ENGINE DECISION (Stage 06: technical spike and engine selection)

**Status: PARTIAL. The engine choice cannot yet be made on evidence.** The spike project is written but **has not been run**. No Unity comparison exists. No Android build or device test exists. This document says exactly what was and was not done, so nothing here should be read as a measurement.

## 1. What blocked the spike

| Step | Outcome | Blocker | Label |
|---|---|---|---|
| Get Godot 4.7.2 into the container | Done. Downloaded `Godot_v4.7.2-stable_linux.x86_64.zip` (77,860,424 bytes) from the official GitHub release; **SHA-512 matches** the published `SHA512-SUMS.txt` | The vendor's own download host (`godot-releases.nbg1.your-objectstorage.com`) is not on the network allowlist, so I used the same release on GitHub | VERIFIED |
| Unpack and run it headless | **Not done** | The session's security classifier **denied** the command that unpacked and ran the downloaded binary. I did not try to get around it | BLOCKED |
| Run `l01_check.gd` (reproduce the Python model's CC-L01 numbers) | Not done | Needs the step above | BLOCKED |
| Run `bench.gd` (50, 200, 500 walkers on 7, 25, 50 nodes) | Not done | Needs the step above | BLOCKED |
| Unity 6.3 LTS spike | Not attempted | Needs the Unity Hub or editor, a Unity account and licence sign-in, and a GUI or batch-mode licence. No route from this container | BLOCKED |
| Android export of either engine | Not attempted | Needs the Android SDK and export templates (not reachable from this container) and a device | BLOCKED |
| Test on a real phone | Not possible | No device and no attached computer (R-01) | BLOCKED |
| iOS export | Not possible | The spec says it needs macOS and Xcode; Godot's iOS export page could not be read (rate-limited, HTTP 429) | UNVERIFIED |
| Rendering tests (grain, zoom bands, ribbon trails, draw counts) | Not possible here | Headless has no renderer; a real run needs a graphics device | BLOCKED |

## 2. Facts I could verify (read 2026-11-23)

| Fact | Source | Label |
|---|---|---|
| Godot 4.7.2 is the current stable, dated 18 August 2026; Godot 4.8 is in beta (beta 4) | Godot download page and archive | VERIFIED |
| Godot 4.7 notes standalone Android exporting and publishing, and an Android editor | Godot 4.7 release page | VERIFIED |
| Godot is MIT licensed: free for any purpose, commercial included, with only the copyright notice to ship; your game's licence is your own | Godot licence page | VERIFIED |
| Unity 6.3 LTS is supported until December 2027 (6.0 LTS until October 2026) | Unity 6 support page | VERIFIED |
| Unity's documentation shows a version list that includes 6000.3 (LTS), later versions up to a 7000.0 alpha | Unity 6.3 manual page | VERIFIED (list read loosely) |
| From 31 August 2026, new apps and updates on Google Play must target Android 16 (API level 36) or higher | Google Play target-API page | VERIFIED |
| Android's Frame Pacing library page exists | Android developers | VERIFIED (page loaded, not studied) |
| Unity pricing and licence cost | Unity pricing URL returned 404 | **UNVERIFIED** |
| Godot Android and iOS export documentation, `InputEventScreenTouch`, `MultiMeshInstance2D`, 2D transforms | docs.godotengine.org rate-limited (HTTP 429, bot check) | **UNVERIFIED** |

## 3. The spike that is ready to run

`spikes/godot-sim/` (see its README):
- `sim_core.gd`: the CC-RULESET-01C simulation as a plain `RefCounted` with no scene tree, mirroring the Python model line for line.
- `l01_check.gd`: runs 12 cases (the spec's rev0 level and candidate R1, including running-action cases) and compares each number with `expected_python_model.json`. **If this passes, risk R-16 (the model has never matched an engine) is closed.**
- `bench.gd`: per-tick cost at 50, 200 and 500 walkers on 7, 25 and 50 node graphs; prints p50, p95, p99, max, mean, total, memory delta and a determinism check; writes JSON.

What it measures: **game logic cost only, CPU only.** It does not measure rendering. Numbers from this container's CPU (Intel Xeon 2.10 GHz, 4 cores, 16 GB) would not predict a phone's.

## 4. Provisional choice (PROPOSED, not decided)

**Godot 4.7.2 with GDScript is the working candidate.** This is a **provisional** choice for planning, not a result of the comparison the spec asks for. Reasons, each labelled:

| Reason | Label |
|---|---|
| It is the spec's default candidate, and 4.7.2 is verified as the current stable (4.8 is a beta the spec says not to ship) | VERIFIED |
| MIT licence: no fee, no royalty, no seat cost | VERIFIED |
| It is the only engine I could actually obtain here and check against a vendor checksum | VERIFIED |
| Godot scenes and scripts are plain text, which suits git and a headless test runner | General knowledge, not verified in this session |
| GDScript may be too slow for the simulation at 500 walkers on a phone | **UNKNOWN: this is the main technical risk** |
| Unity may perform better for logic or tooling | **UNKNOWN: not evaluated** |

**Conditions to make it final** (proposed thresholds, to approve):

1. `l01_check.gd` reports ALL PASS.
2. `bench.gd` shows the simulation tick at 500 walkers on 50 nodes at a p95 of **at most 4 ms** on the target phone, which leaves most of the 16.67 ms frame for rendering. (On this container's CPU a pass is necessary but not sufficient.)
3. A real Android build starts and takes touch input on the target phone.
4. If the tick fails the budget: first try a flatter data layout in GDScript; then the Godot .NET build or a native extension. Do not switch engines without a new approval (spec E1).

## 5. Architecture proposal (PROPOSED, for the Stage 07 scaffold)

Follows the spec's module list and the directory proposal in its section E1.

| Module | Role | Rule |
|---|---|---|
| `simulation` | The rules in `docs/RULES.md`: `SimulationWorld`, `RoadGraph` (immutable per level), `SignPolicy`, `CrowdQueueSystem`, `ScoreEvaluator` | Pure code, **no scene tree**, so it runs headless in CI and in tests |
| `replay` | `ReplayLog` of seed plus commands, event log, hash | The equality check for T-10 and T-13 |
| `camera` | `CameraDirector` | The only thing that sets the world camera |
| `input` | `InputRouter` per `docs/INPUT_SPEC.md` | Owns touches; thresholds in a resource, not in code |
| `rendering` | `MapRenderer` projects simulation snapshots; direction C's staff lines, notes, ribbons, sign | Reads the simulation; never writes to it |
| `audio`, `save` | `AudioDirector`, `SaveService` (versioned, atomic writes) | Reads semantic events |
| `levels` | JSON level files and the validator (V-1 to V-5, `docs/LEVEL01_SPEC.md`) | Data, not code |

Rendering approach to test at Stage 10, not assumed now: static layers drawn once and cached; walkers as batched instances (`MultiMeshInstance2D` is a candidate named in the spec; its page could not be read); ribbons rebuilt at a low rate from edge flux. No design decision depends on this yet.

## 6. What I need from you (the decision)

| Option | What happens |
|---|---|
| **A. Allow the run here** | You allow the command that unpacks and runs the verified Godot binary in this container (a Bash permission, for example for the unpack-and-run of `Godot_v4.7.2-stable_linux.x86_64`). I then run `l01_check.gd` and `bench.gd` and finish the CPU part of the spike here. Rendering, Unity, Android and device tests stay blocked |
| **B. Run it yourself** | On your computer, with Godot 4.7.2 installed: `godot --headless --path spikes/godot-sim --script res://l01_check.gd` then `godot --headless --path spikes/godot-sim --script res://bench.gd`. Paste the output back. Same limits as A, but on your hardware |
| **C. Accept the limitation** | Approve Stage 06 as documented: provisional Godot, no evidence yet, conditions 1 to 4 above carried forward into Stage 07 and Stage 08. This is allowed by the spec ("report limitation rather than fabricate") but it leaves the main risk open |

I recommend **A or B** before approving, because the spec's gate for this stage is evidence, and the cheapest evidence is exactly these two commands.

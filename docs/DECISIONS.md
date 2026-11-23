# DECISIONS

Entry schema (from the spec): `ID | stage | date | question | chosen option | values | rationale | alternatives | approver status | affected files | supersedes ID`.
IDs are stable. Nothing below is **approved** yet. Every entry is PROPOSED until you say so.

---

**CC-D-001**
- stage: 00
- date: 2026-11-22
- question: Start with the baseline one-sign intervention and portrait orientation?
- chosen option: Yes. One movable sign, portrait phone
- values: `max_active_signs = 1`; orientation = portrait
- rationale: It is the spec's baseline and the north-star verb "redirect"
- alternatives: landscape; multiple signs. Both rejected by the spec's one-sign invariant
- approver status: APPROVED by the user on 2026-11-22 ("Confirm the baseline")
- affected files: docs/BRIEF.md
- supersedes: none

**CC-D-002**
- stage: 00
- date: 2026-11-22
- question: Which ruleset is the starting point for Stage 03?
- chosen option: `CC-RULESET-01` exactly as written in the spec, section A
- values: 20 ticks/s; 640 ticks for CC-L01; pass 16 of 20; seed 1007; sign influence radius 90; sign bonus 4.0 s; loop penalty 6.0 s; speeds C 38 / F 34 / I 42
- rationale: Concrete, testable, deliberately provisional
- alternatives: simplify the graph at Stage 03 if the automated trials show the first puzzle is unsolvable or boring
- approver status: PROPOSED. Formal approval at Stage 03
- affected files: docs/BRIEF.md
- supersedes: none

**CC-D-003**
- stage: 00
- date: 2026-11-22
- question: Which engine?
- chosen option: Undecided. Godot 4.7 (GDScript) is the candidate; Unity 6.3 LTS is the comparison
- values: none
- rationale: The spec says to decide at Stage 06 on measured evidence. Neither engine is installed here and the versions cannot be verified from here
- alternatives: Unity 6.3 LTS; Godot 4.8 beta (rejected as a shipping baseline by the spec)
- approver status: PROPOSED. Decided at Stage 06
- affected files: none
- supersedes: none

**CC-D-004**
- stage: 00 (art exploration happened before Stage 05 at the user's request)
- date: 2026-11-22
- question: Is "The Civic Press, revised" (D2) the chosen art direction?
- chosen option: **No, not approved.** It is recorded as a provisional input to the Stage 05 art competition
- values (palette tokens, proposed): paper `#EDE1CC`, panel paper `#F7F0E3`, ink `#1E1A17`, soft black `#433B33`, vermilion `#D6522F` (the sign only), rust `#A86135`, oxblood `#7D3B42`, olive `#7A7B55`, mustard `#C39B34`, shadow paper `#DDCFB8`, stone `#A49A8B`; no blue, teal, cyan, navy
- rationale: The user-supplied reviews rated it the strongest structure so far. Its own critique says it is "not yet approve" as a final direction; people, palette life and tactility were the named weaknesses and were revised in D2. D2 has only been drawn as static pictures and has not been tested in motion, in engine or on a device
- alternatives: A (print atlas), B (paper theater), C (transit score), and the "genuinely different fifth direction" the review's brief asks for
- approver status: PROPOSED. The user said "commit"; I read that as "save this work", not "approve the art direction". Confirm if that is wrong
- affected files: docs/art-exploration/**
- supersedes: none

**CC-D-005**
- stage: 00
- date: 2026-11-22
- question: What are the CC-L01 place names and the objective wording?
- chosen option: A North Gate, B Canal Turn, C Market, D Bridge West, E Bridge East, F School, G Plaza. Objective: "Deliver 16 of 20 before 0:32"
- values: names only
- rationale: The reviews found that "home", "market crossing" and "Plaza" were used inconsistently against what the map showed. Every sentence in the UI and result copy must name something that exists on the map
- alternatives: keep the spec's node letters in the UI (worse for first-time players)
- approver status: PROPOSED
- affected files: docs/BRIEF.md
- supersedes: none

**CC-D-006**
- stage: 00
- date: 2026-11-22
- question: Where do the pre-Stage-05 picture explorations live?
- chosen option: Committed under `docs/art-exploration/round1-…`, `round2-…`, `round3-…` as reference pictures plus the D2 generator scripts
- values: 16 PNG files, 3 JS files
- rationale: They are the evidence behind CC-D-004 and CC-D-005. They are mockups, not game assets, and they contain made-up sample numbers
- alternatives: keep them out of the repository
- approver status: PROPOSED. Informational
- affected files: docs/art-exploration/**
- supersedes: none

**CC-D-007**
- stage: 01
- date: 2026-11-22
- question: What is the differentiation statement, and which novelty is tested first?
- chosen option: Promise: "Place one civic sign at a junction, watch a small city's crowd bend toward it, then see exactly which turn decided the outcome." Test **N1** (one sign biasing next-junction route preference by walker type) first
- values: 11 products compared; 3 candidate novelties (N1 sign as preference, N2 decisive-junction replay, N3 one data source in three zoom languages)
- rationale: N1 is the core verb; N2 and N3 only matter if it is fun. Full evidence in docs/DIFFERENTIATION.md
- alternatives: P2 hard-gate sign, P3 several signs, P4 per-walker skills, P5 drawn paths (all rejected there)
- approver status: APPROVED by the user on 2026-11-22 ("approve stage 1"). The user approved the stage as presented, including the differentiation statement and N1-first
- affected files: docs/DIFFERENTIATION.md
- supersedes: none

**CC-D-008**
- stage: 01
- date: 2026-11-22
- question: Which outbound hosts may the session reach?
- chosen option: 15 exact hosts added to the environment allowlist on the user's "Web access approved"
- values: library.ltmuseum.co.uk, www.londonmuseum.org.uk, isotype.univie.ac.at, www.cooperhewitt.org, www.metmuseum.org, www.w3.org, support.google.com, developer.apple.com, store.steampowered.com, apps.apple.com, en.wikipedia.org, www.nintendo.com, www.pocketgamer.com, toucharcade.com, www.pcgamer.com
- rationale: Stage 01 research and checking the sites cited in the user's documents
- alternatives: unrestricted network access (not chosen)
- approver status: APPROVED by the user on 2026-11-22 (card approval in the environment settings)
- affected files: none (environment setting)
- supersedes: none

**CC-D-009**
- stage: 02
- date: 2026-11-22
- question: Which of the three loops (A one-shot, B placed sign plus one timed 90-degree turn, C re-placeable sign) should Stage 03 specify?
- chosen option: **C (re-placeable sign)**, selected by the user on 2026-11-22. The assistant had recommended B; the user's choice stands
- values: C = one sign; one placement before Start; during the run the sign may be moved to the other socket or turned 90 degrees; a lock of 4.0 s (provisional, to be tuned in Stage 03/08) follows every action; effects only on next-junction decisions; a pause or system interruption does not spend or shorten the lock
- rationale: the user chose the variant with the most depth. Known costs the user accepted by choosing it: highest input-conflict risk with pan and pinch, largest engineering cost, a likely "chase the crowd" dominant strategy (docs/LOOPS.md section 4). Stage 03 must put a measurable mitigation in the rules
- alternatives: A (cheapest, solvable by memory in 8 runs), C (deepest on paper, riskiest to build and to arbitrate with pan and pinch)
- approver status: APPROVED by the user on 2026-11-22 ("Approve Stage 02, choose C")
- affected files: docs/LOOPS.md
- supersedes: none

**CC-D-010**
- stage: 03
- date: 2026-11-22
- question: Is the formal ruleset CC-RULESET-01C approved, and what happens to CC-L01?
- chosen option: Ruleset as written in docs/RULES.md. Level: rev0 is solvable but not a puzzle; **R1 adopted** (option b); R2 two-wave idea held for L02 or L03
- values: loop C, lock 80 ticks, hold timeout 60 ticks, held sign inactive, no commands while paused, deadline tick 600, queue wait on first edge only, initial tokens 1.0. R1: Market moved to (270,115); sockets A and B; walkway BD 0.3 walkers/s; sign bonus 6.0 s; pass 18 of 20. R2 idea: second School-bound wave of 8 at tick 300, pass 16
- rationale: with the spec's numbers the no-sign baseline arrives 20 of 20 and all 8 placements are identical (docs/LEVEL01_SPEC.md section 2). R1 gives baseline 17 (fail) and two distinct passing placements; a running action rarely helps in R1, and R2 shows when it would
- alternatives: (a) keep rev0 and tune at Stage 08, (c) R1 plus R2 now, (d) other
- approver status: APPROVED by the user on 2026-11-23 ("approve and continue" in reply to the Stage 03 gate). The user did not name a CC-L01 option; I recorded my recommended option (b), adopt R1, as the one approved. Correct this if wrong
- affected files: docs/RULES.md, docs/LEVEL01_SPEC.md, docs/SIMULATION_EVENTS.md, docs/analysis/*
- supersedes: none (refines CC-D-002 and CC-D-009)

**CC-D-011**
- stage: 04
- date: 2026-11-23
- question: What is the default sign control, and what are the touch rules?
- chosen option: **A, chosen by the user on 2026-11-23.** Drag from the tray is the primary way to place and move the sign; tapping a ring also places or moves it; tapping the sign turns it. The user has not yet chosen
- values: drag starts after 8 px; pan after 12 px; tap = lift within 220 ms and under 8 px; long press 420 ms; pinch ratio 1.06; snap radius 44 px; hit area 56×56 for sign, ring and tray; edge reserve 24 px each side; required controls at least 44×44, primary at least 48 high; tap-to-move flight 10 ticks (0.5 s)
- rationale: the physical sign is the art direction's centrepiece; a tap alternative keeps the game playable without dragging. Edge width and thresholds are unmeasured starting values
- alternatives: B tap-a-ring primary; C tap only (docs/INPUT_SPEC.md section 6)
- approver status: APPROVED by the user on 2026-11-23 ("Approve Stage 04, choose A")
- affected files: docs/INPUT_SPEC.md, docs/RULES.md (tap-to-move line), docs/stage04-input/*
- supersedes: none

**CC-D-012**
- stage: 05
- date: 2026-11-23
- question: Which art direction is chosen: A print atlas (Civic Press), B fold-out paper theater, or C transit score?
- chosen option: **C, transit score (dark theme), chosen by the user on 2026-11-23.** The assistant had recommended A; the user's choice stands. The user changed their mind twice in the same message (A, then C); the final instruction was "continue with C, dar[k] theme"
- values: weighted rubric (spec B5): A 7.58, B 6.70, C 7.28 (my judgements from static pictures); palette tokens for each in docs/ART_BIBLE.md
- rationale: A scores highest, is the cheapest to build and reads best. C is more distinctive but weak in sunlight and for touch feel. B is the most tactile but the most expensive and noisy. If distinctiveness is weighted above 30 %, C overtakes A
- alternatives: B; C; a revision of any
- approver status: APPROVED by the user on 2026-11-23 ("Approve Stage 05 … continue with C, dark theme"). CC-D-004 (Civic Press D2 provisional) is superseded: D2 is no longer the working direction
- affected files: docs/ART_BIBLE.md, docs/stage05-art/*
- supersedes: CC-D-004
- required changes to C before Stage 10 (PROPOSED, from the contrast tests): use plum for hatched fills only (4.07:1 is below text size 4.5:1); disabled text raised to at least 4.5:1; sign arrow drawn dark on the vermilion disc (4.69:1) instead of parchment (3.11:1); keep daylight legibility as a measured gate on a real phone (R-21)

**CC-D-013**
- stage: 06
- date: 2026-11-23
- question: Which engine and version?
- chosen option: **Provisional: Godot 4.7.2 with GDScript.** Not final. The comparison with Unity 6.3 LTS and any measurement is blocked (docs/ENGINE_DECISION.md)
- values: conditions to make it final: l01_check.gd ALL PASS; simulation tick p95 at most 4 ms at 500 walkers and 50 nodes on the target phone; a real Android build starts and takes touch; no engine switch without a new approval
- rationale: spec default, verified current stable, MIT licence, the only engine I could obtain and checksum here. The main risk (GDScript speed for the simulation at 500 walkers) is unmeasured
- alternatives: Unity 6.3 LTS (not evaluated); Godot .NET or a native extension if GDScript is too slow
- approver status: APPROVED with a stated limitation (user: "Approve Stage 06, option C", 2026-11-23). Option C means: accepted without engine evidence. Conditions 1 to 4 stay open and are re-tested as soon as a runnable Godot exists
- affected files: docs/ENGINE_DECISION.md, docs/SOURCES.md, spikes/godot-sim/*
- supersedes: none

**CC-D-014**
- stage: 06
- date: 2026-11-23
- question: Which outbound hosts may the session reach for the engine spike?
- chosen option: 8 more exact hosts added on the user's request to continue (card approved)
- values: godotengine.org, docs.godotengine.org, downloads.godotengine.org, unity.com, docs.unity.com, github.com, objects.githubusercontent.com, release-assets.githubusercontent.com (plus developer.android.com added earlier in Stage 04)
- rationale: read the spec's source register and fetch the Godot build; GitHub was needed because the vendor's download host redirects to a storage host that is not allowed
- alternatives: unrestricted access (not chosen)
- approver status: APPROVED by the user (environment card)
- affected files: none (environment setting)
- supersedes: none

**CC-D-015**
- stage: 07
- date: 2026-11-23
- question: How is the production repository laid out, and which rules are enforced?
- chosen option: one Godot project at the repository root; layers core, simulation, levels, app (each may use only lower layers); no autoloads; one stable random service; schema-checked event log; table-driven state machine; Python lint, scenario validator and golden check that run without the engine
- values: layer order and rules L1 to L9 in scripts/lint.py; tick 20/s, 640 ticks; RNG xorshift32 with FNV-1a named streams; event hash FNV-1a 32
- rationale: keeps the rules headless and replayable, and gives checks that can run here while the engine cannot
- alternatives: Godot project in a subfolder (rejected: more path indirection); engine random numbers (rejected: not stable across versions); autoload services (rejected by the spec)
- approver status: APPROVED (user: "Approve Stage 07, option A. split app at Stage 09 or 10", 2026-11-23). The `app` layer is to be split into input / rendering / audio-save modules at Stage 09 or 10, with the lint layer table updated then
- affected files: project.godot, src/*, data/*, tests/*, tools/*, scripts/*, docs/ARCHITECTURE.md, docs/VERSION_MANIFEST.md
- supersedes: none

**CC-D-016**
- stage: 09
- date: 2026-11-23
- question: How is touch input arbitrated, and where do the thresholds live?
- chosen option: a pure per-touch state machine (CcGestureRouter) in a new src/input layer; thresholds only in data/input_tokens.json; one Python reference and one GDScript port running the same 21 cases
- values: drag 8 px, pan 12 px, tap 220 ms, long press 420 ms, pinch 1.06, snap 44 px, hit 56 px, edge reserve 24 px, hold timeout 3000 ms (all starting values, unmeasured)
- rationale: logic testable without a phone; the app layer is being split as approved at Stage 07
- alternatives: logic inside the scene script (rejected: untestable headless)
- approver status: APPROVED (user: "Approve Stage 09, option A": a lift off a ring snaps back at once)
- affected files: src/input/*, data/input_tokens.json, tests/fixtures/input_cases.json, scripts/ref_input.py, scripts/lint.py (new layer)
- supersedes: none

**CC-D-017**
- stage: 10
- date: 2026-11-23
- question: How is direction C implemented, and how are routes told apart without colour?
- chosen option: tokens in data/art_tokens.json; CcMapView in a new src/rendering layer; School route solid and Plaza route dashed; high-contrast theme; ribbon width only from counted EDGE_ENTERED
- values: ribbon width = clamp(3 + 1.9 x (sqrt(count) - 1), 3, 16) px; stave grid every 24 px of world space; notes 18 px (failed at 320 px, R-34)
- rationale: the contrast script found amber and sage identical in grayscale
- alternatives: separate hues only (rejected by the calculation)
- approver status: APPROVED (user: "Approve Stage 10, option B": fix narrow-phone legibility with fewer notes or a count badge)
- affected files: data/art_tokens.json, src/rendering/*, src/app/graybox.gd, scripts/check_contrast.py, scripts/ref_ribbon.py, scripts/stage10_preview.py, docs/VISUAL_IMPLEMENTATION.md, docs/stage10/*
- supersedes: none

**CC-D-018**
- stage: 11
- date: 2026-11-23
- question: How does the camera work, and what may each zoom band show?
- chosen option: CameraDirector with priorities touch > user > critical > decorative; Catmull-Rom path through A, B, D, F, G; hysteresis bands (street 1.75/1.55, city 0.85/1.00); ribbons only from the last 20 ticks of EDGE_ENTERED; queue badges (4, or 3 below 360 px wide); camera layer isolated from the simulation by lint rule L10
- values: scroll gain 0.85; inertia k 6.0, cap 1.6 viewport heights per second; zoom 0.65 to 2.80; notes 18 logical px
- rationale: the prompt's C1 to C3, with the camera unable to touch a run
- alternatives: none compared
- approver status: APPROVED (user: "Approve Stage 11, option A": slower editorial glide)
- affected files: src/camera/*, scripts/ref_camera.py, scripts/stage11_preview.py, tests/test_camera.gd, data/art_tokens.json, docs/CAMERA.md, docs/stage11/*
- supersedes: none

**CC-D-019**
- stage: 12
- date: 2026-11-23
- question: How are the six transitions built so they can be skipped or cancelled safely?
- chosen option: one data-driven state machine (data/transitions.json, CcTransition); every game-state callback fires at start; on_end once and cosmetic; touch freezes, skip settles in 100 ms, reduced motion is a 150 ms crossfade
- values: durations 550, 170, 800, 210, 650, 440 ms; auto-camera average limit 468 px/s (provisional)
- rationale: a cancel at any point cannot change a run or duplicate a result
- alternatives: end-of-transition callbacks (rejected: a skip could lose or repeat them)
- approver status: APPROVED (user: "Approve Stage 12, option A": all six as built)
- affected files: data/transitions.json, src/camera/transition.gd, scripts/ref_transitions.py, scripts/stage12_preview.py, tests/test_transitions.gd, docs/TRANSITIONS.md, docs/stage12/*
- supersedes: none

**CC-D-020**
- stage: 13
- date: 2026-11-23
- question: How is the result explained without inventing causes?
- chosen option: claims built only from counted events of the real run plus an executed NO_SIGN baseline on the same seed; DECISION events now carry alt_edge; materiality = different arrivals, pass/fail flip, or at least 10% change in waiting; at most three lines on the result screen; counterfactual phrases banned
- values: material blocked-time threshold 10%; bottleneck shown if at least 100 queue-ticks
- rationale: the prompt forbids fake explanations
- alternatives: model-written prose (rejected: unverifiable)
- approver status: APPROVED (user: "Approve Stage 13, option A")
- affected files: src/simulation/explainer.gd, src/simulation/sim_world.gd (alt_edge), scripts/ref_sim.py, scripts/ref_explain.py, tests/test_explainer.gd, tests/fixtures/explainer_cases.json, docs/BEHAVIOR_MATRIX.md, docs/CAUSAL_EXPLANATION.md, docs/stage13/*
- supersedes: none

**CC-D-021**
- stage: 14
- date: 2026-11-23
- question: What are L02 and L03, and what is not built?
- chosen option: L02 Ferry Landing (move the sign: 30 walkers, goal 28, best fixed placement 26) and L03 Two Narrow Roads (balance the load: 40 walkers, goal 29, two passing placements); both on the L01 geometry; L04 to L08 specified only; no share string; level validator extended; replays stored in data/replays
- values: L02 pass mark 28 of 30; L03 pass mark 29 of 40; moving to Canal Turn at ticks 100 to 230 passes L02
- rationale: found by search in the reference model; each has exactly one lesson and a second solution
- alternatives: new graphs per level (rejected: composition risk); a second wave from the same gate (rejected: gained at most 2)
- approver status: APPROVED (user: "Approve Stage 14, option A": future content emphasises timing)
- affected files: data/levels/*, data/replays/*, scripts/check_levels.py, scripts/stage14_diagrams.py, docs/analysis/stage14_level_search.py, tests/test_levels.gd, docs/LEVELS.md, docs/LEVELS_L04_L08_SPEC.md, docs/stage14/*
- supersedes: none

**CC-D-022**
- stage: 15
- date: 2026-11-23
- question: What does the game sound like, what can the player switch, and what is the default?
- chosen option: eleven original synthesised cues mapped to real events; four independent sliders; haptics off; reduced motion follows the system; patterns always on; left-handed mirror layout; trigger cap 10 per second; critical cues never dropped
- values: master 0.8, effects 0.8, texture 0.5, ui 0.8; max 6 effect voices; cooldowns reroute 250 ms, arrival 120 ms, queue 4 s per street
- rationale: restrained by rule, and tested against a 50-walker stream
- alternatives: licensed music (not allowed without permission)
- approver status: APPROVED (user: "Approve Stage 15, option A", 2026-11-23). Note: the sounds were approved without the listening check being confirmed; tone stays UNVERIFIED by me
- affected files: assets/audio/*, data/audio_map.json, data/visual_cues.json, data/settings_schema.json, src/audio/*, src/core/settings.gd, src/input/dock_layout.gd, scripts/synth_audio.py, ref_audio.py, ref_settings.py, check_audio_files.py, docs/AUDIO.md, docs/ACCESSIBILITY.md, docs/stage15/*
- supersedes: none

**CC-D-023**
- stage: 16
- date: 2026-11-23
- question: How is correctness verified without an engine or a device, and what did it find?
- chosen option: reference-model property and fuzz tests (`scripts/stage16_checks.py`, 283 checks); dock layout made width-aware (never wider than three controls fit; tablets 480 px on the thumb side); device profiling recorded as a release blocker
- values: dock span on tablets 480 px; button width = min(wanted, (span - tray - 24) / 2); fuzz 200 scenarios per level
- rationale: the sweep found a real layout bug (360 wide with larger targets broke the 24 px edge reserve; tablet dock spread 712 px)
- alternatives: skipping the sweep (rejected)
- approver status: APPROVED (user: "Approve Stage 16, option A", 2026-11-23)
- affected files: scripts/stage16_checks.py, scripts/stage16_evidence.py, scripts/ref_settings.py, src/input/dock_layout.gd, scripts/check_all.sh, docs/TEST_REPORT.md, docs/stage16/*
- supersedes: none

**CC-D-024**
- stage: 17
- date: 2026-11-23
- question: How is the playtest run when no players and no build exist?
- chosen option: protocol, consent text, empty outcome grid, one A/B question (reroute ink tick) and three candidate revisions marked as not playtest-derived
- values: 5 to 10 players, 15 minutes each, counts only, no in-game telemetry
- rationale: the prompt forbids invented testers and invented validation
- alternatives: simulated players (rejected: not evidence)
- approver status: PROPOSED. Awaiting "Approve Stage 17"
- affected files: docs/PLAYTEST.md
- supersedes: none

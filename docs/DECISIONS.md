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

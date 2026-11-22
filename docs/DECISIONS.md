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
- approver status: PROPOSED. Awaiting your Stage 00 answer
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

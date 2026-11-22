# LOOPS (Stage 02: three separate 20–45 s rule variants)

Three variants, kept separate on purpose. Nothing here is code; every outcome below is an **illustrative hypothesis (PROPOSED / UNVERIFIED)** until the Stage 08 graybox runs. Source for fixed numbers: the spec, section A (CC-RULESET-01).

## 0. What stays identical in all three (so the comparison is fair)

| Fixed | Value |
|---|---|
| Level | CC-L01 School Crossing, seed 1007, 20 walkers (12 to School, 8 to Plaza) |
| Round | 32 s simulated = 640 ticks at 20 ticks/s; typical repeat cycle under 75 s |
| Pass gate | at least 16 of 20 arrive by 0:32 |
| Score | the spec's A4 formula, unchanged |
| Sign | exactly one; legal sockets B (Canal Turn) and C (Market); headings N, E, S, W |
| Sign effect | a route *preference* at each walker's **next junction decision**, within 90 world units of the sign and aligned with the heading. Never an instant redirect or a block |
| Camera / simulation | the camera never changes the outcome |

What differs is only **when the player may act, and how often.**

## 1. Side by side

| | **A. One-shot** | **B. Placed + one timed turn** | **C. Re-placeable sign** |
|---|---|---|---|
| Player acts | Before Start only: pick socket and heading | Before Start, plus **one** 90° turn at any moment while running | Before Start, plus **move or turn the sign again during the run**, with a lock between actions |
| Actions per run | 1 placement (2 inputs) | 1 placement + 1 turn | 1 placement + as many as the lock allows (about 7 at a 4 s lock, provisional) |
| The 5-second explanation | "Place the sign, point it, press Start." | "Place the sign and point it. While they walk, tap it once to turn it." | "Place the sign. While they walk, pick it up and move or turn it. It must rest between moves." |
| One-sentence instruction | "Drag the sign to a ringed corner, tap to turn it, press Start." | "Same, and tap the sign once during the walk to turn it a quarter." | "Same, and drag it to the other corner when you want. It locks for 4 s after each move." |
| Most likely exploit | Try all 8 options (2 sockets × 4 headings) in 8 runs; deterministic seed means the answer is findable by brute force | Replay and find the best second to turn; the seed makes the timing repeatable | "Chase the crowd": keep moving the sign to wherever the queue is |
| Engineering cost | S | M | L |
| Learnability risk | Low | Medium | High |
| Emergent depth (hypothesis) | Low–medium | Medium | High but fiddly |

Cost key (JUDGEMENT): S = one input phase, M = adds one timed input and a new log entry type, L = adds a live drag during a running simulation, a cooldown state and more input arbitration.

---

## 2. Variant A: one-shot sign, then observation

**Rule:** the sign is placed and turned during PLACEMENT. Pressing Start commits it. After that the player only watches.

**Controls (preliminary):** drag the sign from the dock to a ringed socket (snaps within 44 px); tap the placed sign to turn it 90°; press Start. No input while running except Pause.

**Eight beats**

| # | Beat | What the player does | What they see |
|---|---|---|---|
| 1 | Read the goal | Looks | "Deliver 16 of 20 before 0:32", walkers waiting at North Gate |
| 2 | Pick up | Drags the sign from the dock | Sign lifts; both ringed sockets brighten |
| 3 | Choose a corner | Hovers over Canal Turn | Receiving ring; the real next turns light up as small chevrons |
| 4 | Choose a heading | Taps to turn | Chevrons change with the heading |
| 5 | Commit | Presses Start | Placement locks; clock starts |
| 6 | First reroute | Watches | A few walkers turn differently at the next junction |
| 7 | The cascade | Watches | A queue forms or fails to form on the narrow walkway |
| 8 | Result | Reads | Arrived count and the one junction that mattered |

**Causality:**
```
choose corner + heading ──► sign bonus for walkers near it and aligned with it
        │                                   │
        └──────────── (locked at Start) ────┘
                                            ▼
                         next-junction choices ──► queues ──► arrivals ──► result
```

**Illustrative outcome:** sign at Canal Turn pointing south sends more walkers onto the narrow walkway; the walkway fills and some arrive late.
**Failure mode:** the first run misses 16. The player does not know *why* until the result names the junction.
**Learnability risk (low):** one decision, no timing.
**Emergent depth:** a pure planning puzzle. Depth comes from walker types and the graph, not from the player's hands.
**Likely exploit:** brute force. With a fixed seed the full option set is 8 runs. The mitigation is variety across levels, not rules inside this one.
**Playtest question:** after one failed run, can a tester say which junction they would change, without being told?
**Round length and score:** 32 s, spec formula. Repeat cycle roughly 45–60 s (placement plus run plus result).

---

## 3. Variant B: one placed sign plus one precisely timed turn

**Rule:** as A, plus **one** 90° turn of the placed sign once the simulation is running. The sign cannot move to the other socket. The turn is tied to the tick it was issued on (spec A2). A system interruption does not consume it.

**Controls (preliminary):** as A; during the run, a single tap on the sign turns it 90° once. After use, the sign shows a spent mark and ignores taps. Panning the map never turns the sign (spec C5: a drag over 12 px belongs to the map).

**Eight beats**

| # | Beat | What the player does | What they see |
|---|---|---|---|
| 1 | Read the goal | Looks | Same as A, plus "1 turn left" on the dock |
| 2 | Place | Drags the sign to a ringed corner | Receiving ring, branch previews |
| 3 | Aim | Taps to choose the starting heading | Chevrons follow |
| 4 | Commit | Presses Start | Clock starts; the sign now shows a quarter-turn hint |
| 5 | Watch the first wave | Watches the first 6–10 s | First reroutes; the queue starts to build |
| 6 | The timing decision | Taps the sign **when the queue forms** | Instant indexed 90° turn; short ink tick at the node |
| 7 | The second cascade | Watches | Walkers deciding **after** the turn choose differently; walkers mid-street do not |
| 8 | Result | Reads | Arrived count and the decisive junction, with the turn time |

**Causality:**
```
place + aim ─► bonus ─► next-junction choices ─► queue builds
                                   ▲                   │
   tap at tick t ─► new heading ───┘ (affects only     ▼
                    decisions after t)           arrivals ─► result
```

**Illustrative outcome:** the first heading is fine early; a queue forms at 0:08; turning at 0:09 diverts the later walkers and saves two arrivals.
**Failure mode:** turning too early (before there is any queue) or too late (after the later walkers have already decided).
**Learnability risk (medium):** a new player may not notice the second action. Mitigation: a quiet dock cue "1 turn left", and the placement preview shows the quarter-turn.
**Emergent depth (hypothesis):** one real decision about *when*, without a juggling task.
**Likely exploit:** replay to find the best turn second. Partly the point (deliberate practice), partly a brute-force path. Mitigate with walker-profile differences, not by hiding the timing.
**Playtest question:** in runs where the turn would have helped, do testers use it on purpose, or ignore it, or misfire it?
**Round length and score:** 32 s, spec formula. Repeat cycle roughly 50–70 s.

---

## 4. Variant C: re-placeable sign at a moving junction (still one sign)

**Rule:** one sign, but during the run it may be **moved to the other socket or turned**, with a lock after each action (4.0 s, provisional). The sign still has no effect on walkers already mid-street, and still only on the next junction decision.

**Controls (preliminary):** drag the placed sign to the other ringed socket, or tap it to turn it. A lock ring shows the 4 s wait. Active touch always wins over camera motion (spec C1).

**Eight beats**

| # | Beat | What the player does | What they see |
|---|---|---|---|
| 1 | Read the goal | Looks | Same as A |
| 2 | Place | Drags to a corner | Receiving ring |
| 3 | Aim | Taps to set the heading | Chevrons |
| 4 | Commit | Presses Start | Clock starts |
| 5 | Watch | Watches the first wave | Queue starts at Canal Turn |
| 6 | Move | Drags the sign to Market | A lift, a flight, a snap; lock ring starts |
| 7 | Adjust | Taps to turn after the lock | New heading at the new corner |
| 8 | Result | Reads | Arrived count, with the list of moves and which one mattered |

**Causality:**
```
place + aim ─► bonus at corner X ─► choices near X ─► queues
       ▲                                       │
       └── move or turn at tick t (lock 4 s) ──┘ (affects only decisions after t,
                                                  and only near the sign's new corner)
```

**Illustrative outcome:** the player spots the crowd bunching at Market and moves the sign there.
**Failure mode:** constant fiddling; moving the sign right as walkers have already chosen.
**Learnability risk (high):** drag, tap, lock and timing at once, on a phone, during motion.
**Emergent depth:** highest, but partly from busywork. It rewards watching the crowd and also rewards twitching.
**Likely exploit:** "chase the crowd", moving to wherever the queue is, which may be the dominant strategy and flatten the puzzle.
**Playtest question:** do testers keep watching the crowd, or do they fidget with the sign? (Count actions per run.)
**Round length and score:** 32 s, spec formula. Repeat cycle roughly 55–80 s.

---

## 5. A finding that affects every variant (UNVERIFIED, hand arithmetic)

From the spec's coordinates, straight-line distances, node to node (the real curved sidewalks will be a little longer):

| Route | Length (units) | Time at 38 u/s |
|---|---:|---:|
| A to School via Canal Turn, Bridge West | 457.8 | 12.0 s |
| A to School via Market, Bridge East, Plaza | 613.9 | 16.2 s |
| A to Plaza via Market, Bridge East | 453.9 | 11.9 s |
| A to Plaza via Canal Turn, Bridge West, Bridge East | 592.7 | 15.6 s |

- The natural route for **school-bound** walkers goes through the narrow walkway (1.6 walkers/s).
- The natural route for **plaza-bound** walkers uses the wide roads (3.0/s) and never meets a narrow link.
- If all 12 school-bound walkers leave at tick 0 and enter the walkway at 1.6/s, the last one leaves Canal Turn at about 10.3 s and reaches the School at about **18.9 s**, inside both the 30 s deadline and the 32 s limit.
- So with **no sign at all**, CC-L01 as written may already deliver 20 of 20. That would make the first puzzle too easy, and would make every variant above feel pointless.

This is arithmetic, not a simulation. It does not model the 0.5 s re-evaluation, queue-wait estimates or loop penalties. **Stage 03 must run the no-sign baseline, and the spec already allows editing the graph if the first puzzle is boring.** I am recording it now so that it does not surprise us then.

## 6. Recommendation (PROPOSED, not decided)

**Choose B**, as a hypothesis to test, for these reasons:

1. It is the only variant that adds a decision about *time* without adding a juggling task. That is the cheapest source of the "I should have turned it earlier" feeling that makes someone press Try again.
2. A is the safest and the cheapest, but a planning puzzle with 8 possible answers on a fixed seed is solved by memory; replay interest depends on level variety.
3. C has the most depth on paper, but the likeliest dominant strategy (chase the crowd), the highest input-conflict risk with pan and pinch, and the largest engineering cost. It also moves away from the spec's own tutorial rule.
4. B matches the spec's own baseline (placement plus one mid-run rotation), so choosing it requires no change to an approved rule.

**What would make me change my mind:** if the Stage 08 graybox shows the turn is almost never worth using, move to A. If testers always find the best turn instantly, B degrades to A and C deserves a trial.

**Simplest 5-second explanation (B):** "Place the sign and point it. While they walk, tap it once to turn it."

**Most likely exploit (B):** replaying to find the best turn second.

## 7. Acceptance check for this stage

- A new tester can be told what to do in one sentence per variant (section 1). **Untested with real testers; this is a design claim.**
- No variant relies on a mystery consequence: each effect is next-junction, within 90 units, and previewed before it happens.
- No gameplay code was written.

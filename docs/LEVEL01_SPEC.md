# LEVEL 01 SPEC (Stage 03): CC-L01 School Crossing

Two things are specified here: **rev0**, exactly as written in the spec, and **candidate edits R1 and R2**, which are proposals. The central finding is that rev0, run under the rules in `docs/RULES.md`, is not a puzzle.

All figures come from the throwaway model in `docs/analysis/` (it implements `docs/RULES.md` and `docs/SIMULATION_EVENTS.md`). It has not been checked against a real engine; Stage 08 must reproduce it.

## 1. Rev0: the level as the spec writes it

```
                      A  North Gate (180,50)  spawn
                    /   \
        3.0/s     /       \   3.0/s
                B ---------- C
      Canal Turn  \  3.0/s    /  Market
   (sign slot)     \        /    (sign slot)
        1.6/s     /   \    / 3.0/s
                D ======= E        D-E bridge 1.2/s (narrow)
  Bridge West   |         |   Bridge East
        3.0/s   |         |  3.0/s
                F --------- G
              School   3.0/s   Plaza
```

| Item | Value |
|---|---|
| World | 360 × 620 units |
| Nodes | A (180,50) spawn; B (92,145) and C (262,155) sign sockets; D (120,286); E (254,290); F (106,470) School; G (266,475) Plaza |
| Links (9, each two directed edges) | AB 3.0, AC 3.0, BC 3.0, **BD 1.6**, CE 3.0, **DE 1.2**, DF 3.0, EG 3.0, FG 3.0 walkers/s |
| Spawns | tick 0: 12 to School at A (7 commuters, 3 followers, 2 independents). Tick 40: 8 to Plaza at A (4, 3, 1) |
| Round | 640 ticks (32 s), seed 1007 |
| Pass | 16 of 20 arrive by tick 640; on-time deadline tick 600 |
| Sign | one; sockets B and C; headings N, E, S, W; bonus 4.0 s; radius 90; dot ≥ 0.65; lock 80 ticks; hold 60 ticks |
| Camera path | A, B, D, F |

## 2. Balance and solvability: rev0 is solvable, and trivial

**No-sign baseline** (a placement with no favoured edge, for example B/W):

| Measure | Value |
|---|---|
| Arrived | **20 of 20** |
| On time | 20 |
| Last arrival | tick 396 (19.8 s) |
| `blocked_person_ticks` | 838 |
| Score | 99 |

**All 8 static placements** (placed before Start, never touched):

| Placement | Arrived | Score | Last arrival tick | `blocked_person_ticks` |
|---|---:|---:|---:|---:|
| B/N, B/E, B/S, B/W | 20 | 99 | 396 | 838 |
| C/N, C/E, C/S, C/W | 20 | 99 | 396 | 838 |

The results are identical to the digit: **the sign changes no walker's route**. This is not a modelling slip. The model does apply the bonus (38 decisions carry 4.0 s in the B/S run), but no choice flips.

**Why.** At the two sockets the next-best route costs far more than the sign is worth:

| Decision | Best route (units) | Next-best (units) | Gap | Largest sign benefit |
|---|---:|---:|---:|---|
| At B, going to School | BD 328 | BA 587 | 6.8 s at 38 u/s | follower 4.0 s, commuter 3.2 s, independent 1.4 s |
| At C, going to Plaza | CE 321 | CA 587 | 7.0 s | same |
| At A, going to School (outside the 90-unit range) | AB 458 | AC 587 | 3.4 s | in reach of the sign but **not in range** (A is 129.5 u from B, 133.2 u from C) |
| At A, going to Plaza | AC 454 | AB 593 | 3.7 s | same |

Queue aversion does not rescue it either. Every combination I tried of sign bonus (4 to 12) and walkway rate (0.6 to 1.6 walkers/s) left the no-sign baseline at 20 of 20 (`stage03_exp1_bonus_vs_rate.py`). Walkers who dislike queues re-route by themselves and everyone still arrives inside 32 s.

**Verdict:** rev0 fails the spec's own test for the first level ("a decision visibly changes more than one citizen's trajectory"; "at least one pass and one failure achievable"). The spec anticipated this and says to propose a documented graph edit here.

## 3. Candidate R1 (PROPOSED): make the first fork steerable and the level hard enough to fail

Edits against rev0:

| # | Change | Why |
|---|---|---|
| E-1 | Move Market C from (262,155) to **(270,115)** | At North Gate the fork AB vs AC is the only near-tie (3.4 s). With C further east, heading **E** favours only AC (dot 0.81) and **S** or **W** favour only AB, so a heading can pick a branch |
| E-2 | Sign sockets become **A and B** (two, as the UI expects); C is a plain junction | The sign can only act where a near-tie exists |
| E-3 | Walkway BD service rate **1.6 → 0.3 walkers/s** | Creates real lateness for walkers who take it |
| E-4 | Sign bonus **4.0 → 6.0 s** | A bonus above the 3.4 s fork gap flips followers and commuters, but not independents |
| E-5 | Pass mark **16 → 18** of 20 | Otherwise the no-sign baseline (17) already passes |

**Truth table R1** (favoured edges):

| Socket | N | E | S | W |
|---|---|---|---|---|
| A | none | AC | AB | AB |
| B | BA | BA, BC | BD | none |

**Results R1** (model; pass mark 18):

| Placement | Arrived | Score | Last arrival tick | Walkers whose route differs from baseline |
|---|---:|---:|---:|---:|
| No-effect (A/N, B/N, B/S, B/W) | 17 | 86 | 581 | 0 |
| A/S, A/W | 17 | 86 | 581 | 8 (more blocking, same arrivals) |
| **A/E** | **20** | 99 | 473 | **20** |
| **B/E** | **20** | 97 | 631 | 4 |

- **Passes:** 2 of 8 static placements, by different mechanisms (A/E diverts everyone at the first fork; B/E catches walkers already at Canal Turn). That is two viable strategies, **tested**.
- **Fails:** the baseline and 6 of the 8 placements.
- **Sign effect:** at least 2 downstream choices change (4 and 20 walkers).
- **Profile story:** W6 to W8 in `docs/RULES.md` section 11 show the sign flips followers and commuters but not independents.
- **Caveat:** B/E finishes at tick 631, 9 ticks from the limit. The margin is thin.

**But loop C earns almost nothing in R1.** Of 1440 single running actions, 1369 changed nothing, 42 helped and 29 hurt. The best helpful action is rotating to E at tick 0, which is the same as placing it correctly. The decisive fork happens at spawn, before a running action can matter. A one-shot sign (loop A) would play identically here.

## 4. Candidate R2 (PROPOSED design principle): a second wave makes loop C meaningful

Loop C only matters when **the best sign state for the first wave is bad for the second wave**. Test, on top of R1 with the pass mark back at 16:

- Wave 1: 12 School-bound at tick 0 (7/3/2), as now.
- Wave 2: **8 School-bound at tick 300 (15 s)** (4/3/1), instead of the Plaza-bound wave.

| Play | Arrived |
|---|---:|
| No-effect baseline | 9 |
| Best single static placement (A/E) | 15 |
| A/E, then **turn to N at tick 320** | **16 (pass)** |
| Best with any single running action | 16 |
| Same idea with wave 2 at tick 360 | 13 (too late to rescue) |

So a two-wave level can **require** a mid-run action to pass (15 without, 16 with). Caveats, stated plainly: the margin is one walker; the level loses its Plaza branch; I have not searched the space widely; and it is a proof that the rule can matter, not a tuned level.

## 5. New validator rules (PROPOSED)

Rejections and warnings from the spec (section E2) stay. Add:

| ID | Rule | Rev0 | R1 | R2 |
|---|---|---|---|---|
| V-1 `sign_must_matter` | at least one placement gives a different arrival count or a different route for at least 2 walkers than the no-effect placement. Error if not | **fails** | passes | passes |
| V-2 `baseline_not_trivial` | the no-effect baseline arrives fewer than `pass_count`. Warning | **fails** | passes (17 < 18) | passes |
| V-3 `two_viable_strategies` | at least 2 distinct static placements reach `pass_count`, when the level claims it. Warning | n/a | passes (A/E, B/E) | **fails** (0) |
| V-4 `requires_running_action` | for a level that teaches timing: best static arrivals < `pass_count` ≤ best with at most N actions | n/a | not claimed | passes (15 < 16 ≤ 16) |
| V-5 `report_action_value` | information only: share of single running actions that help or hurt | | 42 / 29 of 1440 | |

V-3 and V-4 are alternatives: a level either offers several static solutions or demands a timing move. The level file declares which lesson it teaches.

## 6. Level file additions (schema v2, PROPOSED)

```json
"sign": { "max_active": 1, "allowed_slots": ["A","B"], "directions": ["N","E","S","W"],
          "actions": "C", "lock_ticks": 80, "hold_ticks": 60,
          "bonus_seconds": 6.0, "radius": 90, "heading_dot_min": 0.65 },
"spawn_schedule": [ { "tick": 0, "count": 12, "origin": "A", "destination": "F",
                      "deadline_tick": 600, "profile_mix": {"COMMUTER":7,"FOLLOWER":3,"INDEPENDENT":2} } ],
"pass_arrivals": 18,
"validation": { "lesson": "static", "expect_baseline_below_pass": true }
```

## 7. What you are asked to decide at this gate

1. Approve `CC-RULESET-01C` (docs/RULES.md), or list any value to override.
2. For CC-L01, choose: **(a)** keep rev0 and fix the level in Stage 08 once there is a graybox; **(b)** adopt R1 now; **(c)** adopt R1 plus the two-wave idea of R2 as the first level's direction; **(d)** something else. I recommend (b) now and the two-wave idea held for L02 or L03, because R1 is the smaller change that passes my own validator.

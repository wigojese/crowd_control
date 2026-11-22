# RULES (Stage 03: formal ruleset, loop C)

Ruleset id: **CC-RULESET-01C** = the spec's CC-RULESET-01 plus the loop you chose at Stage 02 (CC-D-009, C: a re-placeable sign). Status: **PROPOSED**, awaiting "Approve Stage 03". All numbers are either from the spec or marked as new. Evidence for any number I computed is in `docs/analysis/` (throwaway Python, not engine code), reproducible with `python3 -I docs/analysis/<file>`.

## 0. Rule changes against the spec (spec section H2 table)

| # | Current rule | Proposed rule | Expected benefit | Regression risk | Test | Approval |
|---|---|---|---|---|---|---|
| R-1 | Spec A2: "no moving to another socket once RUN begins" (tutorial rounds) | The single sign may be moved to the other legal socket, or turned 90°, while running | Your choice of loop C. More decisions in a round | Highest input-conflict risk with pan and pinch; "chase the crowd" strategy | T-17 to T-21 | Loop chosen by you, CC-D-009. Exact rule: this document |
| R-2 | none | A moved sign is **inactive while it is held** and must be dropped within **60 ticks (3.0 s)** or it snaps back | Makes "chasing" cost something measurable | Feels punishing if the drop zone is hard to hit | T-18, T-19 | New, PROPOSED |
| R-3 | none | **80 ticks (4.0 s) lock** after every running action (move drop or turn) | Caps the number of actions per round at 8 | Too long may feel unresponsive; to be tuned at Stage 08/09 | T-17 | New, PROPOSED |
| R-4 | Spec A3: "predicted remaining travel … plus known queued service times" | Queue wait counts **only the candidate's first edge** (its own queue), not downstream queues | Removes ambiguity and look-ahead | A walker may walk into a known downstream jam | T-27 | Interpretation of an ambiguous sentence, PROPOSED |
| R-5 | Spec A4: "stamped deadline (default 30s)" | Deadline is an **absolute tick** stamped per spawn entry: **600 (30.0 s)**. The pass gate still counts arrivals up to tick 640 (32.0 s) | Resolves the 30 s vs 32 s ambiguity | None | T-22 | Interpretation, PROPOSED |
| R-6 | Spec A3: "never reversing mid-edge" | Also **no reversal at a node** unless the node has exactly one exit | Prevents ping-pong at junctions | A walker can never turn back | T-05 | PROPOSED |
| R-7 | Spec A5: tokens cap max(1, rate × 1 s) | Initial tokens = **1.0** on every edge at tick 0 (not the cap) | Spec says tokens must not pile up across initialisation | None | T-26 | PROPOSED |
| R-8 | Spec A3: edge length "approximate from node coordinates" | Simulation length = straight-line distance between node coordinates; curved drawing is cosmetic | One source of truth | Drawn sidewalks look longer than simulated ones | T-13 | PROPOSED |
| R-9 | Spec A2: pause | **No sign commands while paused**; the lock and hold timers do not advance while paused | Pause cannot be used to re-plan for free | None | T-08, T-20 | PROPOSED |

## 1. States

**Run state (macro).** `INTRO → PLACEMENT → RUNNING ⇄ PAUSED → RESULT → (RETRY → PLACEMENT | EXIT)`

| From | Event | To | Condition |
|---|---|---|---|
| INTRO | finish or skip | PLACEMENT | always allowed |
| PLACEMENT | START | RUNNING | sign must be PLACED, else rejected with `no_sign_placed` |
| RUNNING | PAUSE or OS interruption | PAUSED | always |
| PAUSED | RESUME | RUNNING | always |
| RUNNING | last walker terminal, or tick 640 reached | RESULT | automatic |
| RESULT | RETRY | PLACEMENT | resets **all** state: ticks, walkers, tokens, queues, sign, lock, score |
| RESULT | EXIT | EXIT | always |

Anything else is an illegal transition and is rejected (no state change, `COMMAND_REJECTED` logged).

**Sign state.**

| State | Meaning |
|---|---|
| `DOCK` | not on the map (only before the first placement) |
| `HELD` | picked up: **no influence on anyone** |
| `PLACED(slot, heading)` | active |
| `LOCKED(until_tick)` | placed and active, but pickup and turn are refused until `until_tick` |

During PLACEMENT the simulation is frozen: placing, moving and turning are free and unlimited, with no lock and no hold timer.

## 2. Graph and walker data

- **Nodes:** id, x, y, kind (spawn, junction, destination), `sign_slot` flag. **Directed edges:** each bidirectional link becomes two, ids `from+to` (for example `BD` and `DB`), each with its own token bucket and FIFO.
- **Walker:** `id, profile_id, origin, destination, edge_id, edge_t, base_speed, state, spawn_tick, last_node_ids[3], previous_edge, rng_seed`.
- **Walker states:** `UNSPAWNED → NEEDS_DECISION → QUEUED → ON_EDGE → (NEEDS_DECISION | ARRIVED)`, plus `STRANDED` when no path exists.
- **Profiles:**

| Profile | Sign sensitivity | Crowd sensitivity | Speed (u/s) |
|---|---:|---:|---:|
| COMMUTER | 0.8 | 0.35 | 38 |
| FOLLOWER | 1.0 | 0.9 | 34 |
| INDEPENDENT | 0.35 | 0.2 | 42 |

- **Ids** are assigned in spawn-schedule order, then in the profile order written in the schedule (all of one profile, then the next). Spawn schedule uses absolute ticks.

## 3. Sign influence

A walker at node `j`, considering outgoing edge `e`, gets `sign_bonus_seconds = 4.0` (value overridable per level) when **all** hold:
1. the sign is `PLACED` or `LOCKED` (not `HELD`);
2. the sign's socket node is within **90 world units** of `j`;
3. the unit vector of `e` (from `j` to its far end, straight line) has dot product **≥ 0.65** with the sign's heading vector (N = (0,−1), E = (1,0), S = (0,1), W = (−1,0)).

With the spec's sockets (B and C) and radius 90, the only junction within range of a socket is the socket itself, so the sign affects decisions at its own node only.

**Truth table, CC-L01 as written (sockets B and C).** "Favoured" means the edge gets the bonus. Computed, `docs/analysis/stage03_numeric_check.py`.

| Socket | Heading | Favoured edge(s) | Note |
|---|---|---|---|
| B | N | BA | back toward North Gate |
| B | E | BA, BC | BA dot = 0.680, BC dot = 0.998 |
| B | S | BD | the narrow walkway |
| B | W | none | no edge reaches 0.65: a legal "no effect" placement |
| C | N | CA | |
| C | E | none | legal "no effect" placement |
| C | S | CE | |
| C | W | CB | CA dot = 0.616, below 0.65, so not favoured |

## 4. The decision

At every decision, for each candidate edge `e` leaving the walker's current node (excluding the reverse of its previous edge, unless it has the only exit):

```
cost(e) = travel_seconds(e)
        + crowd_sensitivity * queue_wait_seconds(e)
        + loop_penalty(e)
        - sign_sensitivity * sign_bonus_seconds(e)

travel_seconds(e)      = (length(e) + shortest_path(far_end(e), destination)) / base_speed
queue_wait_seconds(e)  = max(0, ahead(e) + 1 - tokens(e)) / service_rate(e)
ahead(e)               = walkers already in e's FIFO, in front of this walker
loop_penalty(e)        = 6.0 s if far_end(e) is among the walker's last 3 departed-from nodes, else 0
```

The walker picks the **lowest cost**. Ties: lowest edge id (string order). The seeded PRNG is a tie-break of last resort only; with unique edge ids it is never reached, and is kept so that a later rule can use it without changing the log format.

**Evaluation timing.** A walker evaluates when it arrives at a node (on the following tick) and then **every 10 ticks (0.5 s)** while it is still queued. A **sign change** (placed, picked up, dropped, turned) makes every queued walker re-evaluate on that tick. A walker that changes its mind leaves its FIFO and joins the back of the new one, with the current tick as its arrival tick. Decisions are processed in ascending walker id and each one sees the queues as the earlier ones left them.

## 5. Queues and capacity

- Each directed edge has a token bucket: `tokens += service_rate × 0.05` each tick, capped at `max(1, service_rate × 1.0)`. Start: 1.0.
- A walker enters an edge by spending one token. Entry order is FIFO by queue-arrival tick, then by walker id. Edges are served in ascending id order each tick.
- No body collisions, no passing rules. No walker enters a closed edge (service rate 0 blocks; the queue grows until the time limit).
- `blocked_person_ticks` counts one for every tick a walker sits in a FIFO and is not served that tick. Nothing else counts.

## 6. Movement and arrival

`edge_t += base_speed × 0.05 / length` each tick; a walker that entered an edge this tick starts moving on the next. At `edge_t ≥ 1` it is at the far node. If that node is its destination it is `ARRIVED` with `arrival_tick = tick + 1`, otherwise it needs a decision next tick. A walker already on an edge is **never redirected**: sign changes affect only decisions made after the change.

## 7. Player commands (loop C)

Every command is assigned to the next simulation tick and logged with that tick id and an ordinal. Rejected commands change nothing and are not "spent".

| Command | Allowed when | Effect | Rejected with |
|---|---|---|---|
| `PLACE(slot, heading)` | PLACEMENT, sign in DOCK | sign becomes PLACED | `bad_slot`, `wrong_state` |
| `MOVE(slot)` | PLACEMENT any time; RUNNING if not locked and not held | PLACEMENT: moves instantly. RUNNING: sign becomes HELD at the pickup tick, must be dropped within 60 ticks on a legal socket | `bad_slot`, `locked`, `already_held`, `paused_no_commands` |
| `DROP(slot)` | sign is HELD | sign becomes PLACED at `slot`, heading kept, **lock starts: 80 ticks** | `bad_slot` (snap-back, below) |
| `ROTATE` | PLACEMENT any time; RUNNING if not locked and not held | heading advances 90° clockwise (N→E→S→W→N); lock starts (80 ticks) in RUNNING | `locked`, `held`, `paused_no_commands` |
| `START` | PLACEMENT, sign PLACED | → RUNNING | `no_sign_placed` |
| `PAUSE`, `RESUME` | RUNNING / PAUSED | as in the state table | |

**Snap-back.** If a HELD sign is not dropped on a legal socket within 60 ticks, it returns to its previous socket and heading, is active again, and **no lock starts** (the inactive time was the cost).

**Same-tick order.** Commands for one tick apply in ordinal order. A rotate and a drop in the same tick apply as logged.

**Measurable anti-"chase the crowd" rules:** (a) the held sign has no effect, (b) 4 s lock after each action, (c) 3 s drop timeout, (d) the result reports `sign_actions` so a level can be validated against fidgeting.

## 8. End, result and score

- Round ends at the first of: all walkers `ARRIVED` or `STRANDED`; tick 640.
- Score exactly as the spec: `delivery_rate = correct_arrivals / total_spawned`; `on_time_rate = delivered_by_deadline / max(1, correct_arrivals)`; `congestion_share = blocked_person_ticks / max(1, total_person_ticks)`; `score = round(100 × (0.70×delivery + 0.20×on_time + 0.10×(1 − clamp01(congestion_share))))`.
- `total_person_ticks` = sum over walkers of the ticks they were alive (spawned and not yet arrived).
- **PASS** is separate: `correct_arrivals ≥ pass_count` (arrivals up to and including tick 640). A score never overrides it.
- Player-facing claims allowed only if the log supports them: arrival counts, the edge with the most blocked ticks, the number of walkers whose chosen edge at a node differs from the baseline replay, `sign_actions`, and the tick of each action. Nothing else.

## 9. Seeds

`seed` is the level seed (1007 for CC-L01). The simulation owns one isolated RNG stream, seeded from it, that no rendering or audio code may touch. In this ruleset decisions are fully determined without randomness; the stream exists only for the tie-break of last resort.

## 10. Pseudocode

```
tick(t):
  apply_commands(t)                      # in ordinal order; may set sign_changed
  finish_drop_or_snap_back(t)            # may set sign_changed
  spawn(t)
  refill_tokens()
  for w in walkers sorted by id:
      if w.needs_decision or (w.queued and (t - w.last_eval >= 10 or sign_changed)):
          best = argmin over candidate edges of cost(w, e)   # ties: lowest edge id
          move w to the back of FIFO[best] if best != current queue
          log DECISION
  for e in edges sorted by id:
      while tokens[e] >= 1 and FIFO[e] not empty:
          w = pop head; tokens[e] -= 1; w.enter(e); log EDGE_ENTERED
  for w in on_edge walkers not entered this tick:
      w.edge_t += speed * 0.05 / length(e)
      if w.edge_t >= 1: arrive_at_far_node(w)               # ARRIVED or needs decision
  count blocked_person_ticks and total_person_ticks
```

Full tick order and event list: `docs/SIMULATION_EVENTS.md`.

## 11. Eight worked examples (CC-L01 as written unless stated; from `stage03_exp5_worked_examples.py`)

Costs in seconds: travel / crowd / loop / sign / total.

| # | Situation | Candidate costs | Result |
|---|---|---|---|
| W1 | Commuter to School at Canal Turn, sign B/S, no queue | BC 16.42/0/0/0 = **16.42**; BD 8.64/0/0/−3.2 = **5.44**; BA excluded (reverse) | BD |
| W2 | Follower to School at Canal Turn, sign B/E, 5 waiting on BD, no tokens | BC 18.36/0/0/−4.0 = **14.36**; BD 9.66/3.38/0/0 = **13.03** | BD, but only by 1.3 s: the queue nearly flips it |
| W3 | Independent to School at Canal Turn, sign B/S | BC **14.86**; BD 7.82/0/0/−1.4 = **6.42** | BD |
| W4 | Commuter to Plaza at Market, sign C/W (favours CB) | CB 16.67/0/0/−3.2 = **13.47**; CE **8.44**; CA excluded | CE: the 3.2 s bonus cannot close a 8.2 s gap |
| W5 | Commuter to School at Market after A→B→C (loop) | CA 15.55 + loop **6.0** = **21.55**; CE **11.94**; CB excluded | CE |
| W6 | Follower to School at North Gate, **R1** (sign A/E, bonus 6.0) | AB **13.46**; AC 17.80/0/0/−6.0 = **11.80** | AC: the sign flips a follower |
| W7 | Commuter, same | AB **12.05**; AC 15.93/0/0/−4.8 = **11.13** | AC: flips |
| W8 | Independent, same | AB **10.90**; AC 14.41/0/0/−2.1 = **12.31** | AB: ignores the sign |

W6–W8 show the profile story the spec asks for: the sign moves followers and commuters, not independents.

## 12. Acceptance tests (GIVEN / WHEN / THEN)

IDs are stable for the Stage 07 test skeleton.

| ID | GIVEN | WHEN | THEN |
|---|---|---|---|
| T-01 | sign PLACED at B | a walker decides at A, C, D | its cost has no sign term (sign affects only its own node within 90 u) |
| T-02 | RUNNING, sign PLACED at B | `MOVE(Z)` where Z is not a legal socket | rejected `bad_slot`; sign unchanged; no lock started |
| T-03 | sign PLACED | a second `PLACE` is issued | rejected `wrong_state`; exactly one sign exists |
| T-04 | a level with no link B–D | a walker at B decides | no BD edge is ever a candidate; no walker is on a missing edge |
| T-05 | a walker at a node with several exits, previous edge known | it decides | the reverse edge is not a candidate; at a one-exit node it is |
| T-06 | three walkers queue at the same edge on ticks 10, 10, 12 | tokens allow one per tick | order is by arrival tick, then id: (10, id lower), (10, id higher), (12) |
| T-07 | a link with service rate 0 | the round runs | nobody enters it; walkers behind it remain queued; result at tick 640 |
| T-08 | RUNNING at tick 200 | PAUSE for any real time, then RESUME | tick is still 200; lock and hold timers unchanged; sign commands rejected while paused |
| T-09 | a walker reaches its destination | the node is processed twice (replay) | it is counted as arrived once |
| T-10 | same level, seed and command log | run twice | identical event-log hash |
| T-11 | two commands share tick 100 with ordinals 1 and 2 | run | applied in ordinal order, every time |
| T-12 | a walker is on an edge when the sign turns | it later reaches the node | the turn affects its decision at that node only; its current edge is unchanged |
| T-13 | the same run | rendered at 30, 60 and 120 Hz with different camera zoom | identical event-log hash |
| T-14 | CC-L01 | run to tick 640 | every walker has `ARRIVED` or an unarrived count; none is lost |
| T-15 | a level whose profile mix does not sum to the batch count | loaded | validator rejects it |
| T-16 | a run state is saved and loaded | resume | log hash and tick are identical; a corrupted save falls back to restart with a notice |
| T-17 | sign LOCKED for ticks 200–280 | `ROTATE` at tick 250 | rejected `locked`; the sign is unchanged and no action is spent |
| T-18 | sign picked up at tick 300 | a walker decides at tick 305 | no sign bonus is applied to it |
| T-19 | sign HELD at tick 300 and never dropped | tick 360 arrives | sign returns to its previous socket and heading, active, no lock |
| T-20 | the app is backgrounded for 60 s while LOCKED | resume | the lock has not shortened |
| T-21 | walkers are queued at B and the sign is turned at tick 205 | tick 205 | all queued walkers at the affected nodes re-evaluate on that tick, not at their next 10-tick slot |
| T-22 | a walker arrives at tick 601 | result | counted for the pass gate; **not** on time |
| T-23 | a walker is served the same tick it queues | result | contributes 0 to `blocked_person_ticks` |
| T-24 | sign at B heading W | any decision at B | no edge is favoured; results equal the no-sign run |
| T-25 | a walker at C after A→B→C heading to School | it decides | CA carries the 6.0 s loop penalty |
| T-26 | tick 0 | inspect tokens | every edge has exactly 1.0 tokens |
| T-27 | CC-L01 as written, no sign effect (B/W) | run (golden numbers, model-derived; reconfirm at Stage 08) | arrived 20, on time 20, blocked_person_ticks 838, last arrival tick 396, score 99 |
| T-28 | a walker has no path to its destination | it decides | `STRANDED` is logged, the validator fails the level, play shows an explanation |

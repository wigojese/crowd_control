# SIMULATION EVENTS (Stage 03)

Every visible outcome must trace to one of these events. If a statement cannot be derived from the log, the game must not show it (spec A4).

## 1. Tick order (the single source of truth for ordering)

Per tick `t` from 0 to 639, `dt = 0.05 s`:

| Step | What happens | Events written |
|---:|---|---|
| 1 | Apply commands assigned to tick `t`, in ordinal order | `COMMAND_ACCEPTED` or `COMMAND_REJECTED` |
| 2 | Complete a pending drop, or snap back a hold that timed out | `SIGN_DROPPED`, `SIGN_SNAPPED_BACK` |
| 3 | Spawn walkers whose `spawn_tick == t` | `WALKER_SPAWNED` |
| 4 | Refill token buckets | none |
| 5 | Decisions: new arrivals, 10-tick re-evaluations, sign-change re-evaluations, in ascending walker id | `DECISION`, `QUEUE_JOINED`, `QUEUE_LEFT` |
| 6 | Service: edges in ascending id, FIFO, one token per entry | `EDGE_ENTERED` |
| 7 | Movement of walkers that were already on an edge | none |
| 8 | Arrival at a node | `NODE_ARRIVED`; `WALKER_ARRIVED` if it is the destination; `WALKER_STRANDED` if no path |
| 9 | Metrics: `blocked_person_ticks`, `total_person_ticks` | none (aggregated) |
| after 639 | End of round | `RUN_ENDED` |

Pause does not advance `t`. A sign change in step 1 or 2 is visible to the decisions in step 5 of the same tick.

## 2. Event catalogue

Every event carries `tick` and a monotonically increasing `seq` inside the tick.

| Event | Extra fields | Source of truth for |
|---|---|---|
| `COMMAND_ACCEPTED` | `command, slot, heading, ordinal` | the replay and the action count |
| `COMMAND_REJECTED` | `command, reason` (`bad_slot, locked, held, already_held, wrong_state, no_sign_placed, paused_no_commands`) | player-facing "why" for a refused action |
| `SIGN_PICKED` | `from_slot, heading` | start of the inactive window |
| `SIGN_DROPPED` | `slot, heading, lock_until` | new sign position and lock |
| `SIGN_SNAPPED_BACK` | `slot, heading` | a failed move |
| `SIGN_ROTATED` | `heading, lock_until` | a turn |
| `WALKER_SPAWNED` | `walker, profile, origin, destination, deadline_tick` | the spawn table |
| `DECISION` | `walker, node, chosen_edge, cost_by_edge{travel,crowd,loop,sign}, reason` | any route-change claim |
| `QUEUE_JOINED` / `QUEUE_LEFT` | `walker, edge, position` | queue claims |
| `EDGE_ENTERED` | `walker, edge, tokens_after` | edge flux for ribbons |
| `NODE_ARRIVED` | `walker, node` | node visit table (`node_visits.csv`) |
| `WALKER_ARRIVED` | `walker, tick, on_time` | arrival count, on-time count |
| `WALKER_STRANDED` | `walker, node` | the "no path" message |
| `RUN_ENDED` | `reason` (`all_done`, `time_limit`), aggregate counters | the result |

`DECISION.reason` is one of: `lowest_cost`, `forced_single_exit`, `sign_flipped` (the chosen edge would not be the lowest-cost without the sign bonus), `queue_flipped` (it would not be without the queue term). The two "flipped" reasons are computed by also evaluating the candidate costs with that term removed; a result sentence such as "7 rerouted here" is only allowed from `sign_flipped` counts.

## 3. Replay log

```
ReplayLog = {
  ruleset_version: "CC-RULESET-01C", level_hash, seed, engine_build,
  actions: [ {tick, ordinal, command, slot, heading} ... ]   # sorted by tick, then ordinal
}
```
Impossible commands (for example a drop with no pickup) are rejected on load. Two runs with the same `ReplayLog` and level must produce the same event-log hash; this hash is the equality check for T-10 and T-13.

## 4. What the result screen may say

| Claim | Allowed only if |
|---|---|
| "14/20 arrived" | counted from `WALKER_ARRIVED` |
| "5 waited at Canal Turn → Bridge West" | `QUEUE_JOINED` on edge `BD` with at least that many walkers blocked over time; edge named from the level file |
| "7 of 9 took the narrow walkway" | `DECISION` events at the sign's node in the window; counts from the log |
| "Your sign pointed south" | the last `SIGN_*` or placement event |
| "N rerouted because of your sign" | count of `DECISION.reason == sign_flipped` |
| "Turning earlier would have helped" | **never**, unless a counterfactual run with that command log was actually executed |
| any comparison with another heading | only from an actual replay of that heading on the same seed |

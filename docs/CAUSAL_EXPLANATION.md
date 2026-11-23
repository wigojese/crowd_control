# CAUSAL EXPLANATION (Stage 13)

Code: `src/simulation/explainer.gd` (GDScript, **not run**) and `scripts/ref_explain.py` (reference, **run**). The simulation now logs `alt_edge` on every DECISION flagged `sign_flipped` or `queue_flipped`: the street the walker would have taken without that term, found by actually re-evaluating the costs.

## 1. How a reason is chosen

1. **Counted events only.** "Your sign changed the route of N walkers" counts distinct walkers with a DECISION of reason `sign_flipped`. A walker re-evaluated several times counts once (A/E: 22 decisions, 8 walkers).
2. **Helped or hurt only from an executed baseline.** The comparison "against no sign on the same seed" needs a NO_SIGN run of the same level that was actually run. Without one the sentence does not exist. Material means: a different arrival count, a pass or fail flip, or at least 10% more or less time spent waiting.
3. **Where the waiting was** comes from QUEUE_JOINED and EDGE_ENTERED pairs (still-waiting walkers count to the end of the round).
4. **Never** a statement about another heading or timing that was not run ("turning earlier would have helped"). Tests ban counterfactual and stereotype phrases from all generated copy.
5. The result screen shows at most three lines: result, comparison or "no effect", bottleneck.

## 2. Result copy, generated from the real traces

| Scenario | Lines shown (verbatim) |
|---|---|
| Sign at North Gate, east | 1. 20 / 20 arrived. Goal 18: reached. 2. Compared with no sign on the same seed, your sign delivered 3 more (20 against 17) and turned a miss into a pass. 3. Your sign at North Gate (pointing east) changed the route of 8 walkers: all of them at North Gate took North Gate to Market instead of North Gate to Canal Turn. |
| No sign | 1. 17 / 20 arrived. Goal 18: 1 short. 2. No sign was placed in this round. 3. Most waiting: Canal Turn and Bridge West, 107.5 walker-seconds in queues (all walkers added up). |
| Sign at North Gate, north | 1. 17 / 20 arrived. Goal 18: 1 short. 2. The result matches no sign on the same seed (17 against 17 arrived). 3. Your sign at North Gate (pointing north) changed no walker's route. |
| Sign at Canal Turn, east | 1. 20 / 20 arrived. Goal 18: reached. 2. Compared with no sign ... 3 more (20 against 17) and turned a miss into a pass. 3. Your sign at Canal Turn (pointing east) changed the route of 2 walkers: ... |

All claims with their evidence are in `docs/stage13/claims_*.json`; event traces in `docs/stage13/trace_*.csv`.

## 3. Edge-case list

| Case | Behaviour | Tested |
|---|---|---|
| A sign that changes no route (A/N, B/N) | says "changed no walker's route" and "matches no sign"; no help or harm claimed | yes |
| A sign that re-routes walkers but the result is the same (A/S: 4 walkers, 17 against 17) | says both facts | yes (A/S in the run; the copy has no "hurt" because the difference is under 10%) |
| Few direct re-routes, big gain (B/E: 2 walkers, +3 arrivals) | states only the two facts; it does not claim why the other walkers gained | yes |
| No baseline available | no comparison sentence | yes |
| No sign at all | "No sign was placed"; no sign claim | yes |
| Walker flips several times | counted once | yes |
| Sign events removed from the log | the re-route claim becomes "changed no walker's route" | yes |
| Waiting at the end of the round | counted up to the last tick | in the reference |
| Ties in the largest group | broken by the street names, the same in both implementations | by construction, not separately tested |
| A baseline that also changed the sign mid-run | **not handled**: the baseline is always NO_SIGN | open |
| Running actions (rotate or move during the round) in the copy | **not covered**: the copy talks about the initial sign only | open (needs a replay-aware claim) |

## 4. Not done

- GDScript explainer tests have not run (`tests/test_explainer.gd`, 4 tests).
- The result screen does not display these lines yet; the explainer is not wired to the UI.
- The three scenario videos are reference renderings from model data at 2x speed, not engine captures.

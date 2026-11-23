# BEHAVIOR MATRIX (Stage 13)

Only the three approved profiles exist (CC-D-002). **A profile describes how a walker weighs a sign and a crowd, not who a person is.** The names are working labels for rule sets, and no copy speaks about people by age, gender, origin or class.

## 1. The three profiles (values from `docs/RULES.md`, ruleset CC-RULESET-01C)

| Profile | Sign sensitivity | Crowd aversion | Speed | Sign bonus in time units (R1: 6.0) | What it means |
|---|---:|---:|---:|---:|---|
| Commuter | 0.8 | 0.35 | 38 | 4.8 s | follows a sign when the unsigned routes differ by less than 4.8 s; tolerates queues |
| Follower | 1.0 | 0.9 | 34 | 6.0 s | the strongest sign response, but the strongest dislike of queues |
| Independent | 0.35 | 0.2 | 42 | 2.1 s | mostly ignores signs and crowds; fastest |

## 2. Sign response variants

A sign at a junction favours the outgoing streets whose direction is within about 49 degrees of its heading (dot product at least 0.65). A favoured street gets a cost reduction of sensitivity times bonus. The rule is the same for every profile; only the numbers differ. Density is shown as counted ribbons (Stage 10 and 11), with no extra rule.

## 3. What each profile did in the real runs (Python port of the engine rules, level CC-L01-R1)

| Scenario | Commuter (11 walkers) | Follower (6) | Independent (3) |
|---|---|---|---|
| Sign at North Gate, east (20 of 20) | 7 of 11 re-routed, 11 arrived, mean 17.2 s | 1 of 6 re-routed, 6 arrived, mean 19.5 s | 0 of 3 re-routed, 3 arrived, mean 15.5 s |
| Sign at Canal Turn, east (20 of 20) | 2 of 11 re-routed, 11 arrived, mean 18.3 s | 0 of 6 re-routed, 6 arrived, mean 22.1 s | 0 of 3 re-routed, 3 arrived, mean 25.0 s |
| No sign (17 of 20) | 0 of 11 re-routed, 10 arrived, mean 18.3 s | 0 of 6 re-routed, 6 arrived, mean 22.1 s | 0 of 3 re-routed, 1 arrived, mean 15.2 s |
| Sign at North Gate, north (17 of 20) | 0 of 11 re-routed, 10 arrived, mean 18.3 s | 0 of 6 re-routed, 6 arrived, mean 22.1 s | 0 of 3 re-routed, 1 arrived, mean 15.2 s |
| Sign at North Gate, south (17 of 20) | 4 of 11 re-routed, 10 arrived, mean 21.4 s | 0 of 6 re-routed, 6 arrived, mean 21.6 s | 0 of 3 re-routed, 1 arrived, mean 13.8 s |

Reading it: in the best placement, **7 of 11 commuters were re-routed and 1 of 6 followers; no independent was.** That is the profile story the rules intend for independents (the sign barely moves them). That followers, with the strongest sign sensitivity, were re-routed least is a **fact from the run, and I have not established why** (my hypothesis, **UNVERIFIED**: their strong queue aversion offsets the sign at the moment they decide). Whether that reads as a sensible behaviour or a rule that needs a change is the strategic-depth question below.

Reproduce: `python3 -I scripts/stage13_evidence.py`.

## 4. Follower investigation (bug or feature?)

Verdict: **feature as written, not an engine bug. The rule does what RULES.md says; the profile name promises more than the rule delivers.**

Evidence (level CC-L01-R1, sign at North Gate pointing east; probe script not committed, rerun by tracing `ref_sim.World.cost` for walkers at node A):
- "Re-routed" counts only DECISION events with reason `sign_flipped`. A walker whose best route already runs along the sign is never counted.
- 3 of 6 followers (destination Plaza) already prefer `A>C` with no sign (13.9 s against 17.4 s). They follow the sign direction but are not re-routed.
- The other 3 followers (destination School) prefer `A>B` by 4.3 s without a sign (13.5 s against 17.8 s). The sign bonus is 6.0 s, so the sign wins on paper. Their crowd aversion (0.9) charges about 2.1 s for the queue that builds on `A>C`, which cancels most of the bonus. The first two take `A>B`; the third takes `A>C` once a queue forms on `A>B` (13.9 s against 14.0 s). Result: 1 of 6 flipped.
- Taking the sign-favoured edge at North Gate: followers 4 of 6 (3 of 6 with no sign), commuters 11 of 11 (4 of 11 with no sign), independents 1 of 3 (1 of 3).
- The Stage 13 hypothesis is **verified**: queue aversion offsets the sign at the moment of decision. Counterfactual with follower crowd aversion 0.35 (the commuter value): 3 of 6 flip, 6 of 6 take `A>C`.

Options for the user: (A) keep the rule and rename the profile or its text (for example "Queue-averse"), (B) lower follower crowd aversion to about 0.35 to 0.5 so followers follow signs, which changes the no-sign baseline (arrivals 17 to 14 to 15) and every Stage 13 fixture, or (C) keep both and add a result-screen line that says why followers ignored the sign. No change made. Rules stay as approved until the user chooses.

# CROWD CONTROL: Project brief (Stage 00)

Date: 2026-11-22 (container date). Source of truth for scope: *Crowd Control Precision Master Prompt v2.0* (23 Nov 2026), referred to here as "the spec". Labels used throughout: **VERIFIED**, **IMPLEMENTED/TESTED**, **PROPOSED**, **UNKNOWN**.

## 1. What the game is (from the spec, section 0)

A phone-first, real-time spatial strategy game. The player redirects a miniature city's pedestrian flow with **one movable directional sign**. Citizens have visible destinations and three simple behaviour profiles (Commuter, Follower, Independent). A 25–45 second simulation produces readable cascades. The player learns to predict collective movement, not control it directly.

North-star verb: **redirect**. Loop: read, intervene, predict, watch the cascade, understand, retry.

## 2. Exact user requests so far

| # | Request | Where it came from | Status |
|---|---|---|---|
| U-1 | Run the project under the spec's one-stage-then-stop approval gate | Master prompt, sections 2 and J | VERIFIED (document supplied by the user) |
| U-2 | Give a visual feel and opinion before everything else, as pictures | First chat message | Done; images are in `docs/art-exploration/round1-A-B-C/` |
| U-3 | Redo the prototypes per the "Visual Identity Critical Review" | Second upload | Done; `round2-D-civic-press/` |
| U-4 | Redo them again per the "Civic Press Critique" | Third upload | Done; `round3-D2-civic-press-revised/` |
| U-5 | "Commit and move to the next stage" | Latest message | This commit. The next stage is Stage 00, the first unapproved stage (no stage has been approved yet) |
| U-6 | No blue in the standard palette | Stated inside the user-supplied critique documents ("your objection to blue"), not in a chat message | **UNVERIFIED as a direct instruction.** Please confirm |

## 3. Platform and form factor

- Target: portrait smartphone, 19.5:9 to 16:9, tablets adapted. First platform Android. iOS export feasibility is decided at Stage 06 (needs a Mac with Xcode).
- Orientation: portrait. Round length 25–45 s of simulated time; L01 is 32 s (640 ticks at 20 ticks/s).
- Offline play, no accounts, no ads, no monetisation in the slice. English first, localisation-ready (Georgian later).

## 4. Baseline rules to be tested (not yet approved)

`CC-RULESET-01`, level `CC-L01 School Crossing`: 7 nodes, 9 bidirectional links, 20 citizens (12 to School, 8 to Plaza), one sign at socket B or C, pass at 16 of 20 arrived by 32 s, seed 1007. Full numbers are in the spec, section A. They are design baselines, not validated facts. Approval of the exact ruleset is Stage 03.

## 5. Out of scope for the initial slice

City editor, accounts, multiplayer, live service, boosters, UGC servers, crowd-crush simulation, photoreal assets, traffic lights, cars, real geodata, ads, loot boxes, streak pressure, 3D camera freedom. Adding any needs a user-approved scope change.

## 6. What exists today (audit, Stage 00)

| Item | Finding | Label |
|---|---|---|
| Git repository | Present, remote `origin` = `github.com/wigojese/crowd_control`, branch `claude/dreamy-mayer-963iwr` | VERIFIED |
| Commits before this stage | None | VERIFIED |
| Engine project / scripts / scenes | None | VERIFIED |
| Tests, CI, screenshots of a running game | None (nothing runs yet) | VERIFIED |
| Licence file | None | VERIFIED |
| Assets with licence provenance | None. Fonts used in mockups (Bitstream Charter, Inter, JetBrains Mono) were whatever was installed in the container; their distribution terms for a shipped game have **not** been checked | UNKNOWN |
| Code issues to audit | Nothing to audit. There is no game code | VERIFIED |
| Art explorations | Static pictures only: rounds 1–3 under `docs/art-exploration/`. Not game assets, not an in-engine result | VERIFIED |

## 7. Environment facts (this container)

| Fact | Finding | Label |
|---|---|---|
| Godot, Unity, `adb` | Not installed | VERIFIED |
| Java, Python 3, Node 22, Git | Installed | VERIFIED |
| Chromium and Playwright | Pre-installed, used for the mockup renders | VERIFIED |
| Real Android or iOS test device | None attached. No user computer is attached either | VERIFIED |
| Outbound web (as of Stage 00) | Only an allowlist. A test of 9 sites cited by the user's documents (W3C WCAG, Android and Apple docs, museum pages) reached **none** of them usefully: 7 failed DNS, 2 Apple pages returned only titles | VERIFIED |
| Godot 4.7 and Unity 6.3 LTS being the current stable lines | Cannot be checked from here | UNKNOWN (`VERIFY_ON_TARGET_ENGINE`) |

## 8. Desired platforms and test hardware

Wanted: a recorded mid-range Android phone for the spec's 60 FPS target and a 10-minute thermal run; later an iOS device and a Mac. Available now: **none**. This is an explicit blocker for any claim of on-device performance (spec stages 06, 08–12, 16).

## 9. Assumptions list

| ID | Assumption | Status |
|---|---|---|
| AS-01 | Portrait phone, one-sign baseline, L01 first | PROPOSED. Awaiting your confirmation (the Stage 00 question) |
| AS-02 | `CC-RULESET-01` numbers are the starting point for Stage 03 | PROPOSED |
| AS-03 | Godot 4.7 (GDScript) is only a candidate; engine chosen at Stage 06 on measured evidence | PROPOSED |
| AS-04 | The Civic Press revised direction ("D2") is a provisional input to the Stage 05 art competition, not an approved direction | PROPOSED. See CC-D-004 |
| AS-05 | Node names are fixed: A North Gate, B Canal Turn, C Market, D Bridge West, E Bridge East, F School, G Plaza | PROPOSED. See CC-D-005 |
| AS-06 | Objective wording uses "Deliver 16 of 20 before 0:32" (not "home") | PROPOSED |
| AS-07 | The `.md` stage docs live in `docs/`; the engine project does not exist until Stage 07 | PROPOSED |
| AS-08 | No blue in the standard palette (U-6) | UNVERIFIED |
| AS-09 | A solo user reviews each stage; no external testers yet | UNKNOWN |

## 10. Spec ambiguities found while reading it

1. Section C2 says the camera path ends with "pullback to C plaza overview", but C is Market and G is Plaza.
2. L01 has a 32 s time limit but each citizen's default deadline is 30 s (section A4). Both can hold at once, but the result copy must say which one applies.
3. Stage 05 sets up the art competition and approval gate, yet three rounds of art exploration have already happened at your request, ahead of Stage 05. Those are recorded as inputs, not as approvals.
4. The spec's source register (section I) cannot be date-verified from this container (see section 7).

_Update 2026-11-22 (Stage 01): the user approved web access and 15 hosts were added; see CC-D-008 and docs/RISKS.md R-03._

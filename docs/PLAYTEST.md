# PLAYTEST (Stage 17): protocol only. NO PLAYERS HAVE BEEN TESTED.

**Honest status.** There is no playable build (Godot has never run here, no APK) and no testers. Nothing below is an observation. The outcome grid is empty on purpose; I will not fill it with invented sessions. Stage 17's acceptance (changes address documented friction, no overstated significance) can only be met once real sessions exist: **BLOCKED**.

**What a session needs:** a phone with a build of CC-L01 to L03 (Stage 16 blocker R-51), a screen recording or a moderator's notes, 5 to 10 people aged 13+ who have not seen the game, 15 minutes each.

## 1. Moderator script (read aloud; do not explain the sign)

1. "Thanks. We are testing the game, not you. You can stop any time. I'll note what you do, not who you are."
2. Hand over the phone at the title. Say nothing else for 5 seconds. **Record:** first thing touched, time to first touch (s).
3. Let them play L01 unaided. Allowed prompt only after 30 s of no action: "What do you think you can do here?"
4. After the first result: "In one sentence, what does the sign do?" (mental model, verbatim). "Why did you win or lose?" (compare with the game's own explanation).
5. Let them retry freely up to 5 minutes, then offer L02 and L03. **Record:** attempts per level, wrong taps, rotations, sign moves, whether they chose to retry.
6. Motion comfort: "Did any movement bother you?" Offer reduced motion; record whether they found the setting.
7. Close: "What was confusing? What would you change?" Thank them.

## 2. What is recorded per session (anonymous ID P01, P02...; no name, no face, no voice kept)

| Field | How |
|---|---|
| First action and its latency | stopwatch or recording |
| Wrong taps (taps that did nothing or rotated by accident) | count |
| Attempts and pass/fail per level | count |
| Mental model sentence | verbatim |
| Could they say why they lost (matches game's cause: y/n) | moderator judgement |
| Replay urge | did they restart unprompted (y/n) |
| Motion comfort | answer + setting used |
| Severity-worthy friction | free note |

## 3. Consent language (read before starting; for 13 to 17 year olds also needs a parent or guardian to agree)

"We are testing a game. If you agree, we will watch you play for about 15 minutes and write notes. We will not record your name, face or voice. Your notes are labelled P01, P02, and nothing identifies you. Playing is optional, you can stop at any time without giving a reason, and you can ask us to delete your notes. The game collects no data about you." Agree: yes / no, initials of the moderator who read it.

No in-game metrics are sent anywhere (none authorised). If you later want opt-in aggregate metrics, say so; it is not built.

## 4. Outcome grid (EMPTY)

| ID | First action (s) | Wrong taps | L01 attempts / pass | L02 | L03 | Mental model | Knew why lost | Retried unprompted | Motion | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| P01 | | | | | | | | | | |
| ... | | | | | | | | | | |

Severity scale: S1 blocks play or causes confusion in 3 or more players; S2 slows 2 players; S3 one-off. With 5 to 10 players report counts, never percentages or "significant".

## 5. One A/B question (single variable)

**Question:** Does a visible "ink tick" at the junction when the sign flips a walker's choice (cue `reroute_tick`, still only designed) help players say why the crowd turned? **A:** no tick. **B:** tick. Same level (L01), same seed, alternate players A/B/A/B. **Measure:** the mental-model sentence mentions the sign changing the route (y/n). With 5 to 10 players this can show a hint, not proof; report it that way.

## 6. Three candidate revisions (PROPOSED from known risks, NOT from playtests)

| # | Revision | Source of the doubt | Playtest to confirm |
|---|---|---|---|
| 1 | Build the three muted-play visual cues still only designed (pickup lift, turn ring, refused shake) | R-49 | Do muted players notice a refused move? |
| 2 | At 320 wide, start the camera at district zoom with scroll instead of atlas zoom | R-50 | Do small-phone players see walkers at the start? |
| 3 | A second wave whose best heading differs from wave 1 so running play matters | R-30, R-31 | Do players rotate mid-run on purpose? |

Each stays a proposal until real friction supports it.

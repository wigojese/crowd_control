# AUDIO (Stage 15)

**I cannot hear.** Every sound below is original, synthesised from scratch by `scripts/synth_audio.py` (sine, triangle, filtered noise, a small feedback delay; no samples, no recordings, no third-party material or music). Level, length, clipping, DC offset and spectrum are **measured** (`scripts/check_audio_files.py`). Whether the sounds are pleasant, readable and restrained is **UNVERIFIED** until a person listens. The sounds are deterministic: the same bytes come out on every run.

## 1. Tone (PROPOSED, for your approval)

Quiet, mechanical and warm: a dry click for pickup, a three-step ratchet for the 90° turn, a soft wooden thud for the drop. Crowd arrival is a soft pluck whose pitch walks up a pentatonic scale, so a good run becomes a rising phrase. Success is a rising four-note arpeggio with a short tail; failure is two falling notes, soft, **not a buzzer**. The foot texture is a low, quiet bed of soft steps whose loudness follows how many people are walking, never one sound per footstep.

## 2. Cue sheet and event-to-sound mapping (`data/audio_map.json`)

| Cue | File | Length | Peak | Category | Critical | Triggered by | Visual equivalent (status) | Haptic |
|---|---|---:|---:|---|---|---|---|---|
| sign_pickup | `assets/audio/sign_pickup.wav` | 80 ms | -4.4 dBFS | effects | yes | SIGN_PICKED | sign_lift (designed) | light_tick |
| sign_turn | `assets/audio/sign_turn.wav` | 200 ms | -4.4 dBFS | effects | yes | SIGN_ROTATED | arrow_turn_and_lock_ring (designed) | none |
| sign_drop | `assets/audio/sign_drop.wav` | 170 ms | -4.4 dBFS | effects | yes | SIGN_DROPPED | transition:sign_drops (implemented_in_data) | light_thud |
| command_rejected | `assets/audio/command_rejected.wav` | 120 ms | -4.4 dBFS | effects | yes | COMMAND_REJECTED | sign_shake_and_lock_text (designed) | double_tick |
| foot_bed | `assets/audio/foot_bed.wav` | 2000 ms | -9.1 dBFS | texture | no | EDGE_ENTERED minus NODE_ARRIVED (continuous gain) | moving_notes (implemented_in_code) | none |
| queue_compress | `assets/audio/queue_compress.wav` | 700 ms | -4.4 dBFS | effects | no | QUEUE_JOINED at position 3 or more (once per 4 s per street) | queue_hatch_and_badge (implemented_in_code) | none |
| reroute_tick | `assets/audio/reroute_tick.wav` | 200 ms | -4.4 dBFS | effects | no | DECISION with reason sign_flipped (once per 250 ms) | ink_tick_at_node (designed) | none |
| arrival_pluck | `assets/audio/arrival_pluck.wav` | 250 ms | -4.4 dBFS | effects | no | WALKER_ARRIVED (once per 120 ms, pentatonic pitch by arrival count) | arrival_counter (designed) | none |
| result_success | `assets/audio/result_success.wav` | 1200 ms | -4.4 dBFS | effects | yes | RUN_ENDED and passed | result_card_and_transition:outcome_pullback (implemented_in_data) | soft_pulse |
| result_failure | `assets/audio/result_failure.wav` | 1200 ms | -4.4 dBFS | effects | yes | RUN_ENDED and not passed | result_card_and_transition:outcome_pullback (implemented_in_data) | none |
| ui_tap | `assets/audio/ui_tap.wav` | 50 ms | -4.4 dBFS | ui | no | button press (UI only) | button_press_state (designed) | none |

All files: 22.05 kHz, 16 bit, mono, peak at most −3 dBFS (measured −4.4 dBFS, foot bed −9.1 dBFS), no clipped sample, none longer than 1.2 s. **Licence:** the project's own original work; no third-party licence applies. The release licence for these files is the owner's choice.

## 3. Rules that keep 50 pedestrians from becoming noise

Sounds come only from the events above, never from a timer. At most 10 triggers in any second, at most 6 overlapping effect voices, per-cue cooldowns, critical cues never dropped. The foot texture is one looping bed driven by a gain, not a trigger per walker. Tested on a 50-walker stress stream: **78 sound triggers for 251 events, at most 10 in a second, at most 4 overlapping voices**, the result sound still once.

## 4. Real runs rendered to audio (open and listen)

`docs/stage15/mix_AE_run.wav` (level L01, sign east at North Gate: 23 sound plays in 32 s) and `mix_L02_move.wav` (L02 with the sign moved at 8 s: 37 plays). Mix peaks measured at -2.3 and -1.7 dBFS with no clipping. **The peak is above the −3 dBFS target I set for single cues**: overlapping cues add up; a limiter or lower defaults may be needed (decide after listening).

## 5. Haptics

Optional and off by default. Mapping only (no device to feel it on): light tick on pickup, light thud on drop, double tick on a refused action, soft pulse on success, none on failure. Nothing in the game needs haptics.

## 6. Not done

- Nothing plays these files yet: there is no engine audio code, only the pure scheduler (`src/audio/audio_scheduler.gd`, **not run**).
- No mix-down check on phone speakers or earphones; no loudness check against any standard (only peak and RMS).
- The pentatonic pitch shift is done by resampling in the evidence script; the engine would use its own pitch control (UNVERIFIED).

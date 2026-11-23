# INPUT STATES (Stage 09)

Code: `src/input/gesture_router.gd` (GDScript, not run) and `scripts/ref_input.py` (Python reference, run). Thresholds: `data/input_tokens.json` only. Each touch has its own state; the owner is fixed at touch-down (docs/INPUT_SPEC.md section 5).

Per-touch states: IDLE, UI_PRESS, SIGN_PENDING, SIGN_DRAG, SIGN_INSPECT, LOCK_REJECT, MAP_PENDING, PAN, PINCH, IGNORED. (The spec's DOCK_DRAG and SIGN_TAP are folded in: a tray drag is SIGN_PENDING with source `tray` then SIGN_DRAG; a tap is decided on release, so it needs no state.)

## Transitions observed when running the 21 cases (Python reference)

| From | To | Seen in cases |
|---|---|---|
| IDLE | IGNORED | G-09 |
| IDLE | LOCK_REJECT | G-11 |
| IDLE | MAP_PENDING | G-05, G-06, G-13, X-04 |
| IDLE | PINCH | G-06, G-07 |
| IDLE | SIGN_PENDING | G-01, G-02, G-03, G-04, G-07, G-08, G-08b, G-10, G-12, G-14, G-15, X-01, X-02, X-05 |
| IDLE | UI_PRESS | G-11, G-13, X-03 |
| IGNORED | IDLE | G-06, G-07, G-09, G-15 |
| LOCK_REJECT | IDLE | G-04, G-11 |
| MAP_PENDING | PAN | G-05, G-13, X-04 |
| MAP_PENDING | PINCH | G-06 |
| PAN | IDLE | G-05, X-04 |
| PINCH | IDLE | G-06, G-07 |
| PINCH | IGNORED | G-06, G-07 |
| SIGN_DRAG | IDLE | G-08, G-08b, G-10 |
| SIGN_DRAG | IGNORED | G-15 |
| SIGN_INSPECT | IDLE | G-12 |
| SIGN_PENDING | IDLE | G-01, G-02, G-14, X-01, X-02, X-05 |
| SIGN_PENDING | LOCK_REJECT | G-04 |
| SIGN_PENDING | PINCH | G-07 |
| SIGN_PENDING | SIGN_DRAG | G-03, G-08, G-08b, G-10, G-15 |
| SIGN_PENDING | SIGN_INSPECT | G-12 |
| UI_PRESS | IDLE | G-11, G-13, X-03 |

## Rules in words

| Event | Where the touch started | Result |
|---|---|---|
| down | a button | UI_PRESS; the button fires only if the finger lifts inside it |
| down | within 24 px of a screen edge, not on a button | IGNORED (OS gesture may run) |
| down | sign, mode PAUSED | LOCK_REJECT state, "paused" message, nothing else |
| down | sign, ring, or tray | SIGN_PENDING |
| down, second finger | map or sign, while another finger is down on the map | both fingers PINCH; a pending sign action is cancelled |
| down | anywhere else on the map | MAP_PENDING |
| move over 8 px | SIGN_PENDING, source sign, unlocked or tray | SIGN_DRAG: SIGN_PICKUP |
| move over 8 px | SIGN_PENDING, source sign, locked | LOCK_REJECT: swallows the rest of the touch |
| move over 8 px | SIGN_PENDING, source ring | PAN (a ring is part of the map) |
| move over 12 px | MAP_PENDING | PAN |
| held 420 ms, still | SIGN_PENDING on the sign | SIGN_INSPECT; release does nothing |
| held 3000 ms in SIGN_DRAG | | SNAPBACK (timeout) |
| up within 220 ms and under 8 px | SIGN_PENDING on the sign | SIGN_TURN (or LOCK_REJECT if locked) |
| up within 220 ms and under 8 px | SIGN_PENDING on another ring | SIGN_MOVE_TAP (or LOCK_REJECT if locked) |
| up | SIGN_DRAG | SIGN_DROP on a ring within 44 px, else SNAPBACK (off_ring) |
| cancel | SIGN_DRAG | SNAPBACK (cancelled); no lock, one sign |
| cancel | anything else | CANCELLED |

## Latency instrumentation

`first_ack` in the router records, per touch, the milliseconds from touch-down to the first intent. In the Python run it is 0 ms for touches that get a PRESS_FEEDBACK on touch-down and at most 30 ms where the first intent is a PAN (the case's own timestamps), which only proves the logic answers on the same event it receives. **It is not the player-visible latency.** The measured number needs a real phone with the frame time added (BLOCKED, see docs/TEST_LOG.md T09-07).

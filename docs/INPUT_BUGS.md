# INPUT BUGS AND OPEN INPUT ISSUES (Stage 09)

Found by running the Python reference (`scripts/ref_input.py`) on `tests/fixtures/input_cases.json`. **No bug has been found on a device, because no device was used.**

| ID | Found by | Description | Status |
|---|---|---|---|
| IB-01 | First run of the 21 cases | Case G-07 failed: the second finger landed on the Resume button rectangle, so it was a button press, not a pinch. The router was right; my test coordinate was wrong | Fixed in the test data |
| IB-02 | Writing the router | `docs/INPUT_SPEC.md` G-15 says "the finger lifts off a ring and the 3 s timeout expires". The router implements the stricter safe reading: a lift off a ring snaps back at once (as G-08), and the 3 s timeout applies to a sign still held by a finger that has not lifted | **Decision needed**: keep, or allow a held-but-lifted sign to wait 3 s |
| IB-03 | Writing the router | A drag that starts on a ring (not the sign) is treated as a pan. The spec does not say | Proposed, unconfirmed |
| IB-04 | Review | The router reads the 24 px edge reserve only for non-button touches; a button inside the reserve works. Intended, but the dock buttons must not be placed in the reserve at 320 wide | Open (layout) |
| IB-05 | Review | Not built: optional tap-cycle mode, the accessibility hit-area extra (`accessible_hit_extra_px` exists in tokens but nothing reads it), haptics, the magnet and snap-back animation, the sign pickup preview. These are drawing and device work (Stage 10) or need your choice | Open |
| IB-06 | Review | An in-progress pinch ends the other finger as IGNORED. Whether it should become a pan with the remaining finger is not decided | Open, feel test needed |
| IB-07 | Not testable | Edge-gesture widths, thumb reach to North Gate, 8/12/220/420 ms thresholds, real first-acknowledgement latency, 390×844 and 320×568 recordings | **BLOCKED**: needs a phone |

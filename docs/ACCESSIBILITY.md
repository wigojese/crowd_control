# ACCESSIBILITY (Stage 15)

## 1. Settings (data/settings_schema.json, CcSettings)

| Setting | Default | Notes |
|---|---|---|
| Master, effects, texture (foot bed), UI volume | 0.8, 0.8, 0.5, 0.8 | four independent sliders, tested independent (effects 0 silences effects and keeps the bed; texture 0 does the reverse) |
| Haptics | off | optional |
| Reduced motion | follow the system | on, off, or system |
| Static camera | off | removes automatic camera moves; the Stage 11 option C |
| Left-handed layout | off | the whole dock row is an exact mirror |
| Pattern equivalents | on | route and queue patterns always drawn |
| Larger targets | off | +8 px height and, where room allows, width |

Sanitising never fails: unknown keys are dropped, numbers clamped, wrong types fall back to the default.

## 2. Controls checklist

| Item | Status |
|---|---|
| Sound is never required: every critical cue has a visual equivalent in the registry | PAPER ONLY: 3 of 6 critical cues have visuals that are only designed, not built (`data/visual_cues.json`, `docs/stage15/muted_timeline.png`) |
| Haptics never required | by design; no haptic code exists |
| Independent audio sliders | logic tested in the Python reference; engine UI not built |
| Reduced motion | all six transitions end at once with a 150 ms crossfade (tested, Stage 12); recording: `reduced_motion_*.mp4` and sheets, from reference data |
| Static camera | a setting and the camera director's reduced-motion path exist; the setting is not wired to the director |
| Left-handed dock | tested: mirror, no overlap, outside the 24 px edge reserve, at 390×844, 320×568 and 412×915, with and without larger targets |
| Hit areas: buttons at least 48 high and 44 wide, tray at least 56 | tested on the layout (55 checks) |
| Patterns as well as colour | School solid, Plaza dashed, queues hatched, sign a disc with an arrow (Stage 10) |
| Text size, dynamic type, screen-reader labels, focus order | **NOT DONE**: labels are written in docs/INPUT_SPEC.md section 8; no VoiceOver or TalkBack test |
| Captions for sound | not needed while visuals stand in; no speech exists |
| Pause on interruption (call, notification) | Stage 16 |

## 3. Colour-vision simulation

Method: Machado, Oliveira and Fernandes (2009) matrices at severity 1.0 in linear RGB, then CIE76 colour difference (ΔE). Picture: `docs/stage15/colour_vision_sheet.png` (the Stage 10 running state in four views). Numbers: `docs/stage15/colour_vision_numbers.json`.

| Pair | Normal | Protanopia | Deuteranopia | Tritanopia | Cue that does not rely on colour |
|---|---:|---:|---:|---:|---|
| amber vs sage (School and Plaza routes) | 42 | 27 | 29 | 42 | solid vs dashed line |
| vermilion vs amber (sign and School route) | 48 | 37 | 20 | 45 | disc with arrow vs line and notes |
| coral vs plum (queue colours) | 33 | 33 | 33 | 18 | hatch pattern |
| sage vs stave (Plaza route and street line) | 33 | 32 | 28 | 22 | dashed vs solid, ribbon width |
| vermilion vs plum (sign and queue hatch) | 46 | 42 | 44 | 33 | disc vs diagonal hatch |

**Result:** under all three simulated deficiencies every pair stays above ΔE 18, so no pair collapses in hue. The weakest are the coral and plum queue colours under tritanopia (18) and vermilion against amber under deuteranopia (20). Every pair also has a cue that does not rely on colour (last column). **Separately**, with colour removed entirely (monochrome), amber and sage have almost the same brightness (1.03:1, Stage 10); the solid and dashed lines are what separate them. This is a simulation, not a test with people who have colour-vision deficiency.

## 4. Accessibility test report

| Test | Result |
|---|---|
| 55 settings and dock-layout checks | RAN, PASS (Python reference); GDScript port BLOCKED |
| Contrast, both themes (Stage 10) | RAN, PASS |
| Colour-vision simulation | RAN; see section 3 |
| Muted player receives every critical cue visually | NOT MET in the game: 3 of 6 critical visuals are not built |
| No mandatory audio or haptics | MET by design (nothing depends on them) |
| Not overwhelming with 50 pedestrians | RAN in the scheduler: 78 triggers for 251 events, 10 per second at most |
| Real screen-reader, switch control, or one-handed use on a phone | **BLOCKED**: no device |
| Testing with disabled players | **NOT DONE**; no person has tested anything |

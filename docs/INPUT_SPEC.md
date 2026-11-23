# INPUT SPEC (Stage 04: touch interaction and first-time-player UX)

Ruleset: CC-RULESET-01C (loop C) on level R1 (sockets at North Gate and Canal Turn, goal 18 of 20). Status: **PROPOSED**, awaiting "Approve Stage 04". Pictures: `docs/stage04-input/` (`d4-states.png`, `d4-hit390.png`, `d4-hit320.png`, `d4-arbitration.png`). Everything here is design; **nothing has been tested on a real phone** (no device, see R-01). Thresholds are starting values.

## 1. Units, transforms and safe areas

**Logical units.** All sizes and thresholds below are in **logical px** (iOS points, Android dp). The engine converts touch positions from physical pixels by dividing by the display density. A threshold is never compared with raw hardware pixels (spec C5).

**World ↔ screen** (rotation = 0, spec C1):
```
screen = (world − center) × zoom + viewport_center + safe_offset
world  = (screen − viewport_center − safe_offset) / zoom + center
```
A touch is always mapped with the **current** camera transform, never the target one. Anchor test: pinching about a focal point must leave that world point within 2 logical px of where it was.

**Layout reserves (proposed).** Read the real insets from the OS at start-up and on rotation; never hard-code.

| Zone | Rule |
|---|---|
| Top inset | Read-only. No control sits in it |
| Bottom inset | Read-only. No control sits in it. The dock ends above it |
| Left and right edge reserve | **24 logical px each side** in the map: a touch that **starts** here is ignored by the game so the OS back gesture wins. A drag that started elsewhere may cross it. Width is a guess: **measure on device** |
| HUD band | Read-only. A touch that starts here is not a map gesture |

**What the platform documents say** (read 2026-11-23):
- Apple, Layout: "Respecting the safe area is essential to make sure system UI and hardware features like the Dynamic Island don't obstruct content and controls." Gestures: in games "developers can work around this area by deferring the system gesture". (developer.apple.com pages, via Apple's documentation data endpoint.)
- Android, Gesture navigation: back is "an inward swipe from either the left or the right edge"; home and quick switch are swipes at the bottom; apps can opt out of back selectively with `setSystemGestureExclusionRects()` (Android 10); a game that needs swipes near the home gesture area can ask for immersive mode. No edge width in dp is given on that page.
- The insets drawn in the pictures (47 top and 34 bottom at 390×844; 24 and 16 at 320×568) are **typical values from general knowledge, not from those pages**. UNVERIFIED.

## 2. Target sizes

Sources: Apple's accessibility page (iOS and iPadOS: **default control size 44×44 pt, minimum 28×28 pt**), Apple's games page ("buttons in iOS must be at least 44x44 pt"), Android touch-target help ("at least 48dp"), WCAG 2.2 (2.5.8, level AA: 24×24 CSS px; 2.5.5, level AAA: 44×44). **Our rule: every required control is at least 44×44, primary controls at least 48 high. This is a game design choice stricter than WCAG AA, not a WCAG requirement.**

| Control | Visual size | Hit area (logical px) | Meets 44 | Notes |
|---|---|---|---|---|
| Play (HOME) | 350×56 | 350×56 | yes | |
| Skip (INTRO) | 104×48 | 104×48 | yes | |
| Sign on map | ring 44 | **56×56** | yes | Same in every state |
| Socket ring on map | ring 44 | **56×56** | yes | |
| Sign tray | 44 | **56×56** | yes | |
| Start, Pause | 104×48 (92×48 at 320 wide) | same | yes | |
| Resume (paused panel) | 260×52 | same | yes | |
| Restart, Home | 124×48 | same | yes | |
| Try again | 196×56 | same | yes | |
| Inspect decision | 138×56 (116×48 at 320 wide) | same | yes | |
| Return to sign | 190×46 | same | yes | |
| Explore rail handle | 28×48 | **44×64** | yes | |

**Spacing.** Apple's layout page suggests placing buttons "so their centers are at least 60 points apart" (read without its surrounding context). The two sockets are about 138 px apart at 390 wide and about 101 px at 320 wide, both over 60. Gaps between adjacent buttons are at least 8 px.

## 3. The eight screen states

Latency targets are from spec E4 (median ≤ 50 ms and 95th percentile ≤ 100 ms for first visible acknowledgement); they are **targets, not measurements**. See `d4-states.png`.

| State | Map | HUD copy | Primary gesture | Owner of a touch | Feedback | Error and recovery | Alternative |
|---|---|---|---|---|---|---|---|
| **HOME** | Quiet title map | "Crowd Control. One sign. A hundred decisions." | Tap **Play** | UI | Press state on touch-down | A second tap while loading is ignored | Large single button; works with a screen reader |
| **INTRO** | 550 ms fly-in, then the level | "Deliver 18 of 20 before 0:32." | Optional **Skip** | UI | The fly-in cuts at once | None needed | Reduced motion: no fly-in, a 150 ms cross-fade |
| **PLACEMENT** | Frozen; both rings visible; real next turns drawn as small chevrons | "Place the sign" / "Drag it to a ringed junction"; **Start** dim | Drag the sign to a ring, **or** tap a ring; tap the sign to turn it | Sign, ring, map, UI per section 5 | Lift on first frame; ring brightens; snap 120–190 ms | A drop off a ring snaps back with "Drop it on a ring". No penalty | Tap-to-place, tap-to-turn, left/right dock layout |
| **RUNNING** | Live. Sign shows a lock ring after each action | "Sign locked 3.1 s" / "Then tap or drag it"; **Pause** | Tap the sign to turn it; drag it (or tap the other ring) to move it | As above; a locked sign swallows a drag | Turn indexed 140–180 ms; lock ring starts the same frame | Refused action: sign shakes 100 ms, says why ("Locked 2.4 s") | Tap-to-move; static camera; haptics optional |
| **PAUSED** | Dimmed; camera may still pan | "Paused" / "Clock and lock are stopped. The sign can't be changed while paused." | **Resume** | UI; the sign ignores touches | Veil in 120 ms | Touches on the sign do nothing and show the same sentence | Large buttons; clear sentence for screen readers |
| **RESULT** | Pulled-back map | "17 / 20 arrived. Goal 18: 1 short." plus the most-delayed edge | **Try again** | UI | Result visible at once; pullback skippable | Nothing to lose | Text states every claim; no colour-only meaning |
| **RETRY** | Last run fades to ghost ink in 320 ms, then settles in 120 ms; sign returns to the tray | "Place the sign" | Place as before | As PLACEMENT | Seed resets, no old score or agents | A tap during the fade is queued, not lost | Reduced motion: instant reset |
| **EXPLORE** | Optional free look; the round keeps running if started during RUNNING | "Free look. Round keeps running." | Drag the **rail** (vertical) or two fingers; **Return to sign** | Rail, map, UI | Camera never changes the simulation | One tap returns to the sign | Static camera setting removes EXPLORE entirely; the game stays completable |

## 4. Safe-area constraints per state

All eight states keep controls out of the top and bottom insets (section 1). On 320×568 the HUD collapses to one line (spec B4): level name, count, time. The 24 px edge reserve applies everywhere except HOME and RESULT buttons, which are wide and centred.

**Layout defects found while drawing this stage** (they existed in the earlier mockups):
1. The D2 HUD started under the status bar and the dock buttons reached about 5 px into the bottom inset. **Fixed** in these pictures by drawing the insets and laying the screen inside them.
2. At 320×568 the North Gate ring touches the HUD band. To fix at Stage 09: 12 px extra top padding on the map for this level.
3. In EXPLORE, "Return to sign" overlaps the School label. Move it or use the label's halo; decide at Stage 09.

## 5. Gestures that must coexist

First-down position decides the owner for the life of that finger (`d4-arbitration.png`). Thresholds are logical px and ms.

| Touch starts on | Gesture | Owner | Result |
|---|---|---|---|
| Sign tray | drag over 8 px | DOCK_DRAG then SIGN_DRAG | Ghost sign follows the finger; the nearest legal ring within 44 px highlights |
| Sign or ring (map) | tap: lift within 220 ms and under 8 px | SIGN_TAP | Turn 90° once if allowed |
| Sign (map) | drag over 8 px, **unlocked** | SIGN_DRAG | In RUNNING the sign is picked up (inactive) and must be dropped on a ring within 3 s |
| Sign (map) | drag over 8 px, **locked** | LOCK_REJECT | Shake, "Locked 2.4 s". **No pan, no pickup** |
| Sign (map) | hold over 420 ms, not moved | SIGN_INSPECT | Callout explaining the sign; no turn |
| Ring (map) | tap, **unlocked** | SIGN_TAP | Moves the sign there with a 0.5 s flight (inactive during it); lock starts on landing |
| Blank map | drag over 12 px | PAN | Map follows the finger. Never touches the sign |
| Blank map | second finger, ratio over 1.06 | PINCH | Takes over; cancels any tentative action |
| Sign (map) | second finger lands | PINCH | Cancels the pending sign action; the sign is unchanged |
| Button | press and release inside | UI | Acts once; the touch never reaches the map |
| EXPLORE rail | drag | PAN along the camera path | Bounded; never leaves the player lost |
| OS edge or system gesture | any | OS | The game receives a cancel and restores a safe state |

**Cancel.** A cancel (system gesture, notification, call) while holding the sign snaps it back to its previous ring and heading. It does not start a lock and does not duplicate or lose the sign (T-19, T-20).

**Single tap cannot both turn and pan.** A tap is decided only when the finger lifts within 220 ms and under 8 px. A touch that moves further is a drag and never a tap.

## 6. Default sign control: the decision for you

| | Placing | Moving while running | Turning | Why |
|---|---|---|---|---|
| **A (recommended)** | **Drag** from the tray; tap a ring also works | Drag the sign, or tap the other ring | Tap the sign | The satisfying physical action is the main one, and a no-drag route always exists |
| B | **Tap a ring** places the sign there | Tap the other ring | Tap the sign | Easiest to learn, least physical |
| C | Tap only, no dragging | Tap the other ring | Tap the sign | Simplest input rules, but loses the tactile "pick up the sign" |

Apple's games page supports "let players tap objects to select them instead of adding a virtual selection button" (option B/C style) and also touch-first controls (A). The sign must stay "physical" for the art direction (a lifted object with a shadow), which favours A. Concern for all three: the North Gate ring is near the top of the screen and may be a long thumb reach on a tall phone. **Untested.** Mitigation: the camera places the active ring in the lower 60 % of the screen whenever the sign is picked up (spec C1 safe offset).

## 7. Twenty-second onboarding transcript (first run, loop C, level R1)

No video, no rules page. Copy is final-style but unapproved.

| Time | Screen | Copy | Player | Game |
|---:|---|---|---|---|
| 0:00 | HOME | "One sign. A hundred decisions." | Taps **Play** | Fly-in begins (550 ms), skippable |
| 0:01 | INTRO | "Deliver 18 of 20 before 0:32." | Looks | Seven walkers wait at North Gate; both rings glow |
| 0:03 | PLACEMENT | "Drag the sign to a ringed junction." | Drags the sign from the tray | Lift on first frame; the nearest ring brightens within 44 px |
| 0:05 | PLACEMENT | none | Releases on **North Gate** | Snap (170 ms). Two small chevrons show the real next turns: Canal Turn and Market |
| 0:06 | PLACEMENT | "Tap the sign to turn it." | Taps the sign | Turns to face east; the chevron toward Market is the one that brightens |
| 0:08 | PLACEMENT | none | Taps **Start** (now enabled) | Clock starts. Within about 3 s the first walker turns |
| 0:11 | RUNNING | none | Watches | A short ink tick at the node marks each walker that chose differently because of the sign |
| 0:13 | RUNNING | "Sign locked 3.1 s" appears after the first action in later runs | Watches | In the very first run no action has been taken yet, so no lock shows |
| 0:15 | RUNNING | "Tap the sign any time to turn it." (once, only if a queue forms) | May tap the sign | Turn indexed 160 ms; lock ring starts the same frame |
| 0:20 | RUNNING | none | Watches | The first reroute has been seen; the first-run guidance ends |

Timings are targets. The spec's own check applies: the first visible route decision must arrive within about 3 s of Start.

## 8. Accessibility alternatives

- **Hand layout:** left- and right-hand dock; the tray and the button swap sides.
- **No drag needed:** every drag has a tap equivalent (section 5).
- **Static camera:** removes EXPLORE and automatic camera moves; the round is still completable.
- **Reduced motion:** fly-in, pullback and retry fade become short cross-fades.
- **Haptics:** optional, never required for any information.
- **Screen readers:** every control has a text label that states state and consequence, for example "Sign. At North Gate. Pointing east. Locked for 3 seconds." Not tested with VoiceOver or TalkBack.
- **No colour-only meaning:** queues are hatched, the lock is a ring with a countdown, and the sign is recognisable in grayscale (see Stage 02 art tests).
- **Larger targets:** an accessibility option adds 8 px to every hit area.

## 9. Twelve or more gesture conflict tests (GIVEN / WHEN / THEN)

| ID | GIVEN | WHEN | THEN |
|---|---|---|---|
| G-01 | RUNNING, sign unlocked | quick tap on the sign | the sign turns once; the map does not pan |
| G-02 | RUNNING, sign unlocked | touch the sign, move 6 px, lift in 200 ms | it counts as a tap: one turn, no pan |
| G-03 | RUNNING, sign unlocked | touch the sign and move 9 px | SIGN_DRAG; the sign is held; the map does not pan |
| G-04 | RUNNING, sign locked | touch the sign and drag | LOCK_REJECT: shake and message; no pan, no pickup; the lock is unchanged |
| G-05 | RUNNING | touch blank map, drag 13 px across the sign | PAN only; the sign is untouched |
| G-06 | RUNNING | touch the map, add a second finger, ratio 1.07 | PINCH; no tap fires |
| G-07 | PLACEMENT | touch the sign, then a second finger lands | the pending sign action is cancelled; the sign is unchanged; PINCH owns the gesture |
| G-08 | PLACEMENT | drag from the tray and release off a ring | the sign snaps back to the tray with "Drop it on a ring"; no penalty |
| G-09 | any | touch starts in the 24 px edge reserve | ignored by the game (the OS gesture may run) |
| G-10 | RUNNING, sign held | a system interruption cancels the touch | the sign snaps back to its previous ring; no lock starts; exactly one sign exists |
| G-11 | PAUSED | tap the sign | nothing happens and the sentence "The sign can't be changed while paused." shows; **Resume** works |
| G-12 | RUNNING | hold the sign 450 ms without moving | callout shows; no turn on release |
| G-13 | RUNNING | one finger presses **Pause** while another pans the map | Pause acts once on release; the pan continues independently |
| G-14 | RUNNING, sign locked | tap the other ring | rejected with the same lock message; the sign does not move |
| G-15 | RUNNING, sign held | the finger lifts off a ring and the 3 s timeout expires | the sign returns to its previous ring and heading, active, no lock |

## 10. Source list (accessed 2026-11-23)

| Page | Used for | Caveat |
|---|---|---|
| [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) | iOS default 44×44 pt and minimum 28×28 pt control size | Read through Apple's documentation data endpoint because the web page needs JavaScript. All Apple pages carry the same "last modified 19 Nov 2026" header, so that is not a per-page date |
| [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout) | Safe area, Dynamic Island, "centers at least 60 points apart" | The 60-point sentence was read without its surrounding context |
| [Apple HIG: Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games) | "buttons in iOS must be at least 44x44 pt" | |
| [Apple HIG: Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls) | Tap objects to select them | |
| [Apple HIG: Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures) | Deferring system gestures in games | |
| [Apple HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion) | Purposeful motion; the Reduce Motion setting | |
| [Android: Gesture navigation](https://developer.android.com/guide/navigation/gesturenav) | Back swipe from either edge; bottom swipes; exclusion rects; immersive mode | No edge widths given |
| [Android Accessibility Help: Touch target size](https://support.google.com/accessibility/android/answer/7101858?hl=en) | 48dp | |
| [WCAG 2.2](https://www.w3.org/TR/wcag/) | 2.5.8 (24 CSS px, AA) and 2.5.5 (44 CSS px, AAA) | |

## 11. What is still unknown

Real edge-gesture widths on devices; real thumb reach to North Gate on a tall phone; whether 8, 12 and 220 ms feel right; real latency; screen-reader behaviour; whether the lock (4 s) and hold (3 s) feel fair in the hand. Each needs a phone (R-01).

# DIFFERENTIATION (Stage 01: comparable products and originality stress test)

Access date for every source below: **2026-11-22**. Evidence labels:
- **PRIMARY**: I read the publisher's or store's own page in full-text form.
- **INFORMAL**: Wikipedia, a review or a news article I read. Useful, not authoritative.
- **JUDGEMENT**: my reading of the evidence. Not measured, not tested on players.

I do not claim any combination below has never been done. I checked 11 products' pages, not the whole market.

## 1. The one-sentence unique promise (PROPOSED)

> Place one civic sign at a junction, watch a small city's crowd bend toward it, then see exactly which turn decided the outcome.

**Skeptic's version:** Unlike a traffic-light game you never stop anyone. Unlike a transit-route game you don't build lines. Unlike tower defense nothing attacks you. You nudge each walker's next-junction choice with one sign, then read why it worked or failed.

## 2. Products compared (11)

Each row has the ONE closest mechanical similarity and the ONE visual-similarity risk, as the spec asks. "Risk vs D2" means against the current provisional art direction (Civic Press, revised): warm paper, ink double-stroke roads, stamped people, vermilion sign.

| # | Product (developer, date shown) | Evidence | Closest mechanical similarity | Visual-similarity risk | Source |
|---|---|---|---|---|---|
| 1 | **Humanity** (tha ltd., Steam release May 15, 2023) | PRIMARY | You steer a crowd that follows commands instead of controlling individuals ("commanding massive, marching crowds to the goal") | The store page sells a "stark iconic style" (visual director Yugo Nakamura). Mono swarms of tiny people are its look. Our walkers at atlas scale must not read as a swarm silhouette | [S1] |
| 2 | **Lemmings** (DMA Design, 14 Feb 1991; mobile review dated 26 Jan 2009) | INFORMAL | Walkers keep their default behaviour until given a limited skill, so the player never controls individuals | Tiny sprites in a hazard landscape. Low risk. Our people are drawn larger and carry a proper identity | [S2], [S3] |
| 3 | **Mini Metro** (Dinosaur Polo Club; App Store page read) | PRIMARY | Draw lines between stations while passengers wait, "redraw your lines to keep them efficient". Closest on "a map you rework under time pressure" | Wikipedia: "bold colours and simple geometry to replicate the appearance of modern transit maps". **Highest overlap** with any transit-diagram look, including Direction C and our ribbon atlas view | [S4], [S5] |
| 4 | **Mini Motorways** (Dinosaur Polo Club; Apple Arcade Sept 2019 per Wikipedia) | PRIMARY + INFORMAL | Build a road network to connect coloured houses to buildings; flow and bottlenecks | Same studio, same flat top-down minimalism. Roads as bold strokes. Our double-stroke ink roads are the nearest thing | [S6], [S7] |
| 5 | **Flight Control** (Firemint; first iOS release Mar 5, 2009; HD on Steam Nov 18, 2010) | PRIMARY + INFORMAL | A finger intervention on a moving crowd of vehicles: "drawing flight paths on-screen". Closest on "touch changes where moving things go" | Low. Bright flat top-down toy look | [S8], [S9], [S10] |
| 6 | **Train Valley** (Flazm, Sept 16, 2015) | INFORMAL | Switches at junctions send traffic down chosen routes | Toy-diorama railway. Low | [S11] |
| 7 | **Traffix: City Rush** (INFINITY GAMES, LDA; App Store page read) | PRIMARY | One tap at a junction changes what flows ("Tap the traffic light … to change its color"). Closest on "one tap at one junction" | The page itself says visuals are "very simple and minimalist". Flat vehicles on roads | [S12] |
| 8 | **Touch Traffic HD** (TRADEGAME Lab; App Store page read) | PRIMARY | Control a signal to minimise total waiting time; emergency vehicles have priority. Closest on "queue time is the score" | Generic cars-on-grid look. Low | [S13] |
| 9 | **Bad North** (Plausible Concept / Raw Fury; Switch Aug 20, 2018, iOS and Android Oct 16, 2019) | PRIMARY + INFORMAL | You "control the broad strokes of the battle, giving high level commands" to small units. Closest on indirect command on a touchscreen | Charming minimalist islands with small figures. PC Gamer (5 Jan 2018) quotes the developer calling it a "minimalistic, real-time tactics roguelite". Medium | [S14], [S15], [S16] |
| 10 | **Pikmin 4** (Nintendo EPD and Eighting, July 21, 2023) | PRIMARY + INFORMAL | You lead and guide a crowd of small creatures rather than direct each one | Miniature toy-world look. Low | [S17], [S18] |
| 11 | **The Pedestrian** (Skookum Arts, Jan 2020 on PC) | INFORMAL | Signs themselves are game objects, rearranged to make a path for a stick figure. Closest on "signage as the interface" | **Pictogram figures on signs.** Our stamped walkers and civic signage must not look like public-sign stick figures | [S19] |

## 3. Mechanic by visual overlap matrix (JUDGEMENT)

Overlap: **H** high, **M** medium, **L** low. Visual overlap is measured against D2 as drawn in `docs/art-exploration/round3-D2-civic-press-revised/`.

| Product | Mechanic overlap | Visual overlap vs D2 |
|---|---|---|
| Humanity | M (crowd obeys, indirect) | M (iconic crowds) |
| Lemmings | M | L |
| Mini Metro | L | **H** |
| Mini Motorways | M | **H** |
| Flight Control | M | L |
| Train Valley | M | L |
| Traffix: City Rush | **H** (one tap, one junction) | M |
| Touch Traffic HD | **H** (signal, wait time) | L |
| Bad North | L | M |
| Pikmin 4 | M | L |
| The Pedestrian | L | M (signage language) |

```
                    visual overlap with D2
                    low              medium            high
mechanic   high     Touch Traffic    Traffix
overlap    medium   Lemmings, FC,    Humanity          Mini Motorways
                    Train Valley,
                    Pikmin 4
           low                       Bad North,        Mini Metro
                                     The Pedestrian
```

The two corners to worry about: **Traffix and Touch Traffic** (mechanic) and **Mini Metro and Mini Motorways** (look).

## 4. Five risky clichés to avoid (JUDGEMENT)

1. **Cars and traffic lights.** The spec already excludes them. Traffix and Touch Traffic own this.
2. **A menu of verbs per walker (Lemmings).** We have one sign and no skill menu.
3. **Bold coloured lines on pale ground with circles for stations** (Mini Metro and Mini Motorways). Keep the atlas view's ribbons ink-and-rust with counts, not saturated transit lines.
4. **Monochrome swarm silhouettes** (Humanity). Keep walkers as three distinct, individually drawn types at street and district scale.
5. **Cozy miniature diorama towns.** Direction B leans this way; it is also a crowded market.

## 5. Three defensible combinations worth prototyping (PROPOSED, not proven novel)

| ID | Combination | Why it differs from the 11 compared | How it would be tested |
|---|---|---|---|
| N1 | **One physical sign that biases a walker's next-junction choice, with different response by walker type.** Nothing is forced or stopped | Lemmings assigns per-walker skills; Flight Control draws exact paths; Traffix and Touch Traffic switch lights (stop or go). I found nothing among the 11 where one placed object shifts route *preference* by profile | Stage 02 loop variants, then the Stage 08 graybox with seed 1007 run twice (sign east, sign south), per the spec's causality proof |
| N2 | **A replay that names the decisive junction with branch percentages** ("7 of 9 took the narrow walkway"), generated from the simulation log | None of the 11 store or review pages I read describes an explanation of this kind. This does not show it doesn't exist elsewhere | Stage 13: the explanation is only shown when the logged events confirm it |
| N3 | **One data source, three zoom languages:** stamped walkers, then counted ribbons, then an atlas of flux, with exact counts preserved | Mini Metro and Mini Motorways stay at one scale | Stage 11 semantic zoom, with a no-duplicate-agent test |

**Which to test first (my recommendation): N1.** It is the core verb. N2 and N3 only matter if N1 is fun.

## 6. Alternative design paths considered (at least 3)

| Path | What it is | Why not (or when) |
|---|---|---|
| P1 (baseline) | One sign, route preference, next-junction effect | Chosen as the baseline in CC-RULESET-01 |
| P2 | Sign as a hard gate: blocks a road (like Traffix) | Collapses into "traffic light". Rejected |
| P3 | Several cheap signs placed freely (Mini Motorways style building) | Breaks the one-sign invariant (spec H2). Rejected unless scope is reopened |
| P4 | Per-walker skills (Lemmings style) | Adds a menu and per-agent micromanagement. Rejected |
| P5 | Draw a path for each group (Flight Control style) | Gives direct control; the game is about prediction. Rejected |

## 7. Checking the sources in your documents

You asked earlier whether I could open the sites your review documents cite. After the hosts were allowed, I read them.

| Cited page | Result | Claim checked | Verdict |
|---|---|---|---|
| London Transport Museum, record 106 | Loaded | Beck's diagram devised 1931, issued 1933 | **Supported.** "In 1931 … Beck … created the first diagrammatic map of the Underground … First issued in 1933". Page says lines run horizontal, vertical or 45°, stations evenly spaced "unlike the geographic map" |
| London Museum, Beck article | Loaded | 1933 map, connections over distance | **Supported for 1933** ("creating the modern London Underground map in 1933"). The 1931 date is on the LTM page, not this one |
| ISOTYPE, University of Vienna | Loaded | Neurath, Reidemeister, Arntz, repeatable pictures | **Partly.** Page covers Neurath, the "Vienna Method of Picture Statistics", Marie Neurath and the Isotype Institute. I did not find Gerd Arntz named in the text I read |
| Cooper Hewitt, "Picturing Language" (2013-08-06) | Loaded | ISOTYPE as a pictorial vocabulary | **Supported** ("a visual vocabulary and a system of meta…"). A 2013 article, used for design history only, not as engineering guidance |
| The Met, screenprint techniques | **Blocked (HTTP 429, bot check)** | Registration and deliberate misregistration | **UNVERIFIED** |
| W3C WCAG 2.2 | Loaded (header last-modified 12 Dec 2024) | Contrast and target-size criteria | **Supported with a correction.** 1.4.3: 4.5:1, large text 3:1. **2.5.8 Target Size (Minimum), level AA, is 24 by 24 CSS pixels.** 44 by 44 is **2.5.5, level AAA** |
| Android touch target help | Loaded | 48dp | **Supported.** "at least 48dp" |
| Apple HIG accessibility | HTTP 200, no body text (page needs JavaScript) | 44pt | **UNVERIFIED** |
| Apple HIG motion | Same | Reduced motion | **UNVERIFIED** |

**What this changes:** the reviews' 44pt and 48dp targets are Apple and Material guidance, and I have only confirmed the Android one. WCAG's AA floor is lower (24px) and its AAA figure is 44px. The spec's own "44pt-equivalent" rule stays; it is a stricter game-design choice, not a WCAG requirement. Rated as risk R-12 in `docs/RISKS.md`.

## 8. Source list (access date 2026-11-22)

| ID | Page | Vendor or author | Date shown | Supports | Caveat |
|---|---|---|---|---|---|
| S1 | [HUMANITY on Steam](https://store.steampowered.com/app/1581480/Humanity/) | Valve store, tha ltd. | Release May 15, 2023 | Crowd command; "stark iconic style" | Publisher marketing |
| S2 | [Lemmings (video game), Wikipedia](https://en.wikipedia.org/wiki/Lemmings_(video_game)) | Wikipedia | Page modified 22 Nov 2026 | 1991 release, DMA Design, skill assignment | Encyclopedia |
| S3 | [Lemmings Tribes Review, Pocket Gamer](https://www.pocketgamer.com/lemmings-tribes/review/) | Kath Brice | Jan 26, 2009 | Lemmings on mobile | Old; a Java mobile title, not the 1991 original |
| S4 | [Mini Metro, App Store](https://apps.apple.com/nz/app/mini-metro/id837860959) | Dinosaur Polo Club | none shown | Draw lines, redraw as stations open | Store text |
| S5 | [Mini Metro, Wikipedia](https://en.wikipedia.org/wiki/Mini_Metro_(video_game)) | Wikipedia | Modified 22 Nov 2026 | "bold colours and simple geometry" | Encyclopedia |
| S6 | [Mini Motorways, App Store](https://apps.apple.com/us/app/mini-motorways/id1453901000) | Dinosaur Polo Club | none shown | Roads, houses, destinations | Store text |
| S7 | [Mini Motorways, Wikipedia](https://en.wikipedia.org/wiki/Mini_Motorways) | Wikipedia | Modified 22 Nov 2026 | Apple Arcade Sept 2019 | Encyclopedia |
| S8 | [Flight Control HD on Steam](https://store.steampowered.com/app/62000) | Firemint | Release Nov 18, 2010 | HD release date | Marketing text |
| S9 | [Flight Control, Wikipedia](https://en.wikipedia.org/wiki/Flight_Control_(video_game)) | Wikipedia | Modified 17 Nov 2026 | First iOS release Mar 5, 2009 | Encyclopedia |
| S10 | [Flight Control's land, sea and air spawn, Pocket Gamer](https://www.pocketgamer.com/articles/014712/r/) | Stuart Dredge | Jul 31, 2009 | "drawing flight paths" | Old feature |
| S11 | [Train Valley, Wikipedia](https://en.wikipedia.org/wiki/Train_Valley) | Wikipedia | Modified 17 Nov 2026 | Release Sept 16, 2015; switches | Encyclopedia |
| S12 | [Traffix: City Rush, App Store](https://apps.apple.com/app/id1465703539) | INFINITY GAMES, LDA | none shown | Tap a traffic light | Store text |
| S13 | [Touch Traffic HD, App Store](https://apps.apple.com/us/app/id514795920) | TRADEGAME Lab Inc. | none shown | Signal control and waiting time | Store text |
| S14 | [Bad North: Jotunn Edition, App Store](https://apps.apple.com/app/id1367121168) | Raw Fury | none shown | High-level commands | Store text |
| S15 | [Bad North, Wikipedia](https://en.wikipedia.org/wiki/Bad_North) | Wikipedia | Modified 17 Nov 2026 | Release dates | Encyclopedia |
| S16 | [Bad North is a strategy roguelike with vikings, PC Gamer](https://www.pcgamer.com/bad-north-is-a-strategy-roguelike-with-vikings-and-charming-brutality) | PC Gamer | 2018-01-05 | "minimalistic, real-time tactics roguelite" | Preview, 2018 |
| S17 | [Pikmin 4, Nintendo](https://www.nintendo.com/us/store/products/pikmin-4-117531/) | Nintendo | none shown | Guide small creatures | Publisher text |
| S18 | [Pikmin 4, Wikipedia](https://en.wikipedia.org/wiki/Pikmin_4) | Wikipedia | Modified 21 Nov 2026 | July 21, 2023 release | Encyclopedia |
| S19 | [The Pedestrian, Wikipedia](https://en.wikipedia.org/wiki/The_Pedestrian_(video_game)) | Wikipedia | Modified 17 Nov 2026 | Signs-as-puzzle, Jan 2020 | Encyclopedia |

Not used as evidence: web-search summaries. I used them only to find candidate games, and every claim above comes from a page I read.

## 9. What this stage could not do

- TouchArcade (bot check) and The Met (HTTP 429) could not be read. The Apple developer pages returned no body text.
- I did not read player reviews of the 11 games beyond the pages cited. "Mechanical similarity" is my reading of the product descriptions, not of play.
- Nothing here was tested on players. Overlap ratings are judgement.

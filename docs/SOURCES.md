# SOURCES (technical register, started at Stage 06)

Fields: page, vendor or author, date shown, date accessed, version it applies to, claim it supports, caveat. "Date shown" is what the page itself shows; "HTTP date" means only the server's last-modified header, which is weaker. Anything not readable is listed as UNVERIFIED, and `VERIFY_ON_TARGET_ENGINE` marks claims to probe on the real engine.

| Page | Vendor | Date shown | Accessed | Applies to | Claim supported | Caveat |
|---|---|---|---|---|---|---|
| [Godot download page (Linux)](https://godotengine.org/download/linux/) | Godot Foundation | "4.7.2 · 18 August 2026" | 2026-11-23 | Godot 4.7.2 | 4.7.2 is the current stable | |
| [Godot download archive](https://godotengine.org/download/archive/) | Godot Foundation | none; HTTP date 18 Nov 2026 | 2026-11-23 | Godot 4.7.x, 4.8 beta | 4.8 is "beta", 4.7.2 is "stable" | |
| [Godot 4.7 release notes](https://godotengine.org/releases/4.7/) | Godot Foundation | HTTP date 6 Nov 2026 | 2026-11-23 | Godot 4.7 | Standalone Android exporting, Android editor | Marketing text |
| [Godot licence](https://godotengine.org/license/) | Godot Foundation | HTTP date 6 Nov 2026 | 2026-11-23 | Godot | MIT licence | |
| [Godot 4.7.2 release assets and SHA512-SUMS](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable) | Godot builds repository | none | 2026-11-23 | Godot 4.7.2 | The Linux zip's checksum matched | Downloaded via GitHub because the vendor's download host is not allowed |
| [Unity 6 releases and support](https://unity.com/releases/unity-6/support) | Unity | none | 2026-11-23 | Unity 6.3 LTS | 6.3 LTS supported until December 2027 | |
| [Unity 6.3 manual](https://docs.unity.com/en-us/engine/6000.3/manual) | Unity | "Last updated 24 days ago" | 2026-11-23 | Unity 6000.3 | The 6.3 manual exists; version list | Relative date only |
| [Meet Google Play's target API level requirement](https://developer.android.com/google/play/requirements/target-sdk) | Google | HTTP date 28 Oct 2026 | 2026-11-23 | Google Play | From 31 Aug 2026, new apps and updates target API 36 or higher | Policy changes; **re-verify at release** |
| [Frame Pacing library](https://developer.android.com/games/sdk/frame-pacing/) | Google | HTTP date 26 Feb 2026 | 2026-11-23 | Android | Page loads | Not studied |
| [Android gesture navigation](https://developer.android.com/guide/navigation/gesturenav) | Google | none | 2026-11-23 | Android 10+ | Back swipe from either edge; exclusion API | No edge widths in dp |
| [Android touch target size](https://support.google.com/accessibility/android/answer/7101858?hl=en) | Google | none | 2026-11-23 | Android | 48dp recommendation | |
| [Apple HIG pages: accessibility, layout, games, game controls, gestures, motion](https://developer.apple.com/design/human-interface-guidelines/accessibility) | Apple | HTTP date 19 Nov 2026 (same for all pages) | 2026-11-23 | iOS and iPadOS | 44×44 pt default and 28×28 pt minimum; safe area; deferring system gestures | Read through Apple's documentation data endpoint; the web pages need JavaScript |
| [WCAG 2.2](https://www.w3.org/TR/wcag/) | W3C | HTTP date 12 Dec 2024 | 2026-11-22 | WCAG 2.2 | 2.5.8 is 24 px (AA); 2.5.5 is 44 px (AAA) | |
| Godot docs: Android export, iOS export, 2D transforms, `InputEventScreenTouch`, `MultiMeshInstance2D` | Godot Foundation | **not read** | 2026-11-23 | Godot 4.7 | none | **UNVERIFIED:** docs.godotengine.org returned HTTP 429 (bot check). `VERIFY_ON_TARGET_ENGINE` |
| Unity pricing, Unity Android requirements | Unity | **not read** | 2026-11-23 | Unity 6.3 | none | **UNVERIFIED:** pricing URL 404; requirements page 404 |

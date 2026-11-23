# STATE

```
CURRENT_STAGE:        05 (Art direction competition with complete visual grammar): AWAITING USER APPROVAL
LAST_APPROVED_STAGE:  04 (user: "Approve Stage 04, choose A", 2026-11-23). Default sign control A: drag primary, tap alternative
NEXT_ACTION:          User picks one art direction (A, B or C, optionally with one named detail from another) and says "Approve Stage 05". Stage 06 starts only after that.
BUILD_HASH:           none (no build exists). Docs commit: see `git log`
ENGINE_VERSION:       none selected. Candidate only: Godot 4.7 stable (UNVERIFIED from this container)
KNOWN_BLOCKERS:
  - No Android test device and no attached user computer (needed from Stage 06)
  - Godot / Unity / adb not installed in the container (needed from Stage 06)
  - Outbound web: user approved web access on 2026-11-22; 15 hosts were added to the environment allowlist (Stage 01 product pages and the sites cited in the user's documents). Stage 06 hosts (godotengine.org, docs.godotengine.org, unity.com, docs.unity.com, developer.android.com) are NOT yet allowed
  - Font and asset licences unchecked (needed before Stage 05 approval)
  - Remote control: not enabled on the user's computer yet; list_computer_folders returned no folders (checked twice, 2026-11-22)
```

## Last approved stage

Stage 00, approved by the user on 2026-11-22 ("Approve Stage 00, Confirm the baseline: Web access approved"). The user explicitly confirmed the baseline (one sign, portrait phone). The test-hardware question was not answered, so that blocker stays open.

## Resume procedure (from the spec, section 2)

Read `docs/STATE.md`, `docs/DECISIONS.md`, `docs/BRIEF.md`, `docs/CHANGELOG.md`, `docs/TEST_REPORT.md`, check `git status`, summarise the last approved stage in 5 lines, continue only the next unapproved stage.
`docs/CHANGELOG.md` and `docs/TEST_REPORT.md` do not exist yet. Stage 00 creates only four documents (BRIEF, STATE, DECISIONS, RISKS). The other two are created when there is something to put in them.

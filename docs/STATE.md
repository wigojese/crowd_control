# STATE

```
CURRENT_STAGE:        00 (Inventory, constraints and starting snapshot): AWAITING USER APPROVAL
LAST_APPROVED_STAGE:  none
NEXT_ACTION:          User replies "Approve Stage 00" (or requests a revision). Nothing else is started before that.
BUILD_HASH:           none (no build exists). Docs commit: see `git log`
ENGINE_VERSION:       none selected. Candidate only: Godot 4.7 stable (UNVERIFIED from this container)
KNOWN_BLOCKERS:
  - No Android test device and no attached user computer (needed from Stage 06)
  - Godot / Unity / adb not installed in the container (needed from Stage 06)
  - Outbound web limited to an allowlist; Stage 01 research and Stage 06 doc checks are BLOCKED/UNVERIFIED until hosts are allowed or the user supplies pages
  - Font and asset licences unchecked (needed before Stage 05 approval)
```

## Last approved stage

None. This is the first stage. The user has not yet given an explicit "Approve Stage 00".

## Resume procedure (from the spec, section 2)

Read `docs/STATE.md`, `docs/DECISIONS.md`, `docs/BRIEF.md`, `docs/CHANGELOG.md`, `docs/TEST_REPORT.md`, check `git status`, summarise the last approved stage in 5 lines, continue only the next unapproved stage.
`docs/CHANGELOG.md` and `docs/TEST_REPORT.md` do not exist yet. Stage 00 creates only four documents (BRIEF, STATE, DECISIONS, RISKS). The other two are created when there is something to put in them.

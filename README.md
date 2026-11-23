# CROWD CONTROL

A portrait mobile pedestrian-flow strategy game: redirect a miniature city's crowd with one movable directional sign.
Status: Stage 18 design-and-reference freeze. Rules, levels, camera, audio and accessibility exist as GDScript plus a tested Python reference; **no engine run, no build, no device or player test yet**. Start with `docs/STATE.md`, then `docs/RELEASE.md` (checklist, blockers, handoff).

## Commands

Checks that need only Python 3 (run here, shown in `docs/TEST_LOG.md`):

```bash
scripts/check_all.sh
```

Engine checks need Godot 4.7.2 stable on `PATH` as `godot` (`scripts/check_all.sh` runs them when it finds it):

```bash
godot --headless --path . --script res://tools/test_runner.gd
```

```bash
godot --headless --path . --script res://tools/scenario_runner.gd -- res://tests/fixtures/scenario_ok.json
```

```bash
godot --headless --path . --quit-after 2
```

The last command must print `BOOT_STATE=READY`. Open the project in the Godot 4.7.2 editor to see the blank boot screen.

## Layout

| Path | Contents |
|---|---|
| `src/core` | `CcRng`, `CcStateMachine`, `CcEventLog`. No scene tree |
| `src/simulation` | Rules (Stage 08). Now only `CcTickFixture` |
| `src/levels` | `CcScenarioValidator` |
| `src/app` | Boot scene |
| `data` | State table, event schema (data, not code) |
| `tests`, `tools` | Test files, fixtures, headless runners |
| `scripts` | Python lint, scenario validator, golden-file check, `check_all.sh` |
| `assets/fonts` | Font licences (no font files yet) |
| `spikes` | Throwaway Stage 06 spike, not part of the project |

Rules: no autoloads or global singletons; the simulation never touches the scene tree; every random draw goes through `CcRng`.
Details: `docs/ARCHITECTURE.md`.

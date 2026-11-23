# Godot simulation spike (Stage 06)

Throwaway. Not the production project (that is created at Stage 07). Written for Godot **4.7.2** stable. **Status: written, not yet run.**

## Run

From the repository root, with Godot 4.7.2 installed as `godot`:

```bash
godot --headless --path spikes/godot-sim --script res://l01_check.gd
```

```bash
godot --headless --path spikes/godot-sim --script res://bench.gd
```

- `l01_check.gd` prints `PASS` or `FAIL` for 12 cases plus a determinism check, then `RESULT: ALL PASS` or the number failed. Exit code 0 on all pass.
- `bench.gd` prints one line per scenario and writes `bench_out.json` to Godot's `user://` folder (the path is printed).

## Files

| File | Purpose |
|---|---|
| `sim_core.gd` | The CC-RULESET-01C simulation, a plain `RefCounted`, no scene tree |
| `l01_check.gd` | Compares results with `expected_python_model.json` (from `docs/analysis/stage03_numeric_check.py`) |
| `bench.gd` | Per-tick cost at 50, 200, 500 walkers on 7, 25, 50 nodes |
| `expected_python_model.json` | Reference numbers from the Python model |

## Honest limits

CPU only, headless: it measures the cost of the game's rules, **not rendering**. A number from a desktop CPU does not predict a phone. Since the code has never been run, a first run may need small syntax fixes.

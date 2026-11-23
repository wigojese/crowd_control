#!/usr/bin/env bash
# Runs every check that works without Godot. Then, if `godot` is installed, the engine checks.
# Usage: scripts/check_all.sh        Exit 0 only if everything that ran passed.
set -u
cd "$(dirname "$0")/.."
fail=0
run() { echo "== $*"; "$@" || fail=1; }
run python3 -I scripts/lint.py
run python3 -I scripts/test_lint.py
run python3 -I scripts/validate_scenarios.py --fixtures
run python3 -I scripts/check_golden.py
run python3 -I scripts/ref_input.py
run python3 -I scripts/ref_ribbon.py
run python3 -I scripts/ref_sim.py
run python3 -I scripts/ref_explain.py
run python3 -I scripts/ref_camera.py
run python3 -I scripts/ref_transitions.py
run python3 -I scripts/check_contrast.py
if command -v godot >/dev/null 2>&1; then
  run godot --headless --path . --script res://tools/test_runner.gd
  run godot --headless --path . --script res://tools/scenario_runner.gd -- res://tests/fixtures/scenario_ok.json
  run godot --headless --path . --quit-after 2
else
  echo "== SKIPPED engine checks: godot is not installed (BLOCKED here, see docs/TEST_LOG.md)"
fi
echo "CHECK_ALL: $([ $fail = 0 ] && echo OK || echo FAILED)"
exit $fail

extends RefCounted
## Tests T-SIM-1..5. The engine simulation must reproduce the Python reference model on level CC-L01-R1.
## Command format: [tick, ordinal, "ROTATE"|"MOVE", argument].

const KEYS := ["arrived", "ontime", "blocked_ticks", "person_ticks", "score", "last_arr", "sign_actions"]


func _world() -> CcSimWorld:
	var level = JSON.parse_string(FileAccess.get_file_as_string("res://data/levels/cc_l01_r1.json"))
	var schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))
	return CcSimWorld.new(level, schema["events"])


func _expected() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/expected_python_model.json"))


func _check(key: String, sign_state: Array, commands: Array) -> String:
	var got := _world().run(sign_state, commands)
	var want: Dictionary = _expected()[key]
	for k in KEYS:
		if int(got[k]) != int(want[k]):
			return "%s: %s got %d want %d" % [key, k, int(got[k]), int(want[k])]
	return ""


func test_no_sign_baseline_fails_the_pass_mark() -> String:
	var got := _world().run([], [])
	if got["passed"]:
		return "baseline passed with %d arrived" % int(got["arrived"])
	return _check("r1_no_sign", [], [])


func test_static_placements_match_reference() -> String:
	for c in [["r1_A_N", ["A", "N"]], ["r1_A_E", ["A", "E"]], ["r1_A_S", ["A", "S"]],
			["r1_B_E", ["B", "E"]], ["r1_B_N", ["B", "N"]]]:
		var problem := _check(c[0], c[1], [])
		if problem != "":
			return problem
	return ""


func test_running_actions_match_reference() -> String:
	var cases := [
		["r1_A_N_rotateE_t0", ["A", "N"], [[0, 0, "ROTATE", "E"]]],
		["r1_B_E_moveA_t100", ["B", "E"], [[100, 0, "MOVE", "A"]]],
		["r1_A_E_rotateN_t200", ["A", "E"], [[200, 0, "ROTATE", "N"]]],
	]
	for c in cases:
		var problem := _check(c[0], c[1], c[2])
		if problem != "":
			return problem
	return ""


func test_east_sign_passes_where_no_sign_fails() -> String:
	var east := _world().run(["A", "E"], [])
	var none := _world().run([], [])
	if not east["passed"] or none["passed"]:
		return "expected A/E to pass and NO_SIGN to fail"
	return ""


func test_replay_is_deterministic() -> String:
	var a := _world().run(["A", "E"], [])
	var b := _world().run(["A", "E"], [])
	return "" if int(a["hash"]) == int(b["hash"]) else "event hash differs between identical runs"


func test_sign_flips_at_least_two_decisions() -> String:
	var w := _world()
	w.run(["A", "E"], [])
	var flipped := 0
	for line in w.events.lines:
		if line.contains("|DECISION|") and line.contains("reason=sign_flipped"):
			flipped += 1
	return "" if flipped >= 2 else "only %d sign_flipped decisions" % flipped

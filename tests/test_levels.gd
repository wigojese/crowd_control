extends RefCounted
## Tests T-LVL-1..3. Every level: no sign fails, every listed solution passes, and the engine rules give the same
## arrivals and event hash as the Python reference replay in data/replays (cross-implementation check).

const LEVELS := ["cc_l01_r1", "cc_l02_ferry", "cc_l03_narrow"]


func _level(name: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/levels/%s.json" % name))


func _world(level: Dictionary) -> CcSimWorld:
	var schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))
	return CcSimWorld.new(level, schema["events"])


func _commands(s: Dictionary) -> Array:
	var out := []
	for c in s["commands"]:
		out.append([int(c[0]), int(c[1]), String(c[2]), String(c[3])])
	return out


func test_no_sign_fails_every_level() -> String:
	for name in LEVELS:
		var lv := _level(name)
		var r := _world(lv).run([], [])
		if r["passed"]:
			return "%s: no sign passed with %d arrived" % [name, int(r["arrived"])]
	return ""


func test_every_listed_solution_passes() -> String:
	for name in LEVELS:
		var lv := _level(name)
		if (lv["solutions"] as Array).size() < 2:
			return "%s: fewer than two solutions" % name
		for s in lv["solutions"]:
			var r := _world(lv).run(s["initial_sign"], _commands(s))
			if not r["passed"]:
				return "%s: solution %s did not pass (%d)" % [name, s["id"], int(r["arrived"])]
	return ""


func test_engine_matches_python_replays() -> String:
	for name in LEVELS:
		var lv := _level(name)
		for s in lv["solutions"]:
			var path := "res://data/replays/%s__%s.json" % [lv["level_id"], s["id"]]
			var rep = JSON.parse_string(FileAccess.get_file_as_string(path))
			var r := _world(lv).run(s["initial_sign"], _commands(s))
			var want: int = int(rep["result"]["arrived"])
			if int(r["arrived"]) != want:
				return "%s %s: arrived %d, reference %d" % [name, s["id"], int(r["arrived"]), want]
			if int(r["hash"]) != int(rep["event_hash"]):
				return "%s %s: event hash differs from the Python reference" % [name, s["id"]]
	return ""

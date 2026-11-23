extends RefCounted
## Tests T-IN-1..3. Runs every case in tests/fixtures/input_cases.json (G-01..G-15 and extras) and compares
## the ordered intent types with the expectation. The Python reference (scripts/ref_input.py) runs the same file.


func _tokens() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/input_tokens.json"))


func _cases() -> Array:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/input_cases.json"))


func _run(c: Dictionary) -> Array:
	var r := CcGestureRouter.new(c["scene"], _tokens())
	var types := []
	for ev in c["events"]:
		var out: Array
		match String(ev["op"]):
			"down":
				out = r.down(int(ev["id"]), ev["pos"], int(ev["t"]))
			"move":
				out = r.move(int(ev["id"]), ev["pos"], int(ev["t"]))
			"up":
				out = r.up(int(ev["id"]), ev["pos"], int(ev["t"]))
			"cancel":
				out = r.cancel(int(ev["id"]), int(ev["t"]))
			_:
				out = r.update(int(ev["t"]))
		for o in out:
			types.append(String(o["type"]))
	return types


func test_all_input_cases() -> String:
	var cases := _cases()
	if cases.size() < 20:
		return "expected at least 20 cases, found %d" % cases.size()
	for c in cases:
		var got := _run(c)
		if str(got) != str(c["expect"]):
			return "%s: got %s want %s" % [c["id"], str(got), str(c["expect"])]
	return ""


func test_no_sign_action_from_a_pan() -> String:
	for c in _cases():
		if String(c["id"]).begins_with("G-05"):
			for t in _run(c):
				if t != "PAN":
					return "pan produced " + String(t)
	return ""


func test_every_pickup_has_exactly_one_resolution() -> String:
	for c in _cases():
		var got := _run(c)
		var pickups := got.count("SIGN_PICKUP")
		var resolved := got.count("SIGN_DROP") + got.count("SNAPBACK")
		if pickups != resolved:
			return "%s: %d pickups but %d resolutions" % [c["id"], pickups, resolved]
	return ""

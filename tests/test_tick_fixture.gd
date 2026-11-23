extends RefCounted
## Tests T-TICK-1..3. The fixture must reproduce scripts/ref_model.py exactly, twice in a row.


func _run() -> Dictionary:
	var gpath := "res://tests/fixtures/tick_fixture_golden.json"
	var g: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(gpath))
	var states = JSON.parse_string(FileAccess.get_file_as_string("res://data/boot_states.json"))
	var schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))["events"]
	var fx := CcTickFixture.new(int(g["seed"]), states, schema)
	var r := fx.run()
	r["golden"] = g
	return r


func test_fixture_matches_golden() -> String:
	var r := _run()
	var g: Dictionary = r["golden"]
	if int(r["spawned"]) != int(g["spawned"]):
		return "spawned %d want %d" % [int(r["spawned"]), int(g["spawned"])]
	if int(r["hash"]) != int(g["hash"]):
		return "hash %d want %d" % [int(r["hash"]), int(g["hash"])]
	return ""


func test_fixture_is_repeatable() -> String:
	return "" if int(_run()["hash"]) == int(_run()["hash"]) else "two runs differ"


func test_fixture_ends_in_ended_state() -> String:
	return "" if _run()["state"] == "ENDED" else "state is " + String(_run()["state"])

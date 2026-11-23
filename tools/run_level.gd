extends SceneTree
## Run one round of a level headless and write the event CSV and a replay JSON.
## Usage: godot --headless --path . --script res://tools/run_level.gd -- <level.json> <SLOT> <HEADING|NONE> [out_dir]
## Example: ... -- res://data/levels/cc_l01_r1.json A E
## Writes <out_dir>/events.csv and <out_dir>/replay.json (default out_dir: user://run). Prints the result.
## STATUS: written; NOT RUN (no runnable Godot).


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3:
		print("usage: run_level.gd -- <level.json> <SLOT|NONE> <HEADING|NONE> [out_dir]")
		quit(2)
		return
	var level = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var errs := CcScenarioValidator.validate(level)
	if errs.size() > 0:
		print("INVALID: ", ",".join(errs))
		quit(1)
		return
	var schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))
	var sign_state: Array = [] if args[1] == "NONE" else [args[1], args[2]]
	var world := CcSimWorld.new(level, schema["events"])
	var res := world.run(sign_state, [])
	var out_dir: String = args[3] if args.size() > 3 else "user://run"
	DirAccess.make_dir_recursive_absolute(out_dir)
	var csv := FileAccess.open(out_dir + "/events.csv", FileAccess.WRITE)
	csv.store_line("tick|seq|type|fields")
	for line in world.events.lines:
		csv.store_line(line)
	csv.close()
	var replay := {"ruleset_version": level["ruleset_version"], "level_id": level["level_id"],
		"seed": level["seed"], "initial_sign": sign_state, "actions": [], "event_hash": res["hash"],
		"engine": Engine.get_version_info()["string"]}
	var rf := FileAccess.open(out_dir + "/replay.json", FileAccess.WRITE)
	rf.store_string(JSON.stringify(replay, "  "))
	rf.close()
	print("RESULT ", JSON.stringify(res))
	quit(0)

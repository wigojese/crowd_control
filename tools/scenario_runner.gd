extends SceneTree
## Headless scenario runner. Validates one scenario file, then runs the Stage 07 tick fixture on its
## seed and prints the event-log hash. The real simulation arrives in Stage 08.
## Run: godot --headless --path . --script res://tools/scenario_runner.gd -- res://tests/fixtures/scenario_ok.json
## STATUS: written; NOT RUN in this container.


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 1:
		print("usage: scenario_runner.gd -- <scenario.json>")
		quit(2)
		return
	var s = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not s is Dictionary:
		print("INVALID: not a JSON object")
		quit(1)
		return
	var errs := CcScenarioValidator.validate(s)
	if errs.size() > 0:
		print("INVALID: ", ",".join(errs))
		quit(1)
		return
	var states = JSON.parse_string(FileAccess.get_file_as_string("res://data/boot_states.json"))
	var schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))
	var fx := CcTickFixture.new(int(s["seed"]), states, schema["events"])
	var r := fx.run()
	print("VALID seed=", int(s["seed"]), " spawned=", r["spawned"], " events=", r["events"], " hash=", r["hash"])
	quit(0)

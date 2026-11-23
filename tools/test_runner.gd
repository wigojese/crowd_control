extends SceneTree
## Headless test runner. Run: godot --headless --path . --script res://tools/test_runner.gd
## Discovers res://tests/test_*.gd, runs every method named test_*, prints PASS/FAIL per test,
## then "RESULT: ALL PASS" or "RESULT: n FAILED". Exit code 0 only when all pass.
## STATUS: written; NOT RUN in this container (Godot execution denied, see docs/TEST_LOG.md).

var failures: int = 0
var run_count: int = 0


func _init() -> void:
	var dir := DirAccess.open("res://tests")
	var files: Array[String] = []
	for f in dir.get_files():
		if f.begins_with("test_") and f.ends_with(".gd"):
			files.append(f)
	files.sort()
	for f in files:
		var script: GDScript = load("res://tests/" + f)
		var inst = script.new()
		var methods: Array[String] = []
		for m in inst.get_method_list():
			if String(m["name"]).begins_with("test_"):
				methods.append(String(m["name"]))
		methods.sort()
		for name in methods:
			run_count += 1
			var problem: String = inst.call(name)
			if problem == "":
				print("PASS ", f, "::", name)
			else:
				failures += 1
				print("FAIL ", f, "::", name, " -> ", problem)
	print("RAN ", run_count, " tests")
	print("RESULT: ", "ALL PASS" if failures == 0 and run_count > 0 else str(failures) + " FAILED")
	quit(0 if failures == 0 and run_count > 0 else 1)

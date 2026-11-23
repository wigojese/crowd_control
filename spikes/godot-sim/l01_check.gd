extends SceneTree
## STAGE 06 SPIKE. Reproduces the Python model's CC-L01 numbers (expected_python_model.json).
## Run: godot --headless --path spikes/godot-sim --script res://l01_check.gd
## STATUS: written, NOT YET RUN.

const Sim = preload("res://sim_core.gd")
const KEYS := ["arrived", "ontime", "blocked_ticks", "person_ticks", "score", "last_arr", "sign_actions"]


func _case(sim, expected: Dictionary, key: String, sign_state: Array, commands: Array) -> int:
	var got: Dictionary = sim.run(sign_state, commands)
	var want: Dictionary = expected[key]
	var ok := true
	for k in KEYS:
		if int(got[k]) != int(want[k]):
			ok = false
	if ok:
		print("PASS ", key)
		return 0
	print("FAIL ", key)
	for k in KEYS:
		print("   ", k, " got ", got[k], " expected ", int(want[k]))
	return 1


func _init() -> void:
	var expected: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://expected_python_model.json"))
	var sim = Sim.new()
	var fails := 0
	sim.schedule = Sim.l01_schedule()
	# rev0: the level as the spec writes it
	sim.configure(Sim.l01_nodes(), Sim.l01_links())
	sim.bonus = 4.0
	fails += _case(sim, expected, "rev0_no_sign", [], [])
	fails += _case(sim, expected, "rev0_B_S", ["B", "S"], [])
	# R1: Market moved, walkway 0.3/s, bonus 6.0
	var n: Dictionary = Sim.l01_nodes()
	n["C"] = Vector2(270, 115)
	var links: Array = Sim.l01_links()
	for l in links:
		if l[0] == "B" and l[1] == "D":
			l[2] = 0.3
	sim.configure(n, links)
	sim.bonus = 6.0
	fails += _case(sim, expected, "r1_A_N", ["A", "N"], [])
	fails += _case(sim, expected, "r1_A_E", ["A", "E"], [])
	fails += _case(sim, expected, "r1_A_S", ["A", "S"], [])
	fails += _case(sim, expected, "r1_B_E", ["B", "E"], [])
	fails += _case(sim, expected, "r1_B_N", ["B", "N"], [])
	fails += _case(sim, expected, "r1_A_N_rotateE_t0", ["A", "N"], [[0, "ROTATE", "E"]])
	fails += _case(sim, expected, "r1_B_E_moveA_t100", ["B", "E"], [[100, "MOVE", "A"]])
	fails += _case(sim, expected, "r1_A_E_rotateN_t200", ["A", "E"], [[200, "ROTATE", "N"]])
	# determinism: same inputs, same hash
	var h1: int = sim.run(["A", "E"], [])["hash"]
	var h2: int = sim.run(["A", "E"], [])["hash"]
	if h1 == h2:
		print("PASS determinism (hash ", h1, ")")
	else:
		print("FAIL determinism ", h1, " vs ", h2)
		fails += 1
	print("RESULT: ", "ALL PASS" if fails == 0 else str(fails) + " FAILED")
	quit(0 if fails == 0 else 1)

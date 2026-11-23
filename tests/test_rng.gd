extends RefCounted
## Tests T-RNG-1..3. Golden values come from scripts/ref_model.py.


func _golden() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/rng_golden.json"))


func test_rng_matches_golden_sequence() -> String:
	var g := _golden()
	var r := CcRng.new(int(g["seed"]))
	for i in range(g["u32"].size()):
		var got := r.next_u32()
		if got != int(g["u32"][i]):
			return "draw %d: got %d want %d" % [i, got, int(g["u32"][i])]
	return ""


func test_rng_same_seed_same_sequence() -> String:
	var a := CcRng.new(1007)
	var b := CcRng.new(1007)
	for i in range(1000):
		if a.next_u32() != b.next_u32():
			return "diverged at %d" % i
	return ""


func test_rng_streams_match_golden_and_differ() -> String:
	var g := _golden()
	var s := CcRng.stream(int(g["seed"]), "spawn")
	if s.next_u32() != int(g["stream_spawn_first"]):
		return "spawn stream first draw differs from golden"
	var other := CcRng.stream(int(g["seed"]), "route")
	if other.next_u32() == int(g["stream_spawn_first"]):
		return "two named streams gave the same first draw"
	return ""

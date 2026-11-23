extends SceneTree
## STAGE 06 SPIKE. Per-tick cost of the simulation core in GDScript at 50, 200 and 500 walkers
## on graphs of 7, 25 and 50 nodes. CPU only, headless: it measures game LOGIC, not rendering.
## Run: godot --headless --path spikes/godot-sim --script res://bench.gd
## STATUS: written, NOT YET RUN. Numbers must come from a real run; none are claimed here.

const Sim = preload("res://sim_core.gd")


func _grid(rows: int, cols: int) -> Array:
	var nodes := {}
	var links := []
	for r in range(rows):
		for c in range(cols):
			var idx := r * cols + c
			nodes["n%d" % idx] = Vector2(c * 90, r * 90)
	var k := 0
	for r in range(rows):
		for c in range(cols):
			var idx := r * cols + c
			var rate := 1.2 if k % 7 == 3 else 3.0
			if c < cols - 1:
				links.append(["n%d" % idx, "n%d" % (idx + 1), rate])
				k += 1
			if r < rows - 1:
				links.append(["n%d" % idx, "n%d" % (idx + cols), rate])
				k += 1
	return [nodes, links]


func _schedule(nn: int, nw: int, node_ids: Array) -> Array:
	var sched := []
	var seed_v := 1007
	var groups := nw / 10
	for g in range(groups):
		seed_v = (seed_v * 1103515245 + 12345) & 0x7fffffff
		var dest: String
		var origin: String
		if nn == 7:
			origin = "A"
			dest = "F" if g % 2 == 0 else "G"
		else:
			origin = node_ids[0]
			dest = node_ids[1 + seed_v % (node_ids.size() - 1)]
		sched.append({"tick": g * 4, "origin": origin, "dest": dest, "mix": [["C", 5], ["F", 3], ["I", 2]]})
	return sched


func _pct(a: Array, p: float) -> float:
	var s := a.duplicate()
	s.sort()
	return s[int(p * (s.size() - 1))]


func _bench(nn: int, nw: int) -> Dictionary:
	var sim = Sim.new()
	var node_ids: Array
	if nn == 7:
		sim.configure(Sim.l01_nodes(), Sim.l01_links())
		node_ids = Sim.l01_nodes().keys()
	else:
		var g: Array = _grid(5, nn / 5)
		sim.configure(g[0], g[1])
		node_ids = g[0].keys()
		node_ids.sort()
	sim.schedule = _schedule(nn, nw, node_ids)
	var mem0 := OS.get_static_memory_usage()
	sim.reset([], [])
	var times := []
	for i in range(Sim.TICKS):
		var t0 := Time.get_ticks_usec()
		sim.step()
		times.append((Time.get_ticks_usec() - t0) / 1000.0)
	var res: Dictionary = sim.result()
	var mem1 := OS.get_static_memory_usage()
	var sum := 0.0
	for x in times:
		sum += x
	# determinism: a second identical run must give the same hash
	var again: Dictionary = sim.run([], [])
	return {"nodes": nn, "walkers": nw, "p50_ms": _pct(times, 0.5), "p95_ms": _pct(times, 0.95),
		"p99_ms": _pct(times, 0.99), "max_ms": _pct(times, 1.0), "mean_ms": sum / times.size(),
		"total_ms": sum, "arrived": res["arrived"], "static_mem_delta_mb": float(mem1 - mem0) / 1048576.0,
		"deterministic": int(res["hash"]) == int(again["hash"])}


func _init() -> void:
	var rows := []
	for cfg in [[7, 50], [7, 200], [7, 500], [25, 50], [25, 200], [25, 500], [50, 50], [50, 200], [50, 500]]:
		var r: Dictionary = _bench(cfg[0], cfg[1])
		rows.append(r)
		print("nodes %2d walkers %3d | p50 %.3f p95 %.3f p99 %.3f max %.3f ms | mean %.3f | arrived %d | mem +%.1f MB | det %s" % [
			r["nodes"], r["walkers"], r["p50_ms"], r["p95_ms"], r["p99_ms"], r["max_ms"], r["mean_ms"], r["arrived"],
			r["static_mem_delta_mb"], str(r["deterministic"])])
	var f := FileAccess.open("user://bench_out.json", FileAccess.WRITE)
	f.store_string(JSON.stringify({"godot": Engine.get_version_info(), "rows": rows}, "  "))
	f.close()
	print("written: ", ProjectSettings.globalize_path("user://bench_out.json"))
	quit(0)

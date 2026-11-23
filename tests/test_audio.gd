extends RefCounted
## Tests T-AUD-1..5. The scheduler must reproduce scripts/ref_audio.py on real traces and respect the limits.


func _map() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/audio_map.json"))


func _golden() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/audio_golden.json"))


func _events(lines: Array) -> Array:
	var out := []
	for ln in lines:
		var p: PackedStringArray = String(ln).split("|", true, 3)
		var f := {}
		for kv in p[3].split(";"):
			var i := kv.find("=")
			if i > 0:
				f[kv.substr(0, i)] = kv.substr(i + 1)
		out.append({"t_ms": int(p[0]) * 50, "type": p[2], "f": f})
	return out


func test_plays_match_reference_on_real_traces() -> String:
	var m := _map()
	for name in _golden().keys():
		var g: Dictionary = _golden()[name]
		var got := CcAudioScheduler.schedule(_events(g["lines"]), m["defaults"], g["passed"], m)
		var want: Array = g["plays"]
		if (got["plays"] as Array).size() != want.size():
			return "%s: %d plays, want %d" % [name, (got["plays"] as Array).size(), want.size()]
		for i in range(want.size()):
			var a: Dictionary = got["plays"][i]
			var same: bool = a["cue"] == want[i]["cue"] and int(a["t_ms"]) == int(want[i]["t_ms"])
			if not same or int(a["pitch"]) != int(want[i]["pitch"]):
				return "%s play %d differs: %s" % [name, i, str(a)]
	return ""


func test_master_zero_is_silent_and_sliders_are_independent() -> String:
	var m := _map()
	var g: Dictionary = _golden()["A/E"]
	var ev := _events(g["lines"])
	var muted: Dictionary = (m["defaults"] as Dictionary).duplicate()
	muted["master"] = 0.0
	if not (CcAudioScheduler.schedule(ev, muted, true, m)["plays"] as Array).is_empty():
		return "master 0 still plays"
	var nofx: Dictionary = (m["defaults"] as Dictionary).duplicate()
	nofx["effects"] = 0.0
	var r := CcAudioScheduler.schedule(ev, nofx, true, m)
	if not (r["plays"] as Array).is_empty() or (r["bed"] as Array).is_empty():
		return "effects 0 should silence effects but keep the bed"
	return ""


func test_fifty_walkers_do_not_become_noise() -> String:
	var m := _map()
	var ev := []
	for wk in range(50):
		var t0 := wk * 160
		ev.append({"t_ms": t0, "type": "DECISION", "f": {"walker": str(wk), "reason": "sign_flipped"}})
		ev.append({"t_ms": t0 + 10, "type": "QUEUE_JOINED", "f": {"edge": "A>B", "position": str(3 + wk % 3)}})
		ev.append({"t_ms": t0 + 20, "type": "EDGE_ENTERED", "f": {"edge": "A>B"}})
		ev.append({"t_ms": t0 + 2001 + wk * 30, "type": "WALKER_ARRIVED", "f": {"on_time": "1"}})
	ev.sort_custom(func(a, b): return int(a["t_ms"]) < int(b["t_ms"]))
	var plays: Array = CcAudioScheduler.schedule(ev, m["defaults"], true, m)["plays"]
	var cap: int = int(m["limits"]["max_triggers_per_second"])
	for p in plays:
		var n := 0
		for q in plays:
			if int(q["t_ms"]) >= int(p["t_ms"]) and int(q["t_ms"]) < int(p["t_ms"]) + 1000:
				n += 1
		if n > cap:
			return "%d triggers in one second (cap %d)" % [n, cap]
	return "" if plays.size() * 2 < ev.size() else "too many sounds: %d for %d events" % [plays.size(), ev.size()]


func test_every_critical_cue_has_a_visual_equivalent() -> String:
	var m := _map()
	var vis = JSON.parse_string(FileAccess.get_file_as_string("res://data/visual_cues.json"))
	for k in (m["cues"] as Dictionary).keys():
		if m["cues"][k]["critical"] and not (vis["visuals"] as Dictionary).has(m["cues"][k]["visual"]):
			return "critical cue %s has no visual equivalent" % k
	return ""

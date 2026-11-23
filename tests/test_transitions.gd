extends RefCounted
## Tests T-TR-1..7. Same rules as scripts/ref_transitions.py on data/transitions.json.

const FRACS := [0.0, 0.25, 0.5, 0.75, 0.99]


func _data() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/transitions.json"))


func _find(d: Dictionary, id: String) -> Dictionary:
	for t in d["transitions"]:
		if t["id"] == id:
			return t
	return {}


func test_six_transitions_run_to_completion_once() -> String:
	var d := _data()
	if (d["transitions"] as Array).size() != 6:
		return "expected six transitions"
	for def in d["transitions"]:
		var tr := CcTransition.new(def, d)
		tr.start()
		var n := 0
		while tr.state == "RUNNING" and n < 1000:
			tr.update(10.0)
			n += 1
		if tr.state != "DONE" or tr.end_calls != ["completed"]:
			return "%s did not complete once" % def["id"]
	return ""


func test_cancel_skip_and_interrupt_at_every_progress_point() -> String:
	var d := _data()
	for def in d["transitions"]:
		var base_events: Array = []
		var first := true
		for how in ["touch", "app_background", "app_interrupt", "skip"]:
			for frac in FRACS:
				var tr := CcTransition.new(def, d)
				tr.start()
				tr.update(frac * float(def["duration_ms"]))
				var before := tr.values()
				if how == "skip":
					tr.skip()
					tr.skip()
					tr.update(float(d["skip_settle_ms"]))
					tr.update(500.0)
				else:
					tr.cancel(how)
					tr.cancel(how)
					tr.skip()
					tr.update(500.0)
					if str(tr.values()) != str(before):
						return "%s: frozen values changed after %s at %f" % [def["id"], how, frac]
				if first:
					base_events = tr.events
					first = false
				if tr.events != base_events:
					return "%s: game-state events differ at %s %f" % [def["id"], how, frac]
				if tr.end_calls.size() != 1:
					return "%s: %d on_end calls" % [def["id"], tr.end_calls.size()]
	return ""


func test_skip_and_reduced_motion_limits() -> String:
	var d := _data()
	if float(d["skip_settle_ms"]) > 150.0 or float(d["reduced_motion_ms"]) > 150.0:
		return "skip or reduced motion over 150 ms"
	for def in d["transitions"]:
		var r := CcTransition.new(def, d, true)
		r.start()
		if r.state != "DONE":
			return "%s: reduced motion did not end at once" % def["id"]
	return ""


func test_sign_drop_bounce_is_restrained() -> String:
	var d := _data()
	var tr := CcTransition.new(_find(d, "sign_drops"), d)
	tr.start()
	if absf(float(tr.values()["sign_scale"]) - 1.08) > 0.000001 or not tr.hooks_fired.has("haptic.sign_drop"):
		return "first frame is not the lifted sign with the haptic"
	var lowest := 9.0
	for i in range(170):
		tr.update(1.0)
		lowest = minf(lowest, float(tr.values()["sign_scale"]))
	if lowest < 0.99 or absf(float(tr.values()["sign_scale"]) - 1.0) > 0.000001:
		return "bounce too deep or not settled: %f" % lowest
	return ""


func test_paper_unfolds_readable_by_250ms_and_labels_after_geometry() -> String:
	var d := _data()
	var tr := CcTransition.new(_find(d, "paper_unfolds"), d)
	tr.start()
	tr.update(200.0)
	if float(tr.values()["labels_alpha"]) != 0.0:
		return "labels appeared before the geometry finished"
	tr.update(50.0)
	return "" if float(tr.values()["streets_alpha"]) >= 0.99 else "geometry not visible by 250 ms"


func test_crossfade_has_no_flash_and_result_shows_at_start() -> String:
	var d := _data()
	var tr := CcTransition.new(_find(d, "district_to_diagram"), d)
	tr.start()
	for i in range(210):
		tr.update(1.0)
		var v := tr.values()
		if absf(float(v["agents_alpha"]) + float(v["ribbons_alpha"]) - 1.0) > 0.000001:
			return "total opacity left 1 at %d ms" % i
	var pb := CcTransition.new(_find(d, "outcome_pullback"), d)
	pb.start()
	var rw := CcTransition.new(_find(d, "ghosted_rewind"), d)
	rw.start()
	if pb.events != ["result_shown"] or rw.events != ["reset_run"]:
		return "result or reset not fired at start"
	return ""


func test_auto_camera_speed_limit() -> String:
	var d := _data()
	var limit: float = float(d["max_auto_translation_viewport_widths_per_s"]) * float(d["viewport_width_px"])
	for def in d["transitions"]:
		var cam: Dictionary = {}
		var zoom := 1.0
		for tr in def["tracks"]:
			if tr["kind"] != "scalar" and cam.is_empty():
				cam = tr
			if tr["name"] == "cam_zoom":
				zoom = maxf(float(tr["from"]), float(tr["to"]))
		if cam.is_empty():
			continue
		var dist := 0.0
		if cam["kind"] == "vec2":
			dist = Vector2(cam["from"][0], cam["from"][1]).distance_to(Vector2(cam["to"][0], cam["to"][1]))
		else:
			var p: Array = cam["points"]
			for i in range(p.size() - 1):
				dist += Vector2(p[i][0], p[i][1]).distance_to(Vector2(p[i + 1][0], p[i + 1][1]))
		var avg: float = dist * zoom / (float(cam["dur_ms"]) / 1000.0)
		if avg > limit:
			return "%s: average camera speed %f over %f" % [def["id"], avg, limit]
	return ""


func test_follow_ink_keeps_the_sign_visible() -> String:
	var d := _data()
	var def := _find(d, "consequence_follows_ink")
	var tr := CcTransition.new(def, d)
	tr.start()
	for i in range(int(def["duration_ms"])):
		tr.update(1.0)
		var v := tr.values()
		var c: Vector2 = v["cam_path"]
		var sy := (50.0 - c.y) * float(v["cam_zoom"]) + 844.0 / 2.0
		if sy - 20.0 < 118.0 or sy + 20.0 > 844.0 - 146.0:
			return "sign left the free band at %d ms (y=%f)" % [i, sy]
	return ""

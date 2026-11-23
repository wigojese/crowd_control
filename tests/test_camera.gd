extends RefCounted
## Tests T-CAM-1..9. Same checks as scripts/ref_camera.py; golden numbers in tests/fixtures/camera_golden.json.


func _golden() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/camera_golden.json"))


func _path() -> CcCameraPath:
	var pts: Array = [Vector2(180, 50), Vector2(92, 145), Vector2(120, 286), Vector2(106, 470), Vector2(266, 475)]
	return CcCameraPath.new(pts)


func test_anchor_survives_pinch_within_2px() -> String:
	var tf := CcCameraTransform.new()
	var worst := 0.0
	for i in range(200):
		var anchor := Vector2(fposmod(i * 37.3, 390.0), 130.0 + fposmod(i * 91.7, 600.0))
		var w0 := tf.s2w(anchor)
		tf.zoom_about(anchor, 0.65 + fposmod(i * 0.173, 2.15))
		worst = maxf(worst, tf.w2s(w0).distance_to(anchor))
	return "" if worst < 0.01 else "anchor moved %f px" % worst


func test_transform_inverse_and_golden() -> String:
	var tf := CcCameraTransform.new()
	tf.center = Vector2(100, 200)
	tf.zoom = 1.7
	tf.viewport = Vector2(320, 568)
	tf.safe_offset = Vector2(3, 11)
	var p := Vector2(55.5, 321.25)
	if tf.s2w(tf.w2s(p)).distance_to(p) > 0.0001:
		return "inverse failed"
	var g: Array = _golden()["w2s"]
	return "" if tf.w2s(p).distance_to(Vector2(g[0], g[1])) < 0.0001 else "differs from golden"


func test_path_matches_golden_and_spacing() -> String:
	var path := _path()
	var g := _golden()
	if absf(path.length - float(g["path_length"])) > 0.001:
		return "length %f want %f" % [path.length, float(g["path_length"])]
	if path.max_spacing() > 5.0:
		return "spacing over 5"
	var fr := [0.0, 0.25, 0.5, 0.75, 1.0]
	for i in range(5):
		var want: Array = g["path_points"][i]
		if path.point_at(fr[i] * path.length).distance_to(Vector2(want[0], want[1])) > 0.001:
			return "point %d differs from golden" % i
	return ""


func test_scrub_and_inertia_rules() -> String:
	if absf(CcCameraPath.scrub_delta(100.0, 1.0) + 85.0) > 0.0001:
		return "scrub gain wrong"
	if absf(CcCameraPath.inertia_velocity(100.0, 0.5, 844.0, 1.0) - 100.0 * exp(-3.0)) > 0.0001:
		return "inertia decay wrong"
	if absf(CcCameraPath.inertia_velocity(1000000.0, 0.0, 844.0, 1.0) - 1.6 * 844.0) > 0.001:
		return "inertia cap wrong"
	return ""


func test_zoom_hysteresis_has_no_flicker() -> String:
	for centre in [1.75, 0.85]:
		var band := CcZoomBands.DISTRICT
		var changes := 0
		for i in range(400):
			var nb := CcZoomBands.update(band, centre + 0.02 * sin(float(i)))
			if nb != band:
				changes += 1
			band = nb
		if changes > 1:
			return "%d band changes around %f" % [changes, centre]
	if CcZoomBands.update(CcZoomBands.CITY, 2.0) != CcZoomBands.STREET:
		return "jump 0.7 to 2.0 did not reach STREET"
	return ""


func test_lod_plan_keeps_counts_exact_and_hides_nothing() -> String:
	var walkers := []
	for i in range(20):
		walkers.append({"id": i, "active": i % 5 != 0})
	var labels := []
	for i in range(12):
		labels.append({"id": "n%d" % i, "priority": i % 4})
	var snap := {"walkers": walkers, "streets": ["A|B", "A|C", "B|C"], "flux": {"A|B#F": 7},
		"queues": {}, "labels": labels}
	for band in [CcZoomBands.CITY, CcZoomBands.DISTRICT, CcZoomBands.STREET]:
		var pl := CcZoomBands.lod_plan(band, snap)
		var ids: Array = pl["agents"]
		var seen := {}
		for id in ids:
			if seen.has(id):
				return "duplicate agent %s in %s" % [str(id), band]
			seen[id] = true
		if int(pl["people_represented"]) != 16 or (pl["streets_visible"] as Array).size() != 3:
			return "count or street lost in " + band
		if (pl["labels"] as Array).size() > int(CcZoomBands.LABEL_CAP[band]):
			return "too many labels in " + band
	return ""


func test_flux_window_and_badges() -> String:
	var ev := [[10, "A|B", "F"], [15, "A|B", "F"], [30, "A|C", "G"], [50, "A|B", "F"]]
	if str(CcZoomBands.flux_window(ev, 35)) != str({"A|C#G": 1}):
		return "window at 35 wrong: " + str(CcZoomBands.flux_window(ev, 35))
	return "" if str(CcZoomBands.cluster_badges({"x": 5, "y": 3})) == str({"x": 5}) else "badge rule wrong"


func test_director_touch_wins_and_freezes() -> String:
	var d := CcCameraDirector.new(CcCameraTransform.new())
	d.request_focus("SIGN_FOCUS", "DECORATIVE", Vector2(180, 60), 1.8, 1.0)
	d.update(0.5)
	var mid_center := d.tf.center
	var mid_zoom := d.tf.zoom
	if d.request_focus("OVERVIEW", "DECORATIVE", Vector2(181, 262), 1.0, 1.0, "queue"):
		return "equal priority queue request was accepted while busy"
	d.touch_begin()
	if d.tf.center != mid_center or d.tf.zoom != mid_zoom or d.state != "USER_PAN":
		return "touch did not freeze the camera"
	if d.request_focus("SIGN_FOCUS", "USER", Vector2(180, 60), 1.8, 0.4):
		return "Return to sign accepted while a finger is down"
	d.touch_end()
	return "" if d.request_focus("SIGN_FOCUS", "USER", Vector2(180, 60), 1.8, 0.4) else "refused after finger lifted"


func test_director_cancel_at_each_progress_and_reduced_motion() -> String:
	for frac in [0.0, 0.25, 0.5, 0.75, 0.99]:
		var d := CcCameraDirector.new(CcCameraTransform.new())
		d.request_focus("SIGN_FOCUS", "USER", Vector2(180, 60), 1.8, 1.0)
		d.update(frac)
		var c := d.tf.center
		var z := d.tf.zoom
		d.touch_begin()
		if d.tf.center != c or d.tf.zoom != z or not d.anim.is_empty():
			return "cancel at %f moved the camera" % frac
	var r := CcCameraDirector.new(CcCameraTransform.new(), true)
	r.request_focus("SIGN_FOCUS", "USER", Vector2(180, 60), 1.8, 1.0)
	var jumped: bool = r.state == "REDUCED_MOTION" and r.tf.zoom == 1.8 and r.anim.is_empty()
	return "" if jumped else "reduced motion did not jump"

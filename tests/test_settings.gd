extends RefCounted
## Tests T-SET-1..2. Settings sanitising and the left/right dock layout, against cases from scripts/ref_settings.py.


func _cases() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/settings_cases.json"))


func test_sanitize_cases() -> String:
	var schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/settings_schema.json"))
	for c in _cases()["sanitize"]:
		var got := CcSettings.sanitize(c["in"], schema)
		if str(got) != str(c["out"]):
			# float printing can differ in form; compare the values key by key
			for k in (c["out"] as Dictionary).keys():
				if str(got[k]) != str(c["out"][k]) and absf(float(got[k]) - float(c["out"][k])) > 0.000001:
					return "key %s: got %s want %s" % [k, str(got[k]), str(c["out"][k])]
	return ""


func test_dock_layout_cases() -> String:
	for c in _cases()["dock"]:
		var got := CcDockLayout.layout(c["left"], c["larger"], Vector2(c["vp"][0], c["vp"][1]), int(c["inset"]))
		for k in (c["out"] as Dictionary).keys():
			for i in range(4):
				if int(got[k][i]) != int(c["out"][k][i]):
					return "%s %s differs at %d: %s vs %s" % [str(c["vp"]), k, i, str(got[k]), str(c["out"][k])]
	return ""

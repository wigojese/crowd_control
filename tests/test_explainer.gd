extends RefCounted
## Tests T-EXP-1..4. The explainer must reproduce the texts of scripts/ref_explain.py on real traces and must
## never cite an event that did not happen.


func _cases() -> Array:
	return JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/explainer_cases.json"))


func test_texts_match_reference() -> String:
	for c in _cases():
		var got := CcExplainer.explain(c["lines"], c["result"], c["baseline"], c["replay"], c["names"])
		if got.size() != (c["expect"] as Array).size():
			return "%s: %d claims, want %d" % [c["id"], got.size(), (c["expect"] as Array).size()]
		for i in range(got.size()):
			if got[i]["text"] != c["expect"][i]["text"] or got[i]["kind"] != c["expect"][i]["kind"]:
				return "%s claim %d: got '%s' want '%s'" % [c["id"], i, got[i]["text"], c["expect"][i]["text"]]
	return ""


func test_no_helped_or_hurt_without_an_executed_baseline() -> String:
	for c in _cases():
		if c["baseline"] == null:
			for cl in CcExplainer.explain(c["lines"], c["result"], null, c["replay"], c["names"]):
				if cl["id"] == "material":
					return "comparison claimed without a baseline run"
	return ""


func test_removing_sign_events_removes_the_reroute_claim() -> String:
	for c in _cases():
		if c["id"] == "A/E":
			var kept := []
			for l in c["lines"]:
				if not String(l).contains("reason=sign_flipped"):
					kept.append(l)
			for cl in CcExplainer.explain(kept, c["result"], c["baseline"], c["replay"], c["names"]):
				if cl["id"] == "reroute" and cl["kind"] != "NO_REROUTE":
					return "reroute claimed after its events were removed"
	return ""


func test_copy_has_no_counterfactual_or_stereotype_phrases() -> String:
	var banned := ["would have", "if you had", "could have", "should have", "lazy", "stupid"]
	for c in _cases():
		for cl in CcExplainer.explain(c["lines"], c["result"], c["baseline"], c["replay"], c["names"]):
			for b in banned:
				if String(cl["text"]).contains(b):
					return "banned phrase '%s' in '%s'" % [b, cl["text"]]
	return ""

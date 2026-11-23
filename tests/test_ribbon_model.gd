extends RefCounted
## Tests T-RIB-1..3. Ribbons must never misrepresent flow.


func _tokens() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/art_tokens.json"))


func test_zero_flow_draws_nothing_and_one_walker_draws_the_minimum() -> String:
	var t := _tokens()
	if CcRibbonModel.width(0, t) != 0.0:
		return "zero count drew a ribbon"
	if absf(CcRibbonModel.width(1, t) - float(t["geometry"]["min_ribbon_px"])) > 0.0001:
		return "one walker is not the minimum width"
	return ""


func test_width_is_monotonic_and_capped() -> String:
	var t := _tokens()
	var prev := 0.0
	for n in range(0, 200):
		var w := CcRibbonModel.width(n, t)
		if w < prev - 0.000001 or w > float(t["geometry"]["max_ribbon_px"]) + 0.000001:
			return "width rule broken at %d" % n
		prev = w
	return ""


func test_counts_come_from_edge_entered_only() -> String:
	var spawn := "3|1|WALKER_SPAWNED|destination=F;origin=A;walker=3"
	var lines := ["0|0|EDGE_ENTERED|edge=A>B;tokens_after=0;walker=1",
		"3|0|EDGE_ENTERED|edge=B>A;tokens_after=0;walker=2",
		spawn, "4|0|EDGE_ENTERED|edge=A>C;tokens_after=0;walker=3"]
	var c := CcRibbonModel.counts_from_event_lines(lines)
	return "" if str(c) == str({"A|B": 2, "A|C": 1}) else str(c)

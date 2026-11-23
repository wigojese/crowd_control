extends RefCounted
## Tests T-EV-1..4. Schema checks on the event log.


func _schema() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))["events"]


func test_unknown_event_type_is_rejected() -> String:
	var l := CcEventLog.new(_schema())
	return "" if l.add(0, "MADE_UP", {})["error"] == "unknown_type" else "accepted unknown type"


func test_missing_required_field_is_rejected() -> String:
	var l := CcEventLog.new(_schema())
	var r := l.add(0, "WALKER_ARRIVED", {"walker": 1})
	return "" if r["error"] == "missing_field" else "accepted incomplete event"


func test_tick_cannot_go_back() -> String:
	var l := CcEventLog.new(_schema())
	l.add(5, "RUN_ENDED", {"reason": "x"})
	return "" if l.add(4, "RUN_ENDED", {"reason": "x"})["error"] == "tick_went_back" else "tick went back"


func test_canonical_line_format() -> String:
	var l := CcEventLog.new(_schema())
	l.add(3, "SIGN_ROTATED", {"lock_until": 83, "heading": "E"})
	return "" if l.lines[0] == "3|0|SIGN_ROTATED|heading=E;lock_until=83" else l.lines[0]

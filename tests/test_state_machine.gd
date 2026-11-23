extends RefCounted
## Tests T-SM-1..4. Invalid and duplicate transitions must be caught and must not change state.


func _def() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/boot_states.json"))


func test_valid_sequence_reaches_ended() -> String:
	var m := CcStateMachine.new()
	if not m.build(_def())["ok"]:
		return "build failed"
	for ev in ["BOOT_COMPLETE", "RUN", "PAUSE", "RESUME", "FINISH"]:
		if not m.fire(ev)["ok"]:
			return "event %s rejected" % ev
	return "" if m.current == "ENDED" else "ended in " + m.current


func test_invalid_transition_is_rejected_and_state_kept() -> String:
	var m := CcStateMachine.new()
	m.build(_def())
	var r := m.fire("PAUSE")  # not allowed from BOOT
	if r["ok"] or r["error"] != "no_transition":
		return "PAUSE from BOOT was not rejected as no_transition"
	return "" if m.current == "BOOT" else "state changed to " + m.current


func test_unknown_event_is_rejected() -> String:
	var m := CcStateMachine.new()
	m.build(_def())
	return "" if m.fire("NOPE")["error"] == "unknown_event" else "unknown event not reported"


func test_duplicate_transition_in_table_is_caught() -> String:
	var d := _def()
	d["transitions"].append({"from": "BOOT", "event": "BOOT_COMPLETE", "to": "RUNNING"})
	var r := CcStateMachine.new().build(d)
	return "" if r["error"] == "duplicate_transition" else "got error '%s'" % r["error"]


func test_double_fire_is_rejected() -> String:
	var m := CcStateMachine.new()
	m.build(_def())
	m.fire("BOOT_COMPLETE")
	var again := m.fire("BOOT_COMPLETE")  # READY has no BOOT_COMPLETE
	return "" if not again["ok"] else "second BOOT_COMPLETE was accepted"

class_name CcStateMachine
extends RefCounted
## Table-driven state machine. The table is data (data/boot_states.json).
## Build errors: duplicate_transition, unknown_state, bad_initial. Fire errors: unknown_event, no_transition.
## An invalid or duplicate transition never changes state and always reports why.

var current: String = ""
var _initial: String = ""
var _states: Dictionary = {}
var _table: Dictionary = {}  # "FROM|EVENT" -> to
var _events: Dictionary = {}


## Returns {"ok": bool, "error": String}. On error the machine is unusable.
func build(def: Dictionary) -> Dictionary:
	_states.clear()
	_table.clear()
	_events.clear()
	for s in def.get("states", []):
		_states[String(s)] = true
	_initial = String(def.get("initial", ""))
	if not _states.has(_initial):
		return {"ok": false, "error": "bad_initial"}
	for t in def.get("transitions", []):
		var from_s := String(t.get("from", ""))
		var to_s := String(t.get("to", ""))
		var ev := String(t.get("event", ""))
		if not _states.has(from_s) or not _states.has(to_s):
			return {"ok": false, "error": "unknown_state"}
		var key := from_s + "|" + ev
		if _table.has(key):
			return {"ok": false, "error": "duplicate_transition"}
		_table[key] = to_s
		_events[ev] = true
	current = _initial
	return {"ok": true, "error": ""}


## Returns {"ok": bool, "error": String, "from": String, "to": String}.
func fire(ev: String) -> Dictionary:
	var from_s := current
	if not _events.has(ev):
		return {"ok": false, "error": "unknown_event", "from": from_s, "to": from_s}
	var key := from_s + "|" + ev
	if not _table.has(key):
		return {"ok": false, "error": "no_transition", "from": from_s, "to": from_s}
	current = _table[key]
	return {"ok": true, "error": "", "from": from_s, "to": current}

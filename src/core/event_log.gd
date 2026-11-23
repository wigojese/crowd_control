class_name CcEventLog
extends RefCounted
## Append-only simulation event log. Only event types listed in data/events.schema.json, with all
## required fields, are accepted. The log hash (FNV-1a 32) is the equality check for replays.
## Canonical line: "tick|seq|TYPE|k1=v1;k2=v2" with keys sorted. Fields must be ints or strings.

var _required: Dictionary = {}
var lines: Array[String] = []
var _tick: int = -1
var _seq: int = 0


## schema_events is the "events" dictionary of data/events.schema.json.
func _init(schema_events: Dictionary = {}) -> void:
	for k in schema_events.keys():
		_required[String(k)] = schema_events[k]


## Returns {"ok": bool, "error": String}. Errors: unknown_type, missing_field, bad_value_type, tick_went_back.
func add(tick: int, type: String, fields: Dictionary) -> Dictionary:
	if not _required.has(type):
		return {"ok": false, "error": "unknown_type"}
	for f in _required[type]:
		if not fields.has(f):
			return {"ok": false, "error": "missing_field"}
	if tick < _tick:
		return {"ok": false, "error": "tick_went_back"}
	if tick != _tick:
		_tick = tick
		_seq = 0
	var keys: Array = fields.keys()
	keys.sort()
	var parts: Array[String] = []
	for k in keys:
		var v = fields[k]
		if typeof(v) != TYPE_INT and typeof(v) != TYPE_STRING:
			return {"ok": false, "error": "bad_value_type"}
		parts.append("%s=%s" % [k, str(v)])
	lines.append("%d|%d|%s|%s" % [tick, _seq, type, ";".join(parts)])
	_seq += 1
	return {"ok": true, "error": ""}


func hash32() -> int:
	var h: int = 0x811C9DC5
	var text := "\n".join(lines)
	for b in text.to_utf8_buffer():
		h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
	return h

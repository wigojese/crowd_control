class_name CcSettings
extends RefCounted
## Player settings: drops unknown keys, clamps numbers, falls back to the default on a wrong type or an unknown choice.
## Never fails. Port of scripts/ref_settings.py. STATUS: written; NOT RUN (no runnable Godot).
## Nothing here is required to play: sound, haptics and motion are all optional.


## schema: the parsed data/settings_schema.json.
static func sanitize(raw, schema: Dictionary) -> Dictionary:
	var out := {"version": int(schema["version"])}
	for key in (schema["fields"] as Dictionary).keys():
		var f: Dictionary = schema["fields"][key]
		var v = f["default"]
		if raw is Dictionary and (raw as Dictionary).has(key):
			v = raw[key]
		match String(f["type"]):
			"float":
				if (v is float or v is int) and typeof(v) != TYPE_BOOL:
					v = clampf(float(v), float(f["min"]), float(f["max"]))
				else:
					v = float(f["default"])
			"bool":
				if typeof(v) != TYPE_BOOL:
					v = f["default"]
			_:
				if not (f["values"] as Array).has(v):
					v = f["default"]
		out[key] = v
	return out

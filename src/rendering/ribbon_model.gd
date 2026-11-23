class_name CcRibbonModel
extends RefCounted
## Ribbon geometry from counted flow. Width comes only from counted EDGE_ENTERED events, so a ribbon cannot show
## flow that did not happen (Stage 10 rule). Port of scripts/ref_ribbon.py. Pure logic, no drawing.
## STATUS: written; NOT RUN (no runnable Godot).


static func width(count: int, tokens: Dictionary) -> float:
	if count <= 0:
		return 0.0
	var g: Dictionary = tokens["geometry"]
	var k: float = float(tokens["ribbon"]["k_px"])
	var mn: float = float(g["min_ribbon_px"])
	return minf(float(g["max_ribbon_px"]), maxf(mn, mn + k * (sqrt(float(count)) - 1.0)))


## "A>B" and "B>A" are the same street.
static func street_key(edge_id: String) -> String:
	var ids: PackedStringArray = edge_id.split(">")
	ids.sort()
	return "|".join(ids)


## lines: canonical event lines "tick|seq|TYPE|k=v;k=v". Returns {street_key: count}.
static func counts_from_event_lines(lines: Array) -> Dictionary:
	var out := {}
	for ln in lines:
		var parts: PackedStringArray = String(ln).split("|", true, 3)
		if parts.size() == 4 and parts[2] == "EDGE_ENTERED":
			for kv in parts[3].split(";"):
				if kv.begins_with("edge="):
					var k := street_key(kv.substr(5))
					out[k] = int(out.get(k, 0)) + 1
	return out

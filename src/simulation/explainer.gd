class_name CcExplainer
extends RefCounted
## Causal reason selector (Stage 13). Port of scripts/ref_explain.py. Every claim is built from counted events of
## the real run and, for "helped or hurt", from an actually executed NO_SIGN run on the same level and seed.
## A claim that cannot be derived from those is never produced. Pure code, no scene tree.
## STATUS: written; NOT RUN (no runnable Godot). Cases: tests/fixtures/explainer_cases.json.

const MATERIAL_BLOCKED_PCT := 10.0
const HEAD_NAME := {"N": "north", "E": "east", "S": "south", "W": "west"}
const ORDER := ["RESULT", "NO_SIGN", "HELPED", "HURT", "NO_MATERIAL_CHANGE", "NO_REROUTE", "REROUTE",
	"BOTTLENECK", "LATE"]


static func _parse(lines: Array) -> Array:
	var out := []
	for ln in lines:
		var parts: PackedStringArray = String(ln).split("|", true, 3)
		var f := {}
		for kv in parts[3].split(";"):
			var i := kv.find("=")
			if i > 0:
				f[kv.substr(0, i)] = kv.substr(i + 1)
		out.append({"tick": int(parts[0]), "type": parts[2], "f": f})
	return out


static func _street(edge: String, names: Dictionary) -> String:
	var ab: PackedStringArray = edge.split(">")
	return "%s to %s" % [names[ab[0]], names[ab[1]]]


static func _key(edge: String) -> String:
	var ab: PackedStringArray = edge.split(">")
	ab.sort()
	return "|".join(ab)


## result and baseline: {arrived, blocked_ticks}. baseline may be null. replay: {initial_sign, actions}.
static func explain(lines: Array, result: Dictionary, baseline, replay: Dictionary, names: Dictionary,
		goal: int = 18, total: int = 20) -> Array:
	var ev := _parse(lines)
	var claims := []
	var arrivals := []
	var flips := []
	for e in ev:
		if e["type"] == "WALKER_ARRIVED":
			arrivals.append(e)
		elif e["type"] == "DECISION" and e["f"].get("reason", "") == "sign_flipped":
			flips.append(e)
	var reached: bool = int(result["arrived"]) >= goal
	var tail := "reached" if reached else "%d short" % (goal - arrivals.size())
	var head := "%d / %d arrived. Goal %d: %s." % [arrivals.size(), total, goal, tail]
	claims.append({"id": "result", "kind": "RESULT", "text": head})
	var sign: Array = replay.get("initial_sign", [])
	if sign.is_empty() and (replay.get("actions", []) as Array).is_empty():
		claims.append({"id": "no_sign", "kind": "NO_SIGN", "text": "No sign was placed in this round."})
	else:
		var groups := {}
		var walkers := {}
		for e in flips:
			var k: String = "%s|%s|%s" % [e["f"]["node"], e["f"]["chosen_edge"], e["f"]["alt_edge"]]
			if not groups.has(k):
				groups[k] = {}
			groups[k][e["f"]["walker"]] = true
			walkers[e["f"]["walker"]] = true
		var where := "the sign"
		if not sign.is_empty():
			where = "%s (pointing %s)" % [names[sign[0]], HEAD_NAME[sign[1]]]
		if walkers.is_empty():
			var none_text := "Your sign at %s changed no walker's route." % where
			claims.append({"id": "reroute", "kind": "NO_REROUTE", "text": none_text})
		else:
			var best_k := ""
			var best_n := -1
			for k in groups.keys():
				var n: int = (groups[k] as Dictionary).size()
				if n > best_n or (n == best_n and k > best_k):
					best_n = n
					best_k = k
			var parts: PackedStringArray = best_k.split("|")
			var share := "all of them" if best_n == walkers.size() else "%d of them" % best_n
			claims.append({"id": "reroute", "kind": "REROUTE",
				"text": "Your sign at %s changed the route of %d walker%s: %s at %s took %s instead of %s." % [
					where, walkers.size(), "" if walkers.size() == 1 else "s", share, names[parts[0]],
					_street(parts[1], names), _street(parts[2], names)]})
		if baseline != null:
			claims.append(_material(result, baseline, reached, goal))
	var joined := {}
	var wait := {}
	var end_tick := 0
	for e in ev:
		end_tick = maxi(end_tick, int(e["tick"]))
	for e in ev:
		var f: Dictionary = e["f"]
		if e["type"] == "QUEUE_JOINED":
			joined["%s#%s" % [f["walker"], f["edge"]]] = int(e["tick"])
		elif e["type"] == "QUEUE_LEFT":
			joined.erase("%s#%s" % [f["walker"], f["edge"]])
		elif e["type"] == "EDGE_ENTERED":
			var jk := "%s#%s" % [f["walker"], f["edge"]]
			if joined.has(jk):
				var sk := _key(f["edge"])
				wait[sk] = int(wait.get(sk, 0)) + int(e["tick"]) - int(joined[jk])
				joined.erase(jk)
	for jk in joined.keys():
		var sk2 := _key(String(jk).split("#")[1])
		wait[sk2] = int(wait.get(sk2, 0)) + end_tick - int(joined[jk])
	var top_key := ""
	var top_wait := -1
	for k in wait.keys():
		if int(wait[k]) > top_wait or (int(wait[k]) == top_wait and k > top_key):
			top_wait = int(wait[k])
			top_key = k
	if top_wait >= 100:
		var ab: PackedStringArray = top_key.split("|")
		claims.append({"id": "bottleneck", "kind": "BOTTLENECK",
			"text": "Most waiting: %s and %s, %s walker-seconds in queues (all walkers added up)." % [
				names[ab[0]], names[ab[1]], _tenths(top_wait)]})
	var late := 0
	for e in arrivals:
		if e["f"]["on_time"] == "0":
			late += 1
	if late > 0:
		claims.append({"id": "late", "kind": "LATE",
			"text": "%d walker%s arrived after the deadline." % [late, "" if late == 1 else "s"]})
	return claims


static func _material(result: Dictionary, baseline: Dictionary, reached: bool, goal: int) -> Dictionary:
	var got: int = int(result["arrived"])
	var was: int = int(baseline["arrived"])
	var da: int = got - was
	var flip: bool = reached != (was >= goal)
	var blocked_was: int = int(baseline["blocked_ticks"])
	var bp: float = 100.0 * float(int(result["blocked_ticks"]) - blocked_was) / float(maxi(1, blocked_was))
	var lead := "Compared with no sign on the same seed, your sign delivered"
	if da > 0 or (flip and reached):
		var more := " and turned a miss into a pass" if flip else ""
		var more_text := "%s %d more (%d against %d)%s." % [lead, da, got, was, more]
		return {"id": "material", "kind": "HELPED", "text": more_text}
	if da < 0 or (flip and not reached):
		return {"id": "material", "kind": "HURT", "text": "%s %d fewer (%d against %d)." % [lead, -da, got, was]}
	if absf(bp) >= MATERIAL_BLOCKED_PCT:
		var dir := "less" if bp < 0.0 else "more"
		var pct := absf(bp)
		var fmt := "Same arrivals as no sign on the same seed (%d), but %.0f%% %s time spent waiting."
		var text := fmt % [got, pct, dir]
		var kind := "HELPED" if bp < 0.0 else "HURT"
		return {"id": "material", "kind": kind, "text": text}
	var same := "The result matches no sign on the same seed (%d against %d arrived)." % [got, was]
	return {"id": "material", "kind": "NO_MATERIAL_CHANGE", "text": same}


## At most `limit` claims for the result screen, result first.
static func select(claims: Array, limit: int = 3) -> Array:
	var sorted := claims.duplicate()
	sorted.sort_custom(func(a, b): return ORDER.find(a["kind"]) < ORDER.find(b["kind"]))
	return sorted.slice(0, limit)


## Ticks / 20 as seconds with one decimal, rounded half up with integers (float formatting differs from the Python reference).
static func _tenths(ticks: int) -> String:
	var t := (ticks + 1) / 2
	return "%d.%d" % [t / 10, t % 10]

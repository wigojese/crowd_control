class_name CcSimWorld
extends RefCounted
## CC-RULESET-01C simulation (docs/RULES.md). Pure code: no scene tree, no clock, no engine random.
## Port of the Stage 06 spike, driven by a level dictionary and writing schema-checked events.
## STATUS: written; NOT RUN (no runnable Godot). Reference numbers: tests/fixtures/expected_python_model.json.

const DT := 0.05
const REEVAL := 10
const LOOP_PEN := 6.0
const DOT_MIN := 0.65
const LOCK := 80
const HOLD := 10
const S_UNSPAWNED := 0
const S_NEEDS := 1
const S_QUEUED := 2
const S_ON_EDGE := 3
const S_ARRIVED := 4

const PROFILES := {
	"C": {"sign": 0.8, "crowd": 0.35, "speed": 38.0},
	"F": {"sign": 1.0, "crowd": 0.9, "speed": 34.0},
	"I": {"sign": 0.35, "crowd": 0.2, "speed": 42.0},
}
const DIRS := {"N": Vector2(0, -1), "E": Vector2(1, 0), "S": Vector2(0, 1), "W": Vector2(-1, 0)}

var events: CcEventLog
var ticks: int = 640
var deadline_tick: int = 600
var pass_mark: int = 18
var bonus: float = 4.0
var tick: int = 0
var walkers: Array = []
var blocked_total: int = 0
var person_total: int = 0
var sign_actions: int = 0
## The sign: slot, head (heading), active, lock_until, drop_at, pending.
var sign: Dictionary = {}

var _nodes: Dictionary = {}
var _edges: Dictionary = {}
var _edge_ids: Array = []
var _out: Dictionary = {}
var _dist: Dictionary = {}
var _schedule: Array = []
var _tokens: Dictionary = {}
var _fifo: Dictionary = {}
var _cmds: Array = []
var _ci: int = 0
var _schema: Dictionary = {}


func _init(level: Dictionary, event_schema: Dictionary) -> void:
	_schema = event_schema
	ticks = int(level.get("ticks", 640))
	deadline_tick = int(level.get("deadline_tick", 600))
	pass_mark = int(level.get("pass_mark", 18))
	bonus = float(level.get("sign_bonus", 4.0))
	for n in level["nodes"]:
		_nodes[String(n["id"])] = Vector2(float(n["x"]), float(n["y"]))
	for e in level["edges"]:
		var a := String(e["from"])
		var b := String(e["to"])
		var length: float = (_nodes[a] as Vector2).distance_to(_nodes[b])
		_edges[a + ">" + b] = {"from": a, "to": b, "len": length, "rate": float(e["rate"])}
		_edges[b + ">" + a] = {"from": b, "to": a, "len": length, "rate": float(e["rate"])}
	_edge_ids = _edges.keys()
	_edge_ids.sort()
	for n in _nodes.keys():
		_out[n] = []
	for e in _edge_ids:
		_out[_edges[e]["from"]].append(e)
	for n in _nodes.keys():
		_dist[n] = _shortest(n)
	_schedule = level["schedule"]


## Start a round. sign_state is [] or [slot, heading]. commands: [[tick, ordinal, "ROTATE"|"MOVE", arg], ...].
func reset(sign_state: Array, commands: Array) -> void:
	events = CcEventLog.new(_schema)
	walkers = []
	var i := 0
	for s in _schedule:
		var mix: Dictionary = s["mix"]
		var profs: Array = mix.keys()
		for p in _prof_order(profs):
			for k in range(int(mix[p])):
				walkers.append({"id": i, "prof": p, "origin": s["origin"], "dest": s["destination"],
					"spawn": int(s["tick"]), "state": S_UNSPAWNED, "node": "", "edge": "", "edge_t": 0.0,
					"hist": [], "q": "", "lasteval": -99, "arr": -1, "prev": ""})
				i += 1
	_tokens = {}
	_fifo = {}
	for e in _edge_ids:
		_tokens[e] = 1.0
		_fifo[e] = []
	sign = {"slot": "", "head": "", "active": false, "lock_until": -1, "drop_at": -1, "pending": ""}
	if sign_state.size() == 2:
		sign["slot"] = sign_state[0]
		sign["head"] = sign_state[1]
		sign["active"] = true
	_cmds = commands.duplicate()
	_cmds.sort_custom(_cmd_less)
	_ci = 0
	tick = 0
	blocked_total = 0
	person_total = 0
	sign_actions = 0


## Profile order inside a spawn group: C, F, I (as the level lists them in the reference model).
func _prof_order(profs: Array) -> Array:
	var order := []
	for p in ["C", "F", "I"]:
		if profs.has(p):
			order.append(p)
	return order


func _cmd_less(a: Array, b: Array) -> bool:
	if a[0] != b[0]:
		return a[0] < b[0]
	if a[1] != b[1]:
		return a[1] < b[1]
	return str(a[3]) < str(b[3])


func _shortest(src: String) -> Dictionary:
	var d := {}
	for n in _nodes.keys():
		d[n] = 1e18
	d[src] = 0.0
	var done := {}
	while true:
		var u := ""
		var best := 1e18
		for n in _nodes.keys():
			if not done.has(n) and d[n] < best:
				best = d[n]
				u = n
		if u == "":
			break
		done[u] = true
		for e in _out[u]:
			var v: String = _edges[e]["to"]
			var nd: float = best + _edges[e]["len"]
			if nd < d[v]:
				d[v] = nd
	return d


func favoured(slot: String, head: String) -> Array:
	var res := []
	for e in _out[slot]:
		var a: String = _edges[e]["from"]
		var b: String = _edges[e]["to"]
		var u: Vector2 = ((_nodes[b] as Vector2) - (_nodes[a] as Vector2)) / float(_edges[e]["len"])
		if u.dot(DIRS[head]) >= DOT_MIN:
			res.append(e)
	return res


func edge_ids() -> Array:
	return _edge_ids


func node_positions() -> Dictionary:
	return _nodes


func queue_length(e: String) -> int:
	return (_fifo[e] as Array).size()


## Cost of leaving `node` along edge e for walker w. use_sign / use_queue switch a term off to
## find out whether it flipped the choice (DECISION.reason).
func _cost(w: Dictionary, node: String, e: String, use_sign: bool, use_queue: bool) -> float:
	var p: Dictionary = PROFILES[w["prof"]]
	var b: String = _edges[e]["to"]
	var rate: float = _edges[e]["rate"]
	var rem: float = (float(_edges[e]["len"]) + float(_dist[b][w["dest"]])) / float(p["speed"])
	var ahead := 0
	if w["q"] != e:
		ahead = (_fifo[e] as Array).size()
	else:
		for k in range((_fifo[e] as Array).size()):
			if _fifo[e][k][0] == w["id"]:
				ahead = k
				break
	var qw: float = maxf(0.0, float(ahead) + 1.0 - float(_tokens[e])) / rate
	var loop := 0.0
	if (w["hist"] as Array).slice(-3).has(b):
		loop = LOOP_PEN
	var bon := 0.0
	if use_sign and sign["active"] and sign["slot"] == node and favoured(sign["slot"], sign["head"]).has(e):
		bon = bonus
	var crowd: float = float(p["crowd"]) * qw if use_queue else 0.0
	return rem + crowd + loop - float(p["sign"]) * bon


func _choose(w: Dictionary, node: String, use_sign: bool, use_queue: bool) -> Array:
	var best_cost := 0.0
	var best_e := ""
	for e in _out[node]:
		if w["prev"] != "" and _edges[e]["to"] == w["prev"] and (_out[node] as Array).size() > 1:
			continue
		var c := _cost(w, node, e, use_sign, use_queue)
		if best_e == "" or c < best_cost - 1e-12 or (absf(c - best_cost) <= 1e-12 and e < best_e):
			best_cost = c
			best_e = e
	return [best_e, best_cost]


func _emit(type: String, fields: Dictionary) -> void:
	var r := events.add(tick, type, fields)
	assert(r["ok"], "event rejected: " + type + " " + String(r["error"]))


func step() -> void:
	var t := tick
	var changed := false
	# 1. pending drop, then commands
	if sign["pending"] != "" and sign["drop_at"] == t:
		sign["slot"] = sign["pending"]
		sign["active"] = true
		sign["lock_until"] = t + LOCK
		sign["pending"] = ""
		sign["drop_at"] = -1
		changed = true
		_emit("SIGN_DROPPED", {"slot": sign["slot"], "heading": sign["head"], "lock_until": sign["lock_until"]})
	while _ci < _cmds.size() and _cmds[_ci][0] == t:
		var c: Array = _cmds[_ci]
		_ci += 1
		if t < sign["lock_until"] or sign["pending"] != "" or sign["slot"] == "":
			var why := "locked" if t < sign["lock_until"] else ("held" if sign["pending"] != "" else "no_sign_placed")
			_emit("COMMAND_REJECTED", {"command": c[2], "reason": why})
			continue
		if c[2] == "ROTATE":
			sign["head"] = c[3]
			sign["lock_until"] = t + LOCK
			changed = true
			sign_actions += 1
			_emit("COMMAND_ACCEPTED", {"command": "ROTATE", "slot": sign["slot"], "heading": c[3], "ordinal": c[1]})
			_emit("SIGN_ROTATED", {"heading": c[3], "lock_until": sign["lock_until"]})
		elif c[2] == "MOVE" and c[3] != sign["slot"]:
			_emit("COMMAND_ACCEPTED", {"command": "MOVE", "slot": c[3], "heading": sign["head"], "ordinal": c[1]})
			_emit("SIGN_PICKED", {"from_slot": sign["slot"], "heading": sign["head"]})
			sign["pending"] = c[3]
			sign["drop_at"] = t + HOLD
			sign["active"] = false
			changed = true
			sign_actions += 1
	# 2. spawn
	for w in walkers:
		if w["state"] == S_UNSPAWNED and w["spawn"] == t:
			w["state"] = S_NEEDS
			w["node"] = w["origin"]
			_emit("WALKER_SPAWNED", {"walker": w["id"], "profile": w["prof"], "origin": w["origin"],
				"destination": w["dest"], "deadline_tick": deadline_tick})
	# 3. refill
	for e in _edge_ids:
		var r: float = _edges[e]["rate"]
		_tokens[e] = minf(maxf(1.0, r), float(_tokens[e]) + r * DT)
	# 4. decisions
	for w in walkers:
		var due: bool = w["state"] == S_NEEDS or (w["state"] == S_QUEUED and (t - w["lasteval"] >= REEVAL or changed))
		if not due:
			continue
		var node: String = w["node"]
		var pick := _choose(w, node, true, true)
		var best_e: String = pick[0]
		var reason := "lowest_cost"
		var alt := ""
		if (_out[node] as Array).size() == 1:
			reason = "forced_single_exit"
		else:
			var without_sign: String = _choose(w, node, false, true)[0]
			var without_queue: String = _choose(w, node, true, false)[0]
			if without_sign != best_e:
				reason = "sign_flipped"
				alt = without_sign
			elif without_queue != best_e:
				reason = "queue_flipped"
				alt = without_queue
		_emit("DECISION", {"walker": w["id"], "node": node, "chosen_edge": best_e, "reason": reason, "alt_edge": alt,
			"cost_milli": int(round(float(pick[1]) * 1000.0))})
		if w["q"] != best_e:
			if w["q"] != "":
				var kept := []
				for x in _fifo[w["q"]]:
					if x[0] != w["id"]:
						kept.append(x)
				_emit("QUEUE_LEFT", {"walker": w["id"], "edge": w["q"], "position": (_fifo[w["q"]] as Array).size()})
				_fifo[w["q"]] = kept
			_fifo[best_e].append([w["id"], t])
			w["q"] = best_e
			_emit("QUEUE_JOINED", {"walker": w["id"], "edge": best_e, "position": (_fifo[best_e] as Array).size() - 1})
		w["state"] = S_QUEUED
		w["lasteval"] = t
	# 5. service
	var entered := {}
	for e in _edge_ids:
		while _tokens[e] >= 1.0 and (_fifo[e] as Array).size() > 0:
			var head_entry: Array = _fifo[e].pop_front()
			var w2: Dictionary = walkers[head_entry[0]]
			_tokens[e] -= 1.0
			w2["state"] = S_ON_EDGE
			w2["edge"] = e
			w2["edge_t"] = 0.0
			w2["q"] = ""
			w2["hist"].append(w2["node"])
			w2["prev"] = w2["node"]
			entered[w2["id"]] = true
			var left := int(round(float(_tokens[e]) * 1000.0))
			_emit("EDGE_ENTERED", {"walker": w2["id"], "edge": e, "tokens_after": left})
	# 6. movement and arrivals
	for w in walkers:
		if w["state"] == S_ON_EDGE and not entered.has(w["id"]):
			var p: Dictionary = PROFILES[w["prof"]]
			w["edge_t"] += float(p["speed"]) * DT / float(_edges[w["edge"]]["len"])
			if w["edge_t"] >= 1.0:
				var b: String = _edges[w["edge"]]["to"]
				w["node"] = b
				w["edge"] = ""
				_emit("NODE_ARRIVED", {"walker": w["id"], "node": b})
				if b == w["dest"]:
					w["state"] = S_ARRIVED
					w["arr"] = t + 1
					_emit("WALKER_ARRIVED", {"walker": w["id"], "arrival_tick": t + 1,
						"on_time": 1 if t + 1 <= deadline_tick else 0})
				else:
					w["state"] = S_NEEDS
	# 8. metrics
	for w in walkers:
		var s: int = w["state"]
		if s == S_QUEUED or s == S_NEEDS or s == S_ON_EDGE:
			person_total += 1
			if s == S_QUEUED:
				blocked_total += 1
	tick += 1


## Final numbers. Score is rounded half to even, as in docs/RULES.md.
func result() -> Dictionary:
	var arrived := 0
	var ontime := 0
	var last := 0
	for w in walkers:
		if w["state"] == S_ARRIVED:
			arrived += 1
			if w["arr"] <= deadline_tick:
				ontime += 1
			last = maxi(last, int(w["arr"]))
	var dr := float(arrived) / float(maxi(1, walkers.size()))
	var otr := float(ontime) / float(maxi(1, arrived))
	var cs := float(blocked_total) / float(maxi(1, person_total))
	var x := 100.0 * (0.7 * dr + 0.2 * otr + 0.1 * (1.0 - clampf(cs, 0.0, 1.0)))
	return {"arrived": arrived, "ontime": ontime, "blocked_ticks": blocked_total, "person_ticks": person_total,
		"score": _round_even(x), "last_arr": last, "sign_actions": sign_actions}


func _round_even(x: float) -> int:
	var f := floorf(x)
	var diff := x - f
	if diff > 0.5 + 1e-9:
		return int(f) + 1
	if diff < 0.5 - 1e-9:
		return int(f)
	return int(f) if int(f) % 2 == 0 else int(f) + 1


## Run a whole round and close the log. Returns the result plus the event hash.
func run(sign_state: Array, commands: Array) -> Dictionary:
	reset(sign_state, commands)
	for i in range(ticks):
		step()
	var res := result()
	_emit("RUN_ENDED", {"reason": "time_limit"})
	res["hash"] = events.hash32()
	res["passed"] = res["arrived"] >= pass_mark
	return res

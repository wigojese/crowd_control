extends RefCounted
## STAGE 06 SPIKE. Not production code. Implements docs/RULES.md (CC-RULESET-01C) for the
## engine comparison. Mirrors docs/analysis/stage03_numeric_check.py so results can be compared.
## STATUS: written, NOT YET RUN (see docs/ENGINE_DECISION.md).

const DT := 0.05
const TICKS := 640
const DEADLINE_TICK := 600
const REEVAL := 10
const LOOP_PEN := 6.0
const DOT_MIN := 0.65
const LOCK := 80
const HOLD := 10
const UNSPAWNED := 0
const NEEDS := 1
const QUEUED := 2
const ON_EDGE := 3
const ARRIVED := 4

var profiles := {
	"C": {"sign": 0.8, "crowd": 0.35, "speed": 38.0},
	"F": {"sign": 1.0, "crowd": 0.9, "speed": 34.0},
	"I": {"sign": 0.35, "crowd": 0.2, "speed": 42.0},
}
var dirv := {"N": Vector2(0, -1), "E": Vector2(1, 0), "S": Vector2(0, 1), "W": Vector2(-1, 0)}
var bonus := 4.0
var nodes := {}
var edges := {}
var edge_ids := []
var out := {}
var spd := {}
var schedule := []
var n_total := 0

var walkers := []
var tokens := {}
var fifo := {}
var sg := {}
var cmds := []
var ci := 0
var tick := 0
var blocked_total := 0
var person_total := 0
var sign_actions := 0
var hash_acc := 2166136261


static func l01_nodes() -> Dictionary:
	return {"A": Vector2(180, 50), "B": Vector2(92, 145), "C": Vector2(262, 155), "D": Vector2(120, 286),
		"E": Vector2(254, 290), "F": Vector2(106, 470), "G": Vector2(266, 475)}


static func l01_links() -> Array:
	return [["A", "B", 3.0], ["A", "C", 3.0], ["B", "C", 3.0], ["B", "D", 1.6], ["C", "E", 3.0],
		["D", "E", 1.2], ["D", "F", 3.0], ["E", "G", 3.0], ["F", "G", 3.0]]


static func l01_schedule() -> Array:
	return [
		{"tick": 0, "origin": "A", "dest": "F", "mix": [["C", 7], ["F", 3], ["I", 2]]},
		{"tick": 40, "origin": "A", "dest": "G", "mix": [["C", 4], ["F", 3], ["I", 1]]},
	]


func configure(nodes_in: Dictionary, links: Array) -> void:
	nodes = nodes_in.duplicate()
	edges = {}
	for l in links:
		var a: String = l[0]
		var b: String = l[1]
		var r: float = l[2]
		var d: float = (nodes[a] as Vector2).distance_to(nodes[b])
		edges[a + ">" + b] = {"from": a, "to": b, "len": d, "rate": r}
		edges[b + ">" + a] = {"from": b, "to": a, "len": d, "rate": r}
	edge_ids = edges.keys()
	edge_ids.sort()
	out = {}
	for n in nodes.keys():
		out[n] = []
	for e in edge_ids:
		out[edges[e]["from"]].append(e)
	spd = {}
	for n in nodes.keys():
		spd[n] = _dijkstra(n)


func _dijkstra(src: String) -> Dictionary:
	var d := {}
	for n in nodes.keys():
		d[n] = 1e18
	d[src] = 0.0
	var done := {}
	while true:
		var u := ""
		var best := 1e18
		for n in nodes.keys():
			if not done.has(n) and d[n] < best:
				best = d[n]
				u = n
		if u == "":
			break
		done[u] = true
		for e in out[u]:
			var v: String = edges[e]["to"]
			var nd: float = best + edges[e]["len"]
			if nd < d[v]:
				d[v] = nd
	return d


func favoured(node: String, head: String) -> Array:
	var res := []
	for e in out[node]:
		var a: String = edges[e]["from"]
		var b: String = edges[e]["to"]
		var l: float = edges[e]["len"]
		var u: Vector2 = ((nodes[b] as Vector2) - (nodes[a] as Vector2)) / l
		if u.dot(dirv[head]) >= DOT_MIN:
			res.append(e)
	return res


func _make_walkers() -> void:
	walkers = []
	var i := 0
	for s in schedule:
		for pm in s["mix"]:
			for k in range(int(pm[1])):
				walkers.append({"id": i, "prof": pm[0], "origin": s["origin"], "dest": s["dest"], "spawn": s["tick"],
					"state": UNSPAWNED, "node": "", "edge": "", "edge_t": 0.0, "hist": [], "q": "",
					"lasteval": -99, "arr": -1, "prev": ""})
				i += 1
	n_total = i


func _cmd_less(a: Array, b: Array) -> bool:
	if a[0] != b[0]:
		return a[0] < b[0]
	if a[1] != b[1]:
		return a[1] < b[1]
	return str(a[2]) < str(b[2])


func reset(sign_state: Array, commands: Array) -> void:
	_make_walkers()
	tokens = {}
	fifo = {}
	for e in edge_ids:
		tokens[e] = 1.0
		fifo[e] = []
	sg = {"slot": "", "head": "", "active": false, "lock_until": -1, "drop_at": -1, "pending": ""}
	if sign_state.size() == 2:
		sg["slot"] = sign_state[0]
		sg["head"] = sign_state[1]
		sg["active"] = true
	cmds = commands.duplicate()
	cmds.sort_custom(_cmd_less)
	ci = 0
	tick = 0
	blocked_total = 0
	person_total = 0
	sign_actions = 0
	hash_acc = 2166136261


func _h(v: int) -> void:
	hash_acc = ((hash_acc ^ v) * 16777619) & 0xFFFFFFFF


func step() -> void:
	var t := tick
	var changed := false
	# 1. commands and pending drop
	if sg["pending"] != "" and sg["drop_at"] == t:
		sg["slot"] = sg["pending"]
		sg["active"] = true
		sg["lock_until"] = t + LOCK
		sg["pending"] = ""
		sg["drop_at"] = -1
		changed = true
	while ci < cmds.size() and cmds[ci][0] == t:
		var c: Array = cmds[ci]
		ci += 1
		if t < sg["lock_until"] or sg["pending"] != "" or sg["slot"] == "":
			continue
		if c[1] == "ROTATE":
			sg["head"] = c[2]
			sg["lock_until"] = t + LOCK
			changed = true
			sign_actions += 1
		elif c[1] == "MOVE" and c[2] != sg["slot"]:
			sg["pending"] = c[2]
			sg["drop_at"] = t + HOLD
			sg["active"] = false
			changed = true
			sign_actions += 1
	# 2. spawn
	for w in walkers:
		if w["state"] == UNSPAWNED and w["spawn"] == t:
			w["state"] = NEEDS
			w["node"] = w["origin"]
	# 3. refill
	for e in edge_ids:
		var r: float = edges[e]["rate"]
		tokens[e] = minf(maxf(1.0, r), tokens[e] + r * DT)
	# 4. decisions
	for w in walkers:
		var due: bool = w["state"] == NEEDS or (w["state"] == QUEUED and (t - w["lasteval"] >= REEVAL or changed))
		if not due:
			continue
		var p: Dictionary = profiles[w["prof"]]
		var best_cost := 0.0
		var best_e := ""
		var best_set := false
		var node: String = w["node"]
		for e in out[node]:
			var b: String = edges[e]["to"]
			if w["prev"] != "" and b == w["prev"] and out[node].size() > 1:
				continue
			var l: float = edges[e]["len"]
			var rate: float = edges[e]["rate"]
			var rem: float = (l + spd[b][w["dest"]]) / p["speed"]
			var ahead := 0
			if w["q"] != e:
				ahead = fifo[e].size()
			else:
				for k in range(fifo[e].size()):
					if fifo[e][k][0] == w["id"]:
						ahead = k
						break
			var qw: float = maxf(0.0, float(ahead) + 1.0 - tokens[e]) / rate
			var loop := 0.0
			var hist: Array = w["hist"]
			if hist.slice(-3).has(b):
				loop = LOOP_PEN
			var bon := 0.0
			if sg["active"] and sg["slot"] == node and e in favoured(sg["slot"], sg["head"]):
				bon = bonus
			var cost: float = rem + p["crowd"] * qw + loop - p["sign"] * bon
			if not best_set or cost < best_cost - 1e-12 or (absf(cost - best_cost) <= 1e-12 and e < best_e):
				best_cost = cost
				best_e = e
				best_set = true
		if w["q"] != best_e:
			if w["q"] != "":
				var nl := []
				for x in fifo[w["q"]]:
					if x[0] != w["id"]:
						nl.append(x)
				fifo[w["q"]] = nl
			fifo[best_e].append([w["id"], t])
			w["q"] = best_e
		w["state"] = QUEUED
		w["lasteval"] = t
		_h(t)
		_h(int(w["id"]))
		_h(best_e.hash())
	# 5. service
	var entered := {}
	for e in edge_ids:
		while tokens[e] >= 1.0 and fifo[e].size() > 0:
			var head_entry: Array = fifo[e].pop_front()
			var w2: Dictionary = walkers[head_entry[0]]
			tokens[e] -= 1.0
			w2["state"] = ON_EDGE
			w2["edge"] = e
			w2["edge_t"] = 0.0
			w2["q"] = ""
			w2["hist"].append(w2["node"])
			w2["prev"] = w2["node"]
			entered[w2["id"]] = true
	# 6. movement and arrivals
	for w in walkers:
		if w["state"] == ON_EDGE and not entered.has(w["id"]):
			var l2: float = edges[w["edge"]]["len"]
			w["edge_t"] += float(profiles[w["prof"]]["speed"]) * DT / l2
			if w["edge_t"] >= 1.0:
				var b2: String = edges[w["edge"]]["to"]
				w["node"] = b2
				w["edge"] = ""
				if b2 == w["dest"]:
					w["state"] = ARRIVED
					w["arr"] = t + 1
				else:
					w["state"] = NEEDS
	# 8. metrics
	for w in walkers:
		var s: int = w["state"]
		if s == QUEUED or s == NEEDS or s == ON_EDGE:
			person_total += 1
			if s == QUEUED:
				blocked_total += 1
	tick += 1


func _round_even(x: float) -> int:
	var f := floorf(x)
	var diff := x - f
	if diff > 0.5 + 1e-9:
		return int(f) + 1
	if diff < 0.5 - 1e-9:
		return int(f)
	return int(f) if int(f) % 2 == 0 else int(f) + 1


func result() -> Dictionary:
	var arrived := 0
	var ontime := 0
	var last := 0
	for w in walkers:
		if w["state"] == ARRIVED:
			arrived += 1
			if w["arr"] <= DEADLINE_TICK:
				ontime += 1
			last = maxi(last, int(w["arr"]))
	var dr := float(arrived) / float(maxi(1, n_total))
	var otr := float(ontime) / float(maxi(1, arrived))
	var cs := float(blocked_total) / float(maxi(1, person_total))
	var x := 100.0 * (0.7 * dr + 0.2 * otr + 0.1 * (1.0 - clampf(cs, 0.0, 1.0)))
	return {"arrived": arrived, "ontime": ontime, "blocked_ticks": blocked_total, "person_ticks": person_total,
		"score": _round_even(x), "last_arr": last, "sign_actions": sign_actions, "hash": hash_acc}


func run(sign_state: Array, commands: Array) -> Dictionary:
	reset(sign_state, commands)
	for i in range(TICKS):
		step()
	return result()

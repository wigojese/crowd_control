class_name CcGestureRouter
extends RefCounted
## Touch ownership and gesture arbitration (docs/INPUT_SPEC.md sections 5 and 9). Pure logic: takes touch
## events as plain data (screen positions in logical px, times in ms) and returns intents. No scene tree.
## Port of scripts/ref_input.py; both run tests/fixtures/input_cases.json.
## STATUS: written; NOT RUN (no runnable Godot). Thresholds come from data/input_tokens.json, nowhere else.
##
## scene = {mode, viewport:[w,h], tray:[x,y], sign:{placed,locked,held,pos,slot}, rings:[{id,pos}], buttons:[{id,rect}]}
## Intent = Dictionary with "type" (PRESS_FEEDBACK, UI, SIGN_TURN, SIGN_PICKUP, SIGN_DRAG_MOVE, SIGN_DROP,
## SIGN_MOVE_TAP, SNAPBACK, LOCK_REJECT, PAUSED_MESSAGE, INSPECT, PAN, PINCH, SIGN_ACTION_CANCELLED, CANCELLED).

var scene: Dictionary = {}
var tok: Dictionary = {}
var touches: Dictionary = {}
var pair: Dictionary = {}
var transitions: Array = []   # [from, to] pairs seen, for the transition-table check
var first_ack: Dictionary = {}  # touch id -> ms from touch-down to first intent


func _init(scene_in: Dictionary, tokens: Dictionary) -> void:
	scene = scene_in
	tok = tokens


static func _v(a: Array) -> Vector2:
	return Vector2(float(a[0]), float(a[1]))


func _in_rect(p: Vector2, r: Array) -> bool:
	return p.x >= r[0] and p.x <= r[0] + r[2] and p.y >= r[1] and p.y <= r[1] + r[3]


func _near(p: Vector2, c: Vector2) -> bool:
	var h: float = float(tok["hit_px"]) / 2.0
	return absf(p.x - c.x) <= h and absf(p.y - c.y) <= h


func _ring_near(p: Vector2) -> String:
	var best := ""
	var best_d := 1e9
	for r in scene["rings"]:
		var d: float = p.distance_to(_v(r["pos"]))
		if d <= float(tok["snap_px"]) and d < best_d:
			best = String(r["id"])
			best_d = d
	return best


func _set_state(tid: int, state: String) -> void:
	transitions.append([touches[tid]["state"], state])
	touches[tid]["state"] = state


func _emit(out: Array, tid: int, t_ms: int, type: String, extra: Dictionary = {}) -> void:
	var d := {"type": type}
	d.merge(extra)
	out.append(d)
	if touches.has(tid) and not first_ack.has(tid):
		first_ack[tid] = t_ms - int(touches[tid]["t0"])


func down(tid: int, pos_in: Array, t_ms: int) -> Array:
	var out := []
	var pos := _v(pos_in)
	var rec := {"state": "IDLE", "start": pos, "pos": pos, "t0": t_ms, "source": "", "target": ""}
	touches[tid] = rec
	for b in scene["buttons"]:
		if _in_rect(pos, b["rect"]):
			rec["source"] = "button"
			rec["target"] = b["id"]
			_set_state(tid, "UI_PRESS")
			_emit(out, tid, t_ms, "PRESS_FEEDBACK", {"target": b["id"]})
			return out
	var w: float = float(scene["viewport"][0])
	if pos.x < float(tok["edge_reserve_px"]) or pos.x > w - float(tok["edge_reserve_px"]):
		_set_state(tid, "IGNORED")
		return out
	var sg: Dictionary = scene["sign"]
	var others := []
	for k in touches.keys():
		if k != tid and ["SIGN_PENDING", "MAP_PENDING", "PAN", "PINCH"].has(touches[k]["state"]):
			others.append(k)
	if others.size() > 0:
		var a: int = others[0]
		if touches[a]["state"] == "SIGN_PENDING":
			_emit(out, a, t_ms, "SIGN_ACTION_CANCELLED")
		_set_state(a, "PINCH")
		_set_state(tid, "PINCH")
		var d0: float = (touches[a]["pos"] as Vector2).distance_to(pos)
		pair = {"a": a, "b": tid, "d_prev": d0, "d0": d0, "active": false}
		return out
	if sg["placed"] and not sg["held"] and _near(pos, _v(sg["pos"])):
		rec["source"] = "sign"
		if scene["mode"] == "PAUSED":
			_set_state(tid, "LOCK_REJECT")
			_emit(out, tid, t_ms, "PAUSED_MESSAGE")
			return out
		_set_state(tid, "SIGN_PENDING")
		_emit(out, tid, t_ms, "PRESS_FEEDBACK", {"target": "sign"})
		return out
	for r in scene["rings"]:
		if _near(pos, _v(r["pos"])):
			rec["source"] = "ring"
			rec["target"] = r["id"]
			_set_state(tid, "SIGN_PENDING")
			_emit(out, tid, t_ms, "PRESS_FEEDBACK", {"target": r["id"]})
			return out
	if not sg["placed"] and _near(pos, _v(scene["tray"])):
		rec["source"] = "tray"
		_set_state(tid, "SIGN_PENDING")
		_emit(out, tid, t_ms, "PRESS_FEEDBACK", {"target": "tray"})
		return out
	_set_state(tid, "MAP_PENDING")
	return out


func move(tid: int, pos_in: Array, t_ms: int) -> Array:
	var out := []
	if not touches.has(tid):
		return out
	var rec: Dictionary = touches[tid]
	var pos := _v(pos_in)
	rec["pos"] = pos
	var st: String = rec["state"]
	if st == "PINCH" and not pair.is_empty() and (tid == pair["a"] or tid == pair["b"]):
		var d: float = (touches[pair["a"]]["pos"] as Vector2).distance_to(touches[pair["b"]]["pos"])
		var ratio: float = d / maxf(float(pair["d0"]), 0.000001)
		var pr: float = float(tok["pinch_ratio"])
		if pair["active"] or ratio > pr or ratio < 1.0 / pr:
			pair["active"] = true
			_emit(out, tid, t_ms, "PINCH", {"scale": d / maxf(float(pair["d_prev"]), 0.000001)})
			pair["d_prev"] = d
		return out
	var moved: float = (rec["start"] as Vector2).distance_to(pos)
	var delta: Array = [pos.x - (rec["start"] as Vector2).x, pos.y - (rec["start"] as Vector2).y]
	if st == "SIGN_PENDING" and moved > float(tok["drag_px"]):
		if rec["source"] == "ring":
			_set_state(tid, "PAN")
			_emit(out, tid, t_ms, "PAN", {"delta": delta})
		elif rec["source"] == "sign" and scene["sign"]["locked"]:
			_set_state(tid, "LOCK_REJECT")
			_emit(out, tid, t_ms, "LOCK_REJECT")
		else:
			_set_state(tid, "SIGN_DRAG")
			_emit(out, tid, t_ms, "SIGN_PICKUP", {"source": rec["source"]})
	elif st == "SIGN_DRAG":
		_emit(out, tid, t_ms, "SIGN_DRAG_MOVE", {"snap": _ring_near(pos)})
	elif st == "MAP_PENDING" and moved > float(tok["pan_px"]):
		_set_state(tid, "PAN")
		_emit(out, tid, t_ms, "PAN", {"delta": delta})
	elif st == "PAN":
		_emit(out, tid, t_ms, "PAN", {"delta": delta})
	return out


## Time passing without a touch event: long press and hold timeout.
func update(t_ms: int) -> Array:
	var out := []
	for tid in touches.keys():
		var rec: Dictionary = touches[tid]
		var el: int = t_ms - int(rec["t0"])
		if rec["state"] == "SIGN_PENDING" and rec["source"] == "sign" and el >= int(tok["long_press_ms"]) \
				and (rec["start"] as Vector2).distance_to(rec["pos"]) <= float(tok["drag_px"]):
			_set_state(tid, "SIGN_INSPECT")
			_emit(out, tid, t_ms, "INSPECT")
		elif rec["state"] == "SIGN_DRAG" and el >= int(tok["hold_timeout_ms"]):
			_set_state(tid, "IGNORED")
			_emit(out, tid, t_ms, "SNAPBACK", {"reason": "timeout"})
	return out


func up(tid: int, pos_in: Array, t_ms: int) -> Array:
	var out := []
	if not touches.has(tid):
		return out
	var rec: Dictionary = touches[tid]
	var pos := _v(pos_in)
	rec["pos"] = pos
	var st: String = rec["state"]
	var moved: float = (rec["start"] as Vector2).distance_to(pos)
	var sg: Dictionary = scene["sign"]
	if st == "UI_PRESS":
		for b in scene["buttons"]:
			if b["id"] == rec["target"] and _in_rect(pos, b["rect"]):
				_emit(out, tid, t_ms, "UI", {"id": b["id"]})
	elif st == "SIGN_PENDING":
		var quick: bool = (t_ms - int(rec["t0"])) <= int(tok["tap_ms"]) and moved < float(tok["drag_px"])
		if quick and rec["source"] == "sign":
			_emit(out, tid, t_ms, "LOCK_REJECT" if sg["locked"] else "SIGN_TURN")
		elif quick and rec["source"] == "ring" and sg["placed"]:
			if sg["locked"]:
				_emit(out, tid, t_ms, "LOCK_REJECT")
			elif rec["target"] != sg["slot"]:
				_emit(out, tid, t_ms, "SIGN_MOVE_TAP", {"slot": rec["target"]})
	elif st == "SIGN_DRAG":
		var ring := _ring_near(pos)
		if ring != "":
			_emit(out, tid, t_ms, "SIGN_DROP", {"slot": ring})
		else:
			_emit(out, tid, t_ms, "SNAPBACK", {"reason": "off_ring"})
	_set_state(tid, "IDLE")
	_finish_pair(tid)
	touches.erase(tid)
	return out


func cancel(tid: int, t_ms: int) -> Array:
	var out := []
	if not touches.has(tid):
		return out
	if touches[tid]["state"] == "SIGN_DRAG":
		_emit(out, tid, t_ms, "SNAPBACK", {"reason": "cancelled"})
	else:
		_emit(out, tid, t_ms, "CANCELLED")
	_set_state(tid, "IDLE")
	if not pair.is_empty() and (tid == pair["a"] or tid == pair["b"]):
		pair = {}
	touches.erase(tid)
	return out


func _finish_pair(tid: int) -> void:
	if pair.is_empty() or (tid != pair["a"] and tid != pair["b"]):
		return
	var other: int = pair["b"] if tid == pair["a"] else pair["a"]
	if touches.has(other) and touches[other]["state"] == "PINCH":
		_set_state(other, "IGNORED")
	pair = {}

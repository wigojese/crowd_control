class_name CcTransition
extends RefCounted
## One of the six cancellable transitions (master prompt C4), driven by data/transitions.json.
## Game-state callbacks (on_start) fire at START only, so cancel or skip can never change a run or lose a result.
## on_end is cosmetic and fires exactly once. No handle to the simulation exists here (lint rule L10).
## Port of scripts/ref_transitions.py. STATUS: written; NOT RUN (no runnable Godot).

var def: Dictionary
var settings: Dictionary
var reduced := false
var state := "IDLE"
var t := 0.0
var events: Array = []
var hooks_fired: Array = []
var end_calls: Array = []
var _frozen: Dictionary = {}
var _settle: Dictionary = {}


func _init(transition_def: Dictionary, global_settings: Dictionary, reduced_motion: bool = false) -> void:
	def = transition_def
	settings = global_settings
	reduced = reduced_motion


static func ease_value(name: String, f_in: float) -> float:
	var f := clampf(f_in, 0.0, 1.0)
	match name:
		"linear":
			return f
		"cubic_out":
			return 1.0 - pow(1.0 - f, 3.0)
		"ease_in_out":
			return 4.0 * f * f * f if f < 0.5 else 1.0 - pow(-2.0 * f + 2.0, 3.0) / 2.0
		"spring":
			return 1.0 if f >= 1.0 else 1.0 - exp(-7.0 * f) * cos(9.0 * f)
	return f


static func _poly_point(points: Array, f: float) -> Vector2:
	var lens: Array = []
	var total := 0.0
	for i in range(points.size() - 1):
		var l: float = Vector2(points[i][0], points[i][1]).distance_to(Vector2(points[i + 1][0], points[i + 1][1]))
		lens.append(l)
		total += l
	var d := f * total
	for i in range(lens.size()):
		var a := Vector2(points[i][0], points[i][1])
		var b := Vector2(points[i + 1][0], points[i + 1][1])
		if d <= float(lens[i]) or i == lens.size() - 1:
			var u := 0.0 if float(lens[i]) == 0.0 else minf(1.0, d / float(lens[i]))
			return a.lerp(b, u)
		d -= float(lens[i])
	return Vector2(points[points.size() - 1][0], points[points.size() - 1][1])


static func track_value(tr: Dictionary, t_ms: float):
	var f := 1.0
	if float(tr["dur_ms"]) > 0.0:
		f = (t_ms - float(tr["delay_ms"])) / float(tr["dur_ms"])
	var e := ease_value(String(tr["easing"]), f)
	if tr["kind"] == "scalar":
		return float(tr["from"]) + (float(tr["to"]) - float(tr["from"])) * e
	if tr["kind"] == "vec2":
		return Vector2(tr["from"][0], tr["from"][1]).lerp(Vector2(tr["to"][0], tr["to"][1]), e)
	return _poly_point(tr["points"], e)


static func end_value(tr: Dictionary):
	return track_value(tr, float(tr["delay_ms"]) + float(tr["dur_ms"]))


func start() -> void:
	if state != "IDLE":
		return
	state = "RUNNING"
	events.append_array(def["on_start"])
	_fire_hooks(0.0)
	if reduced:
		t = float(settings["reduced_motion_ms"])
		_end("completed")


func _fire_hooks(upto: float) -> void:
	for h in def["hooks"]:
		if not hooks_fired.has(h["id"]) and float(h["at"]) * float(def["duration_ms"]) <= upto:
			hooks_fired.append(h["id"])


func _end(reason: String) -> void:
	if state == "DONE" or state == "CANCELLED":
		return
	state = "DONE" if reason == "completed" or reason == "skipped" else "CANCELLED"
	end_calls.append(reason)


func update(dt_ms: float) -> void:
	if state != "RUNNING":
		return
	if not _settle.is_empty():
		_settle["t"] = float(_settle["t"]) + dt_ms
		if float(_settle["t"]) >= float(_settle["dur"]):
			_end("skipped")
		return
	t += dt_ms
	_fire_hooks(t)
	if t >= float(def["duration_ms"]):
		_end("completed")


## Settle to the end state; input is never blocked by any transition, so control is back at once.
func skip() -> void:
	if state != "RUNNING" or not _settle.is_empty():
		return
	_settle = {"t": 0.0, "dur": float(settings["skip_settle_ms"]), "from": values()}


## reason: touch, app_background or app_interrupt. Freezes exactly where it is.
func cancel(reason: String) -> void:
	if state != "RUNNING":
		return
	_frozen = values()
	_end("cancelled:" + reason)


func values() -> Dictionary:
	if not _frozen.is_empty():
		return _frozen
	var out := {}
	if reduced or (state == "DONE" and _settle.is_empty()):
		for tr in def["tracks"]:
			out[tr["name"]] = end_value(tr)
		return out
	if not _settle.is_empty():
		var f := minf(1.0, float(_settle["t"]) / float(_settle["dur"]))
		for tr in def["tracks"]:
			var a = _settle["from"][tr["name"]]
			var b = end_value(tr)
			out[tr["name"]] = lerpf(a, b, f) if a is float else (a as Vector2).lerp(b, f)
		return out
	for tr in def["tracks"]:
		out[tr["name"]] = track_value(tr, t)
	return out

extends Node2D
## Stage 08 graybox: plain debug drawing of CC-L01-R1. No styling on purpose.
## Shows the graph, edge queue lengths, walkers as dots, the sign, and the score numbers.
## Keys (desktop): space = run/pause, R = retry, 1..4 = heading N E S W, A / B = sign socket.
## STATUS: written; NOT RUN or seen (no runnable Godot, no display).

const LEVEL_PATH := "res://data/levels/cc_l01_r1.json"
const HEADS := ["N", "E", "S", "W"]

var _world: CcSimWorld
var _running := false
var _slot := "A"
var _head := "E"
var _commands: Array = []
var _level: Dictionary = {}
var _schema: Dictionary = {}


func _ready() -> void:
	_level = JSON.parse_string(FileAccess.get_file_as_string(LEVEL_PATH))
	_schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))["events"]
	_retry()


func _retry() -> void:
	_world = CcSimWorld.new(_level, _schema)
	_world.reset([_slot, _head], _commands)
	_running = false
	queue_redraw()


func _unhandled_key_input(ev: InputEvent) -> void:
	var event := ev as InputEventKey
	if event == null or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_SPACE:
			_running = not _running
		KEY_R:
			_retry()
		KEY_1, KEY_2, KEY_3, KEY_4:
			_head = HEADS[event.keycode - KEY_1]
			if _world.tick > 0:
				_commands.append([_world.tick, _commands.size(), "ROTATE", _head])
			else:
				_retry()
		KEY_A, KEY_B:
			_slot = "A" if event.keycode == KEY_A else "B"
			if _world.tick > 0:
				_commands.append([_world.tick, _commands.size(), "MOVE", _slot])
			else:
				_retry()


func _physics_process(_delta: float) -> void:
	if _running and _world.tick < _world.ticks:
		_world.step()
		queue_redraw()


func _draw() -> void:
	var pos := _world.node_positions()
	for e in _world.edge_ids():
		var ids: PackedStringArray = String(e).split(">")
		if ids[0] < ids[1]:
			draw_line(pos[ids[0]], pos[ids[1]], Color(0.72, 0.66, 0.56), 2.0)
	for e in _world.edge_ids():
		var n := _world.queue_length(e)
		if n > 0:
			var ids: PackedStringArray = String(e).split(">")
			var mid: Vector2 = (pos[ids[0]] + pos[ids[1]]) * 0.5
			_text(mid, "q%d" % n, Color(0.9, 0.46, 0.35))
	for n in pos.keys():
		draw_circle(pos[n], 6.0, Color(0.94, 0.89, 0.78))
		_text(pos[n] + Vector2(8, -8), String(n), Color.WHITE)
	for w in _world.walkers:
		var p := Vector2.ZERO
		if w["state"] == CcSimWorld.S_ON_EDGE:
			var ids: PackedStringArray = String(w["edge"]).split(">")
			p = pos[ids[0]].lerp(pos[ids[1]], float(w["edge_t"]))
		elif w["state"] == CcSimWorld.S_QUEUED or w["state"] == CcSimWorld.S_NEEDS:
			p = pos[w["node"]]
		else:
			continue
		draw_circle(p, 3.0, Color(0.9, 0.65, 0.2))
	if _world.sign["slot"] != "":
		var sp: Vector2 = pos[_world.sign["slot"]]
		draw_circle(sp, 10.0, Color(0.88, 0.31, 0.18) if _world.sign["active"] else Color(0.4, 0.4, 0.4))
		_text(sp + Vector2(-4, 4), String(_world.sign["head"]), Color.WHITE)
	var r := _world.result()
	var text := "tick %d  arrived %d/20  blocked %d  %s" % [_world.tick, r["arrived"], _world.blocked_total,
		"RUN" if _running else "PAUSED"]
	_text(Vector2(8, 540), text, Color.WHITE)


func _text(at: Vector2, s: String, color: Color) -> void:
	draw_string(ThemeDB.fallback_font, at, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, color)

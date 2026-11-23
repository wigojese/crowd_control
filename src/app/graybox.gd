extends Node2D
## Stage 08 graybox with Stage 10 drawing: controls and HUD text here, map drawing in CcMapView (direction C).
## Shows the graph, edge queue lengths, walkers as dots, the sign, and the score numbers.
## Keys (desktop): space = run/pause, R = retry, H = high contrast, 1..4 = heading N E S W, A / B = sign socket.
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
var _view := CcMapView.new()
var _high_contrast := false


func _ready() -> void:
	add_child(_view)
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
		KEY_H:
			_high_contrast = not _high_contrast
			queue_redraw()
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
	_view.world = _world
	_view.theme = "high_contrast" if _high_contrast else "standard"
	_view.queue_redraw()
	var r := _world.result()
	var text := "tick %d  arrived %d/20  blocked %d  %s" % [_world.tick, r["arrived"], _world.blocked_total,
		"RUN" if _running else "PAUSED"]
	_text(Vector2(8, 540), text, Color.WHITE)


func _text(at: Vector2, s: String, color: Color) -> void:
	draw_string(ThemeDB.fallback_font, at, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, color)

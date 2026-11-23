extends Node2D
## Stage 08 graybox with Stage 10 drawing: controls and HUD text here, map drawing in CcMapView (direction C).
## Shows the graph, edge queue lengths, walkers as dots, the sign, and the score numbers.
## Keys (desktop): space run/pause, R retry, H contrast, 1..4 heading N E S W, A / B socket, 0 no sign.
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
var _hud := Node2D.new()


func _ready() -> void:
	add_child(_view)
	add_child(_hud)  # added after the map so the text is drawn on top of it
	_hud.draw.connect(_draw_hud)
	_level = JSON.parse_string(FileAccess.get_file_as_string(LEVEL_PATH))
	_schema = JSON.parse_string(FileAccess.get_file_as_string("res://data/events.schema.json"))["events"]
	_retry()


func _retry() -> void:
	_world = CcSimWorld.new(_level, _schema)
	_world.reset([] if _slot == "" else [_slot, _head], _commands)
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
		KEY_0:
			if _world.tick == 0:
				_slot = ""
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
	_hud.queue_redraw()


func _clock(seconds: float) -> String:
	var whole := int(ceil(maxf(0.0, seconds)))
	return "%d:%02d" % [whole / 60, whole % 60]


func _draw_hud() -> void:
	var r := _world.result()
	var need := int(_level.get("pass_mark", 18))
	var done := _world.tick >= _world.ticks
	var left := float(_world.ticks - _world.tick) / 20.0
	var dark := Color(0.09, 0.07, 0.06, 0.95)
	_hud.draw_rect(Rect2(0, 0, 390, 112), dark)
	_hud.draw_rect(Rect2(0, 700, 390, 144), dark)
	_text(Vector2(10, 24), "GOAL: %d of 20 people must reach School or Plaza" % need, Color.WHITE, 17)
	_text(Vector2(10, 52), "Time left %s    Arrived %d / 20" % [_clock(left), r["arrived"]], Color.WHITE, 22)
	var status := "Press SPACE to start the walking"
	var col := Color(1.0, 0.85, 0.4)
	if done:
		if int(r["arrived"]) >= need:
			status = "YOU WIN!  Press R to play again"
			col = Color(0.6, 1.0, 0.6)
		else:
			status = "NOT ENOUGH (%d, needed %d). Press R, try another sign" % [r["arrived"], need]
			col = Color(1.0, 0.55, 0.45)
	elif _running:
		status = "Walking...  SPACE pauses"
	elif _world.tick > 0:
		status = "Paused. SPACE continues"
	_text(Vector2(10, 84), status, col, 16)
	var names := {"A": "North Gate (A)", "B": "Canal Turn (B)"}
	var dirs := {"N": "up", "E": "right", "S": "down", "W": "left"}
	var where := "NO SIGN"
	if _slot != "":
		where = "%s pointing %s" % [names[_slot], dirs[_head]]
	_text(Vector2(10, 726), "Sign: " + where, Color.WHITE, 18)
	_text(Vector2(10, 754), "A or B: where the sign stands", Color(0.9, 0.9, 0.8), 16)
	_text(Vector2(10, 776), "1 2 3 4: point up, right, down, left.  0: no sign", Color(0.9, 0.9, 0.8), 16)
	_text(Vector2(10, 798), "SPACE start/pause   R retry   H contrast", Color(0.9, 0.9, 0.8), 16)
	_text(Vector2(10, 826), "F = School   G = Plaza   (red circle = the sign)", Color(0.9, 0.9, 0.8), 16)


func _text(at: Vector2, s: String, color: Color, size: int = 16) -> void:
	_hud.draw_string(ThemeDB.fallback_font, at, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

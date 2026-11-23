class_name CcMapView
extends Node2D
## Direction C (transit score) map drawing. Reads the simulation, never writes to it. All colours and sizes come
## from data/art_tokens.json (no colour literal here). Mirrors scripts/stage10_preview.py, the picture reference.
## Rules implemented here: streets as three-line staves (_draw_streets), walkers as notes by profile (_draw_note),
## queues as plum hatched bands (_draw_queue), counted-flow ribbons that are solid for School and dashed for Plaza
## (_draw_ribbons, widths from CcRibbonModel only), sign as vermilion disc with dark arrow (_draw_sign),
## text with a dark halo (_label), high-contrast theme switch (theme).
## STATUS: written; NOT RUN or seen in the engine (no runnable Godot, no display).

const HEADS := {"N": Vector2(0, -1), "E": Vector2(1, 0), "S": Vector2(0, 1), "W": Vector2(-1, 0)}

var world: CcSimWorld
var theme: String = "standard"  # or "high_contrast"
var ribbon_mode: bool = false
var flow_counts: Dictionary = {}  # {"street|key": count} from CcRibbonModel.counts_from_event_lines
var scale_px: float = 1.2
var origin_px := Vector2(195, 175)
var _tokens: Dictionary = {}


func _ready() -> void:
	_tokens = JSON.parse_string(FileAccess.get_file_as_string("res://data/art_tokens.json"))


func _c(name: String) -> Color:
	return Color(String(_tokens["themes"][theme][name]))


func _p(world_pos: Vector2) -> Vector2:
	return origin_px + (world_pos - Vector2(181, 50)) * scale_px


func _draw() -> void:
	if world == null or _tokens.is_empty():
		return
	var pos := world.node_positions()
	_draw_stave_grid()
	_draw_streets(pos)
	if ribbon_mode:
		_draw_ribbons(pos)
	else:
		for e in world.edge_ids():
			if world.queue_length(e) >= 2:
				_draw_queue(pos, String(e))
	for n in pos.keys():
		draw_circle(_p(pos[n]), 4.5, _c("night"))
		draw_arc(_p(pos[n]), 4.5, 0.0, TAU, 16, _c("stave"), 1.6)
		_label(_p(pos[n]) + Vector2(16, 4), String(n))
	if not ribbon_mode:
		for w in world.walkers:
			_draw_walker(pos, w)
	if world.sign["slot"] != "":
		_draw_sign(_p(pos[world.sign["slot"]]), String(world.sign["head"]))


## Static staff lines on a world-anchored grid: they move with the map, so they never swim during camera moves.
func _draw_stave_grid() -> void:
	var step: float = float(_tokens["geometry"]["stave_grid_px"]) * 2.0
	var faint := _c("stave")
	faint.a = 0.07
	var y := fposmod(origin_px.y - 50.0 * scale_px, step * scale_px) - step * scale_px
	while y < 900.0:
		draw_line(Vector2(-400, y), Vector2(800, y), faint, 0.5)
		y += step * scale_px


func _draw_streets(pos: Dictionary) -> void:
	var g: Dictionary = _tokens["geometry"]
	for e in world.edge_ids():
		var ids: PackedStringArray = String(e).split(">")
		if ids[0] > ids[1]:
			continue
		var a := _p(pos[ids[0]])
		var b := _p(pos[ids[1]])
		var side := (b - a).normalized().orthogonal() * float(g["stave_gap_px"])
		draw_line(a, b, _c("stave"), 1.6)
		draw_line(a + side, b + side, _c("dim"), float(g["stave_line_px"]))
		draw_line(a - side, b - side, _c("dim"), float(g["stave_line_px"]))


func _draw_note(at: Vector2, kind: String, color: Color) -> void:
	draw_circle(at, 4.2, color)
	draw_line(at + Vector2(4, 0), at + Vector2(4, -13), color, 1.6)
	if kind == "F":  # follower: beamed pair
		draw_circle(at + Vector2(9, 0), 4.0, color)
		draw_line(at + Vector2(13, 0), at + Vector2(13, -12), color, 1.5)
		draw_line(at + Vector2(4, -12), at + Vector2(13, -12), color, 2.6)
	elif kind == "I":  # independent: flagged
		draw_line(at + Vector2(4, -13), at + Vector2(10, -9), color, 1.6)


func _draw_walker(pos: Dictionary, w: Dictionary) -> void:
	var at := Vector2.ZERO
	if w["state"] == CcSimWorld.S_ON_EDGE:
		var ids: PackedStringArray = String(w["edge"]).split(">")
		at = _p(pos[ids[0]]).lerp(_p(pos[ids[1]]), float(w["edge_t"]))
	elif w["state"] == CcSimWorld.S_QUEUED or w["state"] == CcSimWorld.S_NEEDS:
		at = _p(pos[w["node"]])
	else:
		return
	_draw_note(at, String(w["prof"]), _c("amber") if w["dest"] == "F" else _c("sage"))


func _draw_queue(pos: Dictionary, edge_id: String) -> void:
	var ids: PackedStringArray = edge_id.split(">")
	var a := _p(pos[ids[0]])
	var dir := (_p(pos[ids[1]]) - a).normalized()
	var len_px := 8.0 + 9.0 * float(world.queue_length(edge_id))
	var n_lines := int(len_px / 5.0)
	for i in range(n_lines):  # diagonal hatching in plum (plum is for fills only)
		var c := a + dir * (6.0 + 5.0 * i)
		draw_line(c + Vector2(-5, 5), c + Vector2(5, -5), _c("plum"), 2.0)


func _draw_ribbons(pos: Dictionary) -> void:
	for key in flow_counts.keys():
		var ids: PackedStringArray = String(key).split("|")
		var w := CcRibbonModel.width(int(flow_counts[key]), _tokens)
		if w > 0.0:
			draw_line(_p(pos[ids[0]]), _p(pos[ids[1]]), _c("amber"), w)


func _draw_sign(at: Vector2, head: String) -> void:
	var d: Vector2 = HEADS[head]
	draw_circle(at, 20.0, _c("vermilion"))
	var tip := at + d * 11.0
	var back := at - d * 7.0
	var side := d.orthogonal() * 8.0
	draw_colored_polygon(PackedVector2Array([tip, back + side, back - side]), _c("sign_arrow"))


func _label(at: Vector2, text: String) -> void:
	var font := ThemeDB.fallback_font
	var halo: int = int(_tokens["geometry"]["label_halo_px"])
	draw_string_outline(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, halo, _c("night"))
	draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, _c("stave"))

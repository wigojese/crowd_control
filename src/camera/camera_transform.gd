class_name CcCameraTransform
extends RefCounted
## World-to-screen transform (master prompt C1): screen = (world - center) * zoom + viewport_center + safe_offset.
## Port of scripts/ref_camera.py. Pure math, no scene tree. STATUS: written; NOT RUN (no runnable Godot).

const ZMIN := 0.65
const ZMAX := 2.80

var center := Vector2(181, 262)
var zoom := 1.0
var viewport := Vector2(390, 844)
var safe_offset := Vector2.ZERO


func w2s(p: Vector2) -> Vector2:
	return (p - center) * zoom + viewport / 2.0 + safe_offset


func s2w(s: Vector2) -> Vector2:
	return (s - viewport / 2.0 - safe_offset) / zoom + center


## Pinch: change zoom so the world point under anchor_screen stays under it.
func zoom_about(anchor_screen: Vector2, new_zoom: float) -> void:
	var a := s2w(anchor_screen)
	zoom = clampf(new_zoom, ZMIN, ZMAX)
	center = a - (anchor_screen - viewport / 2.0 - safe_offset) / zoom


## Camera centre that puts world_pt in the free band between HUD and dock, so a thumb never covers it.
static func compose_focus(world_pt: Vector2, zoom_in: float, vp: Vector2, top_inset: float, hud_h: float,
		bottom_inset: float, dock_h: float) -> Vector2:
	var free_top := top_inset + hud_h
	var free_bottom := vp.y - bottom_inset - dock_h
	var target_y := free_top + 0.42 * (free_bottom - free_top)
	return Vector2(world_pt.x, world_pt.y - (target_y - vp.y / 2.0) / zoom_in)

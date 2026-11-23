class_name CcDockLayout
extends RefCounted
## Dock rectangles for the bottom row: restart, sign tray, pause. Right-handed puts pause on the right (thumb side);
## left-handed is the exact mirror. Port of scripts/ref_settings.py. STATUS: written; NOT RUN.
## Returns {name: [x, y, w, h]} in logical px.


static func layout(left_handed: bool, larger: bool, viewport: Vector2, bottom_inset: int = 34) -> Dictionary:
	var w := int(viewport.x)
	var h := int(viewport.y)
	var bw := 104
	if w <= 320:
		bw = 88 if larger else 92
	var extra := 8 if larger else 0
	if w > 320:
		bw += extra
	var bh := 48 + extra
	var th := 56 + extra
	var tray_w := 56 + extra
	var margin := 28
	var y := h - bottom_inset - 112 + (112 - maxi(bh, th)) / 2
	var xs := [margin, (w - tray_w) / 2, w - margin - bw]
	var tray_y := y - (th - bh) / 2 if th > bh else y
	var rects := {"restart": [xs[0], y, bw, bh], "tray": [xs[1], tray_y, tray_w, th], "pause": [xs[2], y, bw, bh]}
	if left_handed:
		for k in rects.keys():
			var v: Array = rects[k]
			rects[k] = [w - int(v[0]) - int(v[2]), v[1], v[2], v[3]]
	return rects

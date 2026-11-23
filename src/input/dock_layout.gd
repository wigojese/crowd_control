class_name CcDockLayout
extends RefCounted
## Dock rectangles for the bottom row: restart, sign tray, pause. Right-handed puts pause on the right (thumb side);
## left-handed is the exact mirror. Port of scripts/ref_settings.py. STATUS: written; NOT RUN.
## Returns {name: [x, y, w, h]} in logical px.


static func layout(left_handed: bool, larger: bool, viewport: Vector2, bottom_inset: int = 34) -> Dictionary:
	var w := int(viewport.x)
	var h := int(viewport.y)
	var extra := 8 if larger else 0
	var bh := 48 + extra
	var th := 56 + extra
	var tray_w := 56 + extra
	var margin := 28
	var gap := 12
	var want := 104 + extra
	if w <= 320:
		want = 88 if larger else 92
	# Tablets keep the row within thumb reach (480 wide, on the thumb side). Stage 16.
	var span_w := 480 if w > 600 else w - 2 * margin
	var x0 := w - margin - span_w
	var bw := mini(want, (span_w - tray_w - 2 * gap) / 2)
	var y := h - bottom_inset - 112 + (112 - maxi(bh, th)) / 2
	var xs := [x0, x0 + (span_w - tray_w) / 2, x0 + span_w - bw]
	var tray_y := y - (th - bh) / 2 if th > bh else y
	var rects := {"restart": [xs[0], y, bw, bh], "tray": [xs[1], tray_y, tray_w, th], "pause": [xs[2], y, bw, bh]}
	if left_handed:
		for k in rects.keys():
			var v: Array = rects[k]
			rects[k] = [w - int(v[0]) - int(v[2]), v[1], v[2], v[3]]
	return rects

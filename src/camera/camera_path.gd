class_name CcCameraPath
extends RefCounted
## Catmull-Rom camera path through meaningful junctions with an arc-length table (<= 5 world units spacing).
## Scrub and inertia rules from master prompt C2. Port of scripts/ref_camera.py. STATUS: written; NOT RUN.

const SCROLL_GAIN := 0.85
const INERTIA_K := 6.0
const INERTIA_CAP_VIEWPORTS := 1.6

var length: float = 0.0
var table: Array = []  # [s, x, y]


func _init(pts: Array, spacing: float = 4.0) -> void:
	var p: Array = [pts[0]] + pts + [pts[pts.size() - 1]]
	var dense: Array = []
	for i in range(1, p.size() - 2):
		var p0: Vector2 = p[i - 1]
		var p1: Vector2 = p[i]
		var p2: Vector2 = p[i + 1]
		var p3: Vector2 = p[i + 2]
		for k in range(80):
			var t := float(k) / 80.0
			dense.append(((p1 * 2.0) + (p2 - p0) * t + (p0 * 2.0 - p1 * 5.0 + p2 * 4.0 - p3) * t * t
				+ (p3 - p0 + (p1 - p2) * 3.0) * t * t * t) * 0.5)
	dense.append(pts[pts.size() - 1])
	var cum: Array = [0.0]
	for i in range(dense.size() - 1):
		cum.append(float(cum[i]) + (dense[i] as Vector2).distance_to(dense[i + 1]))
	length = cum[cum.size() - 1]
	var n := int(ceil(length / spacing))
	var j := 0
	for i in range(n + 1):
		var s := minf(length, float(i) * spacing)
		while j < cum.size() - 2 and float(cum[j + 1]) < s:
			j += 1
		var span: float = float(cum[j + 1]) - float(cum[j])
		var f := 0.0 if span == 0.0 else (s - float(cum[j])) / span
		var pt: Vector2 = (dense[j] as Vector2).lerp(dense[j + 1], f)
		table.append([s, pt.x, pt.y])


func point_at(s_in: float) -> Vector2:
	var s := clampf(s_in, 0.0, length)
	var lo := 0
	var hi := table.size() - 1
	while hi - lo > 1:
		var mid := (lo + hi) / 2
		if float(table[mid][0]) <= s:
			lo = mid
		else:
			hi = mid
	var a: Array = table[lo]
	var b: Array = table[hi]
	var f := 0.0 if b[0] == a[0] else (s - float(a[0])) / (float(b[0]) - float(a[0]))
	return Vector2(float(a[1]) + (float(b[1]) - float(a[1])) * f, float(a[2]) + (float(b[2]) - float(a[2])) * f)


func max_spacing() -> float:
	var m := 0.0
	for i in range(table.size() - 1):
		m = maxf(m, float(table[i + 1][0]) - float(table[i][0]))
	return m


static func scrub_delta(dy: float, zoom: float) -> float:
	return -dy / zoom * SCROLL_GAIN


static func inertia_velocity(v0: float, t: float, viewport_h: float, zoom: float) -> float:
	var cap := INERTIA_CAP_VIEWPORTS * viewport_h / zoom
	return clampf(v0, -cap, cap) * exp(-INERTIA_K * t)

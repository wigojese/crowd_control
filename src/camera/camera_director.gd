class_name CcCameraDirector
extends RefCounted
## Alone owns the camera transform. UI asks with request_focus(); a touch on the map outranks everything.
## No simulation handle exists here, so the camera cannot change a run. Port of scripts/ref_camera.py.
## STATUS: written; NOT RUN. Priorities: TOUCH 3 > USER 2 > CRITICAL 1 > DECORATIVE 0.

const PRI := {"TOUCH": 3, "USER": 2, "CRITICAL": 1, "DECORATIVE": 0}
const STATES := ["LEVEL_FLYIN", "OVERVIEW", "SIGN_FOCUS", "PATH_SCRUB", "FOLLOW_CASCADE", "RESULT_PULLBACK",
	"REPLAY_RETURN", "USER_PAN", "REDUCED_MOTION"]

var tf: CcCameraTransform
var state := "OVERVIEW"
var pri := -1
var reduced_motion := false
var anim: Dictionary = {}


func _init(transform: CcCameraTransform, reduced: bool = false) -> void:
	tf = transform
	reduced_motion = reduced


## rule: "interrupt" (equal priority may replace), "queue" or "reject_if_busy" (equal priority is refused).
func request_focus(target_state: String, priority: String, target_center: Vector2, target_zoom: float,
		duration: float, rule: String = "interrupt") -> bool:
	var p: int = PRI[priority]
	var busy := not anim.is_empty() or state == "USER_PAN"
	if busy and (p < pri or (p == pri and rule != "interrupt") or rule == "reject_if_busy"):
		return false
	if reduced_motion:
		tf.center = target_center
		tf.zoom = target_zoom
		state = "REDUCED_MOTION"
		pri = -1
		anim = {}
		return true
	state = target_state
	pri = p
	anim = {"t": 0.0, "dur": duration, "c0": tf.center, "z0": tf.zoom, "c1": target_center, "z1": target_zoom}
	return true


func update(dt: float) -> void:
	if anim.is_empty():
		return
	anim["t"] = minf(float(anim["dur"]), float(anim["t"]) + dt)
	var f := 1.0 if float(anim["dur"]) <= 0.0 else float(anim["t"]) / float(anim["dur"])
	var e := 1.0 - pow(1.0 - f, 3.0)
	tf.zoom = exp(log(float(anim["z0"])) + (log(float(anim["z1"])) - log(float(anim["z0"]))) * e)
	tf.center = (anim["c0"] as Vector2).lerp(anim["c1"], e)
	if f >= 1.0:
		anim = {}
		pri = -1


## A finger on the map freezes the camera exactly where it is (no snap to the target).
func touch_begin() -> void:
	anim = {}
	state = "USER_PAN"
	pri = PRI["TOUCH"]


func touch_end() -> void:
	pri = -1

class_name CcZoomBands
extends RefCounted
## Three semantic zoom bands with hysteresis, the 1 s flux window, and the level-of-detail plan (master prompt C3).
## The plan decides what MAY be drawn; counts stay exact. Port of scripts/ref_camera.py. STATUS: written; NOT RUN.

const CITY := "CITY"
const DISTRICT := "DISTRICT"
const STREET := "STREET"
const STREET_IN := 1.75
const STREET_OUT := 1.55
const CITY_IN := 0.85
const CITY_OUT := 1.00
const LABEL_CAP := {"CITY": 4, "DISTRICT": 6, "STREET": 3}


static func update(band: String, z: float) -> String:
	while true:
		var nb := band
		if band == DISTRICT and z >= STREET_IN:
			nb = STREET
		elif band == DISTRICT and z <= CITY_IN:
			nb = CITY
		elif band == STREET and z <= STREET_OUT:
			nb = DISTRICT
		elif band == CITY and z >= CITY_OUT:
			nb = DISTRICT
		if nb == band:
			return band
		band = nb
	return band


## events: [[tick, street_key, dest], ...] of EDGE_ENTERED. Counts over the last `window` ticks.
static func flux_window(events: Array, tick: int, window: int = 20) -> Dictionary:
	var out := {}
	for e in events:
		if tick - window < int(e[0]) and int(e[0]) <= tick:
			var k := "%s#%s" % [e[1], e[2]]
			out[k] = int(out.get(k, 0)) + 1
	return out


## snap: {walkers:[{id,active}], streets:[key], flux:{k:n}, queues:{key:n}, labels:[{id,priority}]}
static func lod_plan(band: String, snap: Dictionary) -> Dictionary:
	var active: Array = []
	for w in snap["walkers"]:
		if w["active"]:
			active.append(w["id"])
	var streets: Array = (snap["streets"] as Array).duplicate()
	streets.sort()
	var labels: Array = (snap["labels"] as Array).duplicate()
	labels.sort_custom(_label_less)
	var label_ids: Array = []
	for l in labels.slice(0, int(LABEL_CAP[band])):
		label_ids.append(l["id"])
	return {"band": band, "people_represented": active.size(), "streets_visible": streets,
		"agents": [] if band == CITY else active, "agent_detail": band == STREET,
		"ribbons": (snap["flux"] as Dictionary).duplicate() if band == CITY else {}, "labels": label_ids}


static func _label_less(a: Dictionary, b: Dictionary) -> bool:
	if a["priority"] != b["priority"]:
		return a["priority"] > b["priority"]
	return str(a["id"]) < str(b["id"])


## Narrow-phone rule: a queue of min_overlap or more notes is one note plus a count badge.
static func cluster_badges(queue_counts: Dictionary, min_overlap: int = 4) -> Dictionary:
	var out := {}
	for k in queue_counts.keys():
		if int(queue_counts[k]) >= min_overlap:
			out[k] = queue_counts[k]
	return out

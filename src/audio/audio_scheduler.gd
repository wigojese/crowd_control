class_name CcAudioScheduler
extends RefCounted
## Turns simulation events into sound plays. Sounds come only from real events; cooldowns, a trigger-per-second cap and
## voice caps keep 50 pedestrians from becoming noise. Critical cues are never dropped. Pure logic: it plays nothing.
## Port of scripts/ref_audio.py. STATUS: written; NOT RUN (no runnable Godot). Map: data/audio_map.json.
## events: [{"t_ms", "type", "f"}]. Returns {"plays": [{t_ms, cue, gain, pitch, source}], "bed": [[t_ms, gain]]}.


static func schedule(events: Array, settings: Dictionary, passed: bool, amap: Dictionary) -> Dictionary:
	var lim: Dictionary = amap["limits"]
	var cues: Dictionary = amap["cues"]
	var plays := []
	var last_cd := {}
	var trig: Array = []
	var active: Array = []
	var moving := 0
	var bed := []
	var arrivals := 0
	var last_bed := -1000000000
	for idx in range(events.size()):
		var ev: Dictionary = events[idx]
		var t: int = int(ev["t_ms"])
		var typ: String = ev["type"]
		var f: Dictionary = ev["f"]
		if typ == "EDGE_ENTERED":
			moving += 1
		elif typ == "NODE_ARRIVED":
			moving = maxi(0, moving - 1)
		if t - last_bed >= 500 and (typ == "EDGE_ENTERED" or typ == "NODE_ARRIVED"):
			var level := minf(1.0, float(moving) / float(lim["foot_bed_full_at_walkers"]))
			bed.append([t, snappedf(level * _gain(settings, "texture"), 0.0001)])
			last_bed = t
		for rule in amap["events"]:
			if rule["event"] != typ:
				continue
			var w: Dictionary = rule.get("when", {})
			if w.has("reason") and f.get("reason", "") != w["reason"]:
				continue
			if w.has("position_at_least") and int(f.get("position", "0")) < int(w["position_at_least"]):
				continue
			var cue: String = ""
			if rule.has("cue"):
				cue = rule["cue"]
			else:
				cue = rule["cue_if_passed"] if passed else rule["cue_if_failed"]
			var c: Dictionary = cues[cue]
			var gain := _gain(settings, String(c["category"]))
			if gain <= 0.0:
				continue
			var key := cue
			if rule.get("cooldown_key", "global") == "edge":
				key = cue + ":" + String(f.get("edge", ""))
			var cd: int = int(rule.get("cooldown_ms", _default_cooldown(cue, lim)))
			if last_cd.has(key) and t - int(last_cd[key]) < cd:
				continue
			trig = trig.filter(func(x): return t - int(x) < 1000)
			active = active.filter(func(a): return int(a[0]) > t)
			if not c["critical"]:
				if trig.size() >= int(lim["max_triggers_per_second"]):
					continue
				var same := 0
				for a in active:
					if a[1] == c["category"]:
						same += 1
				if same >= int(lim["max_voices"][c["category"]]):
					continue
			var pitch := 0
			if cue == "arrival_pluck":
				var sc: Array = amap["arrival_scale_semitones"]
				pitch = int(sc[arrivals % sc.size()]) + 12 * (arrivals / sc.size())
				arrivals += 1
			last_cd[key] = t
			trig.append(t)
			active.append([t + int(c["duration_ms"]), c["category"]])
			plays.append({"t_ms": t, "cue": cue, "gain": gain, "pitch": pitch, "source": idx})
	return {"plays": plays, "bed": bed}


static func _gain(settings: Dictionary, category: String) -> float:
	return snappedf(float(settings["master"]) * float(settings[category]), 0.000001)


static func _default_cooldown(cue: String, lim: Dictionary) -> int:
	match cue:
		"reroute_tick":
			return int(lim["reroute_tick_cooldown_ms"])
		"arrival_pluck":
			return int(lim["arrival_pluck_cooldown_ms"])
		"queue_compress":
			return int(lim["queue_compress_cooldown_ms_per_street"])
	return 0

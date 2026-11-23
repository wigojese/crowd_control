"""Reference for the audio scheduler (src/audio/audio_scheduler.gd), Stage 15. Pure logic: events in, cue plays out.
Sounds come only from real events; rate limits, voice caps and cooldowns stop 50 pedestrians from becoming noise.
Usage: python3 -I scripts/ref_audio.py   (runs the checks on real traces and a 50-walker stress stream)
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP = json.loads((ROOT / "data/audio_map.json").read_text())
VIS = json.loads((ROOT / "data/visual_cues.json").read_text())
sys.path.insert(0, str(ROOT / "scripts"))


def gain_of(settings, category):
    return round(settings["master"] * settings[category], 6)


def schedule(events, settings, passed):
    """events: [(t_ms, type, fields)]. Returns (plays, bed). plays: dict(t_ms, cue, gain, pitch, source). bed: [(t_ms, gain)]."""
    lim, cues = MAP["limits"], MAP["cues"]
    plays, last_cd, trig, active = [], {}, [], []
    moving, bed, arrivals, last_bed = 0, [], 0, -10**9
    for idx, (t, typ, f) in enumerate(events):
        if typ == "EDGE_ENTERED":
            moving += 1
        elif typ == "NODE_ARRIVED":
            moving = max(0, moving - 1)
        if t - last_bed >= 500 and typ in ("EDGE_ENTERED", "NODE_ARRIVED"):
            bed.append((t, round(min(1.0, moving / lim["foot_bed_full_at_walkers"]) * gain_of(settings, "texture"), 4)))
            last_bed = t
        for rule in MAP["events"]:
            if rule["event"] != typ:
                continue
            w = rule.get("when", {})
            if "reason" in w and f.get("reason") != w["reason"]:
                continue
            if "position_at_least" in w and int(f.get("position", 0)) < w["position_at_least"]:
                continue
            cue = rule.get("cue") or (rule["cue_if_passed"] if passed else rule["cue_if_failed"])
            c = cues[cue]
            gain = gain_of(settings, c["category"])
            if gain <= 0.0:
                continue  # muted by the player: the visual equivalent still happens, nothing here
            key = cue if rule.get("cooldown_key") in (None, "global") else cue + ":" + f.get("edge", "")
            cd = rule.get("cooldown_ms")
            if cd is None:
                cd = {"reroute_tick": lim["reroute_tick_cooldown_ms"], "arrival_pluck": lim["arrival_pluck_cooldown_ms"], "queue_compress": lim["queue_compress_cooldown_ms_per_street"]}.get(cue, 0)
            if key in last_cd and t - last_cd[key] < cd:
                continue
            critical = c["critical"]
            trig = [x for x in trig if t - x < 1000]
            active = [(e, cat) for e, cat in active if e > t]
            if not critical:
                if len(trig) >= lim["max_triggers_per_second"]:
                    continue
                if sum(1 for e, cat in active if cat == c["category"]) >= lim["max_voices"][c["category"]]:
                    continue
            pitch = 0
            if cue == "arrival_pluck":
                sc = MAP["arrival_scale_semitones"]
                pitch = sc[arrivals % len(sc)] + 12 * (arrivals // len(sc))
                arrivals += 1
            last_cd[key] = t
            trig.append(t)
            active.append((t + c["duration_ms"], c["category"]))
            plays.append(dict(t_ms=t, cue=cue, gain=gain, pitch=pitch, source=idx))
    return plays, bed


def from_lines(lines):
    out = []
    for ln in lines:
        tick, seq, typ, rest = ln.split("|", 3)
        out.append((int(tick) * 50, typ, dict(kv.split("=", 1) for kv in rest.split(";") if "=" in kv)))
    return out


def max_voices(plays):
    pk = 0
    for p in plays:
        n = sum(1 for q in plays if q["t_ms"] <= p["t_ms"] < q["t_ms"] + MAP["cues"][q["cue"]]["duration_ms"] and MAP["cues"][q["cue"]]["category"] == MAP["cues"][p["cue"]]["category"])
        pk = max(pk, n)
    return pk


def max_per_second(plays):
    return max([sum(1 for q in plays if p["t_ms"] <= q["t_ms"] < p["t_ms"] + 1000) for p in plays] + [0])


def checks():
    import ref_sim
    w = ref_sim.World(ref_sim.load_level())
    res, D = [], MAP["defaults"]

    def ok(n, c):
        res.append((n, bool(c)))
    runs = {}
    for k, s in (("A/E", ["A", "E"]), ("none", [])):
        r = w.run(s)
        runs[k] = (from_lines(w.lines), r["arrived"] >= 18)
    pl, bed = schedule(runs["A/E"][0], D, True)
    cues = [p["cue"] for p in pl]
    ok("A/E: exactly one result sound and it is the success cue", cues.count("result_success") == 1 and cues.count("result_failure") == 0 and pl[-1]["cue"] == "result_success")
    pn, _ = schedule(runs["none"][0], D, False)
    ok("no sign (fail): the failure cue, not the success cue", [p["cue"] for p in pn].count("result_failure") == 1 and "result_success" not in [p["cue"] for p in pn])
    ok("A/E: 20 arrivals give at most 20 arrival plucks and each pitch is on the pentatonic scale", cues.count("arrival_pluck") <= 20 and all(p["pitch"] % 12 in (0, 2, 4, 7, 9) for p in pl if p["cue"] == "arrival_pluck"))
    ok("A/E: at most %d triggers in any second" % MAP["limits"]["max_triggers_per_second"], max_per_second(pl) <= MAP["limits"]["max_triggers_per_second"])
    ok("every play traces to a real event of the matching type", all(from_lines_types(runs["A/E"][0], p) for p in pl))
    ok("no pickup, turn or drop sound in a run with no sign commands", not any(c in ("sign_pickup", "sign_turn", "sign_drop") for c in [p["cue"] for p in pn]))
    ok("A/E: the foot bed is a gain series, never per-step triggers (no foot cue in plays)", "foot_bed" not in cues and len(bed) > 0 and max(g for _, g in bed) <= D["master"] * D["texture"] + 1e-9)
    # muted and slider independence
    mute = dict(D, master=0.0)
    ok("master 0: no sound at all", schedule(runs["A/E"][0], mute, True)[0] == [] and all(g == 0 for _, g in schedule(runs["A/E"][0], mute, True)[1]))
    nofx = dict(D, effects=0.0)
    pf, bf = schedule(runs["A/E"][0], nofx, True)
    ok("effects 0: no effect cues but the foot bed continues (independent sliders)", pf == [] and max(g for _, g in bf) > 0)
    notx = dict(D, texture=0.0)
    ok("texture 0: effects continue, bed silent", len(schedule(runs["A/E"][0], notx, True)[0]) == len(pl) and max([g for _, g in schedule(runs["A/E"][0], notx, True)[1]] + [0]) == 0)
    ok("deterministic: same input, same output", json.dumps(schedule(runs["A/E"][0], D, True)) == json.dumps(schedule(runs["A/E"][0], D, True)))
    # critical cues have a visual equivalent
    crit = [k for k, v in MAP["cues"].items() if v["critical"]]
    reg = VIS["visuals"]
    ok("every gameplay-critical cue names a visual equivalent that exists in the registry", all(MAP["cues"][k]["visual"] in reg for k in crit))
    trs = {t["id"] for t in json.loads((ROOT / "data/transitions.json").read_text())["transitions"]}
    ok("visuals that name a transition point at a real transition id", all(m in trs for v in reg for m in re.findall(r"transition:(\w+)", v)))
    # 50-walker stress
    ev, t = [], 0
    for wk in range(50):
        t0 = wk * 160
        ev += [(t0, "DECISION", dict(walker=str(wk), reason="sign_flipped")), (t0 + 10, "QUEUE_JOINED", dict(walker=str(wk), edge="A>B", position=str(3 + wk % 3))),
               (t0 + 20, "EDGE_ENTERED", dict(walker=str(wk), edge="A>B")), (t0 + 2000 + wk * 30, "NODE_ARRIVED", dict(walker=str(wk), node="B")),
               (t0 + 2001 + wk * 30, "WALKER_ARRIVED", dict(walker=str(wk), arrival_tick="1", on_time="1"))]
    ev.sort(key=lambda e: e[0])
    ev.append((ev[-1][0] + 100, "RUN_ENDED", dict(reason="time_limit")))
    ps, bs = schedule(ev, D, True)
    ok("50 walkers: at most 10 triggers in any second (%d)" % max_per_second(ps), max_per_second(ps) <= 10)
    ok("50 walkers: at most %d overlapping effect voices (%d)" % (MAP["limits"]["max_voices"]["effects"] + 1, max_voices(ps)), max_voices(ps) <= MAP["limits"]["max_voices"]["effects"] + 1)
    ok("50 walkers: queue compression plays at most once per 4 s on one street", all(b["t_ms"] - a["t_ms"] >= 4000 for a, b in zip([p for p in ps if p["cue"] == "queue_compress"], [p for p in ps if p["cue"] == "queue_compress"][1:])))
    ok("50 walkers: fewer sound triggers than events (%d of %d)" % (len(ps), len(ev)), len(ps) < len(ev) / 2)
    ok("50 walkers: the result sound still plays exactly once", [p["cue"] for p in ps].count("result_success") == 1)
    return res


def from_lines_types(events, p):
    rules = [r["event"] for r in MAP["events"] if (r.get("cue") == p["cue"]) or p["cue"] in (r.get("cue_if_passed"), r.get("cue_if_failed"))]
    return events[p["source"]][1] in rules


def main():
    bad = 0
    for n, c in checks():
        print(("PASS " if c else "FAIL ") + n)
        bad += not c
    print("AUDIO RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

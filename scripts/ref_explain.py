"""Reference for the causal reason selector (src/simulation/explainer.gd), Stage 13.
Every sentence is built from counted events of the real run and, for 'helped or hurt', from an actually executed
NO_SIGN run on the same level and seed. A claim that cannot be derived from those two runs is never produced.
Usage: python3 -I scripts/ref_explain.py     (runs the checks against real traces from scripts/ref_sim.py)
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
HEAD_NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
MATERIAL_BLOCKED_PCT = 10.0


def parse(lines):
    out = []
    for ln in lines:
        tick, seq, typ, rest = ln.split("|", 3)
        f = {}
        for kv in rest.split(";"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                f[k] = v
        out.append((int(tick), int(seq), typ, f))
    return out


def street(edge, names):
    a, b = edge.split(">")
    return "%s to %s" % (names[a], names[b])


def tenths(ticks):
    """ticks / 20 seconds to one decimal, rounding half up with integers (float formatting differs between Python and GDScript)."""
    t = (ticks + 1) // 2
    return "%d.%d" % (t // 10, t % 10)


def secs(ticks):
    return tenths(ticks) + " s"


def explain(lines, result, baseline, replay, names, goal=18, total=20):
    """lines: event lines of the real run. result/baseline: result dicts of that run and of the executed NO_SIGN run
    (baseline may be None: then no comparison claim exists). replay: {"initial_sign": [slot, head] or [], "actions": [...]}.
    Returns ordered claims; each: id, kind, text, evidence {event, count, ...}."""
    ev = parse(lines)
    claims = []
    arrivals = [e for e in ev if e[2] == "WALKER_ARRIVED"]
    reached = result["arrived"] >= goal
    claims.append(dict(id="result", kind="RESULT", evidence=dict(event="WALKER_ARRIVED", count=len(arrivals)),
                       text="%d / %d arrived. Goal %d: %s." % (len(arrivals), total, goal, "reached" if reached else "%d short" % (goal - len(arrivals)))))
    sign = replay.get("initial_sign", [])
    flips = [e for e in ev if e[2] == "DECISION" and e[3].get("reason") == "sign_flipped"]
    if not sign and not replay.get("actions"):
        claims.append(dict(id="no_sign", kind="NO_SIGN", evidence=dict(event="none", count=0), text="No sign was placed in this round."))
    else:
        groups = {}
        for t, s, typ, f in flips:
            groups.setdefault((f["node"], f["chosen_edge"], f["alt_edge"]), set()).add(f["walker"])
        walkers = set().union(*groups.values()) if groups else set()
        where = "%s (pointing %s)" % (names[sign[0]], HEAD_NAME[sign[1]]) if sign else "the sign"
        if not walkers:
            claims.append(dict(id="reroute", kind="NO_REROUTE", evidence=dict(event="DECISION:sign_flipped", count=0),
                               text="Your sign at %s changed no walker's route." % where))
        else:
            top = max(groups.items(), key=lambda kv: (len(kv[1]), "|".join(kv[0])))
            (node, chosen, alt), ws = top
            share = "all of them" if len(ws) == len(walkers) else "%d of them" % len(ws)
            claims.append(dict(id="reroute", kind="REROUTE", evidence=dict(event="DECISION:sign_flipped", count=len(walkers), decisions=len(flips), top_group_walkers=len(ws)),
                               text="Your sign at %s changed the route of %d walker%s: %s at %s took %s instead of %s." % (
                                   where, len(walkers), "" if len(walkers) == 1 else "s", share, names[node], street(chosen, names), street(alt, names))))
        if baseline is not None:
            da = result["arrived"] - baseline["arrived"]
            flip = reached != (baseline["arrived"] >= goal)
            bp = 100.0 * (result["blocked_ticks"] - baseline["blocked_ticks"]) / max(1, baseline["blocked_ticks"])
            if da > 0 or (flip and reached):
                kind, txt = "HELPED", "Compared with no sign on the same seed, your sign delivered %d more (%d against %d)%s." % (
                    da, result["arrived"], baseline["arrived"], " and turned a miss into a pass" if flip else "")
            elif da < 0 or (flip and not reached):
                kind, txt = "HURT", "Compared with no sign on the same seed, your sign delivered %d fewer (%d against %d)." % (-da, result["arrived"], baseline["arrived"])
            elif abs(bp) >= MATERIAL_BLOCKED_PCT:
                kind, txt = ("HELPED" if bp < 0 else "HURT"), "Same arrivals as no sign on the same seed (%d), but %.0f%% %s time spent waiting." % (
                    result["arrived"], abs(bp), "less" if bp < 0 else "more")
            else:
                kind, txt = "NO_MATERIAL_CHANGE", "The result matches no sign on the same seed (%d against %d arrived)." % (result["arrived"], baseline["arrived"])
            claims.append(dict(id="material", kind=kind, evidence=dict(event="baseline_run", arrived=result["arrived"], baseline_arrived=baseline["arrived"],
                                                                      blocked=result["blocked_ticks"], baseline_blocked=baseline["blocked_ticks"]), text=txt))
    # bottleneck: total queue wait per street from QUEUE_JOINED to EDGE_ENTERED (or to the end of the round)
    joined, wait = {}, {}
    end_tick = max([e[0] for e in ev] + [0])
    for t, s, typ, f in ev:
        if typ == "QUEUE_JOINED":
            joined[(f["walker"], f["edge"])] = t
        elif typ == "QUEUE_LEFT":
            joined.pop((f["walker"], f["edge"]), None)
        elif typ == "EDGE_ENTERED":
            j = joined.pop((f["walker"], f["edge"]), None)
            if j is not None:
                key = "|".join(sorted(f["edge"].split(">")))
                wait[key] = wait.get(key, 0) + (t - j)
    for (wk, e), j in joined.items():
        key = "|".join(sorted(e.split(">")))
        wait[key] = wait.get(key, 0) + (end_tick - j)
    if wait:
        key, total_w = max(wait.items(), key=lambda kv: (kv[1], kv[0]))
        if total_w >= 100:
            a, b = key.split("|")
            claims.append(dict(id="bottleneck", kind="BOTTLENECK", evidence=dict(event="QUEUE_JOINED/EDGE_ENTERED", street=key, wait_ticks=total_w),
                               text="Most waiting: %s and %s, %s walker-seconds in queues (all walkers added up)." % (names[a], names[b], tenths(total_w))))
    late = [e for e in arrivals if e[3]["on_time"] == "0"]
    if late:
        claims.append(dict(id="late", kind="LATE", evidence=dict(event="WALKER_ARRIVED:on_time=0", count=len(late)),
                           text="%d walker%s arrived after the deadline." % (len(late), "" if len(late) == 1 else "s")))
    return claims


def select(claims, limit=3):
    order = ["RESULT", "NO_SIGN", "HELPED", "HURT", "NO_MATERIAL_CHANGE", "NO_REROUTE", "REROUTE", "BOTTLENECK", "LATE"]
    return sorted(claims, key=lambda c: order.index(c["kind"]))[:limit]


BANNED = ["would have", "if you had", "could have", "should have", "lazy", "stupid", "old people", "kids", "women", "men "]


def checks():
    import ref_sim
    w = ref_sim.World(ref_sim.load_level())
    names = {n["id"]: n["name"] for n in w.level["nodes"]}
    runs = {}
    for k, s in (("none", []), ("A/E", ["A", "E"]), ("A/N", ["A", "N"]), ("A/S", ["A", "S"]), ("B/E", ["B", "E"]), ("B/N", ["B", "N"])):
        r = w.run(s)
        runs[k] = (r, list(w.lines), {"initial_sign": s, "actions": []})
    base = runs["none"][0]
    res = []

    def ok(name, cond):
        res.append((name, bool(cond)))
    out = {k: explain(v[1], v[0], base, v[2], names) for k, v in runs.items()}
    # independent recount from the raw text
    for k, v in runs.items():
        lines = v[1]
        cl = {c["id"]: c for c in out[k]}
        n_arr = sum(1 for l in lines if "|WALKER_ARRIVED|" in l)
        ok(f"{k}: arrivals claim equals a raw recount ({n_arr})", cl["result"]["evidence"]["count"] == n_arr == v[0]["arrived"])
        if "reroute" in cl and cl["reroute"]["kind"] == "REROUTE":
            ws = {re.search(r"walker=(\d+)", l).group(1) for l in lines if "|DECISION|" in l and "reason=sign_flipped" in l}
            ok(f"{k}: rerouted-walker count equals a raw recount ({len(ws)})", cl["reroute"]["evidence"]["count"] == len(ws))
        if k in ("A/N", "B/N"):
            ok(f"{k}: a sign that changed no route says so and claims no help or harm", cl["reroute"]["kind"] == "NO_REROUTE" and cl["material"]["kind"] == "NO_MATERIAL_CHANGE")
        ok(f"{k}: copy has no counterfactual or stereotype phrases", all(not any(b in c["text"] for b in BANNED) for c in out[k]))
        ok(f"{k}: output is deterministic", json.dumps(out[k]) == json.dumps(explain(lines, v[0], base, v[2], names)))
    ok("A/E: helped, +3 arrivals, a miss turned into a pass", next(c for c in out["A/E"] if c["id"] == "material")["kind"] == "HELPED"
       and "3 more (20 against 17)" in next(c for c in out["A/E"] if c["id"] == "material")["text"] and "turned a miss into a pass" in next(c for c in out["A/E"] if c["id"] == "material")["text"])
    ok("B/E: helped although only 2 walkers were re-routed (a cascade the copy does not exaggerate)",
       next(c for c in out["B/E"] if c["id"] == "reroute")["evidence"]["count"] == 2 and next(c for c in out["B/E"] if c["id"] == "material")["kind"] == "HELPED")
    # no sign at all
    ns = explain(runs["none"][1], runs["none"][0], base, {"initial_sign": [], "actions": []}, names)
    ok("no sign: says so and makes no sign claim", [c["kind"] for c in ns if c["kind"] in ("REROUTE", "NO_REROUTE", "HELPED", "HURT", "NO_MATERIAL_CHANGE")] == [] and any(c["kind"] == "NO_SIGN" for c in ns))
    # tamper: remove the sign_flipped lines, the reroute claim must follow
    lines = [l for l in runs["A/E"][1] if "reason=sign_flipped" not in l]
    t = explain(lines, runs["A/E"][0], base, runs["A/E"][2], names)
    ok("removing the sign_flipped events removes the reroute claim", next(c for c in t if c["id"] == "reroute")["kind"] == "NO_REROUTE")
    # no baseline: no comparison claim
    nb = explain(runs["A/E"][1], runs["A/E"][0], None, runs["A/E"][2], names)
    ok("without an executed baseline there is no helped/hurt claim", all(c["id"] != "material" for c in nb))
    # materiality on synthetic results
    r0 = dict(arrived=17, blocked_ticks=1000)
    for label, r, want in (("more arrivals", dict(arrived=18, blocked_ticks=1000), "HELPED"), ("fewer arrivals", dict(arrived=16, blocked_ticks=1000), "HURT"),
                           ("same arrivals, 12% less waiting", dict(arrived=17, blocked_ticks=880), "HELPED"),
                           ("same arrivals, 5% more waiting", dict(arrived=17, blocked_ticks=1050), "NO_MATERIAL_CHANGE")):
        c = explain(runs["A/E"][1], r, r0, runs["A/E"][2], names)
        ok("materiality: " + label + " -> " + want, next(x for x in c if x["id"] == "material")["kind"] == want)
    ok("select keeps the result first and at most three lines", select(out["A/E"])[0]["kind"] == "RESULT" and len(select(out["A/E"])) <= 3)
    # bottleneck comes from a real street
    for k in ("none", "A/E"):
        b = [c for c in out[k] if c["id"] == "bottleneck"]
        ok(f"{k}: bottleneck street exists in the level", all(c["evidence"]["street"].split("|")[0] in names for c in b))
    ok("the no-sign run names Canal Turn and Bridge West as the bottleneck",
       any("Canal Turn and Bridge West" in c["text"] for c in out["none"] if c["id"] == "bottleneck"))
    return res, out


def main():
    res, out = checks()
    bad = 0
    for n, c in res:
        print(("PASS " if c else "FAIL ") + n)
        bad += not c
    if "--show" in sys.argv:
        for k, cl in out.items():
            print("==", k)
            for c in select(cl):
                print("  ", c["text"])
    print("EXPLAIN RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

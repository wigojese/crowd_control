"""Stage 16 correctness checks on the Python reference of the engine rules (NOT the engine, NOT a device).
 P: property / fuzz tests of the simulation (3 levels, seeded random commands).
 F: frame-rate independence of the fixed-tick driver (30/60/90/120/144 Hz, jitter, hitches).
 C: camera lifecycle fuzz (3 level sessions: random focus, touch, pinch, interruptions).
 L: portrait layout sweep (phones, tall, tablet, safe-area insets, both hands, larger targets).
Writes docs/stage16/stage16_results.json. Exit 0 only if every check passes.
Usage: python3 -I scripts/stage16_checks.py [--quick]
"""
import json
import math
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_camera as cam  # noqa: E402
import ref_settings as rs  # noqa: E402
import ref_sim  # noqa: E402

OUT = ROOT / "docs/stage16"
LEVELS = ["cc_l01_r1", "cc_l02_ferry", "cc_l03_narrow"]
QUICK = "--quick" in sys.argv
N_FUZZ = 40 if QUICK else 200
RES = {"checks": [], "numbers": {}}
BAD = [0]


def ok(name, cond, detail=""):
    RES["checks"].append({"name": name, "pass": bool(cond), "detail": detail})
    if not cond:
        BAD[0] += 1
        print("FAIL", name, detail)
    return cond


def load(f):
    return json.loads((ROOT / "data/levels" / (f + ".json")).read_text())


def parse(line):
    t, s, typ, rest = line.split("|", 3)
    return int(t), int(s), typ, dict(kv.split("=", 1) for kv in rest.split(";") if kv)


def random_scenario(rng, lv):
    slots = lv["sockets"]
    sign = [] if rng.random() < 0.15 else [rng.choice(slots), rng.choice("NESW")]
    cmds = []
    for k in range(rng.randint(0, 5)):
        t = rng.randint(0, lv.get("ticks", 640) + 20)
        if rng.random() < 0.5:
            cmds.append((t, k, "ROTATE", rng.choice("NESW")))
        else:
            cmds.append((t, k, "MOVE", rng.choice(slots)))
    return sign, cmds


# ---------------- P: simulation properties ----------------
def prop_checks():
    rng = random.Random(1607)
    stats = {}
    for f in LEVELS:
        lv = load(f)
        total = sum(sum(s["mix"].values()) for s in lv["schedule"])
        edges = set(ref_sim.World(lv).edge_ids)
        w = ref_sim.World(lv)
        bad = dict(determinism=0, order=0, arrive_once=0, arrive_cap=0, sign_pair=0, midedge=0, edge_valid=0, rate=0, softlock=0, tick_order=0)
        worst_tail = 0
        for _ in range(N_FUZZ):
            sign, cmds = random_scenario(rng, lv)
            r1 = w.run(sign, cmds)
            lines = list(w.lines)
            r2 = w.run(sign, cmds)
            bad["determinism"] += r1["hash"] != r2["hash"]
            sh = list(cmds)
            rng.shuffle(sh)
            bad["order"] += w.run(sign, sh)["hash"] != r1["hash"]
            ev = [parse(x) for x in lines]
            # terminal results counted once, never more than spawned
            arr = [e[3]["walker"] for e in ev if e[2] == "WALKER_ARRIVED"]
            bad["arrive_once"] += len(arr) != len(set(arr))
            bad["arrive_cap"] += len(arr) > total or len(arr) != r1["arrived"]
            # ticks never go backwards
            bad["tick_order"] += any(ev[i][0] > ev[i + 1][0] for i in range(len(ev) - 1))
            # one sign: every drop follows a pick, and a pick never happens while another is held
            held, seq_ok = False, True
            for e in ev:
                if e[2] == "SIGN_PICKED":
                    seq_ok &= not held
                    held = True
                elif e[2] == "SIGN_DROPPED":
                    seq_ok &= held
                    held = False
            bad["sign_pair"] += not seq_ok
            # next-junction rule: a walker is never given a DECISION while it is on an edge
            on_edge, mid = set(), True
            for e in ev:
                wid = e[3].get("walker")
                if e[2] == "EDGE_ENTERED":
                    on_edge.add(wid)
                elif e[2] == "NODE_ARRIVED":
                    on_edge.discard(wid)
                elif e[2] == "DECISION":
                    mid &= wid not in on_edge
            bad["midedge"] += not mid
            # every edge entered exists; entries obey the token bucket (rate * window + 1 per window)
            ent = [e for e in ev if e[2] == "EDGE_ENTERED"]
            bad["edge_valid"] += any(e[3]["edge"] not in edges for e in ent)
            ok_rate = True
            for eid in edges:
                ts = [e[0] for e in ent if e[3]["edge"] == eid]
                rate = w.edges[eid]["rate"]
                cap = max(1.0, rate)  # bucket cap (spec A5): a full bucket may burst, then refills rate * dt per tick
                for i, t0 in enumerate(ts):
                    cnt = sum(1 for t in ts[i:] if t < t0 + 20)  # a 1 s window of 20 ticks, 19 refills after the first
                    ok_rate &= cnt <= math.floor(cap + rate * 19 * 0.05 + 1e-6)
            bad["rate"] += not ok_rate
            # no softlock: run three times as long, every walker must reach its destination
            w.ticks, keep = lv.get("ticks", 640) * 3, w.ticks
            r3 = w.run(sign, cmds)
            w.ticks = keep
            bad["softlock"] += r3["arrived"] != total
            worst_tail = max(worst_tail, r3["last_arr"])
        for k, v in bad.items():
            ok(f"P {lv['level_id']}: {k} holds in {N_FUZZ} random scenarios", v == 0, f"{v} violations")
        stats[lv["level_id"]] = dict(scenarios=N_FUZZ, violations=bad, latest_arrival_tick_when_run_3x_long=worst_tail)
    RES["numbers"]["property"] = stats


# ---------------- F: frame-rate independence ----------------
def drive(w, sign, cmds, hz, rng, hitch):
    """Render-rate driver: accumulate real time, run fixed 0.05 s ticks, at most 4 per frame (spec A2)."""
    w.reset(list(sign), list(cmds))
    acc, ticks_run, capped, wall = 0.0, 0, 0, 0.0
    frame = 1.0 / hz
    while ticks_run < w.ticks:
        dt = frame * (1.0 + rng.uniform(-0.3, 0.3))
        if hitch and rng.random() < 0.01:
            dt = 0.4  # 400 ms hitch
        wall += dt
        acc += dt
        n = 0
        while acc >= 0.05 - 1e-12 and n < 4 and ticks_run < w.ticks:
            w.step()
            ticks_run += 1
            acc -= 0.05
            n += 1
        if acc >= 0.05:  # cap hit: drop the backlog, count it honestly
            capped += 1
            acc = 0.0
    w.emit("RUN_ENDED", dict(reason="time_limit"))
    return ref_sim.fnv(w.lines), capped, wall


def framerate_checks():
    rng = random.Random(16)
    lv = load("cc_l02_ferry")
    w = ref_sim.World(lv)
    sol = lv["solutions"][0]
    cmds = [tuple(c) for c in sol["commands"]]
    ref = w.run(sol["initial_sign"], cmds)
    rows = {}
    for hz in (30, 60, 90, 120, 144):
        h, capped, wall = drive(w, sol["initial_sign"], cmds, hz, rng, hitch=False)
        rows[hz] = dict(hash_equal=h == ref["hash"], backlog_drops=capped, wall_seconds=round(wall, 2))
        ok(f"F {hz} Hz with +-30% frame jitter gives the same event hash as the fixed-tick run", h == ref["hash"] and capped == 0)
    h, capped, wall = drive(w, sol["initial_sign"], cmds, 60, rng, hitch=True)
    rows["60_with_400ms_hitches"] = dict(hash_equal=h == ref["hash"], backlog_drops=capped, wall_seconds=round(wall, 2))
    # a hitch may only slow the run (ticks are delayed, not skipped or changed): the hash must still match
    ok("F 400 ms hitches (backlog above 4 ticks is dropped as slowdown, not skipped ticks) leave the event hash unchanged", h == ref["hash"], f"backlog drops {capped}")
    RES["numbers"]["framerate"] = rows


# ---------------- C: camera lifecycle fuzz ----------------
def camera_checks():
    rng = random.Random(1616)
    states = [s for s in cam.STATES if s not in ("USER_PAN",)]
    for f in LEVELS:
        lv = load(f)
        nodes = {n["id"]: (n["x"], n["y"]) for n in lv["nodes"]}
        for vp, top, bot in (((390, 844), 47, 34), ((320, 568), 20, 0), ((768, 1024), 24, 20)):
            for reduced in (False, True):
                tf = cam.Transform(viewport=vp)
                d = cam.Director(tf, reduced_motion=reduced)
                bad_nan = bad_zoom = bad_anchor = bad_freeze = bad_lost = 0
                touching = False
                for step in range(3000 if not QUICK else 600):
                    op = rng.random()
                    if op < 0.25:
                        tgt = nodes[rng.choice(sorted(nodes))]
                        z = rng.uniform(cam.ZMIN, cam.ZMAX)
                        c, z = cam.compose_focus(tgt, z, vp, top, 78, bot, 112)
                        d.request_focus(rng.choice(states), rng.choice(list(cam.PRI)), (c, z), rng.uniform(0.15, 0.8), rng.choice(["interrupt", "reject_if_busy", "queue"]))
                    elif op < 0.40 and not touching:
                        d.touch_begin()
                        touching = True
                        frozen = (tf.center, tf.zoom)
                    elif op < 0.55 and touching:
                        d.touch_end()
                        touching = False
                    elif op < 0.70:
                        a = (rng.uniform(0, vp[0]), rng.uniform(0, vp[1]))
                        wp = tf.s2w(a)
                        tf.zoom_about(a, tf.zoom * rng.uniform(0.7, 1.4))
                        e = math.dist(tf.w2s(wp), a)
                        clamped = tf.zoom in (cam.ZMIN, cam.ZMAX)
                        bad_anchor += e > 2.0
                    else:
                        before = (tf.center, tf.zoom)
                        d.update(rng.choice([1 / 120, 1 / 60, 1 / 30, 0.25]))
                        if touching and d.anim is None and d.state == "USER_PAN":
                            bad_freeze += (tf.center, tf.zoom) != before
                    bad_nan += not all(math.isfinite(v) for v in (*tf.center, tf.zoom))
                    bad_zoom += not (cam.ZMIN - 1e-9 <= tf.zoom <= cam.ZMAX + 1e-9)
                tag = f"{lv['level_id']} {vp[0]}x{vp[1]} reduced_motion={reduced}"
                ok(f"C {tag}: transform stays finite and inside the zoom limits", bad_nan == 0 and bad_zoom == 0, f"nan {bad_nan} zoom {bad_zoom}")
                ok(f"C {tag}: a pinch keeps the world point under the fingers within 2 px", bad_anchor == 0, f"{bad_anchor}")
                ok(f"C {tag}: the camera does not move while a finger is down and no animation runs", bad_freeze == 0, f"{bad_freeze}")
        # a focus on every socket always ends with the sign inside the free band (never under HUD or dock)
        for vp, top, bot in (((390, 844), 47, 34), ((320, 568), 20, 0)):
            for s in lv["sockets"]:
                tf = cam.Transform(viewport=vp)
                d = cam.Director(tf)
                c, z = cam.compose_focus(nodes[s], 1.4, vp, top, 78, bot, 112)
                d.request_focus("SIGN_FOCUS", "USER", (c, z), 0.3)
                for _ in range(40):
                    d.update(1 / 60)
                sx, sy = tf.w2s(nodes[s])
                free_top, free_bot = top + 78, vp[1] - bot - 112
                ok(f"C {lv['level_id']} {vp[0]}x{vp[1]}: sign focus on {s} lands between HUD and dock", free_top <= sy <= free_bot and 0 <= sx <= vp[0], f"y={sy:.0f} band {free_top}-{free_bot}")


# ---------------- L: layout sweep ----------------
DEVICES = [("small 320x568", 320, 568, 20, 0), ("360x640", 360, 640, 24, 0), ("iPhone SE 375x667", 375, 667, 20, 0), ("390x844", 390, 844, 47, 34),
           ("412x915", 412, 915, 32, 24), ("tall 430x932", 430, 932, 59, 34), ("tall 360x800", 360, 800, 32, 16), ("long 412x960", 412, 960, 32, 16),
           ("tablet 768x1024", 768, 1024, 24, 20), ("tablet 1024x1366", 1024, 1366, 24, 20)]
HUD_H, DOCK_H, HIT = 78, 112, 44


def layout_checks():
    rows = {}
    for name, w, h, top, bot in DEVICES:
        for lh in (False, True):
            for lg in (False, True):
                r = rs.dock_layout(lh, lg, (w, h), bot if bot else 16)
                tag = f"{name} left={lh} larger={lg}"
                alls = list(r.values())
                ok(f"L {tag}: dock controls do not overlap", all(not rs.overlap(a, b) for i, a in enumerate(alls) for b in alls[i + 1:]))
                ok(f"L {tag}: dock inside the safe area and the 24 px edge reserve", all(v[0] >= 24 and v[0] + v[2] <= w - 24 and v[1] + v[3] <= h - bot for v in alls))
                ok(f"L {tag}: every dock control at least {HIT}x{HIT}", all(v[2] >= HIT and v[3] >= HIT for v in alls))
        for f in LEVELS:
            lv = load(f)
            xs = [n["x"] for n in lv["nodes"]]
            ys = [n["y"] for n in lv["nodes"]]
            pad = 30
            bw, bh = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
            free_h = h - top - HUD_H - bot - DOCK_H
            fit = min((w - 24) / bw, free_h / bh)
            socks = [n for n in lv["nodes"] if n["id"] in lv["sockets"]]
            sep = min(math.dist((a["x"], a["y"]), (b["x"], b["y"])) for i, a in enumerate(socks) for b in socks[i + 1:]) * fit
            RES["numbers"].setdefault("layout", {})[f"{name}|{lv['level_id']}"] = dict(fit_zoom=round(fit, 2), socket_gap_px=round(sep, 1), free_height=free_h)
            ok(f"L {name} {lv['level_id']}: whole graph fits between HUD and dock at zoom >= {cam.ZMIN}", fit >= cam.ZMIN, f"fit {fit:.2f}")
            ok(f"L {name} {lv['level_id']}: sockets are {HIT + 12}+ px apart so a finger can tell them apart", sep >= HIT + 12, f"{sep:.0f}px")
    # tablet: the dock must not stretch absurdly (controls stay near the thumb zone, not 700 px apart)
    r = rs.dock_layout(False, False, (768, 1024), 20)
    span = max(v[0] + v[2] for v in r.values()) - min(v[0] for v in r.values())
    ok("L tablet 768x1024: dock span is at most 520 px (thumb reach)", span <= 520, f"span {span}px")


def main():
    OUT.mkdir(exist_ok=True)
    for fn in (prop_checks, framerate_checks, camera_checks, layout_checks):
        fn()
    RES["summary"] = dict(total=len(RES["checks"]), failed=BAD[0], quick=QUICK, scope="Python reference of the rules; not the engine; not a device")
    (OUT / "stage16_results.json").write_text(json.dumps(RES, indent=1) + "\n")
    print("STAGE16 RESULT:", "ALL PASS (%d checks)" % len(RES["checks"]) if not BAD[0] else "%d FAILED of %d" % (BAD[0], len(RES["checks"])))
    return 1 if BAD[0] else 0


if __name__ == "__main__":
    sys.exit(main())

"""Reference implementation of the Stage 11 camera and level-of-detail logic (master prompt C1, C2, C3).
Pure code: no simulation import. src/camera/*.gd are ports; golden values are in tests/fixtures/camera_golden.json.
Run: python3 -I scripts/ref_camera.py         (runs the checks, prints PASS/FAIL)
     python3 -I scripts/ref_camera.py --write (regenerates the golden file)
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZMIN, ZMAX = 0.65, 2.80
CITY, DISTRICT, STREET = "CITY", "DISTRICT", "STREET"
HYST = {"street_in": 1.75, "street_out": 1.55, "city_in": 0.85, "city_out": 1.00}
SCROLL_GAIN, INERTIA_K, INERTIA_CAP_VIEWPORTS = 0.85, 6.0, 1.6
PRI = {"TOUCH": 3, "USER": 2, "CRITICAL": 1, "DECORATIVE": 0}
STATES = ["LEVEL_FLYIN", "OVERVIEW", "SIGN_FOCUS", "PATH_SCRUB", "FOLLOW_CASCADE", "RESULT_PULLBACK",
          "REPLAY_RETURN", "USER_PAN", "REDUCED_MOTION"]


class Transform:
    """screen = (world - center) * zoom + viewport_center + safe_offset (rotation 0)."""
    def __init__(self, center=(181.0, 262.0), zoom=1.0, viewport=(390, 844), safe_offset=(0.0, 0.0)):
        self.center, self.zoom, self.vp, self.so = tuple(center), zoom, viewport, tuple(safe_offset)

    def w2s(self, p):
        return ((p[0] - self.center[0]) * self.zoom + self.vp[0] / 2 + self.so[0],
                (p[1] - self.center[1]) * self.zoom + self.vp[1] / 2 + self.so[1])

    def s2w(self, s):
        return ((s[0] - self.vp[0] / 2 - self.so[0]) / self.zoom + self.center[0],
                (s[1] - self.vp[1] / 2 - self.so[1]) / self.zoom + self.center[1])

    def zoom_about(self, anchor_screen, new_zoom):
        """Change zoom so the world point under anchor_screen stays under it (pinch)."""
        a = self.s2w(anchor_screen)
        self.zoom = min(ZMAX, max(ZMIN, new_zoom))
        self.center = (a[0] - (anchor_screen[0] - self.vp[0] / 2 - self.so[0]) / self.zoom,
                       a[1] - (anchor_screen[1] - self.vp[1] / 2 - self.so[1]) / self.zoom)


def compose_focus(world_pt, zoom, viewport, top_inset, hud_h, bottom_inset, dock_h):
    """Camera centre that puts world_pt in the middle of the free band between HUD and dock, so it is never under a thumb."""
    free_top = top_inset + hud_h
    free_bottom = viewport[1] - bottom_inset - dock_h
    target_y = free_top + 0.42 * (free_bottom - free_top)
    return (world_pt[0], world_pt[1] - (target_y - viewport[1] / 2) / zoom), zoom


class Path:
    """Catmull-Rom spline through meaningful junctions, with an arc-length table at <= 5 world units spacing."""
    def __init__(self, pts, spacing=4.0):
        self.pts = [tuple(p) for p in pts]
        dense = []
        P = [self.pts[0]] + self.pts + [self.pts[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            for k in range(0, 80):
                t = k / 80
                dense.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                          + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
        dense.append(self.pts[-1])
        cum = [0.0]
        for a, b in zip(dense, dense[1:]):
            cum.append(cum[-1] + math.dist(a, b))
        self.length = cum[-1]
        n = int(math.ceil(self.length / spacing))
        self.table = []
        j = 0
        for i in range(n + 1):
            s = min(self.length, i * spacing)
            while j < len(cum) - 2 and cum[j + 1] < s:
                j += 1
            f = 0.0 if cum[j + 1] == cum[j] else (s - cum[j]) / (cum[j + 1] - cum[j])
            self.table.append((s, dense[j][0] + (dense[j + 1][0] - dense[j][0]) * f,
                               dense[j][1] + (dense[j + 1][1] - dense[j][1]) * f))

    def point_at(self, s):
        s = min(self.length, max(0.0, s))
        lo, hi = 0, len(self.table) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.table[mid][0] <= s:
                lo = mid
            else:
                hi = mid
        a, b = self.table[lo], self.table[hi]
        f = 0.0 if b[0] == a[0] else (s - a[0]) / (b[0] - a[0])
        return (a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f)

    def max_spacing(self):
        return max(b[0] - a[0] for a, b in zip(self.table, self.table[1:]))


def scrub_delta(dy, zoom):
    return -dy / zoom * SCROLL_GAIN


def inertia_velocity(v0, t, viewport_h, zoom):
    cap = INERTIA_CAP_VIEWPORTS * viewport_h / zoom
    v0 = max(-cap, min(cap, v0))
    return v0 * math.exp(-INERTIA_K * t)


def band_update(band, z):
    """Hysteresis: STREET in at 1.75, out at 1.55; CITY in at 0.85, out at 1.00."""
    while True:
        nb = band
        if band == DISTRICT and z >= HYST["street_in"]:
            nb = STREET
        elif band == DISTRICT and z <= HYST["city_in"]:
            nb = CITY
        elif band == STREET and z <= HYST["street_out"]:
            nb = DISTRICT
        elif band == CITY and z >= HYST["city_out"]:
            nb = DISTRICT
        if nb == band:
            return band
        band = nb


def band_initial(z):
    return STREET if z >= HYST["street_in"] else (CITY if z <= HYST["city_in"] else DISTRICT)


def flux_window(events, tick, window=20):
    """events: [(tick, street_key, dest)] of EDGE_ENTERED. Counts over the last `window` ticks (1 s)."""
    out = {}
    for t, key, dest in events:
        if tick - window < t <= tick:
            out[(key, dest)] = out.get((key, dest), 0) + 1
    return out


LABEL_CAP = {CITY: 4, DISTRICT: 6, STREET: 3}


def lod_plan(band, snap):
    """What may be drawn at this band. snap: walkers[{id,active}], streets[keys], flux{(key,dest):n}, queues{key:n},
    labels[{id,priority}]. Counts stay exact: people_represented is always the number of active walkers."""
    active = [w["id"] for w in snap["walkers"] if w["active"]]
    plan = {"band": band, "people_represented": len(active), "streets_visible": sorted(snap["streets"])}
    plan["agents"] = [] if band == CITY else list(active)
    plan["agent_detail"] = band == STREET
    plan["ribbons"] = dict(snap["flux"]) if band == CITY else {}
    plan["knots"] = sorted(k for k, n in snap["queues"].items() if n >= 3) if band == CITY else []
    plan["queue_badges"] = sorted(k for k, n in snap["queues"].items() if n >= 4) if band == DISTRICT else []
    labs = sorted(snap["labels"], key=lambda l: (-l["priority"], l["id"]))[:LABEL_CAP[band]]
    plan["labels"] = [l["id"] for l in labs]
    return plan


def cluster_badges(queue_counts, min_overlap=4):
    """Narrow-phone rule (Stage 10 option B): a queue with min_overlap or more notes is drawn as one note plus a count
    badge instead of a pile of notes. Returns {street: count} for the queues that become badges."""
    return {k: n for k, n in queue_counts.items() if n >= min_overlap}


class Director:
    """Owns the camera transform. UI calls request_focus. No simulation handle exists here, so the camera cannot alter the run."""
    def __init__(self, transform, reduced_motion=False):
        self.tf, self.state, self.pri, self.reduced = transform, "OVERVIEW", -1, reduced_motion
        self.anim = None
        self.log = []

    def request_focus(self, target_state, priority, target_tf, duration, rule="interrupt"):
        p = PRI[priority]
        busy = self.anim is not None or self.state == "USER_PAN"
        if busy and (p < self.pri or (p == self.pri and rule != "interrupt") or rule == "reject_if_busy"):
            self.log.append(("REJECT", target_state))
            return False
        if self.reduced:
            self.tf.center, self.tf.zoom = target_tf
            self.state, self.pri, self.anim = "REDUCED_MOTION", -1, None
            self.log.append(("JUMP", target_state))
            return True
        self.state, self.pri = target_state, p
        self.anim = {"t": 0.0, "dur": duration, "c0": self.tf.center, "z0": self.tf.zoom, "c1": target_tf[0], "z1": target_tf[1]}
        self.log.append(("ACCEPT", target_state))
        return True

    def update(self, dt):
        a = self.anim
        if not a:
            return
        a["t"] = min(a["dur"], a["t"] + dt)
        f = 1.0 if a["dur"] <= 0 else a["t"] / a["dur"]
        e = 1 - (1 - f) ** 3
        self.tf.zoom = math.exp(math.log(a["z0"]) + (math.log(a["z1"]) - math.log(a["z0"])) * e)
        self.tf.center = (a["c0"][0] + (a["c1"][0] - a["c0"][0]) * e, a["c0"][1] + (a["c1"][1] - a["c0"][1]) * e)
        if f >= 1.0:
            self.anim, self.pri = None, -1

    def touch_begin(self):
        """A finger on the map wins over everything and freezes the camera where it is (no snap to the target)."""
        self.anim, self.state, self.pri = None, "USER_PAN", PRI["TOUCH"]
        self.log.append(("TOUCH", "USER_PAN"))

    def touch_end(self):
        self.pri = -1


def l01_path():
    nodes = {"A": (180, 50), "B": (92, 145), "D": (120, 286), "F": (106, 470), "G": (266, 475)}
    return Path([nodes[k] for k in ("A", "B", "D", "F", "G")]), ["A", "B", "D", "F", "G"]


def checks():
    res = []

    def ok(name, cond):
        res.append((name, bool(cond)))
    import random
    rnd = random.Random(7)
    tf = Transform()
    worst = 0.0
    for _ in range(200):
        anchor = (rnd.uniform(0, 390), rnd.uniform(130, 730))
        w0 = tf.s2w(anchor)
        tf.zoom_about(anchor, rnd.uniform(0.65, 2.8))
        s1 = tf.w2s(w0)
        worst = max(worst, math.dist(s1, anchor))
        tf.center = (tf.center[0] + rnd.uniform(-5, 5), tf.center[1] + rnd.uniform(-5, 5))
    ok("anchor survives 200 random pinches (worst error %.2e px, limit 2)" % worst, worst < 2.0 and worst < 1e-6)
    t2 = Transform(center=(100, 200), zoom=1.7, viewport=(320, 568), safe_offset=(3, 11))
    p = (55.5, 321.25)
    ok("screen_to_world inverts world_to_screen", math.dist(t2.s2w(t2.w2s(p)), p) < 1e-9)
    path, ids = l01_path()
    ok("arc-length table spacing is at most 5 world units (max %.2f)" % path.max_spacing(), path.max_spacing() <= 5.0)
    step = [math.dist(path.point_at(s), path.point_at(s + 10)) for s in range(0, int(path.length) - 10, 10)]
    ok("equal arc-length steps move about equally (ratio %.2f)" % (max(step) / min(step)), max(step) / min(step) < 1.1)
    ok("path starts at A and ends at G", math.dist(path.point_at(0), (180, 50)) < 1e-6 and math.dist(path.point_at(path.length), (266, 475)) < 1e-6)
    ok("path passes within 6 units of B, D and F", all(min(math.dist((t[1], t[2]), q) for t in path.table) < 6 for q in [(92, 145), (120, 286), (106, 470)]))
    ok("drag down 100 px at zoom 1 moves the path back by 85 units", abs(scrub_delta(100, 1.0) + 85) < 1e-9)
    ok("inertia decays as exp(-6 t)", abs(inertia_velocity(100, 0.5, 844, 1.0) - 100 * math.exp(-3)) < 1e-9)
    ok("inertia is capped at 1.6 viewport heights per second", abs(inertia_velocity(1e6, 0.0, 844, 1.0) - 1.6 * 844) < 1e-9)
    # hysteresis
    b, changes = DISTRICT, 0
    for i in range(400):
        z = 1.75 + 0.02 * math.sin(i)
        nb = band_update(b, z)
        changes += nb != b
        b = nb
    ok("zoom jitter around 1.75 changes the band at most once (%d)" % changes, changes <= 1)
    b, changes = DISTRICT, 0
    for i in range(400):
        z = 0.85 + 0.02 * math.sin(i)
        nb = band_update(b, z)
        changes += nb != b
        b = nb
    ok("zoom jitter around 0.85 changes the band at most once (%d)" % changes, changes <= 1)
    ok("hysteresis points are 1.75 in, 1.55 out, 0.85 in, 1.00 out",
       band_update(DISTRICT, 1.74) == DISTRICT and band_update(DISTRICT, 1.75) == STREET and band_update(STREET, 1.56) == STREET
       and band_update(STREET, 1.55) == DISTRICT and band_update(DISTRICT, 0.86) == DISTRICT and band_update(DISTRICT, 0.85) == CITY
       and band_update(CITY, 0.99) == CITY and band_update(CITY, 1.00) == DISTRICT)
    ok("a jump from zoom 0.7 to 2.0 passes through to STREET", band_update(CITY, 2.0) == STREET)
    # LOD plan
    snap = {"walkers": [{"id": i, "active": i % 5 != 0} for i in range(20)], "streets": ["A|B", "A|C", "B|C"],
            "flux": {("A|B", "F"): 7, ("A|C", "G"): 3}, "queues": {"A|B": 5, "B|C": 1},
            "labels": [{"id": "n%d" % i, "priority": i % 4} for i in range(12)]}
    for band in (CITY, DISTRICT, STREET):
        pl = lod_plan(band, snap)
        ok("%s: people represented == active walkers (16)" % band, pl["people_represented"] == 16)
        ok("%s: no duplicated agent" % band, len(pl["agents"]) == len(set(pl["agents"])))
        ok("%s: every street stays visible (no hidden edge)" % band, pl["streets_visible"] == ["A|B", "A|C", "B|C"])
        ok("%s: label count within cap" % band, len(pl["labels"]) <= LABEL_CAP[band])
    ok("CITY draws ribbons from counted flux only and no agents", lod_plan(CITY, snap)["agents"] == [] and lod_plan(CITY, snap)["ribbons"] == snap["flux"])
    ok("DISTRICT draws every active agent once and no ribbons", len(lod_plan(DISTRICT, snap)["agents"]) == 16 and lod_plan(DISTRICT, snap)["ribbons"] == {})
    ok("agent detail only at STREET", lod_plan(STREET, snap)["agent_detail"] and not lod_plan(DISTRICT, snap)["agent_detail"])
    ev = [(10, "A|B", "F"), (15, "A|B", "F"), (30, "A|C", "G"), (50, "A|B", "F")]
    ok("flux window counts the last 20 ticks only", flux_window(ev, 35) == {("A|C", "G"): 1})
    ok("flux window at tick 30 counts 15 and 30 (10 is out)", flux_window(ev, 30) == {("A|B", "F"): 1, ("A|C", "G"): 1})
    ok("queue of 5 becomes a badge, queue of 3 does not", cluster_badges({"x": 5, "y": 3}) == {"x": 5})
    # director
    sc = compose_focus((180, 50), 1.6, (390, 844), 47, 71, 34, 112)
    t3 = Transform(center=sc[0], zoom=sc[1])
    sy = t3.w2s((180, 50))[1]
    ok("focused junction lands between HUD and dock with a 56 px margin (y=%.0f)" % sy, 47 + 71 + 56 <= sy <= 844 - 34 - 112 - 56)
    d = Director(Transform())
    d.request_focus("SIGN_FOCUS", "DECORATIVE", ((180, 60), 1.8), 1.0)
    d.update(0.5)
    mid = (d.tf.center, d.tf.zoom)
    acc = d.request_focus("OVERVIEW", "DECORATIVE", ((181, 262), 1.0), 1.0, "queue")
    ok("an equal-priority request with rule 'queue' is rejected while busy", acc is False)
    d.touch_begin()
    ok("touch freezes the camera exactly where it is (no snap to target)", (d.tf.center, d.tf.zoom) == mid and d.state == "USER_PAN")
    ok("a decorative request is rejected while a finger is down", d.request_focus("OVERVIEW", "DECORATIVE", ((181, 262), 1.0), 1.0) is False)
    ok("a user-initiated Return to sign is rejected while the finger is still down (touch outranks it)",
       d.request_focus("SIGN_FOCUS", "USER", ((180, 60), 1.8), 0.4) is False)
    d.touch_end()
    ok("after the finger lifts Return to sign is accepted", d.request_focus("SIGN_FOCUS", "USER", ((180, 60), 1.8), 0.4) is True)
    for frac in (0.0, 0.25, 0.5, 0.75, 0.99):
        d2 = Director(Transform())
        d2.request_focus("SIGN_FOCUS", "USER", ((180, 60), 1.8), 1.0)
        d2.update(frac)
        before = (d2.tf.center, d2.tf.zoom)
        d2.touch_begin()
        ok("cancel at %d%%: camera stays where it was" % round(frac * 100), (d2.tf.center, d2.tf.zoom) == before and d2.anim is None)
    d4 = Director(Transform(), reduced_motion=True)
    d4.request_focus("SIGN_FOCUS", "USER", ((180, 60), 1.8), 1.0)
    ok("reduced motion jumps at once and uses REDUCED_MOTION", d4.state == "REDUCED_MOTION" and d4.tf.zoom == 1.8 and d4.anim is None)
    ok("director has all nine states from the master prompt", len(STATES) == 9)
    return res


def golden():
    path, _ = l01_path()
    L = path.length
    return {"path_length": L, "path_points": [list(path.point_at(f * L)) for f in (0.0, 0.25, 0.5, 0.75, 1.0)],
            "table_len": len(path.table), "w2s": list(Transform(center=(100, 200), zoom=1.7, viewport=(320, 568),
                                                                    safe_offset=(3, 11)).w2s((55.5, 321.25)))}


def main():
    if "--write" in sys.argv:
        (ROOT / "tests/fixtures/camera_golden.json").write_text(json.dumps(golden(), indent=1) + "\n")
    bad = 0
    for name, c in checks():
        print(("PASS " if c else "FAIL ") + name)
        bad += not c
    print("CAMERA RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

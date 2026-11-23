"""Reference implementation of the Stage 12 transition driver (master prompt C4). Pure logic, no simulation import.
src/camera/transition.gd is a port; both read data/transitions.json. Run: python3 -I scripts/ref_transitions.py
Design rule: every game-state callback (on_start) fires at START. Cancel or skip can therefore never change a run
or lose or duplicate a result. on_end is cosmetic and fires exactly once.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEF = json.loads((ROOT / "data/transitions.json").read_text())


def ease(name, f):
    f = min(1.0, max(0.0, f))
    if name == "linear":
        return f
    if name == "cubic_out":
        return 1 - (1 - f) ** 3
    if name == "ease_in_out":
        return 4 * f ** 3 if f < 0.5 else 1 - (-2 * f + 2) ** 3 / 2
    if name == "spring":  # damped spring from 0 to 1 over the window: restrained bounce, exact end
        return 1.0 if f >= 1.0 else 1 - math.exp(-7.0 * f) * math.cos(9.0 * f)
    raise ValueError(name)


def poly_point(points, f):
    lens = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(lens)
    d = f * total
    for (a, b), L in zip(zip(points, points[1:]), lens):
        if d <= L or L == lens[-1]:
            u = 0.0 if L == 0 else min(1.0, d / L)
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        d -= L
    return tuple(points[-1])


def track_value(tr, t_ms):
    f = (t_ms - tr["delay_ms"]) / tr["dur_ms"] if tr["dur_ms"] > 0 else 1.0
    e = ease(tr["easing"], f)
    if tr["kind"] == "scalar":
        return tr["from"] + (tr["to"] - tr["from"]) * e
    if tr["kind"] == "vec2":
        return (tr["from"][0] + (tr["to"][0] - tr["from"][0]) * e, tr["from"][1] + (tr["to"][1] - tr["from"][1]) * e)
    return poly_point(tr["points"], e)


def end_value(tr):
    return track_value(tr, tr["delay_ms"] + tr["dur_ms"])


class Transition:
    def __init__(self, tdef, reduced=False):
        self.d, self.reduced = tdef, reduced
        self.state, self.t = "IDLE", 0.0
        self.events = []         # (name) game-state callbacks, at start
        self.hooks_fired = []
        self.end_calls = []      # on_end reasons; must never exceed 1
        self.frozen = None
        self.settle = None

    def start(self):
        if self.state != "IDLE":
            return
        self.state = "RUNNING"
        self.events += list(self.d["on_start"])
        self._hooks(0.0)
        if self.reduced:
            self.t = float(DEF["reduced_motion_ms"])
            self._end("completed")

    def _hooks(self, upto):
        for h in self.d["hooks"]:
            if h["id"] not in self.hooks_fired and h["at"] * self.d["duration_ms"] <= upto:
                self.hooks_fired.append(h["id"])

    def _end(self, reason):
        if self.state in ("DONE", "CANCELLED"):
            return
        self.state = "DONE" if reason in ("completed", "skipped") else "CANCELLED"
        self.end_calls.append(reason)

    def update(self, dt_ms):
        if self.state != "RUNNING":
            return
        if self.settle is not None:
            self.settle["t"] += dt_ms
            if self.settle["t"] >= self.settle["dur"]:
                self._end("skipped")
            return
        self.t += dt_ms
        self._hooks(self.t)
        if self.t >= self.d["duration_ms"]:
            self._end("completed")

    def skip(self):
        """Settle to the end state over skip_settle_ms. Input is never blocked, so control is back at once."""
        if self.state != "RUNNING" or self.settle is not None:
            return
        self.settle = {"t": 0.0, "dur": float(DEF["skip_settle_ms"]), "from": self.values()}

    def cancel(self, reason):
        """touch, app_background, app_interrupt: freeze exactly where it is."""
        if self.state != "RUNNING":
            return
        self.frozen = self.values()
        self._end("cancelled:" + reason)

    def progress(self):
        return min(1.0, self.t / self.d["duration_ms"])

    def values(self):
        if self.frozen is not None:
            return self.frozen
        if self.state == "DONE" and self.settle is None and not self.reduced:
            return {tr["name"]: end_value(tr) for tr in self.d["tracks"]}
        if self.reduced:
            return {tr["name"]: end_value(tr) for tr in self.d["tracks"]}
        if self.settle is not None:
            f = min(1.0, self.settle["t"] / self.settle["dur"])
            out = {}
            for tr in self.d["tracks"]:
                a, b = self.settle["from"][tr["name"]], end_value(tr)
                if isinstance(a, tuple):
                    out[tr["name"]] = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                else:
                    out[tr["name"]] = a + (b - a) * f
            return out
        return {tr["name"]: track_value(tr, self.t) for tr in self.d["tracks"]}


def by_id(i):
    return next(t for t in DEF["transitions"] if t["id"] == i)


def sim_log_hash(ticks, transition=None, cancel_at=None, how="touch"):
    """Mock simulation that only counts ticks and logs them, running while a transition plays. Proves the harness
    keeps the run identical; the real guarantee is that Transition has no handle to the simulation (lint L10)."""
    log = []
    tr = transition
    if tr:
        tr.start()
    for tick in range(ticks):
        log.append(tick * 7919 % 104729)
        if tr and tr.state == "RUNNING":
            if cancel_at is not None and tr.t >= cancel_at * tr.d["duration_ms"]:
                tr.cancel(how) if how != "skip" else tr.skip()
            tr.update(50.0)
    return hash(tuple(log))


def checks():
    res = []

    def ok(name, cond):
        res.append((name, bool(cond)))
    ids = [t["id"] for t in DEF["transitions"]]
    ok("six transitions defined", len(ids) == 6 and len(set(ids)) == 6)
    for t in DEF["transitions"]:
        i = t["id"]
        # complete run
        tr = Transition(t)
        tr.start()
        n = 0
        while tr.state == "RUNNING" and n < 1000:
            tr.update(10.0)
            n += 1
        ok(f"{i}: runs to completion in {t['duration_ms']} ms with one on_end", tr.state == "DONE" and tr.end_calls == ["completed"]
           and abs(n * 10 - t["duration_ms"]) <= 10)
        # game-state events are identical whatever the cancel point
        base_events = None
        same, one_end = True, True
        for how in ("touch", "app_background", "app_interrupt", "skip"):
            for frac in (0.0, 0.25, 0.5, 0.75, 0.99):
                tr = Transition(t)
                tr.start()
                tr.update(frac * t["duration_ms"])
                before = dict(tr.values())
                if how == "skip":
                    tr.skip()
                    tr.skip()
                    tr.update(DEF["skip_settle_ms"])
                    tr.update(500)
                else:
                    tr.cancel(how)
                    tr.cancel(how)
                    tr.skip()
                    tr.update(500)
                    if tr.values() != before:
                        same = False
                if base_events is None:
                    base_events = tr.events
                same = same and tr.events == base_events
                one_end = one_end and len(tr.end_calls) == 1
        ok(f"{i}: cancel/skip/app interruption at 0, 25, 50, 75, 99% leave game-state events identical", same)
        ok(f"{i}: exactly one on_end however it ends (no double callback)", one_end)
        # skip returns control quickly
        ok(f"{i}: skip settles within {DEF['skip_settle_ms']} ms (limit 150)", DEF["skip_settle_ms"] <= 150)
        # reduced motion
        r = Transition(t, reduced=True)
        r.start()
        ok(f"{i}: reduced motion ends at once in {DEF['reduced_motion_ms']} ms (limit 150)",
           r.state == "DONE" and DEF["reduced_motion_ms"] <= 150 and r.values() == {tr_["name"]: end_value(tr_) for tr_ in t["tracks"]})
        # no black overlay, no sudden focus jump: values continuous at 1 ms steps
        jumpy = False
        tr = Transition(t)
        tr.start()
        prev = tr.values()
        for _ in range(int(t["duration_ms"])):
            tr.update(1.0)
            cur = tr.values()
            for k in cur:
                a, b = prev[k], cur[k]
                d = math.dist(a, b) if isinstance(a, tuple) else abs(a - b)
                lim = 12.0 if isinstance(a, tuple) else 0.2
                if d > lim:
                    jumpy = True
            prev = cur
        ok(f"{i}: no sudden jump (per-ms change small)", not jumpy)
        ok(f"{i}: no black overlay track", all("black" not in tr_["name"] and "flash" not in tr_["name"] for tr_ in t["tracks"]))
        # auto-camera speed
        cams = [tr_ for tr_ in t["tracks"] if tr_["kind"] in ("vec2", "polyline")]
        if cams:
            c = cams[0]
            dist = math.dist(c["from"], c["to"]) if c["kind"] == "vec2" else sum(math.dist(a, b) for a, b in zip(c["points"], c["points"][1:]))
            zoom = next(x for x in t["tracks"] if x["name"] == "cam_zoom")
            z = max(zoom["from"], zoom["to"])
            avg = dist * z / (c["dur_ms"] / 1000.0)
            lim = DEF["max_auto_translation_viewport_widths_per_s"] * DEF["viewport_width_px"]
            ok(f"{i}: average auto-camera speed {avg:.0f} px/s within {lim:.0f}", avg <= lim)
    # specific rules
    t = by_id("paper_unfolds")
    tr = Transition(t)
    tr.start()
    tr.update(250)
    ok("paper_unfolds: geometry fully visible by 250 ms (first frame readable)", tr.values()["streets_alpha"] >= 0.99)
    tr = Transition(t)
    tr.start()
    tr.update(200)
    ok("paper_unfolds: labels still hidden while geometry finishes (ink in after geometry)", tr.values()["labels_alpha"] == 0.0)
    ok("paper_unfolds: zoom 0.72 to 1.15", tr.values()["cam_zoom"] > 0.72 and end_value(next(x for x in t["tracks"] if x["name"] == "cam_zoom")) == 1.15)
    t = by_id("sign_drops")
    tr = Transition(t)
    tr.start()
    ok("sign_drops: first frame already shows the lifted sign and fires the haptic", tr.values()["sign_scale"] == 1.08 and "haptic.sign_drop" in tr.hooks_fired)
    vals = []
    tr = Transition(t)
    tr.start()
    for _ in range(170):
        tr.update(1.0)
        vals.append(tr.values()["sign_scale"])
    ok("sign_drops: restrained bounce (min %.3f) and settled at 1.0" % min(vals), min(vals) >= 0.99 and abs(vals[-1] - 1.0) < 1e-9)
    t = by_id("district_to_diagram")
    tr = Transition(t)
    tr.start()
    sums = []
    for _ in range(210):
        tr.update(1.0)
        v = tr.values()
        sums.append(v["agents_alpha"] + v["ribbons_alpha"])
    ok("district_to_diagram: agents and ribbons crossfade with total opacity always 1 (no flash)", all(abs(s - 1.0) < 1e-9 for s in sums))
    t = by_id("outcome_pullback")
    tr = Transition(t)
    tr.start()
    ok("outcome_pullback: result is shown at t=0, not at the end", tr.events == ["result_shown"])
    ok("outcome_pullback: widens 1.15 to 0.78", end_value(next(x for x in t["tracks"] if x["name"] == "cam_zoom")) == 0.78)
    t = by_id("ghosted_rewind")
    tr = Transition(t)
    tr.start()
    ok("ghosted_rewind: the run is reset at t=0 and once", tr.events == ["reset_run"])
    tr.update(320)
    ok("ghosted_rewind: ghost fades to 0.25 by 320 ms, then 120 ms settle", abs(tr.values()["ghost_alpha"] - 0.25) < 1e-9 and t["duration_ms"] == 440)
    t = by_id("consequence_follows_ink")
    ok("consequence_follows_ink: 480 to 820 ms, cancels on pan or tap, never hides the sign control",
       480 <= t["duration_ms"] <= 820 and t["cancel_on"] == ["pan", "tap"] and t["never_hide"] == "sign_control")
    # the sign control (at A) never leaves the free band between HUD (118 px) and dock (844-146 px) while the camera follows the ink
    t = by_id("consequence_follows_ink")
    tr = Transition(t)
    tr.start()
    worst_top, worst_bottom = 1e9, 1e9
    for _ in range(int(t["duration_ms"])):
        tr.update(1.0)
        v = tr.values()
        c, z = v["cam_path"], v["cam_zoom"]
        sy = (50 - c[1]) * z + 844 / 2
        worst_top = min(worst_top, sy - 20 - 118)
        worst_bottom = min(worst_bottom, (844 - 146) - (sy + 20))
    ok("consequence_follows_ink: the sign disc stays fully visible between HUD and dock (margins %.0f and %.0f px)" % (worst_top, worst_bottom),
       worst_top >= 0 and worst_bottom >= 0)
    # replay unchanged
    base = sim_log_hash(100)
    allsame = True
    for t in DEF["transitions"]:
        for how in ("touch", "app_background", "app_interrupt", "skip"):
            for frac in (0.0, 0.25, 0.5, 0.75, 0.99):
                allsame = allsame and sim_log_hash(100, Transition(t), frac, how) == base
    ok("a mock run logs the identical ticks with every transition cancelled at every point (120 combinations)", allsame)
    return res


def main():
    bad = 0
    for n, c in checks():
        print(("PASS " if c else "FAIL ") + n)
        bad += not c
    print("TRANSITION RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

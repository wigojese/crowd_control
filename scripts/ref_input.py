"""Reference implementation of the Stage 09 gesture router (docs/INPUT_SPEC.md sections 5 and 9).
Pure logic: takes touch events, returns intents. src/input/gesture_router.gd is a line-for-line port and runs the
same cases (tests/fixtures/input_cases.json). Run: python3 -I scripts/ref_input.py   (prints PASS/FAIL per case)
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "data/input_tokens.json").read_text())


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class Router:
    def __init__(self, scene, tokens=TOK):
        self.scene, self.tok = scene, tokens
        self.touches = {}   # id -> dict(state, start, pos, t0, source, target, acked)
        self.pair = None    # pinch: dict(a, b, d_prev, active)
        self.log = []       # (state transitions) for the transition table check
        self.first_ack = {}  # id -> ms from down to first intent

    # -- helpers
    def _in_rect(self, p, r):
        return r[0] <= p[0] <= r[0] + r[2] and r[1] <= p[1] <= r[1] + r[3]

    def _near(self, p, c, half=None):
        h = (self.tok["hit_px"] / 2) if half is None else half
        return abs(p[0] - c[0]) <= h and abs(p[1] - c[1]) <= h

    def _ring_near(self, p):
        best, bd = None, 1e9
        for r in self.scene["rings"]:
            d = dist(p, r["pos"])
            if d <= self.tok["snap_px"] and d < bd:
                best, bd = r["id"], d
        return best

    def _set(self, tid, state):
        t = self.touches[tid]
        self.log.append((t["state"], state))
        t["state"] = state

    def _emit(self, out, tid, t_ms, typ, **kw):
        d = {"type": typ, **kw}
        out.append(d)
        tt = self.touches.get(tid)
        if tt is not None and tid not in self.first_ack:
            self.first_ack[tid] = t_ms - tt["t0"]

    # -- API
    def down(self, tid, pos, t_ms):
        out, sc = [], self.scene
        w = sc["viewport"][0]
        rec = {"state": "IDLE", "start": pos, "pos": pos, "t0": t_ms, "source": None, "target": None}
        self.touches[tid] = rec
        for b in sc["buttons"]:
            if self._in_rect(pos, b["rect"]):
                rec.update(source="button", target=b["id"])
                self._set(tid, "UI_PRESS")
                self._emit(out, tid, t_ms, "PRESS_FEEDBACK", target=b["id"])
                return out
        if pos[0] < self.tok["edge_reserve_px"] or pos[0] > w - self.tok["edge_reserve_px"]:
            self._set(tid, "IGNORED")
            return out
        sg = sc["sign"]
        others = [k for k, v in self.touches.items() if k != tid and v["state"] in
                  ("SIGN_PENDING", "MAP_PENDING", "PAN", "PINCH")]
        if others:  # a second finger on the map: pinch pairing
            a = others[0]
            if self.touches[a]["state"] == "SIGN_PENDING":
                self._emit(out, a, t_ms, "SIGN_ACTION_CANCELLED")
            self._set(a, "PINCH")
            self._set(tid, "PINCH")
            self.pair = {"a": a, "b": tid, "d_prev": dist(self.touches[a]["pos"], pos),
                         "d0": dist(self.touches[a]["pos"], pos), "active": False}
            return out
        if sg["placed"] and not sg["held"] and self._near(pos, sg["pos"]):
            if sc["mode"] == "PAUSED":
                rec["source"] = "sign"
                self._set(tid, "LOCK_REJECT")
                self._emit(out, tid, t_ms, "PAUSED_MESSAGE")
                return out
            rec["source"] = "sign"
            self._set(tid, "SIGN_PENDING")
            self._emit(out, tid, t_ms, "PRESS_FEEDBACK", target="sign")
            return out
        for r in sc["rings"]:
            if self._near(pos, r["pos"]):
                rec.update(source="ring", target=r["id"])
                self._set(tid, "SIGN_PENDING")
                self._emit(out, tid, t_ms, "PRESS_FEEDBACK", target=r["id"])
                return out
        if not sg["placed"] and self._near(pos, sc["tray"]):
            rec["source"] = "tray"
            self._set(tid, "SIGN_PENDING")
            self._emit(out, tid, t_ms, "PRESS_FEEDBACK", target="tray")
            return out
        self._set(tid, "MAP_PENDING")
        return out

    def move(self, tid, pos, t_ms):
        out, rec, sc, tok = [], self.touches.get(tid), self.scene, self.tok
        if rec is None:
            return out
        rec["pos"] = pos
        st = rec["state"]
        if st == "PINCH" and self.pair and tid in (self.pair["a"], self.pair["b"]):
            d = dist(self.touches[self.pair["a"]]["pos"], self.touches[self.pair["b"]]["pos"])
            ratio = d / max(self.pair["d0"], 1e-6)
            if self.pair["active"] or ratio > tok["pinch_ratio"] or ratio < 1 / tok["pinch_ratio"]:
                self.pair["active"] = True
                self._emit(out, tid, t_ms, "PINCH", scale=round(d / max(self.pair["d_prev"], 1e-6), 4))
                self.pair["d_prev"] = d
            return out
        moved = dist(rec["start"], pos)
        if st == "SIGN_PENDING" and moved > tok["drag_px"]:
            if rec["source"] == "ring":
                self._set(tid, "PAN")
                self._emit(out, tid, t_ms, "PAN", delta=[pos[0] - rec["start"][0], pos[1] - rec["start"][1]])
            elif rec["source"] == "sign" and sc["sign"]["locked"]:
                self._set(tid, "LOCK_REJECT")
                self._emit(out, tid, t_ms, "LOCK_REJECT")
            else:
                self._set(tid, "SIGN_DRAG")
                self._emit(out, tid, t_ms, "SIGN_PICKUP", source=rec["source"])
        elif st == "SIGN_DRAG":
            self._emit(out, tid, t_ms, "SIGN_DRAG_MOVE", snap=self._ring_near(pos))
        elif st == "MAP_PENDING" and moved > tok["pan_px"]:
            self._set(tid, "PAN")
            self._emit(out, tid, t_ms, "PAN", delta=[pos[0] - rec["start"][0], pos[1] - rec["start"][1]])
        elif st == "PAN":
            self._emit(out, tid, t_ms, "PAN", delta=[pos[0] - rec["start"][0], pos[1] - rec["start"][1]])
        return out

    def update(self, t_ms):
        """Time passing without a touch event: long press and hold timeout."""
        out = []
        for tid, rec in list(self.touches.items()):
            el = t_ms - rec["t0"]
            if rec["state"] == "SIGN_PENDING" and rec["source"] == "sign" and el >= self.tok["long_press_ms"] \
                    and dist(rec["start"], rec["pos"]) <= self.tok["drag_px"]:
                self._set(tid, "SIGN_INSPECT")
                self._emit(out, tid, t_ms, "INSPECT")
            elif rec["state"] == "SIGN_DRAG" and el >= self.tok["hold_timeout_ms"]:
                self._set(tid, "IGNORED")
                self._emit(out, tid, t_ms, "SNAPBACK", reason="timeout")
        return out

    def up(self, tid, pos, t_ms):
        out, rec, sc, tok = [], self.touches.get(tid), self.scene, self.tok
        if rec is None:
            return out
        rec["pos"] = pos
        st = rec["state"]
        moved = dist(rec["start"], pos)
        if st == "UI_PRESS":
            for b in sc["buttons"]:
                if b["id"] == rec["target"] and self._in_rect(pos, b["rect"]):
                    self._emit(out, tid, t_ms, "UI", id=b["id"])
        elif st == "SIGN_PENDING":
            quick = (t_ms - rec["t0"]) <= tok["tap_ms"] and moved < tok["drag_px"]
            if quick and rec["source"] == "sign":
                if sc["sign"]["locked"]:
                    self._emit(out, tid, t_ms, "LOCK_REJECT")
                else:
                    self._emit(out, tid, t_ms, "SIGN_TURN")
            elif quick and rec["source"] == "ring" and sc["sign"]["placed"]:
                if sc["sign"]["locked"]:
                    self._emit(out, tid, t_ms, "LOCK_REJECT")
                elif rec["target"] != sc["sign"]["slot"]:
                    self._emit(out, tid, t_ms, "SIGN_MOVE_TAP", slot=rec["target"])
        elif st == "SIGN_DRAG":
            ring = self._ring_near(pos)
            if ring is not None:
                self._emit(out, tid, t_ms, "SIGN_DROP", slot=ring)
            else:
                self._emit(out, tid, t_ms, "SNAPBACK", reason="off_ring")
        self._set(tid, "IDLE")
        if self.pair and tid in (self.pair["a"], self.pair["b"]):
            other = self.pair["b"] if tid == self.pair["a"] else self.pair["a"]
            if other in self.touches and self.touches[other]["state"] == "PINCH":
                self._set(other, "IGNORED")
            self.pair = None
        del self.touches[tid]
        return out

    def cancel(self, tid, t_ms):
        out, rec = [], self.touches.get(tid)
        if rec is None:
            return out
        if rec["state"] == "SIGN_DRAG":
            self._emit(out, tid, t_ms, "SNAPBACK", reason="cancelled")
        else:
            self._emit(out, tid, t_ms, "CANCELLED")
        self._set(tid, "IDLE")
        if self.pair and tid in (self.pair["a"], self.pair["b"]):
            self.pair = None
        del self.touches[tid]
        return out


def run_case(case):
    r = Router(case["scene"])
    types = []
    for ev in case["events"]:
        op = ev["op"]
        if op == "down":
            out = r.down(ev["id"], ev["pos"], ev["t"])
        elif op == "move":
            out = r.move(ev["id"], ev["pos"], ev["t"])
        elif op == "up":
            out = r.up(ev["id"], ev["pos"], ev["t"])
        elif op == "cancel":
            out = r.cancel(ev["id"], ev["t"])
        else:
            out = r.update(ev["t"])
        types += [o["type"] for o in out]
    return types, r


def main():
    cases = json.loads((ROOT / "tests/fixtures/input_cases.json").read_text())
    bad = 0
    for c in cases:
        got, _ = run_case(c)
        ok = got == c["expect"]
        print(("PASS " if ok else "FAIL ") + c["id"], "" if ok else "got %s want %s" % (got, c["expect"]))
        bad += not ok
    print("INPUT RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

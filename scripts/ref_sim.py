"""Python port of src/simulation/sim_world.gd (CC-RULESET-01C) that writes the same canonical event lines.
Purpose: (1) check the logic of the GDScript against the Stage 03 model's numbers, (2) produce event traces for the
Stage 13 explainer. Independent of docs/analysis/stage03_numeric_check.py (it reads the level JSON).
Usage: python3 -I scripts/ref_sim.py   (self-check against tests/fixtures/expected_python_model.json)
"""
import heapq
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DT, REEVAL, LOOP_PEN, DOT_MIN, LOCK, HOLD = 0.05, 10, 6.0, 0.65, 80, 10
PROFILES = {"C": dict(sign=0.8, crowd=0.35, speed=38.0), "F": dict(sign=1.0, crowd=0.9, speed=34.0), "I": dict(sign=0.35, crowd=0.2, speed=42.0)}
DIRS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
UNSP, NEEDS, QUEUED, ON_EDGE, ARRIVED = range(5)


def fnv(lines):
    h = 0x811C9DC5
    for b in "\n".join(lines).encode():
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h


class World:
    def __init__(self, level):
        self.level = level
        self.ticks, self.deadline, self.bonus = int(level.get("ticks", 640)), int(level.get("deadline_tick", 600)), float(level.get("sign_bonus", 4.0))
        self.nodes = {n["id"]: (float(n["x"]), float(n["y"])) for n in level["nodes"]}
        self.edges = {}
        for e in level["edges"]:
            a, b = e["from"], e["to"]
            L = math.dist(self.nodes[a], self.nodes[b])
            self.edges[a + ">" + b] = dict(frm=a, to=b, len=L, rate=float(e["rate"]))
            self.edges[b + ">" + a] = dict(frm=b, to=a, len=L, rate=float(e["rate"]))
        self.edge_ids = sorted(self.edges)
        self.out = {n: [e for e in self.edge_ids if self.edges[e]["frm"] == n] for n in self.nodes}
        self.dist = {n: self._sp(n) for n in self.nodes}
        self.schedule = level["schedule"]

    def _sp(self, src):
        d = {n: 1e18 for n in self.nodes}
        d[src] = 0.0
        pq = [(0.0, src)]
        while pq:
            c, u = heapq.heappop(pq)
            if c > d[u]:
                continue
            for e in self.out[u]:
                v = self.edges[e]["to"]
                nd = c + self.edges[e]["len"]
                if nd < d[v]:
                    d[v] = nd
                    heapq.heappush(pq, (nd, v))
        return d

    def favoured(self, slot, head):
        res = []
        for e in self.out[slot]:
            a, b, L = self.edges[e]["frm"], self.edges[e]["to"], self.edges[e]["len"]
            ux, uy = (self.nodes[b][0] - self.nodes[a][0]) / L, (self.nodes[b][1] - self.nodes[a][1]) / L
            if ux * DIRS[head][0] + uy * DIRS[head][1] >= DOT_MIN:
                res.append(e)
        return res

    def reset(self, sign_state, commands):
        self.lines, self.seq, self.last_tick, self.tick = [], 0, -1, 0
        self.walkers, i = [], 0
        for s in self.schedule:
            for p in [p for p in ("C", "F", "I") if p in s["mix"]]:
                for _ in range(int(s["mix"][p])):
                    self.walkers.append(dict(id=i, prof=p, origin=s["origin"], dest=s["destination"], spawn=int(s["tick"]), state=UNSP, node="",
                                             edge="", edge_t=0.0, hist=[], q="", lasteval=-99, arr=-1, prev=""))
                    i += 1
        self.tokens = {e: 1.0 for e in self.edge_ids}
        self.fifo = {e: [] for e in self.edge_ids}
        self.sign = dict(slot="", head="", active=False, lock_until=-1, drop_at=-1, pending="")
        if len(sign_state) == 2:
            self.sign.update(slot=sign_state[0], head=sign_state[1], active=True)
        self.cmds = sorted(commands, key=lambda c: (c[0], c[1], str(c[3])))
        self.ci = 0
        self.blocked = self.person = self.sign_actions = 0

    def emit(self, typ, fields):
        if self.tick != self.last_tick:
            self.last_tick, self.seq = self.tick, 0
        self.lines.append("%d|%d|%s|%s" % (self.tick, self.seq, typ, ";".join("%s=%s" % (k, fields[k]) for k in sorted(fields))))
        self.seq += 1

    def cost(self, w, node, e, use_sign, use_queue):
        p, b, rate = PROFILES[w["prof"]], self.edges[e]["to"], self.edges[e]["rate"]
        rem = (self.edges[e]["len"] + self.dist[b][w["dest"]]) / p["speed"]
        if w["q"] != e:
            ahead = len(self.fifo[e])
        else:
            ahead = next(k for k, x in enumerate(self.fifo[e]) if x[0] == w["id"])
        qw = max(0.0, ahead + 1.0 - self.tokens[e]) / rate
        loop = LOOP_PEN if b in w["hist"][-3:] else 0.0
        bon = self.bonus if (use_sign and self.sign["active"] and self.sign["slot"] == node and e in self.favoured(self.sign["slot"], self.sign["head"])) else 0.0
        return rem + (p["crowd"] * qw if use_queue else 0.0) + loop - p["sign"] * bon

    def choose(self, w, node, use_sign, use_queue):
        best_c, best_e = 0.0, ""
        for e in self.out[node]:
            if w["prev"] != "" and self.edges[e]["to"] == w["prev"] and len(self.out[node]) > 1:
                continue
            c = self.cost(w, node, e, use_sign, use_queue)
            if best_e == "" or c < best_c - 1e-12 or (abs(c - best_c) <= 1e-12 and e < best_e):
                best_c, best_e = c, e
        return best_e, best_c

    def step(self):
        t, sg, changed = self.tick, self.sign, False
        if sg["pending"] != "" and sg["drop_at"] == t:
            sg.update(slot=sg["pending"], active=True, lock_until=t + LOCK, pending="", drop_at=-1)
            changed = True
            self.emit("SIGN_DROPPED", dict(slot=sg["slot"], heading=sg["head"], lock_until=sg["lock_until"]))
        while self.ci < len(self.cmds) and self.cmds[self.ci][0] == t:
            c = self.cmds[self.ci]
            self.ci += 1
            if t < sg["lock_until"] or sg["pending"] != "" or sg["slot"] == "":
                why = "locked" if t < sg["lock_until"] else ("held" if sg["pending"] != "" else "no_sign_placed")
                self.emit("COMMAND_REJECTED", dict(command=c[2], reason=why))
                continue
            if c[2] == "ROTATE":
                sg["head"], sg["lock_until"], changed = c[3], t + LOCK, True
                self.sign_actions += 1
                self.emit("COMMAND_ACCEPTED", dict(command="ROTATE", slot=sg["slot"], heading=c[3], ordinal=c[1]))
                self.emit("SIGN_ROTATED", dict(heading=c[3], lock_until=sg["lock_until"]))
            elif c[2] == "MOVE" and c[3] != sg["slot"]:
                self.emit("COMMAND_ACCEPTED", dict(command="MOVE", slot=c[3], heading=sg["head"], ordinal=c[1]))
                self.emit("SIGN_PICKED", dict(from_slot=sg["slot"], heading=sg["head"]))
                sg.update(pending=c[3], drop_at=t + HOLD, active=False)
                changed = True
                self.sign_actions += 1
        for w in self.walkers:
            if w["state"] == UNSP and w["spawn"] == t:
                w["state"], w["node"] = NEEDS, w["origin"]
                self.emit("WALKER_SPAWNED", dict(walker=w["id"], profile=w["prof"], origin=w["origin"], destination=w["dest"], deadline_tick=self.deadline))
        for e in self.edge_ids:
            r = self.edges[e]["rate"]
            self.tokens[e] = min(max(1.0, r), self.tokens[e] + r * DT)
        for w in self.walkers:
            due = w["state"] == NEEDS or (w["state"] == QUEUED and (t - w["lasteval"] >= REEVAL or changed))
            if not due:
                continue
            node = w["node"]
            best_e, best_c = self.choose(w, node, True, True)
            reason, alt = "lowest_cost", ""
            if len(self.out[node]) == 1:
                reason = "forced_single_exit"
            else:
                no_sign, no_queue = self.choose(w, node, False, True)[0], self.choose(w, node, True, False)[0]
                if no_sign != best_e:
                    reason, alt = "sign_flipped", no_sign
                elif no_queue != best_e:
                    reason, alt = "queue_flipped", no_queue
            self.emit("DECISION", dict(walker=w["id"], node=node, chosen_edge=best_e, reason=reason, alt_edge=alt, cost_milli=int(round(best_c * 1000.0))))
            if w["q"] != best_e:
                if w["q"] != "":
                    self.emit("QUEUE_LEFT", dict(walker=w["id"], edge=w["q"], position=len(self.fifo[w["q"]])))
                    self.fifo[w["q"]] = [x for x in self.fifo[w["q"]] if x[0] != w["id"]]
                self.fifo[best_e].append((w["id"], t))
                w["q"] = best_e
                self.emit("QUEUE_JOINED", dict(walker=w["id"], edge=best_e, position=len(self.fifo[best_e]) - 1))
            w["state"], w["lasteval"] = QUEUED, t
        entered = set()
        for e in self.edge_ids:
            while self.tokens[e] >= 1.0 and self.fifo[e]:
                wid, _ = self.fifo[e].pop(0)
                w2 = self.walkers[wid]
                self.tokens[e] -= 1.0
                w2.update(state=ON_EDGE, edge=e, edge_t=0.0, q="", prev=w2["node"])
                w2["hist"].append(w2["node"])
                entered.add(wid)
                self.emit("EDGE_ENTERED", dict(walker=wid, edge=e, tokens_after=int(round(self.tokens[e] * 1000.0))))
        for w in self.walkers:
            if w["state"] == ON_EDGE and w["id"] not in entered:
                w["edge_t"] += PROFILES[w["prof"]]["speed"] * DT / self.edges[w["edge"]]["len"]
                if w["edge_t"] >= 1.0:
                    b = self.edges[w["edge"]]["to"]
                    w["node"], w["edge"] = b, ""
                    self.emit("NODE_ARRIVED", dict(walker=w["id"], node=b))
                    if b == w["dest"]:
                        w["state"], w["arr"] = ARRIVED, t + 1
                        self.emit("WALKER_ARRIVED", dict(walker=w["id"], arrival_tick=t + 1, on_time=1 if t + 1 <= self.deadline else 0))
                    else:
                        w["state"] = NEEDS
        for w in self.walkers:
            if w["state"] in (QUEUED, NEEDS, ON_EDGE):
                self.person += 1
                if w["state"] == QUEUED:
                    self.blocked += 1
        self.tick += 1

    def result(self):
        arr = [w for w in self.walkers if w["state"] == ARRIVED]
        ont = [w for w in arr if w["arr"] <= self.deadline]
        dr, otr, cs = len(arr) / max(1, len(self.walkers)), len(ont) / max(1, len(arr)), self.blocked / max(1, self.person)
        x = 100.0 * (0.7 * dr + 0.2 * otr + 0.1 * (1.0 - min(1.0, max(0.0, cs))))
        f = math.floor(x)
        d = x - f
        score = f + 1 if d > 0.5 + 1e-9 else (f if d < 0.5 - 1e-9 else (f if f % 2 == 0 else f + 1))
        return dict(arrived=len(arr), ontime=len(ont), blocked_ticks=self.blocked, person_ticks=self.person, score=int(score),
                    last_arr=max([w["arr"] for w in arr], default=0), sign_actions=self.sign_actions)

    def run(self, sign_state, commands=()):
        self.reset(list(sign_state), list(commands))
        for _ in range(self.ticks):
            self.step()
        r = self.result()
        self.emit("RUN_ENDED", dict(reason="time_limit"))
        r["hash"] = fnv(self.lines)
        r["passed"] = r["arrived"] >= int(self.level.get("pass_mark", 18))
        return r


def load_level():
    return json.loads((ROOT / "data/levels/cc_l01_r1.json").read_text())


def main():
    exp = json.loads((ROOT / "tests/fixtures/expected_python_model.json").read_text())
    keys = ["arrived", "ontime", "blocked_ticks", "person_ticks", "score", "last_arr", "sign_actions"]
    w = World(load_level())
    cases = [("r1_no_sign", [], []), ("r1_A_N", ["A", "N"], []), ("r1_A_E", ["A", "E"], []), ("r1_A_S", ["A", "S"], []),
             ("r1_B_E", ["B", "E"], []), ("r1_B_N", ["B", "N"], []),
             ("r1_A_N_rotateE_t0", ["A", "N"], [(0, 0, "ROTATE", "E")]), ("r1_B_E_moveA_t100", ["B", "E"], [(100, 0, "MOVE", "A")]),
             ("r1_A_E_rotateN_t200", ["A", "E"], [(200, 0, "ROTATE", "N")])]
    bad = 0
    for name, s, c in cases:
        r = w.run(s, c)
        ok = all(int(r[k]) == int(exp[name][k]) for k in keys)
        bad += not ok
        print(("PASS " if ok else "FAIL ") + name, "" if ok else {k: (r[k], exp[name][k]) for k in keys if r[k] != exp[name][k]})
    h1, h2 = w.run(["A", "E"])["hash"], w.run(["A", "E"])["hash"]
    print(("PASS" if h1 == h2 else "FAIL"), "event hash repeats (%d)" % h1)
    bad += h1 != h2
    print("REF_SIM RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

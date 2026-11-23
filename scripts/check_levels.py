"""Level checks and Stage 14 evidence (Python reference of the engine rules, NOT engine).
For every level in data/levels: valid, baseline fails, every listed solution passes, passing placements are few
(not trivial), screen composition fits at 390x844 and 320x568, sockets are far enough apart to touch.
Writes docs/stage14/difficulty_matrix.json, data/replays/*.json, first_failures.json. Exit 0 only if every check passes.
Usage: python3 -I scripts/check_levels.py
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_sim  # noqa: E402
import ref_explain as ex  # noqa: E402
import validate_scenarios as vs  # noqa: E402
OUT = ROOT / "docs/stage14"
LEVELS = ["cc_l01_r1", "cc_l02_ferry", "cc_l03_narrow"]
HUD_BOTTOM, DOCK_TOP = 118, 844 - 146


def total_walkers(lv):
    return sum(sum(s["mix"].values()) for s in lv["schedule"])


def main():
    OUT.mkdir(exist_ok=True)
    (ROOT / "data/replays").mkdir(exist_ok=True)
    bad, matrix, failures = 0, {}, {}

    def ok(name, cond):
        nonlocal bad
        print(("PASS " if cond else "FAIL ") + name)
        bad += not cond
    for f in LEVELS:
        lv = json.loads((ROOT / "data/levels" / (f + ".json")).read_text())
        lid, total, pm = lv["level_id"], total_walkers(lv), lv["pass_mark"]
        w = ref_sim.World(lv)
        names = {n["id"]: n["name"] for n in lv["nodes"]}
        ok(f"{lid}: passes the scenario validator", vs.validate(lv) == [])
        base = w.run([])
        ok(f"{lid}: no sign fails ({base['arrived']} of {total}, pass mark {pm})", base["arrived"] < pm)
        statics = {a + h: w.run([a, h])["arrived"] for a in lv["sockets"] for h in "NESW"}
        passing = sorted(k for k, v in statics.items() if v >= pm)
        ok(f"{lid}: not trivial, {len(passing)} of {len(statics)} fixed placements pass", len(passing) <= len(statics) // 2)
        ok(f"{lid}: at least two tested solutions listed", len(lv["solutions"]) >= 2)
        sol_rows = []
        for s in lv["solutions"]:
            cmds = [tuple(c) for c in s["commands"]]
            r = w.run(s["initial_sign"], cmds)
            ok(f"{lid}: solution {s['id']} passes ({r['arrived']} of {total})", r["arrived"] >= pm)
            sol_rows.append(dict(id=s["id"], arrived=r["arrived"], event_hash=r["hash"]))
            (ROOT / "data/replays" / f"{lid}__{s['id']}.json").write_text(json.dumps(dict(
                ruleset_version=lv["ruleset_version"], level_id=lid, seed=lv["seed"], initial_sign=s["initial_sign"],
                actions=[dict(tick=c[0], ordinal=c[1], command=c[2], argument=c[3]) for c in s["commands"]],
                result=dict(arrived=r["arrived"], passed=r["arrived"] >= pm), event_hash=r["hash"],
                note="Python reference of the engine rules; replay the same actions in the engine and compare the hash (BLOCKED here)"), indent=1) + "\n")
        # lesson check for L02: a fixed sign cannot pass, a moved sign can
        if lv.get("fixed_placement_best_expected") is not None:
            ok(f"{lid}: best fixed placement is {max(statics.values())} (documented {lv['fixed_placement_best_expected']}) and fails", max(statics.values()) == lv["fixed_placement_best_expected"] and max(statics.values()) < pm)
            window = [t for t in range(100, 300, 10) if w.run(["A", "E"], [(t, 0, "MOVE", "B")])["arrived"] >= pm]
            ok(f"{lid}: moving the sign to Canal Turn passes over a window of {window[0]} to {window[-1]} ticks ({len(window)} tested starts)", len(window) >= 8)
            matrix_window = (window[0], window[-1])
        else:
            matrix_window = None
        # composition: everything inside the free band at zoom 1.0, sockets far enough apart
        xs, ys = [n["x"] for n in lv["nodes"]], [n["y"] for n in lv["nodes"]]
        ok(f"{lid}: map fits 390x844 at zoom 1.0 ({max(xs)-min(xs):.0f} x {max(ys)-min(ys):.0f} px, free band 342 x {DOCK_TOP-HUD_BOTTOM-40})", max(xs) - min(xs) <= 342 and max(ys) - min(ys) <= DOCK_TOP - HUD_BOTTOM - 40)
        pos = {n["id"]: (n["x"], n["y"]) for n in lv["nodes"]}
        socks = lv["sockets"]
        dmin = min(math.dist(pos[a], pos[b]) for i, a in enumerate(socks) for b in socks[i + 1:])
        ok(f"{lid}: sockets {dmin:.0f} px apart at 390 wide ({dmin*0.82:.0f} at 320 wide), at least 60 for touch", dmin * 0.82 >= 60)
        # first failures, explained from events
        fails = {}
        for label, s in (("no_sign", []), ("fixed_best", list(max(statics, key=statics.get)))):
            r = w.run(s)
            if r["arrived"] < pm:
                cl = ex.explain(list(w.lines), r, base, {"initial_sign": s, "actions": []}, names, goal=pm, total=total)
                fails[label] = dict(arrived=r["arrived"], copy=[c["text"] for c in ex.select(cl)])
        failures[lid] = fails
        matrix[lid] = dict(name=lv["name"], walkers=total, pass_mark=pm, no_sign=base["arrived"], best_fixed=max(statics.values()),
                           fixed_placements_passing=passing, fixed_placements_tested=len(statics), solutions=sol_rows,
                           move_window_ticks=matrix_window, margin_over_no_sign=pm - base["arrived"], lesson=lv["lesson"])
    json.dump(matrix, open(OUT / "difficulty_matrix.json", "w"), indent=1)
    json.dump(failures, open(OUT / "first_failures.json", "w"), indent=1)
    print("LEVELS RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

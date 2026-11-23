"""Stage 08 experiment (user chose feedback option B: spawn window first). PYTHON MODEL, not engine.
Question: does adding a third walker group at tick 200/300/360 make a mid-round sign action decisive?
Method: for each extra group (origin, destination, tick) take the best static placement and the best
placement plus ONE action (tick 100..460 step 40). Gain = difference in arrivals out of 27 walkers.
Run: python3 -I docs/analysis/stage08_r2_experiment.py   (about 1 minute)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import stage03_numeric_check as m  # noqa: E402

n = dict(m.NODES)
n["C"] = (270, 115)
m.configure(n, [(a, b, 0.3 if (a, b) == ("B", "D") else r) for a, b, r in m.LINKS])
m.BONUS = 6.0
BASE = [(0, "A", "F", [("C", 7), ("F", 3), ("I", 2)]), (40, "A", "G", [("C", 4), ("F", 3), ("I", 1)])]


def arrived(sg, cmds, sched):
    m.SCHEDULE[:] = sched
    w = m.run(sg, cmds, trace=True)["walkers"]
    return sum(x["state"] == "ARRIVED" for x in w)


rows = []
for o in "ABCE":
    for d in "FG":
        for t in (200, 300, 360):
            if o == d:
                continue
            s = BASE + [(t, o, d, [("C", 4), ("F", 2), ("I", 1)])]
            best_static = max(arrived((sl, h), [], s) for sl in "AB" for h in "NESW")
            best_one = best_static
            for sg in [("A", "E"), ("A", "N"), ("B", "E"), ("B", "N")]:
                for tt in range(100, 500, 40):
                    for a, x in [("ROTATE", y) for y in "NESW"] + [("MOVE", "A"), ("MOVE", "B")]:
                        best_one = max(best_one, arrived(sg, [(tt, a, x)], s))
            rows.append((best_one - best_static, o, d, t, best_static, best_one, arrived(None, [], s)))
rows.sort(reverse=True)
print("gain, origin, dest, tick, best_static, best_with_one_action, no_sign   (27 walkers)")
for r in rows[:8]:
    print(r)

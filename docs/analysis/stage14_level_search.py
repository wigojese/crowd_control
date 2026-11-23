"""Stage 14 design search (Python model, NOT engine): find a second walker wave for the L01 graph where a mid-round sign
action beats every fixed placement. Writes docs/analysis/stage14_search_out.json. Usage: python3 -I docs/analysis/stage14_level_search.py
"""
import itertools
import json
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
    return sum(x["state"] == "ARRIVED" for x in w), len(w)


def main():
    rows = []
    for o, d, tick, size in itertools.product("ABC", "FG", (160, 240, 320), (6, 10)):
        if o == d:
            continue
        mix = [("C", size // 2 + 1), ("F", size // 4), ("I", size - size // 2 - 1 - size // 4)]
        s = BASE + [(tick, o, d, mix)]
        total = arrived(None, [], s)[1]
        base = arrived(None, [], s)[0]
        statics = {(sl, h): arrived((sl, h), [], s)[0] for sl in "AB" for h in "NESW"}
        best_static = max(statics.values())
        best_one, arg = best_static, None
        for (sl, h) in sorted(statics, key=statics.get, reverse=True)[:3]:
            for tt in (tick - 60, tick - 20, tick + 10):
                for a, x in [("ROTATE", y) for y in "NESW"] + [("MOVE", "A"), ("MOVE", "B")]:
                    v = arrived((sl, h), [(tt, a, x)], s)[0]
                    if v > best_one:
                        best_one, arg = v, (sl, h, tt, a, x)
        rows.append(dict(origin=o, dest=d, tick=tick, size=size, total=total, baseline=base, best_static=best_static, best_one_action=best_one, gain=best_one - best_static, arg=arg))
    rows.sort(key=lambda r: -r["gain"])
    json.dump(rows, open(pathlib.Path(__file__).resolve().parent / "stage14_search_out.json", "w"), indent=1)
    for r in rows[:8]:
        print(r)


if __name__ == "__main__":
    main()

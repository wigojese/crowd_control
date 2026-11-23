"""Stage 08 evidence from the PYTHON REFERENCE MODEL (docs/analysis/stage03_numeric_check.py), level CC-L01-R1.
This is NOT engine output. It writes docs/stage08/scenarios.csv, first_decisions.csv, replay_*.json so the
numbers the Godot code must reproduce (tests/test_sim_l01.gd) are on record and reviewable.
Usage: python3 -I scripts/stage08_reference_runs.py
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docs/analysis"))
import stage03_numeric_check as m  # noqa: E402

OUT = ROOT / "docs/stage08"
n = dict(m.NODES)
n["C"] = (270, 115)
links = [(a, b, 0.3 if (a, b) == ("B", "D") else r) for a, b, r in m.LINKS]
m.configure(n, links)
m.BONUS = 6.0
PASS_MARK = 18

CASES = [
    ("NO_SIGN", None, []),
    ("A/N", ("A", "N"), []), ("A/E", ("A", "E"), []), ("A/S", ("A", "S"), []),
    ("B/E", ("B", "E"), []), ("B/N", ("B", "N"), []),
    ("A/N then ROTATE E at tick 0", ("A", "N"), [(0, "ROTATE", "E")]),
    ("B/E then MOVE A at tick 100", ("B", "E"), [(100, "MOVE", "A")]),
    ("A/E then ROTATE N at tick 200", ("A", "E"), [(200, "ROTATE", "N")]),
]


def main():
    OUT.mkdir(exist_ok=True)
    rows, traces = [], {}
    for name, sg, cmds in CASES:
        r = m.run(sg, cmds, trace=True)
        traces[name] = r.pop("walkers")
        rows.append([name, r["arrived"], r["ontime"], r["blocked_ticks"], r["score"], r["last_arr"],
                     "PASS" if r["arrived"] >= PASS_MARK else "FAIL"])
    with open(OUT / "scenarios.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "arrived_of_20", "on_time", "blocked_ticks", "score", "last_arrival_tick", "vs_pass_mark_18"])
        w.writerows(rows)
    base, east = traces["NO_SIGN"], traces["A/E"]
    flips = 0
    with open(OUT / "first_decisions.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["walker", "profile", "destination", "no_sign_first_edge", "A/E_first_edge", "changed"])
        for b, e in zip(base, east):
            be, ee = b["decisions"][0][2], e["decisions"][0][2]
            flips += be != ee
            w.writerow([b["id"], b["prof"], b["dest"], be, ee, int(be != ee)])
    for name, sg, cmds in (("NO_SIGN", None, []), ("A_E", ("A", "E"), [])):
        rr = m.run(sg, cmds)
        (OUT / ("replay_%s.json" % name)).write_text(json.dumps({
            "source": "python reference model, not engine", "ruleset_version": "CC-RULESET-01C",
            "level_id": "CC-L01-R1", "seed": 1007, "initial_sign": list(sg) if sg else [], "actions": [],
            "result": {k: rr[k] for k in ("arrived", "ontime", "blocked_ticks", "score", "last_arr")}}, indent=1) + "\n")
    print("scenarios:")
    for r in rows:
        print("  ", r)
    print("walkers whose first route choice changed between NO_SIGN and A/E: %d of 20" % flips)
    return 0


if __name__ == "__main__":
    sys.exit(main())

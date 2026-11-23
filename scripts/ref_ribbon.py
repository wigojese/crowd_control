"""Reference for the ribbon model (src/rendering/ribbon_model.gd). Ribbon width comes ONLY from counted EDGE_ENTERED
events, so a ribbon cannot show flow that did not happen. Run: python3 -I scripts/ref_ribbon.py  (checks + prints PASS/FAIL)
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "data/art_tokens.json").read_text())


def width(count, tok=TOK):
    if count <= 0:
        return 0.0
    g, r = tok["geometry"], tok["ribbon"]
    return min(g["max_ribbon_px"], max(g["min_ribbon_px"], g["min_ribbon_px"] + r["k_px"] * (math.sqrt(count) - 1.0)))


def edge_key(edge_id):
    """'AB' and 'BA' are the same street. In the simulation edge ids look like 'A>B'."""
    a, b = edge_id.split(">")
    return "|".join(sorted((a, b)))


def counts_from_event_lines(lines):
    """Count EDGE_ENTERED events per undirected street from canonical event lines 'tick|seq|TYPE|k=v;k=v'."""
    out = {}
    for ln in lines:
        parts = ln.split("|", 3)
        if len(parts) == 4 and parts[2] == "EDGE_ENTERED":
            f = dict(kv.split("=", 1) for kv in parts[3].split(";"))
            k = edge_key(f["edge"])
            out[k] = out.get(k, 0) + 1
    return out


def main():
    bad = 0

    def check(name, ok):
        nonlocal bad
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    check("zero count draws nothing", width(0) == 0.0)
    check("one walker draws the minimum width", abs(width(1) - TOK["geometry"]["min_ribbon_px"]) < 1e-9)
    ws = [width(n) for n in range(0, 200)]
    check("width never decreases as the count grows", all(a <= b + 1e-12 for a, b in zip(ws, ws[1:])))
    check("width is capped", max(ws) <= TOK["geometry"]["max_ribbon_px"] + 1e-9)
    check("width is at least the minimum for any real flow", all(w >= TOK["geometry"]["min_ribbon_px"] for w in ws[1:]))
    check("both directions of a street share one key", edge_key("A>B") == edge_key("B>A"))
    lines = ["0|0|EDGE_ENTERED|edge=A>B;tokens_after=0;walker=1", "3|0|EDGE_ENTERED|edge=B>A;tokens_after=0;walker=2",
             "3|1|WALKER_SPAWNED|destination=F;origin=A;profile=C;walker=3;deadline_tick=600",
             "4|0|EDGE_ENTERED|edge=A>C;tokens_after=0;walker=3"]
    c = counts_from_event_lines(lines)
    check("counts come from EDGE_ENTERED only, merged by street", c == {"A|B": 2, "A|C": 1})
    print("RIBBON RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

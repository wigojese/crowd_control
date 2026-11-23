"""Stage 13 evidence generator (Python reference only, NOT engine):
 - docs/stage13/trace_<scenario>.csv       event traces from scripts/ref_sim.py
 - docs/stage13/claims_<scenario>.json     causal claims from scripts/ref_explain.py
 - docs/stage13/profile_matrix.json        per-profile counts in each scenario
 - docs/stage13/frames_svg/<scenario>/*.svg  frames for the three scenario videos (then: cd docs/stage13 && node shot13.js)
Usage: python3 -I scripts/stage13_evidence.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_sim  # noqa: E402
import ref_explain as ex  # noqa: E402
import ref_camera as cam  # noqa: E402
import stage11_preview as s11  # noqa: E402
OUT = ROOT / "docs/stage13"
SCEN = [("east_at_north_gate", ["A", "E"], "Sign at North Gate, pointing east"), ("no_sign", [], "No sign"),
        ("east_at_canal_turn", ["B", "E"], "Sign at Canal Turn, pointing east")]


def main():
    OUT.mkdir(exist_ok=True)
    w = ref_sim.World(ref_sim.load_level())
    names = {n["id"]: n["name"] for n in w.level["nodes"]}
    base = w.run([])
    matrix = {}
    for key, sign, label in SCEN + [("north_at_north_gate", ["A", "N"], ""), ("south_at_north_gate", ["A", "S"], "")]:
        r = w.run(sign)
        lines = list(w.lines)
        prof = {}
        for l in lines:
            if "|WALKER_SPAWNED|" in l:
                f = dict(kv.split("=") for kv in l.split("|")[3].split(";"))
                prof[f["walker"]] = f["profile"]
        stats = {p: dict(walkers=sum(1 for v in prof.values() if v == p), rerouted=set(), arrivals=[]) for p in "CFI"}
        for l in lines:
            f = dict(kv.split("=", 1) for kv in l.split("|", 3)[3].split(";") if "=" in kv)
            if "|DECISION|" in l and f.get("reason") == "sign_flipped":
                stats[prof[f["walker"]]]["rerouted"].add(f["walker"])
            if "|WALKER_ARRIVED|" in l:
                stats[prof[f["walker"]]]["arrivals"].append(int(f["arrival_tick"]))
        matrix[key] = {p: dict(walkers=s["walkers"], rerouted=len(s["rerouted"]), arrived=len(s["arrivals"]),
                               mean_arrival_s=round(sum(s["arrivals"]) / 20.0 / max(1, len(s["arrivals"])), 1)) for p, s in stats.items()}
        replay = {"initial_sign": sign, "actions": []}
        claims = ex.explain(lines, r, base, replay, names)
        (OUT / f"trace_{key}.csv").write_text("tick|seq|type|fields\n" + "\n".join(lines) + "\n")
        json.dump({"scenario": key, "sign": sign, "result": {k: r[k] for k in ("arrived", "ontime", "blocked_ticks", "score", "passed")},
                   "claims": [dict(c, shown=c in ex.select(claims)) for c in claims]}, open(OUT / f"claims_{key}.json", "w"), indent=1)
    json.dump(matrix, open(OUT / "profile_matrix.json", "w"), indent=1)
    # video frames: every 4 ticks (5 per second of play), 2x speed in the video, plus a held result card with the copy
    ticks = set(range(4, 641, 4))
    for key, sign, label in SCEN:
        (OUT / "frames_svg" / key).mkdir(parents=True, exist_ok=True)
        r = w.run(sign)
        copy = [c["text"] for c in ex.select(ex.explain(list(w.lines), r, base, {"initial_sign": sign, "actions": []}, names))]
        import stage10_preview as s10
        snaps = s11.run_model(tuple(sign) if sign else None, ticks)
        tf = cam.Transform(center=(181, 262), zoom=0.95)
        for i, tk in enumerate(sorted(snaps)):
            svg, _ = s11.draw(tf, cam.DISTRICT, snaps[tk], tk, sign=tuple(sign) if sign else None, caption=label)
            (OUT / "frames_svg" / key / f"f{i:03d}.svg").write_text(svg)
        last = sorted(snaps)[-1]
        svg, _ = s11.draw(tf, cam.DISTRICT, snaps[last], last, sign=tuple(sign) if sign else None, caption=label)
        card = ['<rect x="12" y="690" width="366" height="120" rx="10" fill="#100C0A" stroke="#EFE3C8" stroke-width="1.2"/>']
        y = 712
        for line in copy:
            words, cur, rows = line.split(), "", []
            for wd in words:
                if len(cur) + len(wd) > 50:
                    rows.append(cur)
                    cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            rows.append(cur)
            for rw in rows:
                card.append(f'<text x="24" y="{y}" font-size="11.5" fill="#EFE3C8">{rw}</text>')
                y += 15
            y += 4
        final = svg.replace("</svg>", "".join(card) + "</svg>")
        for j in range(25):
            (OUT / "frames_svg" / key / f"f{len(snaps)+j:03d}.svg").write_text(final)
        print(key, r["arrived"], len(snaps) + 25, "frames")
    print(json.dumps(matrix["east_at_north_gate"]))


if __name__ == "__main__":
    main()

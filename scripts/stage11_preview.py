"""Stage 11 PREVIEW renderer (NOT the engine): the camera, three zoom bands and a 20 s walkthrough drawn from the
Python reference camera (scripts/ref_camera.py) and a real model run (level CC-L01-R1, sign A/E).
Usage: python3 -I scripts/stage11_preview.py   -> docs/stage11/frames_svg/*.svg, zoom_*.svg, narrow320.svg
Then: cd docs/stage11 && node shot11.js
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_camera as cam  # noqa: E402
import stage10_preview as s10  # noqa: E402
m = s10.m
OUT = ROOT / "docs/stage11"
TOK = s10.TOK
NAMES = s10.NAMES
NOTE_PX = 18.0  # logical px, independent of zoom (Stage 10 option B)


def run_model(sign, snap_ticks):
    events, snaps = [], {}

    def hook(t, W, fifo, sg, entered):
        for wid in entered:
            w = W[wid]
            events.append((t, "|".join(sorted((w["edge"][0], w["edge"][1]))), w["dest"]))
        if t + 1 in snap_ticks:
            snaps[t + 1] = {"walkers": [dict(id=w["id"], prof=w["prof"], dest=w["dest"], state=w["state"], node=w["node"], edge=w["edge"],
                                              t=w["t"], q=w["q"]) for w in W],
                            "qlen": {e: len(q) for e, q in fifo.items()}, "events": list(events)}
    m.run(sign, [], hook=hook)
    return snaps


def draw(tf, band, snap, tick, vp=(390, 844), sign=("A", "E"), caption="", theme="standard"):
    c = TOK["themes"][theme]
    W, H = vp
    z = tf.zoom
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
           f'<defs><pattern id="hatch" width="5" height="5" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
           f'<line x1="0" y1="0" x2="0" y2="5" stroke="{c["plum"]}" stroke-width="2.2"/></pattern></defs>',
           f'<rect width="{W}" height="{H}" fill="{c["night"]}"/>']
    # world-anchored staff grid: every 24 world units, so it moves with the map
    y0 = -200
    for gy in range(0, 560, 24):
        sy = tf.w2s((0, gy))[1]
        svg.append(f'<line x1="0" y1="{sy:.1f}" x2="{W}" y2="{sy:.1f}" stroke="{c["stave"]}" stroke-width=".5" opacity=".07"/>')
    win = cam.flux_window([(t, k, d) for t, k, d in snap["events"]], tick)
    drawn_streets = set()
    for e, (a, b, L, r) in m.EDGES.items():
        if a > b:
            continue
        (x1, y1), (x2, y2) = tf.w2s(m.NODES[a]), tf.w2s(m.NODES[b])
        drawn_streets.add(a + "|" + b)
        ln = math.hypot(x2 - x1, y2 - y1) or 1
        gap = 3.2 * min(z, 1.6)
        px, py = -(y2 - y1) / ln * gap, (x2 - x1) / ln * gap
        narrow = r < 1.0
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c["stave"]}" stroke-width="{1.6:.1f}" '
                   f'{"stroke-dasharray=\"5 4\"" if narrow else ""}/>')
        if not narrow:
            for sg in (1, -1):
                svg.append(f'<line x1="{x1+px*sg:.1f}" y1="{y1+py*sg:.1f}" x2="{x2+px*sg:.1f}" y2="{y2+py*sg:.1f}" stroke="{c["dim"]}" stroke-width="1" opacity=".75"/>')
    snapd = {"walkers": [{"id": w["id"], "active": w["state"] in ("NEEDS", "QUEUED", "ON_EDGE")} for w in snap["walkers"]],
             "streets": sorted(drawn_streets), "flux": win,
             "queues": {"|".join(sorted((e[0], e[1]))): n for e, n in snap["qlen"].items() if n},
             "labels": [{"id": k, "priority": p} for k, p in (("F", 5), ("G", 5), ("A", 4), ("B", 3), ("C", 2), ("D", 2), ("E", 2))]}
    plan = cam.lod_plan(band, snapd)
    if band == cam.CITY:
        for (key, dest), cnt in sorted(win.items()):
            a, b = key.split("|")
            (x1, y1), (x2, y2) = tf.w2s(m.NODES[a]), tf.w2s(m.NODES[b])
            ln = math.hypot(x2 - x1, y2 - y1) or 1
            off = 4 if dest == "G" else -4
            ox, oy = -(y2 - y1) / ln * off, (x2 - x1) / ln * off
            dash = "" if dest == "F" else 'stroke-dasharray="9 6"'
            svg.append(f'<line x1="{x1+ox:.1f}" y1="{y1+oy:.1f}" x2="{x2+ox:.1f}" y2="{y2+oy:.1f}" stroke="{c["amber"] if dest == "F" else c["sage"]}" '
                       f'stroke-width="{s10.rib.width(cnt):.1f}" opacity=".92" {dash}/>')
        for key in plan["knots"]:
            a, b = key.split("|")
            (x1, y1), (x2, y2) = tf.w2s(m.NODES[a]), tf.w2s(m.NODES[b])
            svg.append(f'<circle cx="{(x1+x2)/2:.1f}" cy="{(y1+y2)/2:.1f}" r="9" fill="url(#hatch)" stroke="{c["plum"]}" stroke-width="1.5"/>')
    else:
        scale = 1.0 if band == cam.DISTRICT else 1.45
        counts = {}
        badge_q = cam.cluster_badges({k: n for k, n in snapd["queues"].items()}, 3 if W < 360 else 4) if band == cam.DISTRICT else {}
        for w in snap["walkers"]:
            if w["state"] == "ON_EDGE":
                (x1, y1), (x2, y2) = tf.w2s(m.NODES[w["edge"][0]]), tf.w2s(m.NODES[w["edge"][1]])
                x, y = x1 + (x2 - x1) * w["t"], y1 + (y2 - y1) * w["t"]
            elif w["state"] in ("QUEUED", "NEEDS"):
                nx, ny = tf.w2s(m.NODES[w["node"]])
                if w["q"]:
                    key = "|".join(sorted((w["q"][0], w["q"][1])))
                    if key in badge_q:
                        continue  # drawn once as a badge, below
                    k = counts.get(w["q"], 0)
                    counts[w["q"]] = k + 1
                    (x1, y1), (x2, y2) = tf.w2s(m.NODES[w["q"][0]]), tf.w2s(m.NODES[w["q"][1]])
                    ln = math.hypot(x2 - x1, y2 - y1) or 1
                    x, y = nx + (x2 - x1) / ln * (12 + k * 10 * scale), ny + (y2 - y1) / ln * (12 + k * 10 * scale)
                else:
                    x, y = nx, ny
            else:
                continue
            col = c["amber"] if w["dest"] == "F" else c["sage"]
            g = f'<g transform="translate({x:.1f} {y:.1f}) scale({scale}) translate({-x:.1f} {-y:.1f})">{s10.note(x, y, w["prof"], col, c)}</g>'
            svg.append(g)
        for key, n in badge_q.items():
            e = [e for e in snap["qlen"] if "|".join(sorted((e[0], e[1]))) == key and snap["qlen"][e]][0]
            (x1, y1), (x2, y2) = tf.w2s(m.NODES[e[0]]), tf.w2s(m.NODES[e[1]])
            ln = math.hypot(x2 - x1, y2 - y1) or 1
            bx, by = x1 + (x2 - x1) / ln * 26, y1 + (y2 - y1) / ln * 26
            svg.append(s10.note(bx, by, "C", c["amber"], c))
            svg.append(f'<rect x="{bx+8:.1f}" y="{by-22:.1f}" width="30" height="18" rx="9" fill="{c["night"]}" stroke="{c["plum"]}" stroke-width="1.6"/>'
                       f'<text x="{bx+23:.1f}" y="{by-9:.1f}" font-size="11" font-family="JetBrains Mono" fill="{c["stave"]}" text-anchor="middle">x{n}</text>')
        for e, n in snap["qlen"].items():
            key = "|".join(sorted((e[0], e[1])))
            if n >= 2 and key not in badge_q:
                (x1, y1), (x2, y2) = tf.w2s(m.NODES[e[0]]), tf.w2s(m.NODES[e[1]])
                ln = math.hypot(x2 - x1, y2 - y1) or 1
                l2 = min(ln * .8, 8 + n * 10 * scale)
                ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
                svg.append(f'<line x1="{x1+ux*6:.1f}" y1="{y1+uy*6:.1f}" x2="{x1+ux*l2:.1f}" y2="{y1+uy*l2:.1f}" stroke="url(#hatch)" stroke-width="12" stroke-linecap="round" opacity=".9"/>')
    for k, xy in m.NODES.items():
        x, y = tf.w2s(xy)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.5 if band != cam.STREET else 6}" fill="{c["night"]}" stroke="{c["stave"]}" stroke-width="1.6"/>')
        if k in "AB":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{19 if band != cam.STREET else 27}" fill="none" stroke="{c["stave"]}" stroke-width="1.6" stroke-dasharray="4 4"/>')
        if k in plan["labels"]:
            svg.append(f'<text x="{x+14:.1f}" y="{y+4:.1f}" font-size="12" font-weight="600" fill="{c["stave"]}" stroke="{c["night"]}" stroke-width="3" paint-order="stroke">{NAMES[k]}</text>')
    if sign:
        x, y = tf.w2s(m.NODES[sign[0]])
        r = 20 if band != cam.STREET else 28
        svg.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({r/20}) translate({-x:.1f} {-y:.1f})">{s10.sign_svg(x, y, sign[1], c)}</g>')
    svg.append(f'<rect width="{W}" height="64" fill="{c["panel"]}"/><text x="16" y="26" font-size="11" font-weight="700" letter-spacing="1.4" fill="{c["dim"]}">{band}  ZOOM {z:.2f}</text>')
    svg.append(f'<text x="16" y="50" font-size="13" fill="{c["stave"]}">{caption}</text>')
    svg.append(f'<text x="{W-16}" y="26" font-size="11" font-family="JetBrains Mono" fill="{c["dim"]}" text-anchor="end">tick {tick}  people {plan["people_represented"]}</text>')
    svg.append(f'<text x="{W/2}" y="{H-6}" font-size="9" fill="{c["dim"]}" text-anchor="middle" opacity=".8">PREVIEW FROM MODEL DATA, NOT ENGINE</text></svg>')
    return "\n".join(svg), plan


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "frames_svg").mkdir(exist_ok=True)
    ticks = set(range(2, 402, 2)) | {120}
    snaps = run_model(("A", "E"), ticks)
    # 1) three zoom bands, identical tick 120, same focus point (Canal Turn / Market side)
    focus = m.NODES["B"]
    plans = {}
    for name, z in (("city", 0.78), ("district", 1.2), ("street", 2.2)):
        tf = cam.Transform(center=(focus[0] + 40 / z if z < 2 else focus[0] + 30, focus[1] + 20), zoom=z)
        band = cam.band_initial(z)
        svg, plan = draw(tf, band, snaps[120], 120, caption="Same simulation tick, three information bands")
        (OUT / f"zoom_{name}.svg").write_text(svg)
        plans[name] = {k: plan[k] for k in ("band", "people_represented", "agents", "labels")}
    # 2) 320 px wide, laid out for 320x568 (option B: fixed 18 px notes, badges for long queues)
    tfn = cam.Transform(center=(181, 262), zoom=0.95, viewport=(320, 568))
    svg, _ = draw(tfn, cam.DISTRICT, snaps[120], 120, vp=(320, 568), caption="320 x 568, notes stay 18 px, long queue = badge")
    (OUT / "narrow320.svg").write_text(svg)
    # 3) 20 s walkthrough, 10 frames per second, sim tick = 20 per second
    path, ids = cam.l01_path()
    d = cam.Director(cam.Transform(center=(181, 262), zoom=0.72))
    d.request_focus("LEVEL_FLYIN", "DECORATIVE", ((180, 150), 1.15), 1.2)
    frames, band = [], cam.band_initial(0.72)
    log = []
    for f in range(200):
        t = f / 10.0
        tick = 2 * (f + 1)
        if t < 2.0:
            d.update(0.1)
        elif t < 14.0:
            if d.state != "FOLLOW_CASCADE":
                d.state, d.anim = "FOLLOW_CASCADE", None
            s = path.length * (t - 2.0) / 12.0
            p = path.point_at(s)
            z = 1.15 + (1.9 - 1.15) * min(1.0, (t - 2.0) / 2.0)
            c, _z = cam.compose_focus(p, z, (390, 844), 47, 71, 34, 112)
            d.tf.center, d.tf.zoom = c, z
        else:
            if t == 14.0:
                d.state = "RESULT_PULLBACK"
                d.anim = {"t": 0.0, "dur": 4.0, "c0": d.tf.center, "z0": d.tf.zoom, "c1": (181, 262), "z1": 0.78}
            d.update(0.1)
        band = cam.band_update(band, d.tf.zoom)
        log.append((round(t, 1), d.state, round(d.tf.zoom, 2), band))
        svg, _ = draw(d.tf, band, snaps[tick], tick, caption={"LEVEL_FLYIN": "Level fly-in", "FOLLOW_CASCADE": "Following the path A, B, D, F, G",
                                                              "RESULT_PULLBACK": "Pullback to the atlas"}.get(d.state, d.state))
        (OUT / "frames_svg" / f"f{f:03d}.svg").write_text(svg)
    changes = sum(1 for a, b in zip(log, log[1:]) if a[3] != b[3])
    json.dump({"zoom_plans": plans, "walkthrough_band_changes": changes, "walkthrough_log_sample": log[::20]},
              open(OUT / "preview_numbers.json", "w"), indent=1)
    print("band changes during the walkthrough:", changes)
    print(plans)


if __name__ == "__main__":
    main()

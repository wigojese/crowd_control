"""Stage 12 PREVIEW renderer (NOT the engine): the six transitions driven by scripts/ref_transitions.py over a real
model run (CC-L01-R1, sign A/E). Writes docs/stage12/<id>/frames/*.svg and <id>_sheet.svg. Then: cd docs/stage12 && node shot12.js
Frame times are the reference driver's own timeline (30 fps), not an on-device capture.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_camera as cam  # noqa: E402
import ref_transitions as rt  # noqa: E402
import stage10_preview as s10  # noqa: E402
import stage11_preview as s11  # noqa: E402
m, TOK, NAMES = s10.m, s10.TOK, s10.NAMES
OUT = ROOT / "docs/stage12"
C = TOK["themes"]["standard"]
W, H = 390, 844
FPS = 30


def g(op, body):
    return f'<g opacity="{op:.3f}">{body}</g>' if body else ""


def frame(tf, snap, tick, fx, title, tms, sign_slot="A", sign_head="E"):
    """fx: streets_alpha, labels_alpha, agents_alpha, ribbons_alpha, ghost_alpha, sign_scale, edge_highlight, glow"""
    z = tf.zoom
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
           f'<defs><pattern id="hatch" width="5" height="5" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
           f'<line x1="0" y1="0" x2="0" y2="5" stroke="{C["plum"]}" stroke-width="2.2"/></pattern></defs>',
           f'<rect width="{W}" height="{H}" fill="{C["night"]}"/>']
    grid = "".join(f'<line x1="0" y1="{tf.w2s((0, gy))[1]:.1f}" x2="{W}" y2="{tf.w2s((0, gy))[1]:.1f}" stroke="{C["stave"]}" stroke-width=".5" opacity=".07"/>'
                   for gy in range(0, 560, 24))
    out.append(grid)
    streets, hl = [], []
    for e, (a, b, L, r) in m.EDGES.items():
        if a > b:
            continue
        (x1, y1), (x2, y2) = tf.w2s(m.NODES[a]), tf.w2s(m.NODES[b])
        ln = math.hypot(x2 - x1, y2 - y1) or 1
        gap = 3.2 * min(z, 1.6)
        px, py = -(y2 - y1) / ln * gap, (x2 - x1) / ln * gap
        narrow = r < 1.0
        streets.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C["stave"]}" stroke-width="1.6" '
                       f'{"stroke-dasharray=\"5 4\"" if narrow else ""}/>')
        if not narrow:
            for s in (1, -1):
                streets.append(f'<line x1="{x1+px*s:.1f}" y1="{y1+py*s:.1f}" x2="{x2+px*s:.1f}" y2="{y2+py*s:.1f}" stroke="{C["dim"]}" stroke-width="1" opacity=".75"/>')
        if fx.get("highlight_edge") == a + b:
            hl.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C["amber"]}" stroke-width="7" stroke-linecap="round"/>')
    out.append(g(fx.get("streets_alpha", 1.0), "".join(streets)))
    out.append(g(fx.get("edge_highlight", 0.0), "".join(hl)))
    # ghost trajectories of the previous run: gray ink from counted flux
    ghost = []
    for (key, dest), cnt in sorted(fx.get("ghost_flux", {}).items()):
        a, b = key.split("|")
        (x1, y1), (x2, y2) = tf.w2s(m.NODES[a]), tf.w2s(m.NODES[b])
        ghost.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C["stave"]}" stroke-width="{s10.rib.width(cnt)+2:.1f}" '
                     f'{"stroke-dasharray=\"9 6\"" if dest == "G" else ""}/>')
    out.append(g(fx.get("ghost_alpha", 0.0) * 0.5, "".join(ghost)))
    ribs = []
    for (key, dest), cnt in sorted(cam.flux_window(snap["events"], tick).items()):
        a, b = key.split("|")
        (x1, y1), (x2, y2) = tf.w2s(m.NODES[a]), tf.w2s(m.NODES[b])
        ln = math.hypot(x2 - x1, y2 - y1) or 1
        off = 4 if dest == "G" else -4
        ox, oy = -(y2 - y1) / ln * off, (x2 - x1) / ln * off
        ribs.append(f'<line x1="{x1+ox:.1f}" y1="{y1+oy:.1f}" x2="{x2+ox:.1f}" y2="{y2+oy:.1f}" stroke="{C["amber"] if dest == "F" else C["sage"]}" '
                    f'stroke-width="{s10.rib.width(cnt):.1f}" {"stroke-dasharray=\"9 6\"" if dest == "G" else ""}/>')
    out.append(g(fx.get("ribbons_alpha", 0.0), "".join(ribs)))
    notes = []
    for w in snap["walkers"]:
        if w["state"] == "ON_EDGE":
            (x1, y1), (x2, y2) = tf.w2s(m.NODES[w["edge"][0]]), tf.w2s(m.NODES[w["edge"][1]])
            x, y = x1 + (x2 - x1) * w["t"], y1 + (y2 - y1) * w["t"]
        elif w["state"] in ("QUEUED", "NEEDS"):
            x, y = tf.w2s(m.NODES[w["node"]])
        else:
            continue
        notes.append(s10.note(x, y, w["prof"], C["amber"] if w["dest"] == "F" else C["sage"], C))
    out.append(g(fx.get("agents_alpha", 1.0), "".join(notes)))
    nodes, labels = [], []
    for k, xy in m.NODES.items():
        x, y = tf.w2s(xy)
        nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{C["night"]}" stroke="{C["stave"]}" stroke-width="1.6"/>')
        if k in "AB":
            nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="none" stroke="{C["stave"]}" stroke-width="1.6" stroke-dasharray="4 4"/>')
        labels.append(f'<text x="{x+14:.1f}" y="{y+4:.1f}" font-size="12" font-weight="600" fill="{C["stave"]}" stroke="{C["night"]}" stroke-width="3" paint-order="stroke">{NAMES[k]}</text>')
    out.append(g(fx.get("streets_alpha", 1.0), "".join(nodes)))
    out.append(g(fx.get("labels_alpha", 1.0), "".join(labels)))
    sx, sy = tf.w2s(m.NODES[sign_slot])
    sc = fx.get("sign_scale", 1.0)
    glow = fx.get("socket_glow", 0.0)
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="27" fill="none" stroke="{C["vermilion"]}" stroke-width="3" opacity="{glow:.2f}"/>')
    out.append(f'<g transform="translate({sx:.1f} {sy:.1f}) scale({sc:.3f}) translate({-sx:.1f} {-sy:.1f})">{s10.sign_svg(sx, sy, sign_head, C)}</g>')
    out.append(f'<rect width="{W}" height="64" fill="{C["panel"]}"/><text x="16" y="26" font-size="11" font-weight="700" letter-spacing="1.4" fill="{C["dim"]}">{title.upper()}</text>')
    out.append(f'<text x="{W-16}" y="26" font-size="11" font-family="JetBrains Mono" fill="{C["stave"]}" text-anchor="end">{tms:.0f} ms</text>')
    out.append(f'<text x="16" y="50" font-size="12" fill="{C["dim"]}">zoom {tf.zoom:.2f}   centre ({tf.center[0]:.0f}, {tf.center[1]:.0f})</text>')
    out.append(f'<text x="{W/2}" y="{H-6}" font-size="9" fill="{C["dim"]}" text-anchor="middle" opacity=".8">PREVIEW FROM MODEL DATA, NOT ENGINE</text></svg>')
    return "\n".join(out)


def main():
    OUT.mkdir(exist_ok=True)
    snaps = s11.run_model(("A", "E"), {2, 120, 400})
    final_flux = {}
    for t, key, dest in snaps[400]["events"]:
        final_flux[(key, dest)] = final_flux.get((key, dest), 0) + 1
    base = {"streets_alpha": 1.0, "labels_alpha": 1.0, "agents_alpha": 1.0, "ribbons_alpha": 0.0}
    summary = {}
    for t in rt.DEF["transitions"]:
        i = t["id"]
        (OUT / i).mkdir(exist_ok=True)
        (OUT / i / "frames").mkdir(exist_ok=True)
        tr = rt.Transition(t)
        tr.start()
        n_frames = int(math.ceil(t["duration_ms"] / 1000 * FPS)) + 1
        hold = 8
        times = []
        sheet_idx = {round(k * (n_frames - 1) / 5) for k in range(6)}
        sheet = []
        for f in range(n_frames + hold):
            tms = min(f * 1000 / FPS, t["duration_ms"])
            tr2 = rt.Transition(t)
            tr2.start()
            tr2.update(tms)
            v = tr2.values()
            tf = cam.Transform(center=v.get("cam_center", v.get("cam_path", (181, 262))), zoom=v.get("cam_zoom", 1.0))
            fx = dict(base)
            snap, tick = snaps[120], 120
            if i == "paper_unfolds":
                fx.update(streets_alpha=v["streets_alpha"], labels_alpha=v["labels_alpha"])
                snap, tick = snaps[2], 2
                tf = cam.Transform(center=v["cam_center"], zoom=v["cam_zoom"])
            elif i == "sign_drops":
                tf = cam.Transform(center=(181, 262), zoom=1.0)
                fx.update(sign_scale=v["sign_scale"], socket_glow=v["socket_glow"])
                snap, tick = snaps[2], 2
            elif i == "consequence_follows_ink":
                tf = cam.Transform(center=v["cam_path"], zoom=v["cam_zoom"])
                fx.update(edge_highlight=v["edge_highlight"], highlight_edge="AC")
            elif i == "district_to_diagram":
                tf = cam.Transform(center=(181, 262), zoom=0.9)
                fx.update(agents_alpha=v["agents_alpha"], ribbons_alpha=v["ribbons_alpha"])
            elif i == "outcome_pullback":
                snap, tick = snaps[400], 400
                fx.update(ribbons_alpha=v["ribbons_alpha"], agents_alpha=1.0 - v["ribbons_alpha"])
            elif i == "ghosted_rewind":
                tf = cam.Transform(center=(181, 262), zoom=0.9)
                fx.update(agents_alpha=0.0, ghost_alpha=v["ghost_alpha"], ghost_flux=final_flux)
                snap, tick = snaps[2], 2
                snap = dict(snap, walkers=[])  # the run was reset at t=0: no agents, no old score
            svg = frame(tf, snap, tick, fx, i.replace("_", " "), min(tms, t["duration_ms"]))
            (OUT / i / "frames" / f"f{f:03d}.svg").write_text(svg)
            if f in sheet_idx:
                sheet.append((f, svg, tms))
        summary[i] = {"frames": n_frames + hold, "duration_ms": t["duration_ms"], "fps": FPS, "sheet_frames": [s[0] for s in sheet]}
        (OUT / i / "sheet.json").write_text(json.dumps([s[0] for s in sheet]))
    json.dump(summary, open(OUT / "frames_summary.json", "w"), indent=1)
    print(summary)


if __name__ == "__main__":
    main()

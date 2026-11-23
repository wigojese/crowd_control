"""Stage 10 PREVIEW renderer. NOT the game engine. Draws direction C (transit score) from real simulation-model runs
(docs/analysis/stage03_numeric_check.py, level CC-L01-R1) into SVG, so the visual language can be judged on real
data while no Godot can run here. Every picture is labelled 'PREVIEW, NOT ENGINE'. Ribbon widths come from counted
edge entries via scripts/ref_ribbon.py. Usage: python3 -I scripts/stage10_preview.py   (writes docs/stage10/*.svg)
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docs/analysis"))
sys.path.insert(0, str(ROOT / "scripts"))
import stage03_numeric_check as m  # noqa: E402
import ref_ribbon as rib  # noqa: E402

OUT = ROOT / "docs/stage10"
TOK = json.loads((ROOT / "data/art_tokens.json").read_text())
NAMES = {"A": "North Gate", "B": "Canal Turn", "C": "Market", "D": "Bridge West", "E": "Bridge East", "F": "School", "G": "Plaza"}
n = dict(m.NODES)
n["C"] = (270, 115)
m.configure(n, [(a, b, 0.3 if (a, b) == ("B", "D") else r) for a, b, r in m.LINKS])
m.BONUS = 6.0
W, H, S = 390, 844, 1.2


def P(xy):
    return (195 + (xy[0] - 181) * S, 175 + (xy[1] - 50) * S)


def collect(sign, at_ticks):
    """Run the model once, keep a snapshot at the wanted ticks and cumulative flux/queue stats."""
    snaps, flux, qsum = {}, {}, {}

    def hook(t, Wk, fifo, sg, entered):
        for wid in entered:
            w = Wk[wid]
            key = (rib.edge_key(w["edge"][0] + ">" + w["edge"][1]), w["dest"])
            flux[key] = flux.get(key, 0) + 1
        for e, q in fifo.items():
            qsum[e] = qsum.get(e, 0) + len(q)
        if t + 1 in at_ticks:
            ws = []
            for w in Wk:
                ws.append({"id": w["id"], "prof": w["prof"], "dest": w["dest"], "state": w["state"], "node": w["node"],
                           "edge": w["edge"], "t": w["t"], "q": w["q"]})
            qlen = {e: len(q) for e, q in fifo.items()}
            snaps[t + 1] = {"walkers": ws, "qlen": qlen, "sign": dict(sg), "flux": dict(flux)}

    res = m.run(sign, [], hook=hook)
    return res, snaps, qsum


def pal(theme):
    return TOK["themes"][theme]


def note(x, y, kind, color, c):
    """A walker as a note: single, beamed pair (follower), flagged (independent)."""
    s = ""
    if kind == "C":
        s += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="4.6" ry="3.5" fill="{color}" transform="rotate(-20 {x:.1f} {y:.1f})"/>'
        s += f'<line x1="{x+4:.1f}" y1="{y:.1f}" x2="{x+4:.1f}" y2="{y-13:.1f}" stroke="{color}" stroke-width="1.6"/>'
    elif kind == "F":
        for dx in (-5, 4):
            s += f'<ellipse cx="{x+dx:.1f}" cy="{y:.1f}" rx="4" ry="3.1" fill="{color}" transform="rotate(-20 {x+dx:.1f} {y:.1f})"/>'
            s += f'<line x1="{x+dx+3.5:.1f}" y1="{y:.1f}" x2="{x+dx+3.5:.1f}" y2="{y-12:.1f}" stroke="{color}" stroke-width="1.5"/>'
        s += f'<line x1="{x-1.5:.1f}" y1="{y-12:.1f}" x2="{x+7.5:.1f}" y2="{y-12:.1f}" stroke="{color}" stroke-width="2.6"/>'
    else:
        s += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="4.4" ry="3.3" fill="{color}" transform="rotate(-20 {x:.1f} {y:.1f})"/>'
        s += f'<line x1="{x+4:.1f}" y1="{y:.1f}" x2="{x+4:.1f}" y2="{y-13:.1f}" stroke="{color}" stroke-width="1.5"/>'
        s += f'<path d="M{x+4:.1f} {y-13:.1f} q6 2 4 8" fill="none" stroke="{color}" stroke-width="1.6"/>'
    return s


def sign_svg(x, y, head, c, lifted=False):
    d = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}[head]
    px, py = -d[1], d[0]
    tip = (x + d[0] * 11, y + d[1] * 11)
    b1 = (x - d[0] * 7 + px * 8, y - d[1] * 7 + py * 8)
    b2 = (x - d[0] * 7 - px * 8, y - d[1] * 7 - py * 8)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="{c["vermilion"]}"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="none" stroke="{c["stave"]}" stroke-width="1.5" opacity=".8"/>'
            f'<path d="M{tip[0]:.1f} {tip[1]:.1f} L{b1[0]:.1f} {b1[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f} Z" fill="{c["sign_arrow"]}"/>'
            f'<path d="M{x-4:.1f} {y-20:.1f} l4 5 l4 -5" fill="{c["night"]}"/>')


def frame(theme, state, snap, total_arrived, tick, sign, qsum, label, mode="run", width=W):
    c = pal(theme)
    g = TOK["geometry"]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{width}" height="{int(H*width/W)}" '
           f'font-family="Inter, sans-serif">']
    svg.append(f'<defs><pattern id="hatch" width="5" height="5" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
               f'<line x1="0" y1="0" x2="0" y2="5" stroke="{c["plum"]}" stroke-width="2.2"/></pattern></defs>')
    svg.append(f'<rect width="{W}" height="{H}" fill="{c["night"]}"/>')
    for yy in range(0, int(H), g["stave_grid_px"] * 2):  # static staff lines, world-anchored grid
        svg.append(f'<line x1="0" y1="{yy}" x2="{W}" y2="{yy}" stroke="{c["stave"]}" stroke-width=".5" opacity=".07"/>')
    flux = snap["flux"] if snap else {}
    # streets
    for e, (a, b, L, r) in m.EDGES.items():
        if a > b:
            continue
        (x1, y1), (x2, y2) = P(m.NODES[a]), P(m.NODES[b])
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        px, py = -dy / ln * 3.2, dx / ln * 3.2
        narrow = r < 1.0
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c["stave"]}" stroke-width="13" opacity=".09"/>')
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c["stave"]}" stroke-width="1.6" '
                   f'{"stroke-dasharray=\"5 4\"" if narrow else ""}/>')
        if not narrow:
            for sgn in (1, -1):
                svg.append(f'<line x1="{x1+px*sgn:.1f}" y1="{y1+py*sgn:.1f}" x2="{x2+px*sgn:.1f}" y2="{y2+py*sgn:.1f}" '
                           f'stroke="{c["dim"]}" stroke-width="1" opacity=".75"/>')
    # ribbons (counted flux); the School ribbon is solid and the Plaza ribbon dashed so grayscale still separates them
    if mode == "result":
        for (key, dest), cnt in sorted(flux.items()):
            a, b = key.split("|")
            (x1, y1), (x2, y2) = P(m.NODES[a]), P(m.NODES[b])
            off = 0 if dest == "F" else 0
            col = c["amber"] if dest == "F" else c["sage"]
            dash = "" if dest == "F" else 'stroke-dasharray="9 6"'
            ln = math.hypot(x2 - x1, y2 - y1)
            ox, oy = -(y2 - y1) / ln * (4 if dest == "G" else -4), (x2 - x1) / ln * (4 if dest == "G" else -4)
            svg.append(f'<line x1="{x1+ox:.1f}" y1="{y1+oy:.1f}" x2="{x2+ox:.1f}" y2="{y2+oy:.1f}" stroke="{col}" '
                       f'stroke-width="{rib.width(cnt):.1f}" stroke-linecap="butt" opacity=".92" {dash}/>')
            mx, my = (x1 + x2) / 2 + ox * 2.2, (y1 + y2) / 2 + oy * 2.2
            svg.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-size="11" font-family="JetBrains Mono" fill="{c["stave"]}" '
                       f'stroke="{c["night"]}" stroke-width="3" paint-order="stroke" text-anchor="middle">{cnt}</text>')
    # queues: plum hatched band along the street behind the node
    if snap and mode == "run":
        for e, q in snap["qlen"].items():
            if q >= 2:
                a, b = m.EDGES[e][0], m.EDGES[e][1]
                (x1, y1), (x2, y2) = P(m.NODES[a]), P(m.NODES[b])
                ln = math.hypot(x2 - x1, y2 - y1)
                ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
                l2 = min(ln * .8, 8 + q * 9)
                svg.append(f'<line x1="{x1+ux*6:.1f}" y1="{y1+uy*6:.1f}" x2="{x1+ux*l2:.1f}" y2="{y1+uy*l2:.1f}" '
                           f'stroke="{c["night"]}" stroke-width="15" stroke-linecap="round"/>')
                svg.append(f'<line x1="{x1+ux*6:.1f}" y1="{y1+uy*6:.1f}" x2="{x1+ux*l2:.1f}" y2="{y1+uy*l2:.1f}" '
                           f'stroke="url(#hatch)" stroke-width="13" stroke-linecap="round"/>')
    # nodes, sockets, emblems, labels
    for k, xy in m.NODES.items():
        x, y = P(xy)
        if k in "AB":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="none" stroke="{c["stave"]}" stroke-width="1.6" '
                       f'stroke-dasharray="4 4" opacity=".9"/>')
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{c["night"]}" stroke="{c["stave"]}" stroke-width="1.6"/>')
        if k == "F":
            svg.append(f'<path d="M{x-11:.1f} {y+4:.1f} v-11 l11 -7 l11 7 v11 z" fill="{c["night"]}" stroke="{c["amber"]}" stroke-width="2"/>')
        if k == "G":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{c["night"]}" stroke="{c["sage"]}" stroke-width="2" '
                       f'stroke-dasharray="3 3"/>')
        lx = x + (16 if k in "ADG" or k == "F" and False else -16)
        anchor = "start" if k in "CEG" else "end"
        lx = x + (16 if anchor == "start" else -16)
        ly = y + 4
        if k in "FG":
            lx, anchor, ly = x, "middle", y + 30
        if k == "A":
            lx, anchor, ly = x, "middle", y - 28
        svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="12" font-weight="600" fill="{c["stave"]}" text-anchor="{anchor}" '
                   f'stroke="{c["night"]}" stroke-width="{g["label_halo_px"]}" paint-order="stroke">{NAMES[k]}</text>')
    # walkers
    if snap and mode == "run":
        counts = {}
        for w in snap["walkers"]:
            st = w["state"]
            if st == "ON_EDGE":
                a, b = w["edge"][0], w["edge"][1]
                (x1, y1), (x2, y2) = P(m.NODES[a]), P(m.NODES[b])
                x, y = x1 + (x2 - x1) * w["t"], y1 + (y2 - y1) * w["t"]
            elif st in ("QUEUED", "NEEDS"):
                nx, ny = P(m.NODES[w["node"]])
                k = counts.get(w["q"] or w["node"], 0)
                counts[w["q"] or w["node"]] = k + 1
                if w["q"]:
                    a, b = w["q"][0], w["q"][1]
                    (x1, y1), (x2, y2) = P(m.NODES[a]), P(m.NODES[b])
                    ln = math.hypot(x2 - x1, y2 - y1)
                    ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
                    x, y = nx + ux * (10 + k * 9), ny + uy * (10 + k * 9)
                else:
                    x, y = nx, ny
            else:
                continue
            col = c["amber"] if w["dest"] == "F" else c["sage"]
            svg.append(note(x, y, w["prof"], col, c))
    # the sign
    if sign and mode != "tray":
        slot, head = sign
        x, y = P(m.NODES[slot])
        svg.append(sign_svg(x, y, head, c))
    # HUD
    svg.append(f'<rect y="0" width="{W}" height="118" fill="{c["panel"]}"/>')
    svg.append(f'<text x="20" y="72" font-size="12" font-weight="700" letter-spacing="1.5" fill="{c["dim"]}">SCHOOL CROSSING</text>')
    svg.append(f'<text x="20" y="104" font-size="30" font-weight="200" font-family="JetBrains Mono" fill="{c["stave"]}">'
               f'{total_arrived}<tspan font-size="16" fill="{c["dim"]}"> / 20</tspan></text>')
    secs = tick / 20
    svg.append(f'<text x="{W-20}" y="104" font-size="30" font-weight="200" font-family="JetBrains Mono" fill="{c["stave"]}" '
               f'text-anchor="end">0:{int(secs):02d}</text>')
    svg.append(f'<text x="{W-20}" y="72" font-size="12" fill="{c["dim"]}" text-anchor="end">{label[0]}</text>')
    svg.append(f'<line x1="20" y1="114" x2="{W-20}" y2="114" stroke="{c["dim"]}" stroke-width="1" opacity=".5"/>')
    svg.append(f'<line x1="20" y1="114" x2="{20+(W-40)*tick/640:.1f}" y2="114" stroke="{c["amber"]}" stroke-width="3"/>')
    # dock
    svg.append(f'<rect y="{H-112}" width="{W}" height="112" fill="{c["panel"]}"/>')
    if mode == "tray":
        svg.append(f'<text x="{W/2}" y="{H-92}" font-size="13" fill="{c["dim"]}" text-anchor="middle">Drag the sign to a ringed junction</text>')
        svg.append(sign_svg(W / 2, H - 56, "E", c))
    elif mode == "result":
        svg.append(f'<text x="{W/2}" y="{H-90}" font-size="14" font-weight="600" fill="{c["stave"]}" text-anchor="middle">{label[1]}</text>')
        svg.append(f'<text x="{W/2}" y="{H-70}" font-size="12" fill="{c["dim"]}" text-anchor="middle">{label[2]}</text>')
        svg.append(f'<rect x="97" y="{H-60}" width="196" height="40" rx="20" fill="none" stroke="{c["stave"]}" stroke-width="1.6"/>')
        svg.append(f'<text x="{W/2}" y="{H-35}" font-size="14" font-weight="700" fill="{c["stave"]}" text-anchor="middle">Try again</text>')
    else:
        for i, tx in enumerate(("Restart", "Pause")):
            x0 = 20 if i == 0 else W - 20 - 124
            svg.append(f'<rect x="{x0}" y="{H-86}" width="124" height="48" rx="24" fill="none" stroke="{c["stave"]}" stroke-width="1.6"/>')
            svg.append(f'<text x="{x0+62}" y="{H-57}" font-size="14" font-weight="700" fill="{c["stave"]}" text-anchor="middle">{tx}</text>')
        svg.append(f'<text x="{W/2}" y="{H-96}" font-size="12" fill="{c["dim"]}" text-anchor="middle">{label[1]}</text>')
    svg.append(f'<text x="{W/2}" y="{H-6}" font-size="9" fill="{c["dim"]}" text-anchor="middle" opacity=".8">PREVIEW FROM MODEL DATA, NOT ENGINE</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def longest_wait(qsum):
    best = max(qsum.items(), key=lambda kv: kv[1])
    return "%s to %s" % (NAMES[best[0][0]], NAMES[best[0][1]])


def arrived(snap):
    return sum(w["state"] == "ARRIVED" for w in snap["walkers"])


def main():
    OUT.mkdir(exist_ok=True)
    ticks = {1, 120, 240, 640}
    res_e, sn_e, q_e = collect(("A", "E"), ticks)
    res_n, sn_n, q_n = collect(None, ticks)
    files = {}
    files["s1_placement"] = frame("standard", 1, None, 0, 0, None, {}, ("Place the sign", ""), mode="tray")
    files["s2_run_AE_t120"] = frame("standard", 2, sn_e[120], arrived(sn_e[120]), 120, ("A", "E"), q_e,
                                    ("Sign: North Gate, east", "Tap the sign to turn it"))
    files["s3_run_nosign_t240"] = frame("standard", 3, sn_n[240], arrived(sn_n[240]), 240, None, q_n,
                                        ("No sign placed", "Queues forming"))
    files["s4_result_AE"] = frame("standard", 4, sn_e[640], res_e["arrived"], 640, ("A", "E"), q_e,
                                  ("Goal 18", "%d / 20 arrived. Goal 18: reached." % res_e["arrived"],
                                   "Longest wait: " + longest_wait(q_e)), mode="result")
    files["s5_result_nosign"] = frame("standard", 5, sn_n[640], res_n["arrived"], 640, None, q_n,
                                      ("Goal 18", "%d / 20 arrived. Goal 18: %d short." % (res_n["arrived"], 18 - res_n["arrived"]),
                                       "Longest wait: " + longest_wait(q_n)), mode="result")
    files["v_highcontrast_t120"] = frame("high_contrast", 2, sn_e[120], arrived(sn_e[120]), 120, ("A", "E"), q_e,
                                         ("Sign: North Gate, east", "Tap the sign to turn it"))
    files["v_result_AE_highcontrast"] = frame("high_contrast", 4, sn_e[640], res_e["arrived"], 640, ("A", "E"), q_e,
                                              ("Goal 18", "%d / 20 arrived. Goal 18: reached." % res_e["arrived"],
                                               "Longest wait: " + longest_wait(q_e)), mode="result")
    for k, v in files.items():
        (OUT / (k + ".svg")).write_text(v)
    json.dump({"A/E": {k: res_e[k] for k in ("arrived", "ontime", "score")},
               "NO_SIGN": {k: res_n[k] for k in ("arrived", "ontime", "score")}}, open(OUT / "preview_numbers.json", "w"), indent=1)
    print("wrote", len(files), "SVGs; A/E", res_e["arrived"], "NO_SIGN", res_n["arrived"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

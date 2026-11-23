"""Route diagrams for the levels (SVG, from the level files). Edge width shows capacity (walkers per second),
spawn groups show origin, time, size and destination, and the tested solutions are drawn as sign symbols.
Usage: python3 -I scripts/stage14_diagrams.py ; then node docs/stage14/shot14.js
"""
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "data/art_tokens.json").read_text())["themes"]["standard"]
OUT = ROOT / "docs/stage14"
LEVELS = ["cc_l01_r1", "cc_l02_ferry", "cc_l03_narrow"]
W, H = 390, 620


def P(n):
    return (40 + (n["x"] - 80) * 1.5, 150 + (n["y"] - 40) * 0.88)


def main():
    OUT.mkdir(exist_ok=True)
    c = TOK
    for f in LEVELS:
        lv = json.loads((ROOT / "data/levels" / (f + ".json")).read_text())
        nodes = {n["id"]: n for n in lv["nodes"]}
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
               f'<rect width="{W}" height="{H}" fill="{c["night"]}"/>',
               f'<text x="16" y="26" font-size="11" font-weight="700" letter-spacing="1.4" fill="{c["dim"]}">{lv["level_id"]}</text>',
               f'<text x="16" y="48" font-size="16" font-weight="700" fill="{c["stave"]}">{lv["name"]}</text>',
               f'<text x="16" y="66" font-size="10.5" fill="{c["dim"]}">deliver {lv["pass_mark"]} of {sum(sum(s["mix"].values()) for s in lv["schedule"])} before 0:30. Edge width = capacity per second.</text>']
        for e in lv["edges"]:
            (x1, y1), (x2, y2) = P(nodes[e["from"]]), P(nodes[e["to"]])
            svg.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{c["stave"]}" stroke-width="{1 + e["rate"] * 2.2:.1f}" opacity=".55" '
                       f'{"stroke-dasharray=\"6 4\"" if e["rate"] < 0.5 else ""}/>')
            svg.append(f'<text x="{(x1+x2)/2+6:.0f}" y="{(y1+y2)/2:.0f}" font-size="10" font-family="JetBrains Mono" fill="{c["dim"]}" stroke="{c["night"]}" stroke-width="3" paint-order="stroke">{e["rate"]}/s</text>')
        for nid, n in nodes.items():
            x, y = P(n)
            ring = f'<circle cx="{x:.0f}" cy="{y:.0f}" r="17" fill="none" stroke="{c["stave"]}" stroke-width="1.4" stroke-dasharray="4 4"/>' if nid in lv["sockets"] else ""
            svg.append(ring + f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{c["night"]}" stroke="{c["stave"]}" stroke-width="1.6"/>'
                       f'<text x="{x+12:.0f}" y="{y+4:.0f}" font-size="11" font-weight="600" fill="{c["stave"]}" stroke="{c["night"]}" stroke-width="3" paint-order="stroke">{n["name"]}</text>')
        ly = 84
        for s in lv["schedule"]:
            col = c["amber"] if s["destination"] == "F" else c["sage"]
            n_w = sum(s["mix"].values())
            svg.append(f'<text x="16" y="{ly}" font-size="10.5" font-family="JetBrains Mono" fill="{col}">{s["tick"]/20:.0f} s: {n_w} walkers from {nodes[s["origin"]]["name"]} to {nodes[s["destination"]]["name"]}</text>')
            ly += 14
        d4 = {"N": "north", "E": "east", "S": "south", "W": "west"}
        sy0 = H - 118
        for j, sol in enumerate(lv["solutions"]):
            slot, head = sol["initial_sign"]
            x, y = P(nodes[slot])
            d = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}[head]
            sx, sy = x + (-30 if j == 0 else 30), y + 26
            svg.append(f'<g transform="translate({sx:.0f} {sy:.0f})"><circle r="10" fill="{c["vermilion"]}"/><path d="M{d[0]*8} {d[1]*8} L{-d[0]*4-d[1]*6} {-d[1]*4+d[0]*6} L{-d[0]*4+d[1]*6} {-d[1]*4-d[0]*6} Z" fill="{c["night"]}"/>'
                       f'<text y="4" text-anchor="middle" font-size="9" font-weight="700" fill="{c["night"]}" opacity="0"> </text></g>')
            svg.append(f'<text x="{sx:.0f}" y="{sy-14:.0f}" font-size="9.5" font-weight="700" text-anchor="middle" fill="{c["stave"]}" stroke="{c["night"]}" stroke-width="3" paint-order="stroke">{j+1}</text>')
            then = "".join(", then %s to %s at %d s" % (cm[2].lower(), nodes[cm[3]]["name"], cm[0] // 20) for cm in sol["commands"])
            svg.append(f'<text x="16" y="{sy0 + j*14}" font-size="10.5" fill="{c["stave"]}">Solution {j+1}: sign at {nodes[slot]["name"]} pointing {d4[head]}{then}</text>')
        words, rows, cur = ("Lesson: " + lv["lesson"]).split(), [], ""
        for wd in words:
            if len(cur) + len(wd) > 60:
                rows.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        rows.append(cur)
        for k, rw in enumerate(rows[:3]):
            svg.append(f'<text x="16" y="{H-76 + k*13}" font-size="10" fill="{c["dim"]}">{rw}</text>')
        svg.append(f'<text x="{W/2}" y="{H-5}" font-size="9" text-anchor="middle" fill="{c["dim"]}" opacity=".8">DIAGRAM FROM THE LEVEL FILE. NUMBERS MARK EACH SOLUTION</text></svg>')
        (OUT / f"route_{f}.svg").write_text("\n".join(svg))
    print("ok")


if __name__ == "__main__":
    main()

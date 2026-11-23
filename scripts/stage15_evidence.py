"""Stage 15 evidence (Python reference, NOT engine): rendered mix of a real run, muted-equivalence timeline,
colour-vision simulation of the Stage 10 pictures, reduced-motion frames. Usage: python3 -I scripts/stage15_evidence.py
then: cd docs/stage15 && node shot15.js
"""
import json
import pathlib
import sys
import wave

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_audio as ra  # noqa: E402
import ref_sim  # noqa: E402
import ref_transitions as rt  # noqa: E402
import ref_camera as cam  # noqa: E402
import stage12_preview as s12  # noqa: E402
import stage11_preview as s11  # noqa: E402
OUT = ROOT / "docs/stage15"
SR = 22050
MAP = ra.MAP


def load(name):
    with wave.open(str(ROOT / MAP["cues"][name]["file"]), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768.0


def shift(x, semis):
    f = 2 ** (semis / 12.0)
    idx = np.arange(0, len(x) - 1, f)
    return np.interp(idx, np.arange(len(x)), x)


def mix(plays, bed, seconds):
    out = np.zeros(int(SR * (seconds + 1.5)))
    for p in plays:
        s = shift(load(p["cue"]), p["pitch"]) if p["pitch"] else load(p["cue"])
        i = int(p["t_ms"] / 1000 * SR)
        n = min(len(s), len(out) - i)
        out[i:i + n] += s[:n] * p["gain"]
    loop = load("foot_bed")
    for k, (t, g) in enumerate(bed):
        t1 = bed[k + 1][0] if k + 1 < len(bed) else t + 500
        i0, i1 = int(t / 1000 * SR), min(len(out), int(t1 / 1000 * SR))
        seg = np.resize(np.roll(loop, -(i0 % len(loop))), i1 - i0)
        out[i0:i1] += seg * g * 0.6
    return out


def write(path, x):
    pk = np.max(np.abs(x))
    if pk > 0.9:
        x = x * 0.9 / pk
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return dict(duration_s=round(len(x) / SR, 1), peak_dbfs=round(float(20 * np.log10(np.max(np.abs(x)) + 1e-12)), 1),
                rms_dbfs=round(float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)), 1), clipped=int(np.sum(np.abs(x) >= 0.999)), scaled_down=bool(pk > 0.9))


# Machado, Oliveira, Fernandes 2009, severity 1.0, linear RGB
SIM = {"protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
       "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
       "tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}


def to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def simulate(rgb, m):
    return to_srgb(to_lin(np.asarray(rgb, dtype=float)) @ np.array(m).T)


def lab(rgb):
    c = to_lin(np.asarray(rgb, dtype=float))
    xyz = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ c
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def main():
    OUT.mkdir(exist_ok=True)
    w = ref_sim.World(ref_sim.load_level())
    w.run(["A", "E"])
    ev = ra.from_lines(list(w.lines))
    plays, bed = ra.schedule(ev, MAP["defaults"], True)
    mix_stats = {"A/E": write(OUT / "mix_AE_run.wav", mix(plays, bed, 32))}
    lv = json.loads((ROOT / "data/levels/cc_l02_ferry.json").read_text())
    w2 = ref_sim.World(lv)
    w2.run(["A", "E"], [(160, 0, "MOVE", "B")])
    ev2 = ra.from_lines(list(w2.lines))
    p2, b2 = ra.schedule(ev2, MAP["defaults"], True)
    mix_stats["L02 move"] = write(OUT / "mix_L02_move.wav", mix(p2, b2, 32))
    # muted equivalence timeline: every play row with the visual equivalent that must accompany it
    vis = json.loads((ROOT / "data/visual_cues.json").read_text())["visuals"]
    rows = []
    for p in plays + p2:
        pass
    cue_ids = [k for k in MAP["cues"] if k != "foot_bed" and k != "ui_tap"]
    colors = {"implemented_in_code": "#A8B56A", "implemented_in_data": "#E6A532", "designed": "#E8765A"}
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" width="900" height="420" font-family="Inter, sans-serif">', '<rect width="900" height="420" fill="#17120F"/>',
           '<text x="16" y="26" font-size="14" font-weight="700" fill="#EFE3C8">Muted play: every sound has a visual equivalent. L02 solution run (sign moved at 8 s), real events, 32 s</text>',
           '<text x="16" y="44" font-size="11" fill="#B7A98F">dot = a sound would play here. dot colour = how far the matching visual is built: green in drawing code, amber in a data file, coral designed only (not built)</text>']
    for r, cue in enumerate(cue_ids):
        y = 80 + r * 30
        v = MAP["cues"][cue]["visual"]
        svg.append(f'<text x="16" y="{y+4}" font-size="11" fill="#EFE3C8">{cue}{"  (critical)" if MAP["cues"][cue]["critical"] else ""}</text>')
        svg.append(f'<line x1="200" y1="{y}" x2="880" y2="{y}" stroke="#EFE3C8" stroke-width=".5" opacity=".3"/>')
        for p in p2:
            if p["cue"] == cue:
                x = 200 + p["t_ms"] / 32000 * 680
                svg.append(f'<circle cx="{x:.1f}" cy="{y}" r="4" fill="{colors[vis[v]["status"]]}"/>')
        svg.append(f'<text x="885" y="{y-6}" font-size="8.5" fill="#B7A98F" text-anchor="end">{v}</text>')
    for s in range(0, 33, 4):
        x = 200 + s / 32 * 680
        svg.append(f'<text x="{x:.0f}" y="{80+len(cue_ids)*30+14}" font-size="10" fill="#B7A98F" text-anchor="middle">{s} s</text>')
    n_design = sum(1 for k in cue_ids if MAP["cues"][k]["critical"] and vis[MAP["cues"][k]["visual"]]["status"] == "designed")
    n_crit = sum(1 for k in cue_ids if MAP["cues"][k]["critical"])
    svg.append(f'<text x="16" y="{80+len(cue_ids)*30+44}" font-size="12" fill="#E8765A">Honest result: {n_design} of {n_crit} critical cues have a visual equivalent that is only designed, not built. The muted-player requirement is met on paper, not in the game.</text></svg>')
    (OUT / "muted_timeline.svg").write_text("\n".join(svg))
    # colour-vision simulation of the Stage 10 run picture and a numeric check of the key colour pairs
    tok = json.loads((ROOT / "data/art_tokens.json").read_text())["themes"]["standard"]
    pairs = [("amber", "sage", "School and Plaza routes", "solid vs dashed line"), ("vermilion", "amber", "sign and School route", "disc with arrow vs line and notes"),
             ("coral", "plum", "queue colours", "hatch pattern"), ("sage", "stave", "Plaza route and street line", "dashed vs solid, ribbon width"), ("vermilion", "plum", "sign and queue hatch", "disc vs diagonal hatch")]
    table = {}
    for mode, m in SIM.items():
        table[mode] = {}
        for a, b, what, pattern in pairs:
            la = lab(simulate(hexrgb(tok[a]), m))
            lb = lab(simulate(hexrgb(tok[b]), m))
            table[mode][f"{a} vs {b}"] = round(float(np.linalg.norm(la - lb)), 1)
    normal = {f"{a} vs {b}": round(float(np.linalg.norm(lab(hexrgb(tok[a])) - lab(hexrgb(tok[b])))), 1) for a, b, _, _ in pairs}
    json.dump({"delta_e76_normal": normal, "delta_e76_by_simulation": table,
               "pairs": [dict(pair=f"{a} vs {b}", meaning=what, non_colour_cue=pat) for a, b, what, pat in pairs],
               "method": "Machado, Oliveira and Fernandes 2009 matrices at severity 1.0, applied in linear RGB; CIE76 delta E. A delta E under 10 is treated as 'needs a non-colour cue'."},
              open(OUT / "colour_vision_numbers.json", "w"), indent=1)
    src = Image.open(ROOT / "docs/stage10/s2_run_AE_t120.png").convert("RGB")
    a = np.asarray(src, dtype=float)
    tiles = [("Normal", src)]
    for mode, m in SIM.items():
        sim = to_srgb(to_lin(a) @ np.array(m).T)
        tiles.append((mode.capitalize(), Image.fromarray(sim.astype("uint8"))))
    W, H = tiles[0][1].size
    sheet = Image.new("RGB", (W * 4 // 2 + 30, H // 2 + 30), (30, 30, 30))
    for i, (name, im) in enumerate(tiles):
        sheet.paste(im.resize((W // 2, H // 2)), (i * (W // 2 + 10) + 5, 25))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, (name, _) in enumerate(tiles):
        d.text((i * (W // 2 + 10) + 8, 6), name, fill=(239, 227, 200))
    sheet.save(OUT / "colour_vision_sheet.png")
    # reduced motion: start frame and end frame for two transitions, to be cross-faded over 150 ms
    snaps = s11.run_model(("A", "E"), {2, 120, 400})
    base = {"streets_alpha": 1.0, "labels_alpha": 1.0, "agents_alpha": 1.0, "ribbons_alpha": 0.0}
    for tid in ("paper_unfolds", "outcome_pullback"):
        t = rt.by_id(tid)
        pair = []
        for when in (0.0, float(t["duration_ms"])):
            tr = rt.Transition(t)
            tr.start()
            tr.update(when)
            v = tr.values()
            fx = dict(base)
            if tid == "paper_unfolds":
                fx.update(streets_alpha=v["streets_alpha"], labels_alpha=v["labels_alpha"])
                tf = cam.Transform(center=v["cam_center"], zoom=v["cam_zoom"])
                snap, tick = snaps[2], 2
            else:
                tf = cam.Transform(center=v["cam_center"], zoom=v["cam_zoom"])
                fx.update(ribbons_alpha=v["ribbons_alpha"], agents_alpha=1.0 - v["ribbons_alpha"])
                snap, tick = snaps[400], 400
            pair.append(s12.frame(tf, snap, tick, fx, tid.replace("_", " ") + (" start" if when == 0 else " end"), when))
        (OUT / f"reduced_{tid}_start.svg").write_text(pair[0])
        (OUT / f"reduced_{tid}_end.svg").write_text(pair[1])
    json.dump(mix_stats, open(OUT / "mix_stats.json", "w"), indent=1)
    print(mix_stats)
    print(json.dumps({"normal": normal, "protanopia": table["protanopia"], "deuteranopia": table["deuteranopia"], "tritanopia": table["tritanopia"]}, indent=0))
    print("plays A/E", len(plays), "L02", len(p2), "foot bed points", len(bed))


if __name__ == "__main__":
    main()

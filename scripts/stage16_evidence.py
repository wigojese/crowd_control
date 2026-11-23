"""Stage 16 evidence: layout renderings at small/tall/tablet widths (model data, NOT engine screenshots) and a licence audit
of every tracked file. Usage: python3 -I scripts/stage16_evidence.py
"""
import collections
import json
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_settings as rs  # noqa: E402
import stage16_checks as sc  # noqa: E402
OUT = ROOT / "docs/stage16"
NIGHT, STAVE, VERM, PANEL, DIM = (24, 28, 38), (226, 226, 214), (214, 82, 47), (44, 50, 66), (130, 134, 146)


def font(n):
    try:
        return ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf", n)
    except OSError:
        return ImageFont.load_default()


def render(name, w, h, top, bot, level="cc_l01_r1", lh=False, lg=False):
    sc_ = 2
    im = Image.new("RGB", (w * sc_, h * sc_), NIGHT)
    d = ImageDraw.Draw(im)
    S = lambda *v: [x * sc_ for x in v]  # noqa: E731
    d.rectangle(S(0, 0, w, top), fill=(60, 30, 30))
    d.text(S(6, 2), "inset %d" % top, fill=STAVE, font=font(10 * sc_))
    d.rectangle(S(12, top + 6, w - 12, top + 78), fill=PANEL, outline=DIM)
    d.text(S(20, top + 14), "HUD: level, 9 / 20, 00:18", fill=STAVE, font=font(13 * sc_))
    lv = sc.load(level)
    xs, ys = [n["x"] for n in lv["nodes"]], [n["y"] for n in lv["nodes"]]
    pad = 30
    bw, bh = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    free_top, free_bot = top + sc.HUD_H, h - bot - sc.DOCK_H
    fit = min((w - 24) / bw, (free_bot - free_top) / bh)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    P = {n["id"]: ((n["x"] - cx) * fit + w / 2, (n["y"] - cy) * fit + (free_top + free_bot) / 2) for n in lv["nodes"]}
    d.rectangle(S(0, free_top, w, free_bot), outline=(70, 90, 70))
    for e in lv["edges"]:
        d.line(S(*P[e["from"]], *P[e["to"]]), fill=DIM, width=3 * sc_)
    for n in lv["nodes"]:
        x, y = P[n["id"]]
        sock = n["id"] in lv["sockets"]
        r = 22 if sock else 7
        d.ellipse(S(x - r, y - r, x + r, y + r), outline=VERM if sock else STAVE, width=2 * sc_)
        d.text(S(x + r + 2, y - 6), n["id"], fill=STAVE, font=font(11 * sc_))
    for k, v in rs.dock_layout(lh, lg, (w, h), bot if bot else 16).items():
        d.rectangle(S(v[0], v[1], v[0] + v[2], v[1] + v[3]), fill=PANEL if k != "tray" else (90, 40, 30), outline=STAVE)
        d.text(S(v[0] + 4, v[1] + v[3] / 2 - 6), k, fill=STAVE, font=font(11 * sc_))
    d.rectangle(S(0, h - bot, w, h), fill=(60, 30, 30))
    d.line(S(24, 0, 24, h), fill=(80, 60, 20))
    d.line(S(w - 24, 0, w - 24, h), fill=(80, 60, 20))
    d.text(S(6, h - 14), "%s  fit zoom %.2f" % (name, fit), fill=STAVE, font=font(10 * sc_))
    return im


def sheet():
    cfg = [("small 320x568", 320, 568, 20, 0, False, False), ("390x844", 390, 844, 47, 34, False, False), ("tall 430x932", 430, 932, 59, 34, True, True),
           ("tablet 768x1024", 768, 1024, 24, 20, False, False)]
    ims = [render(n, w, h, t, b, lh=lh, lg=lg) for n, w, h, t, b, lh, lg in cfg]
    for im, (n, *_r) in zip(ims, cfg):
        im.save(OUT / ("layout_%s.png" % n.split()[-1]))
    H = 900
    th = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    sheet_ = Image.new("RGB", (sum(t.width for t in th) + 20 * (len(th) + 1), H + 40), (12, 12, 16))
    x = 20
    for t in th:
        sheet_.paste(t, (x, 20))
        x += t.width + 20
    sheet_.save(OUT / "layout_contact_sheet.png")


def audit():
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split()
    cat = collections.Counter()
    third = []
    for f in files:
        ext = pathlib.Path(f).suffix.lower() or pathlib.Path(f).name.lower()
        kind = {".gd": "own code", ".py": "own code", ".sh": "own code", ".yml": "own config", ".json": "own data", ".md": "own docs", ".godot": "own config",
                ".wav": "own synthesised audio", ".png": "generated image (own scripts)", ".mp4": "generated video (own scripts)", ".svg": "generated image (own scripts)",
                ".txt": "licence text", ".csv": "own data (generated)", ".tscn": "own scene", "": "own config", ".gitignore": "own config", ".gdignore": "own config", ".js": "own tool", ".html": "own tool"}.get(ext, "UNCLASSIFIED")
        if f.startswith("assets/fonts/licenses"):
            kind = "third-party licence text only (no font file shipped)"
        if ext in (".ttf", ".otf", ".woff", ".woff2", ".ogg", ".mp3", ".jpg", ".jpeg", ".gif", ".webp"):
            third.append(f)
        cat[kind] += 1
        if kind == "UNCLASSIFIED":
            third.append(f)
    fonts_shipped = [f for f in files if f.startswith("assets/") and pathlib.Path(f).suffix.lower() in (".ttf", ".otf", ".woff", ".woff2")]
    res = dict(tracked_files=len(files), by_kind=dict(cat), third_party_or_unclassified=third, font_files_shipped=fonts_shipped,
               note="Classified by extension; origin of each generated file is its script. A file extension is not proof of origin: the audit confirms no font, music or image binary of unknown provenance is tracked, not that every file was reviewed by a lawyer.")
    (OUT / "license_audit.json").write_text(json.dumps(res, indent=1) + "\n")
    print("AUDIT", res["tracked_files"], "files;", "unclassified/third-party binaries:", third or "none", "; fonts shipped:", fonts_shipped or "none")
    return not third


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    sheet()
    sys.exit(0 if audit() else 1)

"""Contrast checks for data/art_tokens.json (WCAG 2.x relative luminance). RAN, not an assertion.
Rules: text on its background at least 4.5:1; graphics (routes, sign, queue) at least 3:1 on night.
Also checks that the route and queue colours are separable by luminance OR are flagged as needing a pattern.
Usage: python3 -I scripts/check_contrast.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    tok = json.loads((ROOT / "data/art_tokens.json").read_text())["themes"]
    bad = 0
    for name, t in tok.items():
        checks = [("stave text on night", t["stave"], t["night"], 4.5), ("dim text on night", t["dim"], t["night"], 4.5),
                  ("disabled text on night", t["disabled"], t["night"], 4.5), ("stave text on panel", t["stave"], t["panel"], 4.5),
                  ("amber route on night", t["amber"], t["night"], 3.0), ("sage route on night", t["sage"], t["night"], 3.0),
                  ("coral queue on night", t["coral"], t["night"], 3.0), ("plum queue on night", t["plum"], t["night"], 3.0),
                  ("vermilion sign on night", t["vermilion"], t["night"], 3.0),
                  ("sign arrow on vermilion disc", t["sign_arrow"], t["vermilion"], 3.0)]
        for label, fg, bg, need in checks:
            r = ratio(fg, bg)
            ok = r >= need
            bad += not ok
            print(("PASS" if ok else "FAIL"), name, label, "%.2f:1 (need %.1f)" % (r, need))
    std = tok["standard"]
    pairs = [("amber", "sage"), ("amber", "coral"), ("sage", "coral")]
    for a, b in pairs:
        r = ratio(std[a], std[b])
        print("INFO standard", a, "vs", b, "luminance ratio %.2f:1%s" % (r, "" if r >= 1.5 else " (too close in grayscale: needs a pattern or shape)"))
    print("CONTRAST RESULT:", "OK" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

"""Reference for settings sanitising and the left/right-hand dock layout (src/core/settings.gd, src/input/dock_layout.gd).
Cases shared with GDScript: tests/fixtures/settings_cases.json. Usage: python3 -I scripts/ref_settings.py [--write]
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "data/settings_schema.json").read_text())


def sanitize(raw, schema=SCHEMA):
    """Unknown keys are dropped, wrong types fall back to the default, numbers are clamped. Never raises."""
    out = {"version": schema["version"]}
    for k, f in schema["fields"].items():
        v = raw.get(k, f["default"]) if isinstance(raw, dict) else f["default"]
        if f["type"] == "float":
            ok = isinstance(v, (int, float)) and not isinstance(v, bool)
            v = min(f["max"], max(f["min"], float(v))) if ok else f["default"]
        elif f["type"] == "bool":
            v = v if isinstance(v, bool) else f["default"]
        else:
            v = v if v in f["values"] else f["default"]
        out[k] = v
    return out


def dock_layout(left_handed, larger, viewport, bottom_inset=34):
    """Rects [x, y, w, h] for restart, tray, pause on one row. Right-handed: pause on the right (thumb side). Left-handed: mirrored."""
    w, h = viewport
    extra = 8 if larger else 0
    bh, th = 48 + extra, 56 + extra
    tray_w = 56 + extra
    margin, gap = 28, 12
    want = (88 if larger else 92) if w <= 320 else 104 + extra
    span_w = 480 if w > 600 else w - 2 * margin  # tablets: keep the row within thumb reach, anchored on the thumb side
    x0 = w - margin - span_w
    bw = min(want, (span_w - tray_w - 2 * gap) // 2)  # never wider than three controls and two gaps allow (Stage 16: 360 wide, larger targets)
    y = h - bottom_inset - 112 + (112 - max(bh, th)) // 2
    xs = [x0, x0 + (span_w - tray_w) // 2, x0 + span_w - bw]
    rects = {"restart": [xs[0], y, bw, bh], "tray": [xs[1], y - (th - bh) // 2 if th > bh else y, tray_w, th], "pause": [xs[2], y, bw, bh]}
    if left_handed:
        rects = {k: [w - v[0] - v[2], v[1], v[2], v[3]] for k, v in rects.items()}  # exact mirror of every rectangle
    return rects


def overlap(a, b):
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


def checks():
    res = []

    def ok(n, c):
        res.append((n, bool(c)))
    d = sanitize({})
    ok("defaults: sound on, haptics off, system reduced motion, patterns on", d["master"] == 0.8 and d["haptics"] is False and d["reduced_motion"] == "system" and d["pattern_equivalents"] is True)
    s = sanitize({"master": 7, "effects": -1, "texture": "loud", "ui": True, "haptics": "yes", "reduced_motion": "maybe", "evil": 1, "left_handed": True})
    ok("clamps numbers, falls back on wrong types and unknown enums, drops unknown keys", s["master"] == 1.0 and s["effects"] == 0.0 and s["texture"] == 0.5 and s["ui"] == 0.8
       and s["haptics"] is False and s["reduced_motion"] == "system" and "evil" not in s and s["left_handed"] is True)
    ok("sanitising twice changes nothing", sanitize(s) == s)
    ok("a non-object becomes the defaults", sanitize("garbage") == d and sanitize(None) == d)
    for vp in ((390, 844), (320, 568), (412, 915)):
        for lh in (False, True):
            for lg in (False, True):
                r = dock_layout(lh, lg, vp, 34 if vp[1] > 600 else 16)
                tag = f"{vp[0]}x{vp[1]} left={lh} larger={lg}"
                ok(f"dock {tag}: no overlap and at least 8 px gap", all(not overlap([a[0] - 4, a[1], a[2] + 8, a[3]], b) for i, (ka, a) in enumerate(r.items()) for kb, b in list(r.items())[i + 1:]))
                ok(f"dock {tag}: outside the 24 px edge reserve", all(v[0] >= 24 and v[0] + v[2] <= vp[0] - 24 for v in r.values()))
                ok(f"dock {tag}: buttons at least 48 high and 44 wide, tray at least 56", r["pause"][3] >= 48 and r["restart"][3] >= 48 and r["pause"][2] >= 44 and r["tray"][2] >= 56 and r["tray"][3] >= 56)
                ok(f"dock {tag}: above the bottom inset", all(v[1] + v[3] <= vp[1] - (34 if vp[1] > 600 else 16) for v in r.values()))
    r, m = dock_layout(False, False, (390, 844)), dock_layout(True, False, (390, 844))
    ok("left-handed layout is the exact mirror of every rectangle", all(r[k][0] + r[k][2] + m[k][0] == 390 and r[k][1:] == m[k][1:] and r[k][2] == m[k][2] for k in r))
    ok("pause is on the right in right-handed, on the left in left-handed", r["pause"][0] > r["restart"][0] and m["pause"][0] < m["restart"][0])
    ok("larger targets add 8 px to every size", dock_layout(False, True, (390, 844))["pause"][3] == 56)
    return res


def cases():
    san = [{"in": x, "out": sanitize(x)} for x in ({}, {"master": 7, "effects": -1, "texture": "loud", "ui": True, "haptics": "yes", "reduced_motion": "maybe", "evil": 1, "left_handed": True},
                                                 {"master": 0.25, "reduced_motion": "on", "static_camera": True}, "garbage", None)]
    docks = [{"left": lh, "larger": lg, "vp": list(vp), "inset": 34 if vp[1] > 600 else 16, "out": dock_layout(lh, lg, vp, 34 if vp[1] > 600 else 16)}
             for vp in ((390, 844), (320, 568)) for lh in (False, True) for lg in (False, True)]
    return {"sanitize": san, "dock": docks}


def main():
    if "--write" in sys.argv:
        (ROOT / "tests/fixtures/settings_cases.json").write_text(json.dumps(cases()))
    bad = 0
    for n, c in checks():
        if not c or "--v" in sys.argv:
            print(("PASS " if c else "FAIL ") + n)
        bad += not c
    print("SETTINGS RESULT:", "ALL PASS (%d checks)" % len(checks()) if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

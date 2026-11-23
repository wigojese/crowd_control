"""Measured checks on the shipped sound files against data/audio_map.json. Usage: python3 -I scripts/check_audio_files.py"""
import json
import pathlib
import sys
import wave

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP = json.loads((ROOT / "data/audio_map.json").read_text())


def load(path):
    with wave.open(str(path), "rb") as w:
        n, sr, ch, sw = w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    return np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0, sr, ch, sw


def main():
    bad = 0

    def ok(n, c):
        nonlocal bad
        print(("PASS " if c else "FAIL ") + n)
        bad += not c
    for name, c in MAP["cues"].items():
        p = ROOT / c["file"]
        ok(f"{name}: file exists", p.exists())
        if not p.exists():
            continue
        x, sr, ch, sw = load(p)
        dur = len(x) / sr * 1000
        ok(f"{name}: 22.05 kHz, mono, 16 bit", sr == MAP["sample_rate"] and ch == 1 and sw == 2)
        ok(f"{name}: duration {dur:.0f} ms matches the map ({c['duration_ms']} ms)", abs(dur - c["duration_ms"]) <= 2)
        peak = 20 * np.log10(np.max(np.abs(x)) + 1e-12)
        ok(f"{name}: peak {peak:.1f} dBFS, at most -3 and no clipped sample", peak <= -3.0 and int(np.sum(np.abs(x) >= 0.999)) == 0)
        ok(f"{name}: DC offset {np.mean(x):+.4f} within 0.01 and ends at silence ({x[-1]:+.4f})", abs(np.mean(x)) < 0.01 and abs(x[-1]) < 0.01 and abs(x[0]) < 0.01)
        if c["loop"]:
            ok(f"{name}: loop ends meet (first {x[0]:+.4f}, last {x[-1]:+.4f})", abs(x[0] - x[-1]) < 0.01)
    ok("every critical cue is at most 1.2 s long (no long wait for a sound)", all(c["duration_ms"] <= 1200 for c in MAP["cues"].values() if c["critical"]))
    print("AUDIO FILES RESULT:", "ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

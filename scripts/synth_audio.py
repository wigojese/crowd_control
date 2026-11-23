"""Original sound cues for Crowd Control, synthesised from scratch (sine, triangle, filtered noise, a feedback delay).
No samples, no recordings, no third-party material. Deterministic: seeded noise, same bytes every run.
Writes assets/audio/*.wav (22.05 kHz, 16 bit, mono) and docs/stage15/audio_stats.json (measured, not assumed).
I cannot hear the result: levels, duration, clipping and spectrum are MEASURED; taste is UNVERIFIED.
Usage: python3 -I scripts/synth_audio.py
"""
import json
import pathlib
import wave

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SR = 22050
RNG = np.random.RandomState(1007)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, attack=0.003, decay=0.08):
    x = np.arange(n) / SR
    return np.minimum(1.0, x / max(attack, 1e-4)) * np.exp(-x / decay)


def noise(d):
    return RNG.uniform(-1, 1, int(SR * d))


def bandpass(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def lowpass(x, hi):
    return bandpass(x, 0, hi)


def pluck(freq, d, decay=0.12, h2=0.35):
    x = t(d)
    s = np.sin(2 * np.pi * freq * x) + h2 * np.sin(2 * np.pi * 2 * freq * x) * np.exp(-x / (decay * 0.5))
    return s * env(len(x), 0.004, decay)


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += sig[:n] * gain


def delay_tail(x, ms=90, fb=0.35, repeats=4):
    out = np.copy(x)
    d = int(SR * ms / 1000)
    for r in range(1, repeats + 1):
        if d * r < len(out):
            out[d * r:] += x[:len(out) - d * r] * (fb ** r)
    return out


def norm(x, peak=0.6):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def cues():
    out = {}
    # sign pickup: one dry click
    b = np.zeros(int(SR * 0.08))
    place(b, bandpass(noise(0.012), 2000, 5500) * env(int(SR * 0.012), 0.0005, 0.004), 0.0, 0.9)
    place(b, np.sin(2 * np.pi * 1400 * t(0.04)) * env(int(SR * 0.04), 0.001, 0.012), 0.0, 0.5)
    out["sign_pickup"] = b
    # 90 degree turn: three ratchet ticks stepping up, then a soft stop
    b = np.zeros(int(SR * 0.2))
    for i, f in enumerate((900, 1050, 1250)):
        place(b, np.sin(2 * np.pi * f * t(0.03)) * env(int(SR * 0.03), 0.0008, 0.009), 0.055 * i, 0.8)
        place(b, bandpass(noise(0.01), 2500, 6000) * env(int(SR * 0.01), 0.0005, 0.003), 0.055 * i, 0.32)
    place(b, np.sin(2 * np.pi * 95 * t(0.07)) * env(int(SR * 0.07), 0.002, 0.03), 0.11, 0.9)
    out["sign_turn"] = b
    # sign drop: soft wooden thud with a settling tick (matches the 170 ms transition)
    b = np.zeros(int(SR * 0.17))
    x = t(0.15)
    sweep = np.sin(2 * np.pi * (150 * x - 300 * x ** 2 + 0))
    place(b, sweep * env(len(x), 0.002, 0.045), 0.0, 1.0)
    place(b, bandpass(noise(0.01), 1500, 4000) * env(int(SR * 0.01), 0.0005, 0.003), 0.0, 0.4)
    place(b, np.sin(2 * np.pi * 700 * t(0.02)) * env(int(SR * 0.02), 0.001, 0.007), 0.08, 0.25)
    out["sign_drop"] = b
    # refused command: a dull double knock (the sign is locked or held)
    b = np.zeros(int(SR * 0.12))
    for i in range(2):
        place(b, np.sin(2 * np.pi * 180 * t(0.04)) * env(int(SR * 0.04), 0.001, 0.015), 0.05 * i, 0.8)
    out["command_rejected"] = b
    # foot texture: a 2 s loop of soft low-passed steps; density and loudness are driven at run time
    b = np.zeros(int(SR * 2.0))
    for k in range(13):
        at = 0.05 + k * 0.15 + RNG.uniform(-0.03, 0.03)
        step = lowpass(noise(0.05), 1400) * env(int(SR * 0.05), 0.002, 0.014)
        place(b, step, at % 1.95, 0.5 + 0.3 * RNG.uniform())
    fade = int(SR * 0.05)
    b[:fade] *= np.linspace(0, 1, fade)
    b[-fade:] *= np.linspace(1, 0, fade)
    out["foot_bed"] = b
    # queue compression: noise band squeezing downward under a low hum, swelling and settling
    d = 0.7
    n = int(SR * d)
    x = t(d)
    seg = n // 3
    parts = [bandpass(noise(seg / SR), lo, hi)[:seg] for lo, hi in ((900, 1300), (500, 800), (260, 420))]
    sig = np.concatenate(parts + [np.zeros(n - 3 * seg)])
    sig = sig * np.sin(np.pi * np.minimum(1.0, x / d)) ** 1.5
    sig += 0.5 * np.sin(2 * np.pi * 88 * x) * np.sin(np.pi * x / d) ** 2
    out["queue_compress"] = sig
    # reroute tick: two short rising notes
    b = np.zeros(int(SR * 0.2))
    place(b, pluck(660, 0.12, 0.05), 0.0, 0.8)
    place(b, pluck(880, 0.14, 0.06), 0.07, 0.9)
    out["reroute_tick"] = b
    # arrival pluck: one soft note; the pitch is chosen at run time from a pentatonic scale
    out["arrival_pluck"] = pluck(523.25, 0.25, 0.09)
    # success: rising arpeggio with a short tail. failure: two falling notes, soft, not a buzzer.
    b = np.zeros(int(SR * 1.2))
    for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        place(b, pluck(f, 0.5, 0.18), 0.15 * i, 0.8)
    out["result_success"] = delay_tail(b, 110, 0.3, 4)[:int(SR * 1.2)]
    b = np.zeros(int(SR * 1.2))
    place(b, pluck(392.0, 0.6, 0.2), 0.0, 0.8)
    place(b, pluck(311.13, 0.7, 0.25), 0.26, 0.8)
    out["result_failure"] = delay_tail(b, 120, 0.3, 3)[:int(SR * 1.2)]
    out["ui_tap"] = np.sin(2 * np.pi * 1000 * t(0.05)) * env(int(SR * 0.05), 0.001, 0.012)
    return out


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def stats(x):
    peak = float(np.max(np.abs(x)))
    rms = float(np.sqrt(np.mean(x ** 2)))
    sp = np.abs(np.fft.rfft(x))
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    return dict(duration_ms=round(len(x) / SR * 1000), peak_dbfs=round(float(20 * np.log10(peak + 1e-12)), 1), rms_dbfs=round(float(20 * np.log10(rms + 1e-12)), 1),
                clipped_samples=int(np.sum(np.abs(x) >= 0.999)), dc_offset=round(float(np.mean(x)), 5),
                spectral_centroid_hz=round(float(np.sum(sp * fr) / (np.sum(sp) + 1e-12))), first_sample=round(float(x[0]), 4), last_sample=round(float(x[-1]), 4))


def main():
    (ROOT / "assets/audio").mkdir(parents=True, exist_ok=True)
    allstats = {}
    for name, x in cues().items():
        x = norm(x, 0.6 if name not in ("foot_bed",) else 0.35)
        f = int(SR * 0.006)
        x[-f:] *= np.linspace(1, 0, f)  # no click at the end of a cue
        write_wav(ROOT / "assets/audio" / (name + ".wav"), x)
        allstats[name] = stats(x)
    (ROOT / "docs/stage15").mkdir(exist_ok=True)
    json.dump(allstats, open(ROOT / "docs/stage15/audio_stats.json", "w"), indent=1)
    for k, v in allstats.items():
        print(k, v)


if __name__ == "__main__":
    main()

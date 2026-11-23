"""Reference implementation of the Stage 07 fixtures (RNG, event log hash, tick fixture).

It exists to produce golden values and to be checked against the GDScript. It is NOT the
game. Run `python3 -I scripts/ref_model.py --write` to regenerate tests/fixtures/*_golden.json.
"""
import json
import pathlib
import sys

MASK = 0xFFFFFFFF
FALLBACK = 0x9E3779B9
ROOT = pathlib.Path(__file__).resolve().parent.parent


class Rng:
    def __init__(self, seed):
        self.s = (seed & MASK) or FALLBACK

    def next_u32(self):
        x = self.s
        x = (x ^ (x << 13)) & MASK
        x ^= x >> 17
        x = (x ^ (x << 5)) & MASK
        self.s = x
        return x

    def next_int(self, n):
        return self.next_u32() % n


def fnv1a32(data: bytes) -> int:
    h = 0x811C9DC5
    for b in data:
        h = ((h ^ b) * 0x01000193) & MASK
    return h


def stream(seed, name):
    return Rng((fnv1a32(name.encode()) ^ seed) & MASK)


def line(tick, seq, etype, fields):
    parts = ";".join("%s=%s" % (k, fields[k]) for k in sorted(fields))
    return "%d|%d|%s|%s" % (tick, seq, etype, parts)


def tick_fixture(seed):
    rng = stream(seed, "spawn")
    lines, seq, last_tick, spawned = [], 0, -1, 0

    def add(tick, etype, fields):
        nonlocal seq, last_tick
        if tick != last_tick:
            last_tick, seq = tick, 0
        lines.append(line(tick, seq, etype, fields))
        seq += 1

    for tick in range(640):
        if rng.next_int(4) == 0:
            dest = "School" if rng.next_int(2) == 0 else "Plaza"
            spawned += 1
            add(tick, "WALKER_SPAWNED", {"walker": spawned, "profile": "C", "origin": "A",
                                         "destination": dest, "deadline_tick": 600})
    add(640, "RUN_ENDED", {"reason": "time_limit"})
    return {"seed": seed, "spawned": spawned, "events": len(lines),
            "hash": fnv1a32("\n".join(lines).encode())}


def main():
    seed = 1007
    r = Rng(seed)
    rng_g = {"seed": seed, "u32": [r.next_u32() for _ in range(16)],
             "stream_spawn_first": stream(seed, "spawn").next_u32()}
    fx = tick_fixture(seed)
    if "--write" in sys.argv:
        (ROOT / "tests/fixtures/rng_golden.json").write_text(json.dumps(rng_g, indent=2) + "\n")
        (ROOT / "tests/fixtures/tick_fixture_golden.json").write_text(json.dumps(fx, indent=2) + "\n")
    print(json.dumps({"rng": rng_g, "fixture": fx}))


if __name__ == "__main__":
    main()

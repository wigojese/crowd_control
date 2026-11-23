"""Checks that the committed golden files equal what scripts/ref_model.py produces now.
Guards against hand-edited or stale golden values. Usage: python3 -I scripts/check_golden.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ref_model as m  # noqa: E402


def main():
    seed = 1007
    r = m.Rng(seed)
    rng_g = {"seed": seed, "u32": [r.next_u32() for _ in range(16)],
             "stream_spawn_first": m.stream(seed, "spawn").next_u32()}
    fx = m.tick_fixture(seed)
    bad = 0
    for name, want in (("rng_golden.json", rng_g), ("tick_fixture_golden.json", fx)):
        got = json.loads((ROOT / "tests/fixtures" / name).read_text())
        ok = got == want
        print(("PASS" if ok else "FAIL"), "golden", name)
        bad += not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

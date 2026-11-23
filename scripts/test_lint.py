"""Self-test for scripts/lint.py: each rule must fire on a deliberately bad copy of the repo.
Proves the lint is not a rubber stamp. Usage: python3 -I scripts/test_lint.py
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lint  # noqa: E402


def fresh():
    d = pathlib.Path(tempfile.mkdtemp())
    for name in ("src", "tests", "tools", "data", "docs", "project.godot"):
        s = ROOT / name
        if s.is_dir():
            shutil.copytree(s, d / name, ignore=shutil.ignore_patterns("*.png", "*.js"))
        else:
            shutil.copy(s, d / name)
    return d


def expect(code, mutate):
    d = fresh()
    mutate(d)
    errs = lint.lint(d)
    shutil.rmtree(d)
    hit = any((" " + code + " ") in e for e in errs)
    print(("PASS " if hit else "FAIL ") + "rule", code, "fires on bad input")
    return 0 if hit else 1


def append(rel, text):
    def f(d):
        with open(d / rel, "a") as fh:
            fh.write(text)
    return f


def main():
    bad = 0
    clean = lint.lint(ROOT)
    print(("PASS" if not clean else "FAIL"), "real repo is clean", clean)
    bad += bool(clean)
    bad += expect("L1", append("src/core/rng_service.gd", "    var spaced = 1\n"))
    bad += expect("L1", append("src/core/rng_service.gd", "var x = 1 \n"))
    bad += expect("L2", append("project.godot", "\n[autoload]\nGlobal=\"*res://x.gd\"\n"))
    bad += expect("L3", append("src/core/bad.gd", "class_name Bad\nextends RefCounted\n"))
    bad += expect("L4", append("src/core/rng_service.gd", "var b = CcScenarioValidator\n"))
    bad += expect("L10", append("src/simulation/tick_fixture.gd", "var cam = CcCameraDirector\n"))
    bad += expect("L5", append("src/simulation/tick_fixture.gd", "var r = randi()\n"))
    bad += expect("L6", append("data/boot_states.json", "{broken"))
    bad += expect("L7", lambda d: (d / "data/events.schema.json").write_text(
        '{"events": {"ONLY_ONE": ["a"]}}'))
    bad += expect("L8", append("src/simulation/tick_fixture.gd", "var t = Time.get_ticks_msec()\n"))
    bad += expect("L9", append("src/app/boot.gd", 'var f = load("res://assets/missing.png")\n'))

    def dup(d):
        p = d / "data/boot_states.json"
        p.write_text(p.read_text().replace(
            '{"from": "BOOT", "event": "BOOT_COMPLETE", "to": "READY"},',
            '{"from": "BOOT", "event": "BOOT_COMPLETE", "to": "READY"},\n'
            '    {"from": "BOOT", "event": "BOOT_COMPLETE", "to": "ENDED"},'))
    bad += expect("L6", dup)
    print("SELF-TEST RESULT:", "OK" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

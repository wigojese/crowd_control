"""Scenario validator for CI (Python mirror of src/levels/scenario_validator.gd).

Both validators must give the verdicts in tests/fixtures/expected_verdicts.json.
Usage: python3 -I scripts/validate_scenarios.py [--fixtures | file.json ...]
Exit 0 only if every check passes.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULESET = "CC-RULESET-01C"
TICKS = 640
COMMANDS = {"PICK", "DROP", "ROTATE", "MOVE"}
HEADINGS = {"N", "E", "S", "W"}


def validate(s):
    errs = []
    if s.get("ruleset_version") != RULESET:
        errs.append("bad_ruleset")
    if not isinstance(s.get("seed"), (int, float)) or isinstance(s.get("seed"), bool):
        errs.append("bad_seed")
    if int(s.get("ticks", 0)) != TICKS:
        errs.append("bad_ticks")
    nodes = set()
    for n in s.get("nodes", []):
        nid = str(n.get("id", ""))
        if nid == "" or nid in nodes:
            errs.append("duplicate_or_empty_node")
        nodes.add(nid)
    edges = set()
    for e in s.get("edges", []):
        eid = str(e.get("id", ""))
        if eid == "" or eid in edges:
            errs.append("duplicate_or_empty_edge")
        edges.add(eid)
        if str(e.get("from", "")) not in nodes or str(e.get("to", "")) not in nodes:
            errs.append("edge_unknown_node")
        if float(e.get("rate", 0.0)) <= 0.0:
            errs.append("edge_rate_not_positive")
    total = 0
    for sp in s.get("schedule", []):
        for k, v in (sp.get("mix") or {}).items():
            if int(v) <= 0:
                errs.append("bad_mix")
            total += int(v)
    if "pass_mark" in s and not (1 <= int(s["pass_mark"]) <= total):
        errs.append("bad_pass_mark")
    for sock in s.get("sockets", []):
        if str(sock) not in nodes:
            errs.append("socket_unknown_node")
    last = -1
    for sp in s.get("schedule", []):
        t = int(sp.get("tick", -1))
        if t < 0 or t >= TICKS:
            errs.append("spawn_tick_out_of_range")
        if t < last:
            errs.append("schedule_not_sorted")
        last = t
        if str(sp.get("origin", "")) not in nodes or str(sp.get("destination", "")) not in nodes:
            errs.append("spawn_unknown_node")
    last_key = -1
    for c in s.get("commands", []):
        if str(c.get("command", "")) not in COMMANDS:
            errs.append("bad_command")
        if "heading" in c and str(c["heading"]) not in HEADINGS:
            errs.append("bad_heading")
        key = int(c.get("tick", -1)) * 1000 + int(c.get("ordinal", 0))
        if key < last_key:
            errs.append("commands_not_sorted")
        last_key = key
    return errs


def check_fixtures():
    fx = ROOT / "tests/fixtures"
    want = json.loads((fx / "expected_verdicts.json").read_text())
    bad = 0
    for name, exp in want.items():
        got = sorted(validate(json.loads((fx / name).read_text())))
        if got == sorted(exp):
            print("PASS verdict", name)
        else:
            print("FAIL verdict", name, "got", got, "want", sorted(exp))
            bad += 1
    return bad


def main():
    args = sys.argv[1:]
    if not args or args == ["--fixtures"]:
        return 1 if check_fixtures() else 0
    bad = 0
    for a in args:
        errs = validate(json.loads(pathlib.Path(a).read_text()))
        print(("VALID " if not errs else "INVALID " + ",".join(errs) + " ") + a)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

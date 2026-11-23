"""Repository lint. Enforces the Stage 07 rules; exits non-zero on any violation.

Rules:
 L1 GDScript uses tabs for indentation (no leading spaces), no trailing whitespace, max 120 columns,
    final newline.
 L2 No [autoload] section in project.godot (no global singletons).
 L3 Every class_name starts with Cc.
 L4 Layer dependencies: core <- simulation <- levels <- app. A file may mention only classes (and
    res://src paths) of its own or lower layers. tests/ and tools/ may use any layer.
 L5 No random source other than CcRng in src/ (randi, randf, randomize, RandomNumberGenerator).
 L6 JSON files parse; the state table has no duplicate (from,event) and no unknown states.
 L7 data/events.schema.json lists exactly the events in docs/SIMULATION_EVENTS.md section 2.
 L8 simulation/ and core/ never touch the scene tree (Node, get_tree, Input, OS.get_ticks, Time.).
 L9 No hard-coded asset paths to files that do not exist (res://assets/...).
Usage: python3 -I scripts/lint.py [--root DIR]   (--root is used by the self-test)
"""
import json
import pathlib
import re
import sys

LAYERS = {"core": 0, "simulation": 1, "levels": 2, "app": 3}


def gd_files(root):
    for p in sorted(root.rglob("*.gd")):
        rel = p.relative_to(root)
        if rel.parts[0] in ("spikes", "docs", ".git"):
            continue
        yield p, rel


def lint(root):
    errs = []

    def err(rel, n, code, msg):
        errs.append("%s:%s: %s %s" % (rel, n, code, msg))

    classes = {}
    for p, rel in gd_files(root):
        m = re.search(r"^class_name (\w+)", p.read_text(), re.M)
        if m:
            if not m.group(1).startswith("Cc"):
                err(rel, 1, "L3", "class_name must start with Cc: " + m.group(1))
            if rel.parts[0] == "src" and rel.parts[1] in LAYERS:
                classes[m.group(1)] = LAYERS[rel.parts[1]]

    for p, rel in gd_files(root):
        text = p.read_text()
        if not text.endswith("\n"):
            err(rel, 0, "L1", "missing final newline")
        layer = LAYERS.get(rel.parts[1]) if rel.parts[0] == "src" and len(rel.parts) > 2 else None
        for n, ln in enumerate(text.split("\n"), 1):
            if re.match(r" +\S", ln):
                err(rel, n, "L1", "space indentation (use tabs)")
            if ln != ln.rstrip():
                err(rel, n, "L1", "trailing whitespace")
            if len(ln.expandtabs(4)) > 120:
                err(rel, n, "L1", "line over 120 columns")
            code = ln.split("##")[0].split("#")[0]
            if rel.parts[0] == "src" and re.search(r"\b(randi|randf|randomize|RandomNumberGenerator|randi_range|randf_range)\b", code):
                err(rel, n, "L5", "use CcRng, not the engine random")
            if layer is not None and layer <= 1 and re.search(r"\b(Node|Node2D|Control|get_tree|Input|Time|OS)\b\s*[.(]", code):
                err(rel, n, "L8", "core/simulation must not touch the scene tree or clock")
            if layer is not None:
                for cname, clayer in classes.items():
                    if clayer > layer and re.search(r"\b" + cname + r"\b", code):
                        err(rel, n, "L4", "%s (layer %d) used from a lower layer" % (cname, clayer))
                for m in re.finditer(r"res://src/(\w+)/", code):
                    if m.group(1) in LAYERS and LAYERS[m.group(1)] > layer:
                        err(rel, n, "L4", "path into higher layer: " + m.group(0))
            for m in re.finditer(r"res://assets/[\w./-]+", code):
                if not (root / m.group(0)[6:]).exists():
                    err(rel, n, "L9", "missing asset " + m.group(0))

    proj = root / "project.godot"
    if proj.exists() and re.search(r"^\[autoload\]", proj.read_text(), re.M):
        err("project.godot", 0, "L2", "[autoload] is not allowed (no global singletons)")

    for p in sorted(root.rglob("*.json")):
        rel = p.relative_to(root)
        if rel.parts[0] in ("spikes", "docs", ".git", "node_modules"):
            continue
        try:
            json.loads(p.read_text())
        except ValueError as e:
            err(rel, 0, "L6", "invalid JSON: %s" % e)

    states = root / "data/boot_states.json"
    if states.exists():
        try:
            d = json.loads(states.read_text())
            seen, known = set(), set(d.get("states", []))
            if d.get("initial") not in known:
                err("data/boot_states.json", 0, "L6", "initial state unknown")
            for t in d.get("transitions", []):
                k = (t.get("from"), t.get("event"))
                if k in seen:
                    err("data/boot_states.json", 0, "L6", "duplicate transition %s" % (k,))
                seen.add(k)
                if t.get("from") not in known or t.get("to") not in known:
                    err("data/boot_states.json", 0, "L6", "transition uses unknown state %s" % (t,))
        except ValueError:
            pass

    schema, doc = root / "data/events.schema.json", root / "docs/SIMULATION_EVENTS.md"
    if schema.exists() and doc.exists():
        try:
            names = set(json.loads(schema.read_text())["events"])
            sect = doc.read_text().split("## 2.")[1].split("## 3.")[0]
            documented = set(re.findall(r"`([A-Z_]{4,})`", "\n".join(
                l.split("|")[1] for l in sect.splitlines() if l.startswith("| `"))))
            if names != documented:
                err("data/events.schema.json", 0, "L7", "differs from docs/SIMULATION_EVENTS.md: only in schema %s, only in doc %s" % (sorted(names - documented), sorted(documented - names)))
        except (ValueError, KeyError, IndexError) as e:
            err("data/events.schema.json", 0, "L7", "cannot compare: %s" % e)
    return errs


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    if "--root" in sys.argv:
        root = pathlib.Path(sys.argv[sys.argv.index("--root") + 1])
    errs = lint(root)
    for e in errs:
        print("LINT", e)
    print("LINT RESULT:", "OK" if not errs else "%d violation(s)" % len(errs))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())

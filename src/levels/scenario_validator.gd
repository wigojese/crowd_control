class_name CcScenarioValidator
extends RefCounted
## Validates a scenario dictionary (parsed JSON). Returns an Array of error codes; empty means valid.
## Same rules as scripts/validate_scenarios.py; both are run on tests/fixtures/scenario_*.json and
## must agree with tests/fixtures/expected_verdicts.json.

const RULESET := "CC-RULESET-01C"
const TICKS := 640
const COMMANDS := ["PICK", "DROP", "ROTATE", "MOVE"]
const HEADINGS := ["N", "E", "S", "W"]


static func validate(s: Dictionary) -> Array[String]:
	var errs: Array[String] = []
	if s.get("ruleset_version", "") != RULESET:
		errs.append("bad_ruleset")
	if typeof(s.get("seed", null)) != TYPE_INT and typeof(s.get("seed", null)) != TYPE_FLOAT:
		errs.append("bad_seed")
	if int(s.get("ticks", 0)) != TICKS:
		errs.append("bad_ticks")
	var node_ids := {}
	for n in s.get("nodes", []):
		var nid := String(n.get("id", ""))
		if nid == "" or node_ids.has(nid):
			errs.append("duplicate_or_empty_node")
		node_ids[nid] = true
	var edge_ids := {}
	for e in s.get("edges", []):
		var eid := String(e.get("id", ""))
		if eid == "" or edge_ids.has(eid):
			errs.append("duplicate_or_empty_edge")
		edge_ids[eid] = true
		if not node_ids.has(String(e.get("from", ""))) or not node_ids.has(String(e.get("to", ""))):
			errs.append("edge_unknown_node")
		if float(e.get("rate", 0.0)) <= 0.0:
			errs.append("edge_rate_not_positive")
	var last := -1
	for sp in s.get("schedule", []):
		var t := int(sp.get("tick", -1))
		if t < 0 or t >= TICKS:
			errs.append("spawn_tick_out_of_range")
		if t < last:
			errs.append("schedule_not_sorted")
		last = t
		if not node_ids.has(String(sp.get("origin", ""))) or not node_ids.has(String(sp.get("destination", ""))):
			errs.append("spawn_unknown_node")
	var last_key := -1
	for c in s.get("commands", []):
		if not COMMANDS.has(String(c.get("command", ""))):
			errs.append("bad_command")
		if c.has("heading") and not HEADINGS.has(String(c["heading"])):
			errs.append("bad_heading")
		var key := int(c.get("tick", -1)) * 1000 + int(c.get("ordinal", 0))
		if key < last_key:
			errs.append("commands_not_sorted")
		last_key = key
	return errs

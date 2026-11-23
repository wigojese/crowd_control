class_name CcTickFixture
extends RefCounted
## Small deterministic fixture for tick and state transition (Stage 07). NOT the game rules.
## Each tick draws one number from the "spawn" stream; one in four ticks spawns a fixture walker.
## Proves: fixed tick count, stable RNG, schema-checked event log, table-driven state machine.
## Golden output: tests/fixtures/tick_fixture_golden.json (from scripts/ref_model.py).

const TICKS := 640
const DEADLINE_TICK := 600

var tick: int = 0
var spawned: int = 0
var machine := CcStateMachine.new()
var events: CcEventLog
var _rng: CcRng


func _init(seed_value: int, state_def: Dictionary, event_schema: Dictionary) -> void:
	_rng = CcRng.stream(seed_value, "spawn")
	events = CcEventLog.new(event_schema)
	var r := machine.build(state_def)
	assert(r["ok"], "state table invalid: " + String(r["error"]))


## Runs the whole fixture round. Returns the result dictionary.
func run() -> Dictionary:
	machine.fire("BOOT_COMPLETE")
	machine.fire("RUN")
	while tick < TICKS:
		step()
	machine.fire("FINISH")
	events.add(TICKS, "RUN_ENDED", {"reason": "time_limit"})
	return {"spawned": spawned, "events": events.lines.size(), "hash": events.hash32(), "state": machine.current}


func step() -> void:
	if _rng.next_int(4) == 0:
		var dest := "School" if _rng.next_int(2) == 0 else "Plaza"
		spawned += 1
		events.add(tick, "WALKER_SPAWNED", {
			"walker": spawned, "profile": "C", "origin": "A",
			"destination": dest, "deadline_tick": DEADLINE_TICK,
		})
	tick += 1

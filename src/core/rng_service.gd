class_name CcRng
extends RefCounted
## Stable random service: xorshift32. Same seed gives the same sequence on every platform and
## engine version, because it uses only integer arithmetic (never randi() or RandomNumberGenerator).
## Reference implementation and golden values: scripts/ref_model.py, tests/fixtures/rng_golden.json.
## Not a singleton: create one per run and pass it in.

const MASK := 0xFFFFFFFF
const FALLBACK := 0x9E3779B9

var _state: int = FALLBACK


func _init(seed_value: int = 1) -> void:
	_state = seed_value & MASK
	if _state == 0:
		_state = FALLBACK


## A separate, reproducible stream for a named purpose (for example "spawn").
## Streams keep one system's draws from shifting another's.
static func stream(seed_value: int, stream_name: String) -> CcRng:
	var h: int = 0x811C9DC5
	for b in stream_name.to_utf8_buffer():
		h = ((h ^ b) * 0x01000193) & MASK
	return CcRng.new((h ^ seed_value) & MASK)


func next_u32() -> int:
	var x: int = _state
	x = (x ^ (x << 13)) & MASK
	x = x ^ (x >> 17)
	x = (x ^ (x << 5)) & MASK
	_state = x
	return x


## Integer in [0, n). Plain modulo: a tiny bias, accepted and documented for this game.
func next_int(n: int) -> int:
	assert(n > 0)
	return next_u32() % n


func state() -> int:
	return _state

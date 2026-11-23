extends Control
## Stage 07 boot screen: an intentionally blank screen showing one verified boot state.
## No game styling. Loads the state table, fires BOOT_COMPLETE, and shows the result.
## Headless proof line (grep for it): BOOT_STATE=READY

const STATES_PATH := "res://data/boot_states.json"

@onready var _label: Label = $Label


func _ready() -> void:
	var def = JSON.parse_string(FileAccess.get_file_as_string(STATES_PATH))
	var machine := CcStateMachine.new()
	var built := machine.build(def if def is Dictionary else {})
	var shown := "BOOT FAILED: " + String(built["error"])
	if built["ok"]:
		var fired := machine.fire("BOOT_COMPLETE")
		shown = machine.current if fired["ok"] else "BOOT FAILED: " + String(fired["error"])
	_label.text = shown
	print("BOOT_STATE=", shown)

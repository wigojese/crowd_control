extends RefCounted
## Tests T-SCN-1. Every fixture scenario must get the verdict in expected_verdicts.json.


func test_fixture_verdicts() -> String:
	var path := "res://tests/fixtures/expected_verdicts.json"
	var want: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	for name in want.keys():
		var s = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/" + name))
		var got := CcScenarioValidator.validate(s)
		got.sort()
		var exp: Array = want[name].duplicate()
		exp.sort()
		if str(got) != str(exp):
			return "%s: got %s want %s" % [name, str(got), str(exp)]
	return ""

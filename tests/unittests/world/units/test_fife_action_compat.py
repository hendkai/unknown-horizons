from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_movingobject_follow_uses_fife_action_compat_helper():
	source = (REPO_ROOT / 'horizons/world/units/movingobject.py').read_text()

	assert 'get_fife_action_name' in source
	assert 'getCurrentAction().getId()' not in source


def test_unit_action_finished_uses_fife_action_compat_helper():
	source = (REPO_ROOT / 'horizons/world/units/unit.py').read_text()

	assert 'get_fife_action_name' in source
	assert 'action.getId()' not in source

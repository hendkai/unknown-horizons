import pytest

import run_uh


def test_python_minimum_rejects_old_interpreter(monkeypatch):
	errors = []

	def fake_exit(title, message):
		errors.append((title, message))
		raise SystemExit(1)

	monkeypatch.setattr(run_uh, 'exit_with_error', fake_exit)

	with pytest.raises(SystemExit):
		run_uh.ensure_python_version((3, 8, 10))

	assert errors == [
		('Unsupported Python version', 'Python3.9 or higher is required to run Unknown Horizons.')
	]


def test_python_minimum_accepts_supported_interpreter(monkeypatch):
	def fake_exit(title, message):
		raise AssertionError('unexpected exit: {} {}'.format(title, message))

	monkeypatch.setattr(run_uh, 'exit_with_error', fake_exit)

	run_uh.ensure_python_version((3, 9, 0))


def test_content_dir_parent_path_finds_macos_bundle_resources(tmp_path, monkeypatch):
	bundle = tmp_path / 'Unknown Horizons.app'
	macos_dir = bundle / 'Contents' / 'MacOS'
	resources_dir = bundle / 'Contents' / 'Resources'
	content_dir = resources_dir / 'content'
	macos_dir.mkdir(parents=True)
	content_dir.mkdir(parents=True)
	launcher = macos_dir / 'run_uh.py'
	launcher.write_text('')

	monkeypatch.setattr(run_uh, '__file__', str(launcher))
	monkeypatch.chdir(tmp_path)

	assert run_uh.get_content_dir_parent_path() == str(resources_dir.resolve())


def test_macos_arm64_fife_error_mentions_native_bindings(monkeypatch):
	monkeypatch.setattr(run_uh.sys, 'platform', 'darwin')
	monkeypatch.setattr(run_uh.sys, 'executable', '/opt/homebrew/bin/python3')
	monkeypatch.setattr(run_uh.platform, 'machine', lambda: 'arm64')
	monkeypatch.setattr(run_uh.platform, 'python_version', lambda: '3.11.8')
	monkeypatch.setattr(run_uh.platform, 'platform', lambda: 'macOS-14.0-arm64')
	monkeypatch.setattr(run_uh.platform, 'mac_ver', lambda: ('14.0', ('', '', ''), ''))

	message = run_uh.format_fife_import_error(
		OSError("mach-o file, but is an incompatible architecture (have 'x86_64', need 'arm64')"),
		['/tmp/fife'])

	assert 'native Apple Silicon Python' in message
	assert 'arm64 Python extension binaries' in message
	assert 'mach-o architecture mismatch' in message
	assert '/opt/homebrew/bin/python3' in message


def test_find_fife_prefers_installed_package(monkeypatch):
	calls = []

	def fake_import():
		calls.append('installed')

	monkeypatch.setattr(run_uh, '_import_fife_bindings', fake_import)

	assert run_uh.find_fife(['/tmp/local-fife'])
	assert calls == ['installed']


def test_find_fife_clears_broken_installed_package_before_fallback(monkeypatch):
	calls = []

	def fake_import():
		calls.append(list(run_uh.sys.path))
		if len(calls) == 1:
			run_uh.sys.modules['fife'] = object()
			raise ImportError('broken installed fife')

		assert 'fife' not in run_uh.sys.modules

	monkeypatch.setattr(run_uh, '_import_fife_bindings', fake_import)

	assert run_uh.find_fife(['/tmp/local-fife'])
	assert calls[1][0] == '/tmp/local-fife'


def test_wrong_architecture_error_detection():
	assert run_uh.is_wrong_architecture_error("mach-o, but wrong architecture")
	assert run_uh.is_wrong_architecture_error("incompatible architecture")
	assert not run_uh.is_wrong_architecture_error("module not found")

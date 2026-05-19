import os
import sys

import pytest

import build_dmg_mac


def create_app_bundle(path):
	contents = path / 'Contents'
	(contents / 'MacOS').mkdir(parents=True)
	(contents / 'Info.plist').write_text('')
	launcher = contents / 'MacOS' / 'Unknown Horizons'
	launcher.write_text('')
	launcher.chmod(0o755)


def test_dmg_artifact_name_uses_bundle_version(monkeypatch, tmp_path):
	monkeypatch.setattr(build_dmg_mac.setup_mac, 'get_bundle_version', lambda: '2026.1')
	app_path = tmp_path / 'Unknown Horizons.app'
	create_app_bundle(app_path)
	calls = []

	def create_dmg(app_path, output_path, volume_name):
		calls.append((app_path, output_path, volume_name))

	monkeypatch.setattr(build_dmg_mac, 'create_dmg', create_dmg)

	result = build_dmg_mac.main([
		'--app-path', str(app_path),
		'--dist-dir', str(tmp_path),
		])

	assert result == 0
	assert calls == [(
		str(app_path),
		str(tmp_path / 'Unknown-Horizons-2026.1.dmg'),
		'Unknown Horizons',
		)]


def test_get_dmg_artifact_name():
	assert build_dmg_mac.get_dmg_artifact_name('2026.1') == 'Unknown-Horizons-2026.1.dmg'


def test_validate_app_bundle_reports_missing_bundle(tmp_path):
	with pytest.raises(RuntimeError) as error:
		build_dmg_mac.validate_app_bundle(str(tmp_path / 'Unknown Horizons.app'))

	assert 'Run "python3 stage_build_mac.py" first' in str(error.value)


def test_validate_app_bundle_reports_missing_executable(tmp_path):
	app_path = tmp_path / 'Unknown Horizons.app'
	contents = app_path / 'Contents'
	(contents / 'MacOS').mkdir(parents=True)
	(contents / 'Info.plist').write_text('')

	with pytest.raises(RuntimeError) as error:
		build_dmg_mac.validate_app_bundle(str(app_path))

	assert 'Contents/MacOS/Unknown Horizons' in str(error.value)


def test_validate_app_bundle_reports_launcher_directory(tmp_path):
	app_path = tmp_path / 'Unknown Horizons.app'
	create_app_bundle(app_path)
	launcher = app_path / 'Contents' / 'MacOS' / 'Unknown Horizons'
	launcher.unlink()
	launcher.mkdir()

	with pytest.raises(RuntimeError) as error:
		build_dmg_mac.validate_app_bundle(str(app_path))

	assert 'Malformed macOS app bundle file path' in str(error.value)
	assert 'Contents/MacOS/Unknown Horizons' in str(error.value)


def test_validate_app_bundle_reports_non_executable_launcher(tmp_path):
	app_path = tmp_path / 'Unknown Horizons.app'
	create_app_bundle(app_path)
	launcher = app_path / 'Contents' / 'MacOS' / 'Unknown Horizons'
	launcher.chmod(0o644)

	with pytest.raises(RuntimeError) as error:
		build_dmg_mac.validate_app_bundle(str(app_path))

	assert 'launcher is not executable' in str(error.value)


def test_create_dmg_removes_existing_output_and_invokes_hdiutil(monkeypatch, tmp_path):
	app_path = tmp_path / 'Unknown Horizons.app'
	create_app_bundle(app_path)
	output_path = tmp_path / 'Unknown-Horizons-2026.1.dmg'
	output_path.write_text('old image')
	calls = []

	monkeypatch.setattr(sys, 'platform', 'darwin')
	monkeypatch.setattr(build_dmg_mac.shutil, 'which', lambda command: '/usr/bin/hdiutil')

	def check_call(command):
		calls.append(command)
		output_path.write_text('new image')

	monkeypatch.setattr(build_dmg_mac.subprocess, 'check_call', check_call)

	build_dmg_mac.create_dmg(str(app_path), str(output_path), 'Unknown Horizons')

	assert output_path.read_text() == 'new image'
	assert calls == [[
		'hdiutil',
		'create',
		'-volname', 'Unknown Horizons',
		'-srcfolder', calls[0][5],
		'-format', 'UDZO',
		'-fs', 'HFS+',
		str(output_path),
		]]
	assert not os.path.exists(calls[0][5])


def test_create_dmg_rejects_unsupported_platform(monkeypatch, tmp_path):
	monkeypatch.setattr(sys, 'platform', 'linux')

	with pytest.raises(RuntimeError) as error:
		build_dmg_mac.create_dmg(
			str(tmp_path / 'Unknown Horizons.app'),
			str(tmp_path / 'Unknown-Horizons-2026.1.dmg'),
			'Unknown Horizons')

	assert 'requires macOS' in str(error.value)


def test_create_dmg_rejects_missing_hdiutil(monkeypatch, tmp_path):
	monkeypatch.setattr(sys, 'platform', 'darwin')
	monkeypatch.setattr(build_dmg_mac.shutil, 'which', lambda command: None)

	with pytest.raises(RuntimeError) as error:
		build_dmg_mac.create_dmg(
			str(tmp_path / 'Unknown Horizons.app'),
			str(tmp_path / 'Unknown-Horizons-2026.1.dmg'),
			'Unknown Horizons')

	assert 'hdiutil' in str(error.value)


def test_build_app_option_invokes_stage_build_before_dmg(monkeypatch, tmp_path):
	app_path = tmp_path / 'Unknown Horizons.app'
	create_app_bundle(app_path)
	calls = []

	monkeypatch.setattr(build_dmg_mac.setup_mac, 'get_bundle_version', lambda: '2026.1')

	def check_call(command):
		calls.append(command)

	monkeypatch.setattr(build_dmg_mac.subprocess, 'check_call', check_call)
	monkeypatch.setattr(build_dmg_mac, 'create_dmg', lambda app_path, output_path, volume_name: None)

	result = build_dmg_mac.main([
		'--build-app',
		'--python-bin', 'python3',
		'--app-path', str(app_path),
		'--dist-dir', str(tmp_path),
		])

	assert result == 0
	assert calls == [['python3', 'stage_build_mac.py']]

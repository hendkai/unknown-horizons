import os

import pytest

import stage_build_mac


def test_validate_source_assets_reports_missing_content(tmp_path, monkeypatch):
	monkeypatch.setattr(stage_build_mac, 'CONTENT_DIR', str(tmp_path / 'content'))
	monkeypatch.setattr(
		stage_build_mac,
		'ICON_PATH',
		os.path.join(stage_build_mac.CONTENT_DIR, 'gui', 'icons', 'Icon.icns'))

	with pytest.raises(RuntimeError) as error:
		stage_build_mac.validate_source_assets()

	assert 'Missing required macOS bundle asset' in str(error.value)
	assert stage_build_mac.CONTENT_DIR in str(error.value)


def test_validate_staging_layout_accepts_required_resources(tmp_path, monkeypatch):
	resources_dir = tmp_path / 'src' / 'Contents' / 'Resources'
	content_dir = resources_dir / 'content'
	(content_dir / 'maps').mkdir(parents=True)
	(resources_dir / 'Icon.icns').write_text('')
	(content_dir / 'settings-template.xml').write_text('')
	(content_dir / 'game.sql').write_text('')
	(content_dir / 'maps' / 'development.sqlite').write_text('')

	monkeypatch.setattr(stage_build_mac, 'RESOURCE_DIR', str(resources_dir))
	monkeypatch.setattr(stage_build_mac, 'STAGED_CONTENT_DIR', str(content_dir))
	monkeypatch.setattr(stage_build_mac, 'STAGED_ICON_PATH', str(resources_dir / 'Icon.icns'))

	stage_build_mac.validate_staging_layout()

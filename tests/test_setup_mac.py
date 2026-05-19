import os

os.environ.setdefault('UH_USER_CONFIG_DIR', '/tmp/unknown-horizons-test-config')
os.environ.setdefault('UH_USER_DATA_DIR', '/tmp/unknown-horizons-test-data')
os.environ.setdefault('UH_USER_CACHE_DIR', '/tmp/unknown-horizons-test-cache')

from horizons.constants import VERSION

import setup_mac


def test_plist_uses_bundle_icon_and_project_version():
	plist = setup_mac.plist

	assert plist['CFBundleIconFile'] == 'Icon.icns'
	assert plist['CFBundleIdentifier'] == 'org.unknown-horizons.UnknownHorizons'
	assert plist['CFBundleExecutable'] == 'Unknown Horizons'
	assert plist['CFBundleShortVersionString'] == VERSION.RELEASE_VERSION
	assert plist['CFBundleVersion'] == VERSION.RELEASE_VERSION


def test_content_is_included_under_resources_content():
	data_includes = setup_mac.get_data_includes()
	icon_path = '/'.join(('content', 'gui', 'icons', 'Icon.icns'))

	assert ('', [icon_path]) in data_includes
	assert any(target == 'content/' for target, files in data_includes)
	assert any(
		target == 'content/gui/icons/' and icon_path in files
		for target, files in data_includes
	)

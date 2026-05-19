#!/usr/bin/env python3

# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import setup_mac

APP_PATH = os.path.join('dist', 'Unknown Horizons.app')
DIST_DIR = 'dist'
VOLUME_NAME = 'Unknown Horizons'


def get_dmg_artifact_name(version):
	"""Return the versioned DMG artifact name."""
	safe_version = version.replace(os.sep, '-').replace('/', '-')
	return 'Unknown-Horizons-{}.dmg'.format(safe_version)


def validate_app_bundle(app_path):
	"""Validate that app_path points at the expected macOS app bundle layout."""
	required_dirs = [
		app_path,
		os.path.join(app_path, 'Contents'),
		os.path.join(app_path, 'Contents', 'MacOS'),
		]
	required_files = [
		os.path.join(app_path, 'Contents', 'Info.plist'),
		os.path.join(app_path, 'Contents', 'MacOS', 'Unknown Horizons'),
		]
	required_paths = required_dirs + required_files
	missing = [path for path in required_paths if not os.path.exists(path)]
	if missing:
		raise RuntimeError(
			'Missing macOS app bundle path(s): {}. Run "python3 stage_build_mac.py" first.'.format(
				', '.join(missing)))
	invalid_dirs = [path for path in required_dirs if not os.path.isdir(path)]
	if invalid_dirs:
		raise RuntimeError(
			'Malformed macOS app bundle directory path(s): {}'.format(', '.join(invalid_dirs)))
	invalid_files = [path for path in required_files if not os.path.isfile(path)]
	if invalid_files:
		raise RuntimeError(
			'Malformed macOS app bundle file path(s): {}'.format(', '.join(invalid_files)))
	executable_path = os.path.join(app_path, 'Contents', 'MacOS', 'Unknown Horizons')
	if not os.access(executable_path, os.X_OK):
		raise RuntimeError(
			'macOS app bundle launcher is not executable: {}'.format(executable_path))


def validate_dmg_tooling():
	"""Fail early when the local platform cannot create macOS disk images."""
	if sys.platform != 'darwin':
		raise RuntimeError('DMG creation requires macOS and the hdiutil system tool.')
	if shutil.which('hdiutil') is None:
		raise RuntimeError('DMG creation requires hdiutil, but it was not found in PATH.')


def build_app_bundle_if_requested(rebuild_app, python_bin):
	if rebuild_app:
		subprocess.check_call([python_bin, 'stage_build_mac.py'])


def create_dmg(app_path, output_path, volume_name):
	"""Create a read-only compressed DMG containing the app bundle."""
	validate_dmg_tooling()
	dist_dir = os.path.dirname(output_path) or '.'
	if not os.path.exists(dist_dir):
		os.makedirs(dist_dir)
	if os.path.exists(output_path):
		os.remove(output_path)

	staging_dir = tempfile.mkdtemp(prefix='unknown-horizons-dmg-', dir=dist_dir)
	try:
		staged_app = os.path.join(staging_dir, os.path.basename(app_path))
		shutil.copytree(app_path, staged_app, symlinks=True)
		applications_link = os.path.join(staging_dir, 'Applications')
		if not os.path.exists(applications_link):
			os.symlink('/Applications', applications_link)

		subprocess.check_call([
			'hdiutil',
			'create',
			'-volname', volume_name,
			'-srcfolder', staging_dir,
			'-format', 'UDZO',
			'-fs', 'HFS+',
			output_path,
			])
	finally:
		shutil.rmtree(staging_dir)

	if not os.path.exists(output_path):
		raise RuntimeError('hdiutil completed but did not create {}'.format(output_path))


def parse_args(argv):
	parser = argparse.ArgumentParser(
		description='Build a versioned Unknown Horizons DMG from the macOS app bundle.')
	parser.add_argument(
		'--app-path', default=APP_PATH,
		help='Path to the existing .app bundle. Defaults to %(default)s.')
	parser.add_argument(
		'--dist-dir', default=DIST_DIR,
		help='Directory for the generated DMG. Defaults to %(default)s.')
	parser.add_argument(
		'--volume-name', default=VOLUME_NAME,
		help='Mounted DMG volume name. Defaults to %(default)s.')
	parser.add_argument(
		'--build-app', action='store_true',
		help='Run stage_build_mac.py before creating the DMG.')
	parser.add_argument(
		'--python-bin', default=sys.executable,
		help='Python executable used with --build-app. Defaults to the current interpreter.')
	return parser.parse_args(argv)


def main(argv=None):
	if argv is None:
		argv = sys.argv[1:]
	args = parse_args(argv)
	version = setup_mac.get_bundle_version()
	output_path = os.path.join(args.dist_dir, get_dmg_artifact_name(version))
	try:
		build_app_bundle_if_requested(args.build_app, args.python_bin)
		validate_app_bundle(args.app_path)
		create_dmg(args.app_path, output_path, args.volume_name)
	except subprocess.CalledProcessError as error:
		print('Command failed with exit code {}: {}'.format(
			error.returncode, ' '.join(error.cmd)), file=sys.stderr)
		return 1
	except RuntimeError as error:
		print(error, file=sys.stderr)
		return 1
	print('Created {}'.format(output_path))
	return 0


if __name__ == '__main__':
	sys.exit(main())

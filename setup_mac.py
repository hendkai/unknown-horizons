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

# usage:
# copy the full content/ folder into src/Contents/Resources/
# moreover copy the fife dir into the current dir
# details can be found at http://wiki.unknown-horizons.org/w/MacOS_build_notes

import os
import platform
import subprocess
from pathlib import Path

from setuptools import setup

# Sets what directory to crawl for files to include
# Relative to location of setup.py; leave off trailing slash
INCLUDES_DIR = 'content'

# Set the root directory for included files
# Relative to the bundle's Resources folder, so '../../' targets bundle root
INCLUDES_TARGET = 'content/'
ICON_FILE = os.path.join('content', 'gui', 'icons', 'Icon.icns')


def get_git_head_version(project_root):
	"""Return the current git HEAD abbreviation without requiring git."""
	git_path = project_root / '.git'
	if git_path.is_file():
		prefix, _, value = git_path.read_text().strip().partition(':')
		if prefix == 'gitdir' and value:
			git_path = (project_root / value.strip()).resolve()

	head_path = git_path / 'HEAD'
	if not head_path.exists():
		return None

	head_ref = head_path.read_text().strip().partition(' ')[2]
	if head_ref:
		head_file = git_path / head_ref
		if not head_file.exists():
			common_dir_path = git_path / 'commondir'
			if common_dir_path.exists():
				common_dir = (git_path / common_dir_path.read_text().strip()).resolve()
				head_file = common_dir / head_ref
	else:
		head_file = head_path

	if head_file.exists():
		return head_file.read_text().strip()[0:7]
	return None


def get_bundle_version():
	"""Return the project version for macOS bundle metadata."""
	project_root = Path(__file__).parent
	try:
		git = "git"
		if platform.system() == "Windows":
			git = "git.exe"

		tag_structure = "20[0-9][0-9].[0-9]*"
		describe = [git, "describe", "--tags", "--match", tag_structure]
		return subprocess.check_output(
			describe,
			cwd=project_root,
			stderr=subprocess.DEVNULL,
			universal_newlines=True,
		).rstrip('\n')
	except (subprocess.CalledProcessError, OSError, RuntimeError):
		try:
			from horizons.constants import VERSION
			return VERSION.RELEASE_VERSION
		except (ImportError, OSError, RuntimeError, subprocess.CalledProcessError):
			pass

		head_version = get_git_head_version(project_root)
		if head_version:
			return head_version

		try:
			with (project_root / 'content' / 'packages' / 'gitversion.txt').open() as f:
				return f.read()
		except IOError:
			return '<unknown>'


def get_data_includes(includes_dir=INCLUDES_DIR, includes_target=INCLUDES_TARGET):
	"""Return data files that py2app should place in Contents/Resources/content."""
	data_includes = [('', [ICON_FILE])]
	for root, dirs, filenames in os.walk(includes_dir):
		if root == includes_dir:
			final = includes_target
		else:
			final = includes_target + root[len(includes_dir) + 1:] + '/'
		files = []
		for file in filenames:
			if file[0] != '.':
				files.append(os.path.join(root, file))
		data_includes.append((final, files))
	return data_includes

PACKAGES = ['horizons', 'fife']
BUNDLE_VERSION = get_bundle_version()

#Info.plist keys for the app
# Icon.icns must be inside Contents/Resources/
plist = {"CFBundleDevelopmentRegion": "en",
		 "CFBundleDisplayName": "Unknown Horizons",
		 "CFBundleExecutable": "Unknown Horizons",
		 "CFBundleIconFile": "Icon.icns",
		 "CFBundleIdentifier": "org.unknown-horizons.UnknownHorizons",
		 "CFBundleName": "Unknown Horizons",
		 "CFBundlePackageType": "APPL",
		 "CFBundleShortVersionString": BUNDLE_VERSION,
		 "CFBundleVersion": BUNDLE_VERSION,
		 "LSArchitecturePriority": ["arm64", "x86_64"],
		 "LSMinimumSystemVersion": "10.15",
		 "NSHighResolutionCapable": True,
		 "NSSupportsAutomaticGraphicsSwitching": True,
		}

APP = ['run_uh.py']
OPTIONS = {'argv_emulation': True, 'packages': PACKAGES, 'plist': plist}


def main():
	setup(
		app=APP,
		data_files=get_data_includes(),
		options={'py2app': OPTIONS},
		setup_requires=['py2app'],
	)


if __name__ == "__main__":
	main()

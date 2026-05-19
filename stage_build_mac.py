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


import getopt
import glob
import os
import shutil
import sys

verbose = False
RESOURCE_DIR = './src/Contents/Resources'
CONTENT_DIR = './content'
ICON_PATH = os.path.join(CONTENT_DIR, 'gui', 'icons', 'Icon.icns')
STAGED_CONTENT_DIR = os.path.join(RESOURCE_DIR, 'content')
STAGED_ICON_PATH = os.path.join(RESOURCE_DIR, 'Icon.icns')
REQUIRED_CONTENT_FILES = (
    'settings-template.xml',
    'game.sql',
    os.path.join('maps', 'development.sqlite'),
)

help_message = '''
Usage: stage_build_mac.py [options]

Options:
    --run                    Start app with "open ./dist/Unknown Horizons.app"
                             when done (all is cleaned before this)
    --fife-dir=<Location>    Optional location of FIFE-trunk fallback
    --python-bin=<Location>  For people with a lot of python,
                             this is totally optional!
    --verbose                Just as it sounds :) will output more info
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def validate_source_assets():
    required_paths = [CONTENT_DIR, ICON_PATH]
    required_paths.extend(os.path.join(CONTENT_DIR, path) for path in REQUIRED_CONTENT_FILES)
    missing = [path for path in required_paths if not os.path.exists(path)]
    if missing:
        raise RuntimeError("Missing required macOS bundle asset(s): {}".format(
            ", ".join(missing)))


def validate_staging_layout():
    required_paths = [STAGED_CONTENT_DIR, STAGED_ICON_PATH]
    required_paths.extend(os.path.join(STAGED_CONTENT_DIR, path) for path in REQUIRED_CONTENT_FILES)
    missing = [path for path in required_paths if not os.path.exists(path)]
    if missing:
        raise RuntimeError("Incomplete macOS bundle staging layout: {}".format(
            ", ".join(missing)))


def setup(fife_dir):
    """
    Setup files and directories
    """
    validate_source_assets()
    if verbose:
        print("Setting up environment")
    # If these two exists we remove them for a clean build
    if os.path.exists('./build'):
        if verbose:
            print("Cleaning build path")
        shutil.rmtree('./build')
    if os.path.exists('./dist'):
        if verbose:
            print("Cleaning dist path")
        shutil.rmtree('./dist')

    # These should have cleaned out, else we remove them
    if os.path.exists('./src'):
        if verbose:
            print("Cleaning src path")
        shutil.rmtree('./src')
    if os.path.exists('./fife'):
        if verbose:
            print("Cleaning fife path")
        shutil.rmtree('./fife')

    if verbose:
        print("Create src directory")
    # The source files, for building app correctly
    os.makedirs(RESOURCE_DIR)

    # Copy fife and content
    if verbose:
        print("Copying Icon.icns")
    shutil.copy(ICON_PATH, RESOURCE_DIR)

    if fife_dir:
        if verbose:
            print("Copying fife source from " + fife_dir + "engine/python/fife")
        shutil.copytree(os.path.join(fife_dir, 'engine', 'python', 'fife'), './fife')

    if verbose:
        print("Copying content into src")
    shutil.copytree(CONTENT_DIR, STAGED_CONTENT_DIR)
    validate_staging_layout()


def tearDown(run):
    shutil.rmtree('./src/')
    if os.path.exists('./fife'):
        shutil.rmtree('./fife')

    # Remove some other styff
    files = glob.glob('*.egg')
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        else:
            shutil.rmtree(f)

    # If the -r or --run arg is passed we start the app after build
    if run:
        os.popen("open ./dist/Unknown\\ Horizons.app")


def build(pyver):
    os.system(pyver + " setup.py build_i18n")
    os.system(pyver + " setup_mac.py py2app")


def main(argv=None):
    global verbose
    fife_dir = False
    pyver = sys.executable
    run = False
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:p:rv", [
                                       "help", "fife-dir=", "python-bin=",
                                       "run", "verbose"])
        except getopt.error as msg:
            raise Usage(msg)

        # option processing
        for option, value in opts:
            if option in ("-p", "--python-bin",):
                pyver = value
            if option in ("-f", "--fife-dir",):
                fife_dir = value
            if option in ("-h", "--help"):
                print(help_message)
                return 0
            if option in ("-r", "--run",):
                run = True
            if option in ("-v", "--verbose",):
                verbose = True

    except Usage as err:
        print(sys.argv[0].split("/")[-1] + ": " + str(err.msg), file=sys.stderr)
        print("\t for help use --help", file=sys.stderr)
        return 2

    setup(fife_dir)
    build(pyver)
    tearDown(run)


if __name__ == "__main__":
    sys.exit(main())

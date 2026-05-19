[![Unknown-Horizons](/content/gfx/uh.png)](http://unknown-horizons.org/)
============================================================

[![Build Status](https://travis-ci.org/unknown-horizons/unknown-horizons.svg?branch=master)](https://travis-ci.org/unknown-horizons/unknown-horizons)
[![Coverage Status](https://coveralls.io/repos/github/unknown-horizons/unknown-horizons/badge.svg?branch=master)](https://coveralls.io/github/unknown-horizons/unknown-horizons?branch=master)
[![Translation status](https://hosted.weblate.org/widgets/uh/-/shields-badge.svg)](https://hosted.weblate.org/engage/uh/?utm_source=widget)
[![#unknown-horizons on Freenode](https://img.shields.io/badge/freenode-%23unknown--horizons-green.svg)](https://webchat.freenode.net/?channels=unknown-horizons)

_Unknown Horizons_ is a 2D real time strategy simulation with an
emphasis on economy and city building. Expand your small
settlement to a strong and wealthy colony, collect taxes and
supply your inhabitants with valuable goods. Increase your
power with a well balanced economy and with strategic trade
and diplomacy.

Find more information about Unknown Horizons on [our website](http://unknown-horizons.org/).


## Installation

For installation instructions check the "Downloads" section on
[our website](http://unknown-horizons.org/downloads/).

## Building from source

To get the latest version of the game, you have to build it from source:

 * [Instructions for GNU/Linux](https://github.com/unknown-horizons/unknown-horizons/wiki/Linux)
 * [Instructions for Windows](https://github.com/unknown-horizons/unknown-horizons/wiki/Windows)
 * [Instructions for OS X](https://github.com/unknown-horizons/unknown-horizons/wiki/MacOS)

If you want to start hacking on Unknown Horizons, check out [this guide](https://github.com/unknown-horizons/unknown-horizons/wiki/Getting-started) and contact us to help you get started. A [development workflow](development/docker/) with containers is also available. We have easy tasks for starters [here](https://github.com/unknown-horizons/unknown-horizons/issues?q=is%3Aopen+is%3Aissue+label%3AD-starter).


## Dependencies


Technology     | Component
---------------|----------
**Python 3**   | Used for everything
**SQLite**     | Maps
**YAML**       | Object files storing component based information, easily scriptable
**[fifengine](https://github.com/fifengine/fifengine)**  | The C++ game engine, provides Python bindings
**[fifechan](https://github.com/fifengine/fifechan)**   | GUI library
**[pyenet](https://github.com/aresch/pyenet)** | The multiplayer library. Can be ignored if you don't want to play multiplayer

### macOS Apple Silicon

Unknown Horizons requires Python 3.9 or newer. On Apple Silicon, run it with a native arm64 Python and native arm64 builds of fifengine/FIFEChan. Do not start the game with an x86_64 Python under Rosetta if you want native execution.

Check the runtime before starting the game:

```bash
python3 -c "import platform, sys; print(platform.machine()); print(sys.executable)"
python3 -c "from fife import fife; print(fife)"
python3 -c "import enet; print(enet)"
```

The first command should print `arm64`. FIFE and FIFEChan are required for startup. ENet is optional; if no native `enet` module is installed, multiplayer is unavailable but local game startup should still work.

### macOS app bundle

The macOS bundle build uses `py2app` and the staging helper in this repository.
Install the normal runtime dependencies first, including Python 3.9 or newer,
fifengine/FIFEChan Python bindings, and `py2app`. Translation and atlas assets
are prepared by the build step.

Build the app bundle from the repository root:

```bash
python3 stage_build_mac.py
```

The expected output is `dist/Unknown Horizons.app`. The bundle contains
`Contents/Resources/Icon.icns` and `Contents/Resources/content/`; config, cache,
logs, and savegames stay in the normal macOS user directories under
`~/Library/Application Support/Unknown Horizons` and
`~/Library/Caches/Unknown Horizons`.

## Community

Type         | Where?
-------------|-----------------------------------------------------------------------
Discord      | https://discord.gg/VX6m2ZX
Bug Tracker  | https://github.com/unknown-horizons/unknown-horizons/issues

More support info [here](https://github.com/unknown-horizons/unknown-horizons/wiki/Support-Infos).

## License

This game is free software. It uses the [GNU General Public License, version 2](https://github.com/unknown-horizons/unknown-horizons/blob/master/doc/licenses/GPL). The licenses used for music, artwork, sounds, etc. can be found [here](https://github.com/unknown-horizons/unknown-horizons/tree/master/doc).

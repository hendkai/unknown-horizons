# Apple-Silicon Build and Smoke Test

This checklist is for native Apple-Silicon release verification. Run it on an
Apple-Silicon Mac with native `arm64` dependencies, not with an `x86_64` Python
under Rosetta.

## Prerequisites

- Python 3.9 or newer, installed as a native `arm64` interpreter.
- Native `arm64` builds of fifengine/FIFE and FIFEChan. They are required for
  startup and GUI rendering.
- `py2app`, used by the macOS app bundle build.
- `gettext` with `msgfmt`, used while building translated assets.
- `hdiutil`, available on macOS and used for DMG creation.
- Optional native `pyenet`/`enet` Python module. It is only required for
  multiplayer. A missing ENet module is acceptable when multiplayer is outside
  the smoke-test scope.

Check the active interpreter before building:

```bash
python3 -c "import platform, sys; print(platform.machine()); print(sys.executable)"
python3 -c "from fife import fife; print(fife)"
python3 -c "import enet; print(enet)"
```

The first command should print `arm64`. FIFE import failures or architecture
mismatch messages must be fixed before using the build for Apple-Silicon
verification. ENet import failures only block multiplayer verification.

## Automated Apple-Silicon Release Build

A GitHub Actions workflow is available in
`.github/workflows/apple-silicon-release.yml`. It runs on a native macOS arm64
runner, rejects Rosetta/x86_64 builds, builds the app bundle, creates a versioned
DMG, writes a SHA-256 checksum, and uploads both files as workflow artifacts.
For tags matching `20[0-9][0-9].*` or `v*`, it also attaches the DMG and checksum
to the GitHub release.

Manual trigger:

```bash
gh workflow run apple-silicon-release.yml --ref <branch-or-tag>
```

The workflow requires native arm64 FIFE/FIFEChan bindings on the runner. If FIFE
is available as a checkout rather than an installed Python package, pass its root
path via the workflow's `fife-root` input. The path must contain
`engine/python/fife`.

## Local One-Command Build

Run from the repository root on an Apple-Silicon Mac:

```bash
scripts/build_apple_silicon_release.sh
```

The script performs the same guard checks as CI, runs the macOS packaging unit
tests, creates `dist/Unknown Horizons.app`, builds
`dist/Unknown-Horizons-<version>.dmg`, and writes
`dist/Unknown-Horizons-<version>.dmg.sha256`.

If FIFE is not installed globally, provide a native arm64 FIFE checkout:

```bash
FIFE_ROOT=/path/to/fifengine scripts/build_apple_silicon_release.sh
```

## Build the App Bundle

Run from the repository root:

```bash
python3 stage_build_mac.py
```

The expected artifact is:

```text
dist/Unknown Horizons.app
```

The staging helper validates required source assets and the app bundle layout.

## Build the DMG

Create a DMG from an existing app bundle:

```bash
python3 build_dmg_mac.py
```

The expected artifact is:

```text
dist/Unknown-Horizons-<version>.dmg
```

To rebuild the app bundle and then create the DMG in one step:

```bash
python3 build_dmg_mac.py --build-app
```

## Installation Verification

1. Mount `dist/Unknown-Horizons-<version>.dmg`.
2. Copy `Unknown Horizons.app` from the mounted DMG to `/Applications`.
3. Launch `/Applications/Unknown Horizons.app`, not the app inside the mounted
   DMG.
4. Confirm the app opens without Python version, FIFE, FIFEChan, or
   architecture mismatch errors.
5. Verify the copied app bundle contains these paths:

```text
/Applications/Unknown Horizons.app/Contents/Resources/content/
/Applications/Unknown Horizons.app/Contents/MacOS/Unknown Horizons
```

The launcher executable at `Contents/MacOS/Unknown Horizons` must be present and
executable. The `Contents/Resources/content/` directory must contain the game
assets used at runtime.

## Smoke-Test Checklist

- Launch the copied `/Applications/Unknown Horizons.app`.
- Verify the main menu is visible, responsive, and rendered without missing
  fonts, images, or UI elements.
- Open settings, change at least one harmless option, close settings, and return
  to the main menu.
- Open help and credits, then return to the main menu.
- Start a new singleplayer game.
- Verify the map loads, the UI remains responsive, and background audio or sound
  effects work when enabled.
- Found a settlement with the ship.
- Build basic infrastructure such as a road and one production or storage
  building.
- Let the game run briefly and confirm there are no obvious stalls, missing
  assets, or repeated runtime errors.
- Save the game.
- Quit to the menu or exit the app.
- Relaunch the copied app and load the saved game.
- Confirm the loaded game preserves the settlement and built structures.

Optional multiplayer check:

- If native `pyenet`/`enet` is installed, open the multiplayer flow far enough to
  verify that the dependency loads and the UI does not fail immediately.
- If ENet is not installed, record multiplayer as not tested. This does not fail
  the Apple-Silicon smoke test unless multiplayer is part of the release scope.

## Optional Automated GUI Coverage

The manual smoke test is still required for release verification on native Apple
Silicon. Existing GUI tests can be used as additional references for the same
flows when a graphical test environment with FIFE is available:

- `tests/gui/menu/test_mainmenu.py`
- `tests/gui/menu/test_singleplayer.py`
- `tests/gui/menu/test_saveload.py`
- `tests/gui/ingame/test_build.py`

Run GUI tests only in an environment prepared for them, for example with the
project's `--gui-tests` pytest option or the existing GUI test runner.

## Troubleshooting

- If `platform.machine()` prints `x86_64`, the build or smoke test is running
  under Rosetta and is not a native Apple-Silicon verification.
- If FIFE or FIFEChan cannot be imported, rebuild or reinstall native `arm64`
  versions before testing the app.
- If the app launches from the build directory but fails after DMG installation,
  recheck the copied app bundle for `Contents/Resources/content/` and
  `Contents/MacOS/Unknown Horizons`.
- If multiplayer fails and ENet is not installed, treat it as an optional
  dependency issue unless multiplayer is explicitly in scope for the release.

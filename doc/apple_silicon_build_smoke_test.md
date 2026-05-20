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

## CI and Release Workflow

The GitHub Actions Apple-Silicon workflow has two paths. Pull requests and
branch pushes run only focused packaging and launcher tests, so they do not
build a DMG, upload artifacts, or publish a GitHub Release.

Manual `workflow_dispatch` runs and release tag pushes run the full release
build through `scripts/build_apple_silicon_release.sh`. That path validates a
native macOS `arm64` host, a native `arm64` Python interpreter, and the required
release tooling before building the app bundle and DMG.

GitHub Release publishing is limited to release tag pushes.

## Build the DMG

Create a DMG from an existing app bundle:

```bash
python3 build_dmg_mac.py
```

The expected artifact is:

```text
dist/Unknown-Horizons-<version>.dmg
```

Before installing the artifact, record its SHA-256 in the smoke-test report:

```bash
shasum -a 256 dist/Unknown-Horizons-<version>.dmg
```

To rebuild the app bundle and then create the DMG in one step:

```bash
python3 build_dmg_mac.py --build-app
```

## Installation Verification

1. Mount `dist/Unknown-Horizons-<version>.dmg`.
2. Remove any existing `/Applications/Unknown Horizons.app` or explicitly
   replace it during the copy. Do not continue if the installed app cannot be
   replaced by the DMG candidate.
3. Copy `Unknown Horizons.app` from the mounted DMG to `/Applications`.
4. Launch `/Applications/Unknown Horizons.app`, not the app inside the mounted
   DMG.
5. Confirm the app opens without Python version, FIFE, FIFEChan, or
   architecture mismatch errors.
6. Verify the copied app bundle contains these paths:

```text
/Applications/Unknown Horizons.app/Contents/Resources/content/
/Applications/Unknown Horizons.app/Contents/MacOS/Unknown Horizons
```

The launcher executable at `Contents/MacOS/Unknown Horizons` must be present and
executable. The `Contents/Resources/content/` directory must contain the game
assets used at runtime.

## Runtime Architecture Verification

The release candidate only satisfies native Apple-Silicon verification when the
installed app runs as `arm64`. Check the app process after launching it from
`/Applications`:

```bash
pgrep -x "Unknown Horizons"
ps -o pid,arch,comm -p <pid>
```

The reported architecture must be `arm64`. Any Python, FIFE, FIFEChan, or
dependency architecture mismatch warning is a failed smoke test until the build
is fixed and retested from a freshly installed DMG.

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

Use a fresh user profile when practical, or record the existing profile used for
testing. Do not mark save/load as passed until the app has been fully quit,
reopened from `/Applications/Unknown Horizons.app`, and the saved game has loaded
successfully.

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

## Smoke-Test Report

Create one filled report per release candidate under
`doc/release_smoke_reports/`, using
`doc/release_smoke_reports/apple_silicon_smoke_test_template.md`.

The report must include:

- Release version and tested DMG path.
- DMG SHA-256.
- Test date, tester, macOS version, and host architecture.
- Confirmation that the app was copied to and launched from
  `/Applications/Unknown Horizons.app`.
- Artifact validation results for mount, copy, executable, and bundled content.
- Runtime validation results for app launch, `arm64` process architecture,
  FIFE/FIFEChan loading, and absence of architecture mismatch warnings.
- Manual flow results for launch, settings, help or credits, singleplayer,
  settlement founding, road and production or storage building placement, save,
  relaunch, and load.
- Final result: `pass`, `fail`, or `blocked`.
- Notes for any workaround, Gatekeeper/quarantine prompt, launch log, stall, or
  known deviation.

Pass the release candidate only when every required launch, settings,
singleplayer, settlement, save, and load check succeeds from the installed
`/Applications` app with native `arm64` runtime validation. Mark the result as
`fail` for runtime or flow regressions. Mark it as `blocked` when the DMG,
hardware, native dependencies, or macOS GUI environment prevent the test from
running.

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

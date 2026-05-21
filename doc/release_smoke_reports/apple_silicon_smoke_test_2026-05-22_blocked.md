# Apple-Silicon Smoke-Test Blocked Attempt

## Summary

- Release version: not available
- Result: blocked
- Tested at: 2026-05-22
- Tester: Hermes
- Notes: Focused packaging tests passed locally and on GitHub Actions after fixing
  the requirements resolver conflict. The full local release build was attempted
  with an arm64 Python virtual environment, but it now stops at the explicit
  release dependency guard because native FIFE Python bindings are not installed.
  No DMG was produced, so installed-app runtime and manual gameplay smoke testing
  could not run.

## Artifact

- DMG path: `dist/Unknown-Horizons-<version>.dmg`
- DMG SHA-256: not available
- App install path: `/Applications/Unknown Horizons.app`
- Existing `/Applications/Unknown Horizons.app` removed or explicitly replaced
  before launch: no

## Host

- macOS version: 26.5
- Host architecture: arm64
- Python version used for build: Python 3.9.6 at
  `/Users/hendrik/.hermes/tmp/unknown-horizons-reqcheck2/bin/python`
- FIFE/FIFEChan source or package: not installed in the build environment;
  `scripts/build_apple_silicon_release.sh` failed with
  `error: required Python import failed: FIFE Python bindings`.
- Test profile or `UH_USER_DIR`: not created

## Preflight / Build Attempt

| Check | Result | Notes |
| --- | --- | --- |
| Focused packaging tests | pass | `scripts/build_apple_silicon_release.sh --test-only` ran 23 tests successfully. |
| GitHub Actions packaging tests | pass | Run `26256885642` passed on master after pinning `pytest-cov==2.5.1`. |
| Host architecture | pass | `uname -m` reported `arm64`. |
| Python architecture | pass | Build Python reported `platform.machine()` as `arm64`. |
| `msgfmt` | pass | Found at `/opt/homebrew/bin/msgfmt`. |
| `hdiutil` | pass | Found at `/usr/bin/hdiutil`. |
| `py2app` | pass | Installed in the temporary build virtual environment. |
| FIFE import | blocked | `from fife import fife` is not importable. |
| FIFEChan/pychan import | blocked | Not reached after FIFE import guard; expected to require native FIFE/FIFEChan bindings. |
| DMG build command | blocked | `PYTHON_BIN=/Users/hendrik/.hermes/tmp/unknown-horizons-reqcheck2/bin/python scripts/build_apple_silicon_release.sh` stopped before py2app with the explicit FIFE guard. |

## Artifact Validation

| Check | Result | Notes |
| --- | --- | --- |
| DMG mounts successfully | blocked | No DMG artifact was produced. |
| Existing `/Applications/Unknown Horizons.app` removed or explicitly replaced | blocked | Install did not proceed because no DMG artifact was produced. |
| `Unknown Horizons.app` copies to `/Applications` | blocked | No mounted DMG app was available to copy. |
| App launched only from `/Applications/Unknown Horizons.app` | blocked | No installed candidate app was available. |
| `Contents/MacOS/Unknown Horizons` exists | blocked | Installed app bundle was not created from a DMG candidate. |
| Launcher executable bit is set | blocked | Installed app bundle was not created from a DMG candidate. |
| `Contents/Resources/content/` exists | blocked | Installed app bundle was not created from a DMG candidate. |

## Runtime Validation

| Check | Result | Notes |
| --- | --- | --- |
| App launches from `/Applications` | blocked | No installed DMG candidate was available. |
| Process architecture is `arm64` | blocked | No app process was launched. |
| FIFE loads | blocked | Native FIFE Python bindings are not installed in the build environment. |
| FIFEChan loads | blocked | Native FIFEChan/pychan bindings are not installed in the build environment. |
| No Python/FIFE/FIFEChan architecture mismatch warnings | blocked | No app process was launched. |
| Main menu appears without missing content or asset errors | blocked | No app process was launched. |

## Manual Flow

| Flow | Result | Notes |
| --- | --- | --- |
| Main menu visible and responsive | blocked | No installed DMG candidate was available. |
| Settings opens and closes | blocked | No installed DMG candidate was available. |
| Help or credits opens and closes | blocked | No installed DMG candidate was available. |
| Singleplayer game starts | blocked | No installed DMG candidate was available. |
| Settlement founded | blocked | No installed DMG candidate was available. |
| Road and one production or storage building placed | blocked | No installed DMG candidate was available. |
| Game saved | blocked | No installed DMG candidate was available. |
| App fully quit | blocked | No installed DMG candidate was available. |
| App relaunched from `/Applications` | blocked | No installed DMG candidate was available. |
| Saved game loaded after relaunch | blocked | No installed DMG candidate was available. |

## Optional Multiplayer

- ENet installed: no
- Multiplayer smoke result: not tested
- Notes: ENet is optional for non-multiplayer release smoke testing, but was not
  installed in the temporary build environment.

## Pass/Fail Decision

The release candidate is blocked, not passed. The next required step is to
provide native arm64 FIFE/FIFEChan Python bindings for the build Python, rerun
`scripts/build_apple_silicon_release.sh`, record the generated DMG and SHA-256,
install the DMG candidate to `/Applications`, and complete the manual runtime,
singleplayer, save, relaunch, and load smoke flow.

# Apple-Silicon Smoke-Test Blocked Attempt

## Summary

- Release version: not available
- Status: interim blocked attempt; not a completed smoke-test report
- Result: blocked
- Tested at: 2026-05-20
- Tester: Codex
- Notes: Native Apple-Silicon host was available, but no release DMG artifact
  existed in this worktree. A documented build attempt was made with
  `python3 build_dmg_mac.py --build-app`; it failed before DMG creation because
  local build/runtime dependencies were unavailable. The installed-DMG smoke flow
  could not be executed and this file must not be used as a release-gate pass.

## Artifact

- DMG path: `dist/Unknown-Horizons-<version>.dmg`
- DMG SHA-256: not available
- App install path: `/Applications/Unknown Horizons.app`
- Existing `/Applications/Unknown Horizons.app` removed or explicitly replaced
  before launch: no

## Build Attempt

| Check | Result | Notes |
| --- | --- | --- |
| Host architecture | pass | `uname -m` reported `arm64`. |
| Python architecture | pass | `python3` reported `platform.machine()` as `arm64`. |
| FIFE import | blocked | `python3 -c 'from fife import fife'` failed with `ModuleNotFoundError: No module named 'fife'`. |
| FIFEChan import | blocked | `python3 -c 'import fifechan'` failed with `ModuleNotFoundError: No module named 'fifechan'`. |
| DMG build command | blocked | `python3 build_dmg_mac.py --build-app` failed before producing `dist/` because `setup.py` could not import `distro`, `setup_mac.py` could not obtain `py2app`, and network access was unavailable for pip. |

## Host

- macOS version: 26.5 (25F71)
- Host architecture: arm64
- Python version used for build: not available
- FIFE/FIFEChan source or package: not available
- Test profile or `UH_USER_DIR`: not created

## Artifact Validation

| Check | Result | Notes |
| --- | --- | --- |
| DMG artifact exists at `dist/Unknown-Horizons-<version>.dmg` | blocked | `dist/` does not exist in this worktree. |
| DMG mounts successfully | blocked | No DMG artifact was available to mount. |
| Existing `/Applications/Unknown Horizons.app` removed or explicitly replaced | blocked | Install did not proceed because no DMG artifact was available. |
| `Unknown Horizons.app` copies to `/Applications` | blocked | No mounted DMG app was available to copy. |
| App launched only from `/Applications/Unknown Horizons.app` | blocked | No installed candidate app was available to launch. |
| `Contents/MacOS/Unknown Horizons` exists | blocked | Installed app bundle was not created from a DMG candidate. |
| Launcher executable bit is set | blocked | Installed app bundle was not created from a DMG candidate. |
| `Contents/Resources/content/` exists | blocked | Installed app bundle was not created from a DMG candidate. |

## Runtime Validation

| Check | Result | Notes |
| --- | --- | --- |
| App launches from `/Applications` | blocked | No installed DMG candidate was available. |
| Process architecture is `arm64` | blocked | No app process was launched. |
| FIFE loads | blocked | No app process was launched. |
| FIFEChan loads | blocked | No app process was launched. |
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

- ENet installed: not checked
- Multiplayer smoke result: not tested
- Notes: Out of scope for this blocked installed-DMG smoke run.

## Pass/Fail Decision

The release candidate is blocked, not passed. This file records only the blocked
attempt and is not a completed release-gate report. A follow-up smoke run must
use a real `dist/Unknown-Horizons-<version>.dmg`, record its SHA-256, install it
to `/Applications`, verify native `arm64` runtime execution, and complete the
manual launch, settings, help or credits, singleplayer, settlement, road plus
building, save, relaunch, and load checks.

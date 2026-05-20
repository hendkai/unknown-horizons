# Apple-Silicon Smoke-Test Report

## Summary

- Release version:
- Result: pass / fail / blocked
- Tested at:
- Tester:
- Notes:

## Artifact

- DMG path: `dist/Unknown-Horizons-<version>.dmg`
- DMG SHA-256:
- App install path: `/Applications/Unknown Horizons.app`
- Existing `/Applications/Unknown Horizons.app` removed or explicitly replaced
  before launch: yes / no

## Host

- macOS version:
- Host architecture: arm64 / other:
- Python version used for build:
- FIFE/FIFEChan source or package:
- Test profile or `UH_USER_DIR`:

## Artifact Validation

| Check | Result | Notes |
| --- | --- | --- |
| DMG mounts successfully | pass / fail / blocked | |
| Existing `/Applications/Unknown Horizons.app` removed or explicitly replaced | pass / fail / blocked | |
| `Unknown Horizons.app` copies to `/Applications` | pass / fail / blocked | |
| App launched only from `/Applications/Unknown Horizons.app` | pass / fail / blocked | |
| `Contents/MacOS/Unknown Horizons` exists | pass / fail / blocked | |
| Launcher executable bit is set | pass / fail / blocked | |
| `Contents/Resources/content/` exists | pass / fail / blocked | |

## Runtime Validation

| Check | Result | Notes |
| --- | --- | --- |
| App launches from `/Applications` | pass / fail / blocked | |
| Process architecture is `arm64` | pass / fail / blocked | |
| FIFE loads | pass / fail / blocked | |
| FIFEChan loads | pass / fail / blocked | |
| No Python/FIFE/FIFEChan architecture mismatch warnings | pass / fail / blocked | |
| Main menu appears without missing content or asset errors | pass / fail / blocked | |

## Manual Flow

| Flow | Result | Notes |
| --- | --- | --- |
| Main menu visible and responsive | pass / fail / blocked | |
| Settings opens and closes | pass / fail / blocked | |
| Help or credits opens and closes | pass / fail / blocked | |
| Singleplayer game starts | pass / fail / blocked | |
| Settlement founded | pass / fail / blocked | |
| Road and one production or storage building placed | pass / fail / blocked | |
| Game saved | pass / fail / blocked | |
| App fully quit | pass / fail / blocked | |
| App relaunched from `/Applications` | pass / fail / blocked | |
| Saved game loaded after relaunch | pass / fail / blocked | |

## Optional Multiplayer

- ENet installed: yes / no
- Multiplayer smoke result: pass / fail / blocked / not tested
- Notes:

## Pass/Fail Decision

Mark the release candidate as `pass` only if every required artifact, runtime,
stale-app replacement, launch, settings, singleplayer, settlement, road plus
production or storage building placement, save, relaunch, and load check passes
from the installed `/Applications` app with `arm64` runtime validation.

Use `fail` for any verified runtime or manual-flow regression. Use `blocked`
when the DMG, hardware, native dependencies, or macOS GUI environment prevents
the smoke test from running.

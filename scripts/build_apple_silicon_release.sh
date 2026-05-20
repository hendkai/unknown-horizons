#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
FIFE_ROOT="${FIFE_ROOT:-}"
DIST_DIR="${DIST_DIR:-dist}"

log() {
	printf '==> %s\n' "$*"
}

fail() {
	printf 'ERROR: %s\n' "$*" >&2
	exit 1
}

require_command() {
	command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

log "Checking Apple Silicon host"
if [ "$(uname -s)" != "Darwin" ]; then
	fail "Apple Silicon release builds must run on macOS. Current OS: $(uname -s)"
fi
if [ "$(uname -m)" != "arm64" ]; then
	fail "Apple Silicon release builds must run on arm64, not $(uname -m). Use a native Apple Silicon runner/interpreter, not Rosetta."
fi

require_command "$PYTHON_BIN"
require_command git
require_command hdiutil
require_command shasum
require_command msgfmt

log "Checking Python interpreter architecture"
PYTHON_ARCH="$($PYTHON_BIN -c 'import platform; print(platform.machine())')"
PYTHON_EXE="$($PYTHON_BIN -c 'import sys; print(sys.executable)')"
log "Python: ${PYTHON_EXE} (${PYTHON_ARCH})"
if [ "$PYTHON_ARCH" != "arm64" ]; then
	fail "Python interpreter is ${PYTHON_ARCH}; expected native arm64."
fi

log "Checking Python build dependencies"
$PYTHON_BIN - <<'PY'
import importlib.util
import sys
missing = [name for name in ("py2app", "setuptools") if importlib.util.find_spec(name) is None]
if missing:
	print("Missing Python package(s): {}".format(", ".join(missing)), file=sys.stderr)
	sys.exit(1)
PY

if [ -n "$FIFE_ROOT" ]; then
	log "Using FIFE_ROOT=${FIFE_ROOT}"
	if [ ! -d "$FIFE_ROOT/engine/python/fife" ]; then
		fail "FIFE_ROOT must contain engine/python/fife, got: ${FIFE_ROOT}"
	fi
else
	log "Checking installed native FIFE bindings"
	$PYTHON_BIN - <<'PY'
from fife import fife
print("FIFE {}.{}.{}".format(
	fife.get_major() if hasattr(fife, "get_major") else "unknown",
	fife.get_minor() if hasattr(fife, "get_minor") else "unknown",
	fife.get_patch() if hasattr(fife, "get_patch") else "unknown",
))
PY
fi

log "Running macOS packaging unit tests"
$PYTHON_BIN -m pytest -q \
	tests/test_setup_arch.py \
	tests/test_setup_mac.py \
	tests/test_stage_build_mac.py \
	tests/test_build_dmg_mac.py

log "Building Unknown Horizons.app"
STAGE_ARGS=("stage_build_mac.py" "--verbose" "--python-bin" "$PYTHON_BIN")
if [ -n "$FIFE_ROOT" ]; then
	STAGE_ARGS+=("--fife-dir" "$FIFE_ROOT")
fi
$PYTHON_BIN "${STAGE_ARGS[@]}"

APP_PATH="${DIST_DIR}/Unknown Horizons.app"
EXECUTABLE_PATH="${APP_PATH}/Contents/MacOS/Unknown Horizons"
INFO_PLIST="${APP_PATH}/Contents/Info.plist"
[ -d "$APP_PATH" ] || fail "App bundle was not created: ${APP_PATH}"
[ -x "$EXECUTABLE_PATH" ] || fail "App launcher missing or not executable: ${EXECUTABLE_PATH}"
[ -f "$INFO_PLIST" ] || fail "Info.plist missing: ${INFO_PLIST}"

log "App bundle metadata"
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$INFO_PLIST"
/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$INFO_PLIST"
file "$EXECUTABLE_PATH"

log "Creating DMG"
$PYTHON_BIN build_dmg_mac.py --app-path "$APP_PATH" --dist-dir "$DIST_DIR"
DMG_PATH="$(/bin/ls -t "${DIST_DIR}"/Unknown-Horizons-*.dmg | head -n 1)"
[ -f "$DMG_PATH" ] || fail "No DMG artifact was created in ${DIST_DIR}"

log "Writing checksum"
shasum -a 256 "$DMG_PATH" | tee "${DMG_PATH}.sha256"

log "Apple Silicon release artifacts"
printf '%s\n%s\n' "$DMG_PATH" "${DMG_PATH}.sha256" | tee "${DIST_DIR}/apple-silicon-artifacts.txt"

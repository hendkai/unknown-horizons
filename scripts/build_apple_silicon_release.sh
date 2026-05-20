#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
FOCUSED_TESTS=(
	"tests/test_setup_arch.py"
	"tests/test_setup_mac.py"
	"tests/test_stage_build_mac.py"
	"tests/test_build_dmg_mac.py"
	"tests/test_launcher_macos.py"
)

fail() {
	printf 'error: %s\n' "$*" >&2
	exit 1
}

require_command() {
	command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

require_python_module() {
	"$PYTHON_BIN" -c "import $1" >/dev/null 2>&1 || fail "required Python module not importable: $1"
}

require_native_arm64_macos() {
	[[ "$(uname -s)" == "Darwin" ]] || fail "Apple-Silicon release builds must run on macOS"
	[[ "$(uname -m)" == "arm64" ]] || fail "Apple-Silicon release builds must run on a native arm64 host"

	local python_arch
	python_arch="$("$PYTHON_BIN" -c 'import platform; print(platform.machine())')"
	[[ "$python_arch" == "arm64" ]] || fail "Python must be a native arm64 interpreter, got: $python_arch"
}

require_release_tooling() {
	require_command git
	require_command hdiutil
	require_command shasum
	require_command msgfmt
	require_python_module py2app
	require_python_module setuptools
}

run_focused_tests() {
	"$PYTHON_BIN" -m pytest "${FOCUSED_TESTS[@]}"
}

build_release() {
	require_native_arm64_macos
	require_release_tooling

	if [[ -n "${FIFE_ROOT:-}" && ! -d "$FIFE_ROOT" ]]; then
		fail "FIFE_ROOT is set but does not exist: $FIFE_ROOT"
	fi

	run_focused_tests
	rm -f dist/*.dmg dist/*.sha256
	"$PYTHON_BIN" build_dmg_mac.py --build-app

	local dmg_files
	dmg_files=(dist/*.dmg)
	[[ -e "${dmg_files[0]}" ]] || fail "DMG was not created in dist/"
	[[ "${#dmg_files[@]}" -eq 1 ]] || fail "expected one DMG in dist/, found ${#dmg_files[@]}"
	shasum -a 256 "${dmg_files[0]}" > "${dmg_files[0]}.sha256"
}

case "${1:-}" in
	--test-only)
		run_focused_tests
		;;
	"")
		build_release
		;;
	*)
		fail "unknown argument: $1"
		;;
esac

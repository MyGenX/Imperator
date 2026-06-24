#!/usr/bin/env bash
set -e

REPO="${IMPERATOR_REPO:-https://github.com/MyGenX/Imperator}"
RAW_INSTALLER="${IMPERATOR_INSTALLER_URL:-https://raw.githubusercontent.com/MyGenX/Imperator/main/cli/imperator/installer.py}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "ERROR python3 or python is required." >&2
  exit 1
fi

SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/cli/imperator/installer.py" ]; then
  "$PYTHON" "$SCRIPT_DIR/cli/imperator/installer.py" "$@"
  exit $?
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR curl is required for remote installer bootstrap." >&2
  exit 1
fi

TMP_INSTALLER="$(mktemp)"
trap 'rm -f "$TMP_INSTALLER"' EXIT

curl -fsSL "$RAW_INSTALLER" -o "$TMP_INSTALLER"
IMPERATOR_REPO="$REPO" "$PYTHON" "$TMP_INSTALLER" "$@"

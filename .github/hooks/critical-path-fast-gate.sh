#!/usr/bin/env bash
set -euo pipefail

# Fast gate aligned with test-plan critical path risks (#1, #2, #5).
# Runs only when the edited file is in a critical area:
# - budget/
# - coinductor/templates/
# - static/css/

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

CHANGED_FILE="${1:-}"

if [[ -n "$CHANGED_FILE" ]]; then
  case "$CHANGED_FILE" in
    budget/*|coinductor/templates/*|static/css/*) ;;
    *)
      echo "quick-gate: skip (outside critical-path scope): $CHANGED_FILE"
      exit 0
      ;;
  esac
fi

PYTHON_BIN="./.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

echo "quick-gate: running critical-path tests (budget app)"
"$PYTHON_BIN" manage.py test budget --failfast --verbosity 0

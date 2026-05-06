#!/usr/bin/env bash
# Run backend unit tests (excludes live integration unless RUN_LIVE=1).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"
PY="./.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Create venv first: cd agri-ai && python3 -m venv backend/.venv && ./backend/.venv/bin/pip install -e 'backend[dev]'"
  exit 1
fi
"$PY" -m pip install -q -e ".[dev]" || true
if [[ "${RUN_LIVE:-}" == "1" ]]; then
  exec "$PY" -m pytest tests/ -v
fi
exec "$PY" -m pytest tests/ -v -m "not integration"

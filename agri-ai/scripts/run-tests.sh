#!/usr/bin/env bash
# Run backend unit tests (excludes live integration unless RUN_LIVE=1).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"
if [[ ! -x .venv/bin/python ]]; then
  echo "Creating backend/.venv …"
  python3 -m venv .venv
fi
PY="./.venv/bin/python"
"$PY" -m pip install -q -e ".[dev]"
if [[ "${RUN_LIVE:-}" == "1" ]]; then
  exec "$PY" -m pytest tests/ -v
fi
exec "$PY" -m pytest tests/ -v -m "not integration"

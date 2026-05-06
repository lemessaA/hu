#!/usr/bin/env bash
# Start FastAPI (8000) + Next.js (3000) in one terminal. Ctrl+C stops both.
# Uses backend/.venv/bin/python explicitly (avoids PEP 668 / wrong pip when conda is active).

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

VENV="${ROOT}/backend/.venv"
PY="${VENV}/bin/python"
PIP="${VENV}/bin/pip"

if [[ ! -x "$PY" ]]; then
  command -v python3 >/dev/null 2>&1 || {
    echo "python3 not found. Install Python 3.11+."
    exit 1
  }
  python3 -m venv "$VENV"
fi

"$PIP" install -q -e "${ROOT}/backend"

if [[ ! -d frontend/node_modules ]]; then
  (cd frontend && npm install)
fi

cleanup() {
  for pid in $(jobs -p); do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap cleanup INT TERM EXIT

(
  cd "${ROOT}/backend"
  exec "$PY" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &

(
  cd "${ROOT}/frontend"
  exec npm run dev
) &

wait || true

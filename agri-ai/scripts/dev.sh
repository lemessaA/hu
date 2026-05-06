#!/usr/bin/env bash
# Start FastAPI (8000) + Next.js (3000) in one terminal. Ctrl+C stops both.
# Requires: Python 3.11+, Node 20+, and Postgres + Redis reachable (see .env).

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ ! -d backend/.venv ]]; then
  python3 -m venv backend/.venv
fi
# shellcheck disable=SC1091
source backend/.venv/bin/activate
pip install -qe "${ROOT}/backend"

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
  exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &

(
  cd "${ROOT}/frontend"
  exec npm run dev
) &

wait || true

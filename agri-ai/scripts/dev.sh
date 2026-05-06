#!/usr/bin/env bash
# Start FastAPI (8000) + Next.js (3000) in one terminal. Ctrl+C stops both.
# Uses backend/.venv/bin/python explicitly (avoids PEP 668 / wrong pip when conda is active).

set -o pipefail

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

echo "Installing backend dependencies into .venv (wait for this to finish)..."
if ! "$PIP" install -e "${ROOT}/backend"; then
  echo "pip install failed. Fix errors above, then run npm run dev again."
  exit 1
fi

if ! "$PY" -c "import uvicorn" 2>/dev/null; then
  echo "uvicorn missing after install."
  exit 1
fi

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
BACK_PID=$!

api_ready() {
  "$PY" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()" >/dev/null 2>&1
}

wait_for_api() {
  local max=60
  local i=0
  echo "Waiting for API at http://127.0.0.1:8000/health ..."
  while (( i < max )); do
    if api_ready; then
      echo "API is up."
      return 0
    fi
    if ! kill -0 "$BACK_PID" 2>/dev/null; then
      echo "Backend exited before /health responded. Check Postgres (DATABASE_URL), Redis, and logs above."
      return 1
    fi
    ((i += 1)) || true
    sleep 1
  done
  echo "Timed out after ${max}s waiting for /health."
  echo "Tip: run Postgres + Redis (e.g. npm run deps:up) and set DATABASE_URL / REDIS_URL in .env"
  return 1
}

if ! wait_for_api; then
  exit 1
fi

(
  cd "${ROOT}/frontend"
  exec npm run dev
) &

wait || true

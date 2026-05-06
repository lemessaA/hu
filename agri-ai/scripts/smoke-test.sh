#!/usr/bin/env bash
# Smoke-test a running API at LIVE_API_BASE (default http://127.0.0.1:8000).
# Usage: source ../.env 2>/dev/null; ./scripts/smoke-test.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi
BASE="${LIVE_API_BASE:-http://127.0.0.1:8000}"
KEY="${API_KEY:-}"

echo "== GET $BASE/health"
curl -sf "$BASE/health" | head -c 400 || {
  echo "FAIL: health"
  exit 1
}
echo ""
echo OK health

HDR=()
if [[ -n "$KEY" ]]; then
  HDR=(-H "X-API-Key: $KEY")
fi

echo "== POST $BASE/chat"
curl -sf "${HDR[@]}" -H "Content-Type: application/json" \
  -d '{"message":"Smoke test: weather in Jimma?","location":"Jimma","session_id":"smoke"}' \
  "$BASE/chat" | head -c 600 || {
  echo "FAIL: chat"
  exit 1
}
echo ""
echo OK chat

echo "== GET $BASE/advice/recent"
curl -sf "${HDR[@]}" "$BASE/advice/recent" | head -c 400 || {
  echo "FAIL: advice"
  exit 1
}
echo ""
echo OK advice

PNG="$ROOT/backend/tests/fixtures/minimal.png"
if [[ ! -f "$PNG" ]]; then
  echo "SKIP analyze-image (no fixture)"
  exit 0
fi
echo "== POST $BASE/analyze-image"
curl -sf "${HDR[@]}" -F "file=@$PNG" "$BASE/analyze-image" | head -c 400 || {
  echo "FAIL: analyze-image"
  exit 1
}
echo ""
echo OK analyze-image
echo "All smoke checks passed."

#!/usr/bin/env bash
# Smoke-test a running API at LIVE_API_BASE (default http://127.0.0.1:8000).
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

TMPPNG=$(mktemp /tmp/agri-smoke-XXXXXX.png)
trap 'rm -f "$TMPPNG"' EXIT
PYTHON=python3
if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  PYTHON="$ROOT/backend/.venv/bin/python"
fi
"$PYTHON" - <<PY
from pathlib import Path
p = Path("$TMPPNG")
p.write_bytes(
    bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
        "0000000c49444154789c63f80f00000101000518d84e0000000049454e44ae426082"
    )
)
PY

echo "== GET $BASE/health"
curl -sf "$BASE/health" | head -c 400
echo ""
echo OK health

HDR=()
if [[ -n "$KEY" ]]; then
  HDR=(-H "X-API-Key: $KEY")
fi

echo "== POST $BASE/chat"
curl -sf "${HDR[@]}" -H "Content-Type: application/json" \
  -d '{"message":"Smoke test: weather in Jimma?","location":"Jimma","session_id":"smoke"}' \
  "$BASE/chat" | head -c 600
echo ""
echo OK chat

echo "== GET $BASE/advice/recent"
curl -sf "${HDR[@]}" "$BASE/advice/recent" | head -c 400
echo ""
echo OK advice

echo "== POST $BASE/analyze-image"
curl -sf "${HDR[@]}" -F "file=@$TMPPNG" "$BASE/analyze-image" | head -c 400
echo ""
echo OK analyze-image
echo "All smoke checks passed."

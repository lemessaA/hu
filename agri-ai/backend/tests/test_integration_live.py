"""Optional live checks against a running uvicorn (RUN_LIVE=1)."""
import os

import httpx
import pytest

BASE = os.environ.get("LIVE_API_BASE", "http://127.0.0.1:8000")
KEY = os.environ.get("API_KEY", "").strip()


@pytest.mark.integration
def test_live_health():
    if os.environ.get("RUN_LIVE") != "1":
        pytest.skip("Set RUN_LIVE=1 to run integration tests")
    r = httpx.get(f"{BASE}/health", timeout=10.0)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") in ("ok", "degraded")


@pytest.mark.integration
def test_live_chat_with_key():
    if os.environ.get("RUN_LIVE") != "1":
        pytest.skip("Set RUN_LIVE=1 to run integration tests")
    if not KEY:
        pytest.skip("Set API_KEY in env for api_key mode tests")
    r = httpx.post(
        f"{BASE}/chat",
        json={
            "message": "Hello — integration test",
            "session_id": "pytest-live",
        },
        headers={"X-API-Key": KEY, "Content-Type": "application/json"},
        timeout=120.0,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "reply" in data
    assert data["reply"]


@pytest.mark.integration
def test_live_analyze_image():
    if os.environ.get("RUN_LIVE") != "1":
        pytest.skip("Set RUN_LIVE=1 to run integration tests")
    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("t.png", png, "image/png")}
    headers = {}
    if KEY:
        headers["X-API-Key"] = KEY
    r = httpx.post(f"{BASE}/analyze-image", files=files, headers=headers, timeout=30.0)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("disease")

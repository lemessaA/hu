"""Auth middleware behaviour (no running server)."""
import asyncio

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.config import get_settings
from app.middleware.auth import verify_api_key


def _request(client: tuple[str, int] | None, headers: list[tuple[bytes, bytes]] | None = None):
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/chat",
            "headers": headers or [],
            "client": client,
        }
    )


def test_auth_mode_none_always_ok(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "none")
    monkeypatch.setenv("ENVIRONMENT", "development")
    get_settings.cache_clear()
    req = _request(("8.8.8.8", 80))
    asyncio.run(verify_api_key(req))


def test_trusted_host_public_ip_forbidden(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "trusted_host")
    monkeypatch.setenv("ENVIRONMENT", "development")
    get_settings.cache_clear()
    req = _request(("8.8.8.8", 80))
    with pytest.raises(HTTPException) as ei:
        asyncio.run(verify_api_key(req))
    assert ei.value.status_code == 403


def test_trusted_host_loopback_ok(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "trusted_host")
    get_settings.cache_clear()
    req = _request(("127.0.0.1", 5555))
    asyncio.run(verify_api_key(req))


def test_api_key_mode_requires_header(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "api_key")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("API_KEY", "secret-test-key")
    get_settings.cache_clear()
    req = _request(("127.0.0.1", 5555))
    with pytest.raises(HTTPException) as ei:
        asyncio.run(verify_api_key(req))
    assert ei.value.status_code == 401


def test_api_key_mode_valid_header(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "api_key")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("API_KEY", "secret-test-key")
    get_settings.cache_clear()
    hdrs = [(b"x-api-key", b"secret-test-key")]
    req = _request(("127.0.0.1", 5555), hdrs)
    asyncio.run(verify_api_key(req))

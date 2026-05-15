"""API protection: API key (default), disabled, or trusted-network only."""
from __future__ import annotations

from fastapi import HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE

from app.config import get_settings


def _is_trusted_host(host: str | None) -> bool:
    """Loopback and private LAN ranges (RFC1918). Not for public internet exposure."""
    if not host:
        return False
    if host in ("127.0.0.1", "::1", "localhost"):
        return True
    if host.startswith("10."):
        return True
    if host.startswith("192.168."):
        return True
    if host.startswith("172."):
        parts = host.split(".")
        if len(parts) >= 2 and parts[0] == "172":
            try:
                second = int(parts[1])
                if 16 <= second <= 31:
                    return True
            except ValueError:
                pass
    return False


async def verify_api_key(request: Request) -> None:
    settings = get_settings()

    if settings.auth_mode == "none":
        return

    if settings.auth_mode == "trusted_host":
        host = request.client.host if request.client else None
        if _is_trusted_host(host):
            return
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Forbidden: client address is not in the trusted network (use loopback or private LAN)",
        )

    # --- api_key mode ---
    if settings.environment != "production" and not settings.api_key:
        return
    if not settings.api_key:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY is not configured (set AUTH_MODE=trusted_host or none for dev)",
        )
    key = request.headers.get("x-api-key")
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        key = auth.split(" ", 1)[1].strip()
    if key != settings.api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

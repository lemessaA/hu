"""API key guard — X-API-Key or Authorization: Bearer."""
from fastapi import HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_503_SERVICE_UNAVAILABLE

from app.config import get_settings


async def verify_api_key(request: Request) -> None:
    settings = get_settings()
    if settings.environment != "production" and not settings.api_key:
        return
    if not settings.api_key:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY is not configured",
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

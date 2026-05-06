"""AgriClimate AI Agent — FastAPI entrypoint."""
import logging
from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.middleware.logging import RequestLoggingMiddleware
from app.models import crop_model
from app.routes import advice, chat, image

settings = get_settings()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    crop_model.load_model()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(image.router)
app.include_router(advice.router)


@app.get("/health")
async def health():
    """Liveness + dependency checks (no API key)."""
    status = {"status": "ok", "service": "agriclimate-backend"}
    try:
        from sqlalchemy import text

        from app.db import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["postgres"] = "ok"
    except Exception as e:  # noqa: BLE001
        status["postgres"] = f"error: {e}"
        status["status"] = "degraded"

    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        status["redis"] = "ok"
        r.close()
    except Exception as e:  # noqa: BLE001
        status["redis"] = f"error: {e}"
        status["status"] = "degraded"

    return status

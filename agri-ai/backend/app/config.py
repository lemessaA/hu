"""
Application configuration (12-factor via environment variables).
"""
from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Tuple

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py → repo root is parents[2]; backend/.env is parents[1]/.env
_CONFIG_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _CONFIG_DIR.parent
_REPO_ROOT = _BACKEND_DIR.parent


def _env_file_paths() -> Tuple[str, ...]:
    """Prefer repo-root `.env` (monorepo dev), then `backend/.env` overrides."""
    paths: List[str] = []
    root_env = _REPO_ROOT / ".env"
    backend_env = _BACKEND_DIR / ".env"
    if root_env.is_file():
        paths.append(str(root_env))
    if backend_env.is_file():
        paths.append(str(backend_env))
    return tuple(paths) if paths else (".env",)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file_paths(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AgriClimate AI Agent"
    environment: str = "development"
    api_key: str = ""  # Used when auth_mode is api_key

    # api_key — shared secret header (default). none — no auth (dev only).
    # trusted_host — allow loopback + private RFC1918 / Docker bridge (no secret).
    auth_mode: Literal["api_key", "none", "trusted_host"] = "api_key"

    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/agriclimate"
    )
    redis_url: str = "redis://localhost:6379/0"

    # Primary LLM: Groq (fast inference; OpenAI-compatible API shape via LangChain)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Optional fallback: any OpenAI-compatible HTTP API (OpenAI, vLLM, etc.)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    cors_origins: str = "http://localhost:3000"

    # Weather API (optional). If unset, service returns deterministic demo data.
    openweather_api_key: str = ""

    memory_window: int = 5

    @field_validator("api_key", mode="before")
    @classmethod
    def strip_api_key(cls, v: object) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            s = s[1:-1].strip()
        return s

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

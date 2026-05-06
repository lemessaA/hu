"""
Application configuration (12-factor via environment variables).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AgriClimate AI Agent"
    environment: str = "development"
    api_key: str = ""  # If empty in dev, auth middleware can allow local traffic

    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/agriclimate"
    )
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI-compatible endpoint (OpenAI, Azure OpenAI, vLLM, Ollama w/ openai plugin, etc.)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    cors_origins: str = "http://localhost:3000"

    # Weather API (optional). If unset, service returns deterministic demo data.
    openweather_api_key: str = ""

    memory_window: int = 5

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

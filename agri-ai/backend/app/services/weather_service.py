"""
Weather data with Redis caching.
"""
import hashlib
import json
import logging
from typing import Any, Dict, Optional

import httpx
import redis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

CACHE_TTL_SECONDS = 30 * 60  # 30 minutes


def _redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def _cache_key(location: str) -> str:
    h = hashlib.sha256(location.strip().lower().encode()).hexdigest()[:32]
    return f"agri:weather:{h}"


def _demo_weather(location: str) -> Dict[str, Any]:
    """Deterministic demo payload when no external API key is configured."""
    return {
        "location": location or "Ethiopia (general)",
        "temperature_c": 24,
        "rainfall_forecast_mm_next_7d": 18,
        "humidity_percent": 62,
        "summary": "Moderate temperatures with light to moderate rain expected this week.",
        "source": "demo",
    }


def get_weather(location: Optional[str]) -> Dict[str, Any]:
    """
    Fetch weather for a location. Uses OpenWeatherMap if OPENWEATHER_API_KEY is set,
    otherwise returns conference-safe demo data. Results are cached in Redis.
    """
    loc = (location or "Addis Ababa, ET").strip()
    rkey = _cache_key(loc)
    try:
        r = _redis()
        cached = r.get(rkey)
        if cached:
            return json.loads(cached)
    except Exception as e:  # noqa: BLE001
        logger.warning("Redis cache read skipped: %s", e)

    data: Dict[str, Any]
    if settings.openweather_api_key:
        try:
            data = _fetch_openweather(loc)
        except Exception as e:  # noqa: BLE001
            logger.warning("OpenWeather fetch failed: %s", e)
            data = _demo_weather(loc)
            data["source"] = "fallback_demo"
    else:
        data = _demo_weather(loc)

    try:
        r = _redis()
        r.setex(rkey, CACHE_TTL_SECONDS, json.dumps(data))
    except Exception as e:  # noqa: BLE001
        logger.warning("Redis cache write skipped: %s", e)
    return data


def _fetch_openweather(location: str) -> Dict[str, Any]:
    """Minimal current weather + simple rain heuristic from OpenWeatherMap."""
    with httpx.Client(timeout=10.0) as client:
        geo = client.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params={"q": location, "limit": 1, "appid": settings.openweather_api_key},
        )
        geo.raise_for_status()
        g = geo.json()
        if not g:
            return _demo_weather(location)
        lat, lon = g[0]["lat"], g[0]["lon"]

        cur = client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": settings.openweather_api_key,
                "units": "metric",
            },
        )
        cur.raise_for_status()
        w = cur.json()
        temp = w["main"]["temp"]
        humidity = w["main"]["humidity"]

        fc = client.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": settings.openweather_api_key,
                "units": "metric",
                "cnt": 8,
            },
        )
        fc.raise_for_status()
        rain_mm = 0.0
        for item in fc.json().get("list", [])[:8]:
            if "rain" in item:
                rain_mm += float(item["rain"].get("3h", 0) or 0)

        return {
            "location": location,
            "temperature_c": round(temp, 1),
            "rainfall_forecast_mm_next_7d": round(rain_mm * 7 / 8, 1),
            "humidity_percent": humidity,
            "summary": w["weather"][0]["description"] if w.get("weather") else "",
            "source": "openweathermap",
        }

"""Weather tool node — populates state.weather_data."""
from __future__ import annotations

import logging
from typing import Any, Dict

from app.agent.nodes.intent import AgentState
from app.services import weather_service

logger = logging.getLogger(__name__)


def weather_node(state: AgentState) -> Dict[str, Any]:
    if not state.get("needs_weather"):
        return {"weather_data": None}
    loc = state.get("location")
    try:
        data = weather_service.get_weather(loc)
    except Exception as e:  # noqa: BLE001
        logger.exception("Weather node failure: %s", e)
        data = {
            "location": loc or "unknown",
            "error": str(e),
            "source": "error",
        }
    return {"weather_data": data}

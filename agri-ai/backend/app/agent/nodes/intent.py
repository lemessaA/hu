"""LangGraph agent nodes — intent, tools, knowledge, reasoning."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypedDict

from app.agent.prompt import SYSTEM_PROMPT
from app.config import get_settings
from app.models import crop_model
from app.services import weather_service

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentState(TypedDict, total=False):
    user_input: str
    location: Optional[str]
    session_id: str
    image_bytes: Optional[bytes]
    crop_result: Optional[Dict[str, Any]]
    chat_history: List[Dict[str, Any]]
    intent: str
    needs_weather: bool
    needs_crop: bool
    needs_knowledge: bool
    weather_data: Optional[Dict[str, Any]]
    knowledge_context: Optional[str]
    final_response: str


WEATHER_KEYWORDS = [
    "rain",
    "rainfall",
    "weather",
    "temperature",
    "humid",
    "forecast",
    "climate",
    "cloud",
    "storm",
    "drought",
    "ዝናብ",
    "አየር",
]
CROP_KEYWORDS = [
    "leaf",
    "disease",
    "pest",
    "blight",
    "rust",
    "crop",
    "teff",
    "maize",
    "wheat",
    "barley",
    "coffee",
    "enset",
    "ሰብል",
    "በሽታ",
]


def intent_node(state: AgentState) -> Dict[str, Any]:
    """
    Detect which tools should run. Routing rules:
    - Weather tool if message mentions weather OR a location is supplied.
    - Crop analysis if an image is present, client supplied crop_result, or crop/disease keywords.
    - Knowledge base always adds light Ethiopia context for reasoning quality.
    """
    text = state.get("user_input", "").lower()
    loc = (state.get("location") or "").strip()

    mentions_weather = any(k in text for k in WEATHER_KEYWORDS)
    needs_weather = bool(loc) or mentions_weather

    has_image = bool(state.get("image_bytes"))
    has_prior_crop = bool(state.get("crop_result"))
    mentions_crop = any(k in text for k in CROP_KEYWORDS)
    needs_crop = has_image or has_prior_crop or mentions_crop

    needs_knowledge = True

    if needs_weather and needs_crop:
        intent = "mixed"
    elif needs_weather:
        intent = "weather"
    elif needs_crop:
        intent = "crop"
    else:
        intent = "general"

    return {
        "needs_weather": needs_weather,
        "needs_crop": needs_crop,
        "needs_knowledge": needs_knowledge,
        "intent": intent,
    }

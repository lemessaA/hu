"""
LangChain tool wrappers (optional composition with agents).
Nodes call services directly for clarity; tools are exposed for testing/extension.
"""
from typing import Any, Dict, Optional

from langchain_core.tools import tool

from app.models import crop_model
from app.services import weather_service


@tool
def weather_tool(location: str) -> Dict[str, Any]:
    """Get temperature, rainfall forecast, and humidity for a location."""
    return weather_service.get_weather(location)


@tool
def crop_tool_from_bytes_placeholder() -> Dict[str, Any]:
    """Placeholder tool — real pipeline uses uploaded image bytes in API layer."""
    return {"error": "Use /analyze-image with multipart file."}


def analyze_crop_image(image_bytes: bytes) -> Dict[str, Any]:
    """Non-tool helper used by graph nodes."""
    return crop_model.predict(image_bytes)

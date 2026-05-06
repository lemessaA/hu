"""
Translation helpers (UI-focused; optional LLM hook for future).
For conference demo, Amharic UI is handled on the frontend; this service
can wrap an external translation API later.
"""
import logging
from typing import Literal

logger = logging.getLogger(__name__)

Locale = Literal["en", "am"]


def translate_hint(text: str, target: Locale) -> str:
    """
    Placeholder: returns English text unchanged.
    Wire to a translation model or API when available.
    """
    if target == "am":
        logger.debug("Translation to Amharic requested (placeholder): %s", text[:80])
    return text

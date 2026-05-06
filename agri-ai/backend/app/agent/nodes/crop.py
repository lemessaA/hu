"""Crop analysis node — runs PyTorch-backed mock classifier when bytes exist."""
from __future__ import annotations

import logging
from typing import Any, Dict

from app.agent.nodes.intent import AgentState
from app.models import crop_model

logger = logging.getLogger(__name__)


def crop_node(state: AgentState) -> Dict[str, Any]:
    if not state.get("needs_crop"):
        return {}
    prior = state.get("crop_result")
    if prior:
        return {"crop_result": prior}
    image_bytes = state.get("image_bytes")
    if image_bytes:
        try:
            result = crop_model.predict(image_bytes)
            return {"crop_result": result}
        except Exception as e:  # noqa: BLE001
            logger.exception("Crop node failure: %s", e)
            return {"crop_result": {"error": str(e)}}
    # Keywords suggested crop topic but no image/analysis yet
    return {
        "crop_result": {
            "note": "No leaf photo uploaded yet. Use image upload for disease check.",
        }
    }

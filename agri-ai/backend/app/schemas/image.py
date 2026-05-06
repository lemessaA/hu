"""Pydantic schemas for image analysis API."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ImageAnalysisResponse(BaseModel):
    disease: str
    confidence: float = Field(ge=0.0, le=1.0)
    treatment: str
    notes: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

"""Pydantic schemas for chat API."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    location: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Farmer location for weather (e.g. Addis Ababa, Oromia)",
    )
    session_id: str = Field(
        default="default",
        max_length=64,
        description="Client session id for Redis short-term memory",
    )
    user_id: Optional[str] = Field(default=None, max_length=128)
    # Optional crop analysis from prior POST /analyze-image
    crop_result: Optional[Dict[str, Any]] = None
    stream: bool = False

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    intent: Optional[str] = None
    weather_data: Optional[Dict[str, Any]] = None
    crop_result: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    created_at: str


class RecentAdviceResponse(BaseModel):
    items: List[ChatHistoryItem]

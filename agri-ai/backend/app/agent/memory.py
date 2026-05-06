"""
Redis-backed short-term chat memory (last N turns) for agent context.
"""
import json
from typing import Any, Dict, List

import redis

from app.config import get_settings

settings = get_settings()


def _client() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def memory_key(session_id: str) -> str:
    return f"agri:memory:{session_id}"


def get_short_term_messages(session_id: str) -> List[Dict[str, Any]]:
    """Return last messages as list of {role, content}."""
    r = _client()
    raw = r.lrange(memory_key(session_id), 0, -1)
    return [json.loads(x) for x in raw]


def append_message(session_id: str, role: str, content: str) -> None:
    """Append a message and trim to memory_window."""
    r = _client()
    key = memory_key(session_id)
    payload = json.dumps({"role": role, "content": content})
    pipe = r.pipeline()
    pipe.rpush(key, payload)
    pipe.ltrim(key, -settings.memory_window, -1)
    pipe.execute()


def clear_session(session_id: str) -> None:
    _client().delete(memory_key(session_id))

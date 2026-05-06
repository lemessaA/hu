"""Persist chat turns to PostgreSQL."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db_models.chat_history import ChatHistory
from app.db_models.user import User


def get_or_create_user(session: Session, external_id: Optional[str]) -> Optional[uuid.UUID]:
    if not external_id:
        return None
    row = session.execute(select(User).where(User.external_id == external_id)).scalar_one_or_none()
    if row:
        return row.id
    u = User(external_id=external_id, display_name=external_id)
    session.add(u)
    session.flush()
    return u.id


def save_message(
    session: Session,
    *,
    session_id: str,
    role: str,
    content: str,
    user_id: Optional[uuid.UUID] = None,
) -> ChatHistory:
    row = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        created_at=datetime.now(timezone.utc),
    )
    session.add(row)
    session.flush()
    return row


def recent_assistant_messages(session: Session, limit: int = 20) -> List[ChatHistory]:
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.role == "assistant")
        .order_by(desc(ChatHistory.created_at))
        .limit(limit)
    )
    return list(session.execute(stmt).scalars().all())

"""Dashboard: recent assistant advice."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.auth import verify_api_key
from app.repositories import chat_repo
from app.schemas.chat import ChatHistoryItem, RecentAdviceResponse

router = APIRouter(tags=["advice"])


@router.get("/advice/recent", response_model=RecentAdviceResponse)
async def recent_advice(
    _auth: None = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    rows = chat_repo.recent_assistant_messages(db, limit=25)
    items = [
        ChatHistoryItem(
            role=r.role,
            content=r.content,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in rows
    ]
    return RecentAdviceResponse(items=items)

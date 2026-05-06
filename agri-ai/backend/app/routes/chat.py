"""Chat and advice endpoints."""
import json
import logging
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agent import memory as memory_service
from app.agent.graph import build_graph
from app.db import get_db
from app.middleware.auth import verify_api_key
from app.repositories import chat_repo
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    request: Request,
    payload: ChatRequest,
    _auth: None = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Run the LangGraph agent pipeline and persist messages."""
    history = memory_service.get_short_term_messages(payload.session_id)
    graph = build_graph()
    state = {
        "user_input": payload.message,
        "location": payload.location,
        "session_id": payload.session_id,
        "image_bytes": None,
        "crop_result": payload.crop_result,
        "chat_history": history,
    }
    user_uuid = chat_repo.get_or_create_user(db, payload.user_id)
    chat_repo.save_message(
        db,
        session_id=payload.session_id,
        role="user",
        content=payload.message,
        user_id=user_uuid,
    )

    if payload.stream:
        raise HTTPException(status_code=400, detail="Use /chat/stream for streaming")

    result = graph.invoke(state)
    reply = result.get("final_response") or ""

    memory_service.append_message(payload.session_id, "user", payload.message)
    memory_service.append_message(payload.session_id, "assistant", reply)

    chat_repo.save_message(
        db,
        session_id=payload.session_id,
        role="assistant",
        content=reply,
        user_id=user_uuid,
    )

    return ChatResponse(
        reply=reply,
        session_id=payload.session_id,
        intent=result.get("intent"),
        weather_data=result.get("weather_data"),
        crop_result=result.get("crop_result"),
        meta={"request_id": getattr(request.state, "request_id", None)},
    )


async def _stream_text(text: str) -> AsyncGenerator[bytes, None]:
    """Chunk UTF-8 text for demo-friendly streaming."""
    chunk_size = 48
    for i in range(0, len(text), chunk_size):
        part = text[i : i + chunk_size]
        yield f"data: {json.dumps({'token': part})}\n\n".encode("utf-8")
    yield f"data: {json.dumps({'done': True})}\n\n".encode("utf-8")


@router.post("/chat/stream")
async def post_chat_stream(
    request: Request,
    payload: ChatRequest,
    _auth: None = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Server-Sent Events style stream after full graph completion (conference-stable)."""
    history = memory_service.get_short_term_messages(payload.session_id)
    graph = build_graph()
    state = {
        "user_input": payload.message,
        "location": payload.location,
        "session_id": payload.session_id,
        "image_bytes": None,
        "crop_result": payload.crop_result,
        "chat_history": history,
    }
    user_uuid = chat_repo.get_or_create_user(db, payload.user_id)
    chat_repo.save_message(
        db,
        session_id=payload.session_id,
        role="user",
        content=payload.message,
        user_id=user_uuid,
    )

    result = graph.invoke(state)
    reply = result.get("final_response") or ""

    memory_service.append_message(payload.session_id, "user", payload.message)
    memory_service.append_message(payload.session_id, "assistant", reply)

    chat_repo.save_message(
        db,
        session_id=payload.session_id,
        role="assistant",
        content=reply,
        user_id=user_uuid,
    )

    meta = {
        "intent": result.get("intent"),
        "weather_data": result.get("weather_data"),
        "crop_result": result.get("crop_result"),
        "session_id": payload.session_id,
        "request_id": getattr(request.state, "request_id", None),
    }
    preamble = f"data: {json.dumps({'meta': meta})}\n\n".encode("utf-8")

    async def gen():
        yield preamble
        async for chunk in _stream_text(reply):
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/chat/multipart", response_model=ChatResponse)
async def post_chat_multipart(
    request: Request,
    message: str = Form(...),
    location: Optional[str] = Form(None),
    session_id: str = Form("default"),
    user_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    _auth: None = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Same as /chat but accepts an optional image for the crop node."""
    raw: Optional[bytes] = None
    if image is not None:
        if image.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
            raise HTTPException(400, "Unsupported image type")
        raw = await image.read()
        if not raw or len(raw) > 5 * 1024 * 1024:
            raise HTTPException(400, "Invalid or too large image")

    history = memory_service.get_short_term_messages(session_id)
    graph = build_graph()
    state = {
        "user_input": message.strip(),
        "location": location,
        "session_id": session_id,
        "image_bytes": raw,
        "crop_result": None,
        "chat_history": history,
    }
    user_uuid = chat_repo.get_or_create_user(db, user_id)
    chat_repo.save_message(
        db, session_id=session_id, role="user", content=message.strip(), user_id=user_uuid
    )

    result = graph.invoke(state)
    reply = result.get("final_response") or ""

    memory_service.append_message(session_id, "user", message.strip())
    memory_service.append_message(session_id, "assistant", reply)

    chat_repo.save_message(
        db, session_id=session_id, role="assistant", content=reply, user_id=user_uuid
    )

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        intent=result.get("intent"),
        weather_data=result.get("weather_data"),
        crop_result=result.get("crop_result"),
        meta={"request_id": getattr(request.state, "request_id", None)},
    )


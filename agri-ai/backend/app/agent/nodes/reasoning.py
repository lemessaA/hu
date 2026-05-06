"""Reasoning node — Groq LLM (default) or OpenAI-compatible fallback."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.agent.nodes.intent import AgentState
from app.agent.prompt import SYSTEM_PROMPT
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _history_to_lc(history: List[Dict[str, Any]]) -> List[Any]:
    msgs: List[Any] = []
    for m in history:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            msgs.append(AIMessage(content=content))
    return msgs[-10:]


def reasoning_node(state: AgentState) -> Dict[str, Any]:
    user_q = state.get("user_input", "")
    weather = state.get("weather_data")
    crop = state.get("crop_result")
    kb = state.get("knowledge_context") or ""
    history = state.get("chat_history") or []

    context_blob = {
        "weather_data": weather,
        "crop_analysis": crop,
        "knowledge_base_excerpt": kb,
    }
    context_str = json.dumps(context_blob, ensure_ascii=False, indent=2)

    if not settings.groq_api_key and not settings.openai_api_key:
        # Offline / conference-safe fallback
        lines = [
            "Problem:",
            f"- Farmer question: {user_q}",
            "",
            "Insight:",
            "- Demo mode (set GROQ_API_KEY or OPENAI_API_KEY). Below is a structured summary from tools.",
            f"- Context: {context_str}",
            "",
            "Action Steps:",
            "- Share a clear photo of affected leaves if disease is suspected.",
            "- Match planting and irrigation to upcoming rainfall when possible.",
            "- Ask your local extension worker to confirm before buying chemicals.",
        ]
        return {"final_response": "\n".join(lines)}

    try:
        llm: BaseChatModel
        if settings.groq_api_key:
            # `api_key` / `model` match current langchain_groq.ChatGroq (alias of groq_api_key / model_name)
            llm = ChatGroq(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                temperature=0.4,
            )
        else:
            llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                model=settings.openai_model,
                temperature=0.4,
            )
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *_history_to_lc(history),
            HumanMessage(
                content=(
                    f"Farmer message:\n{user_q}\n\n"
                    f"Structured tool context (JSON):\n{context_str}\n\n"
                    "Respond in the required format (Problem / Insight / Action Steps)."
                )
            ),
        ]
        resp = llm.invoke(messages)
        text = getattr(resp, "content", None) or str(resp)
        return {"final_response": text.strip()}
    except Exception as e:  # noqa: BLE001
        logger.exception("Reasoning failure: %s", e)
        return {
            "final_response": (
                "Problem:\n- Could not reach the AI model.\n\n"
                "Insight:\n- Please try again shortly.\n\n"
                "Action Steps:\n- Check connectivity; if offline, contact extension support.\n"
                f"Details: {e}"
            )
        }

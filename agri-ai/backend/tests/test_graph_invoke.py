"""LangGraph compiles (imports heavy deps)."""
from app.config import get_settings
from app.agent.graph import build_graph, reset_graph_cache


def test_langgraph_compiles(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    reset_graph_cache()
    g = build_graph()
    assert g is not None
    out = g.invoke(
        {
            "user_input": "What is mulch?",
            "location": None,
            "session_id": "pytest-graph",
            "image_bytes": None,
            "crop_result": None,
            "chat_history": [],
        }
    )
    assert "final_response" in out
    assert len(out["final_response"]) > 10

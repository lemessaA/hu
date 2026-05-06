"""
LangGraph assembly: intent → weather → crop → knowledge → reasoning → END
"""
try:
    from langgraph.graph import END, START, StateGraph
except ImportError:  # pragma: no cover
    from langgraph.graph import END, StateGraph

    START = "__start__"  # type: ignore[misc,assignment]

from app.agent.nodes.crop import crop_node
from app.agent.nodes.intent import AgentState, intent_node
from app.agent.nodes.knowledge import knowledge_node
from app.agent.nodes.reasoning import reasoning_node
from app.agent.nodes.weather import weather_node

_compiled = None


def build_graph():
    """Compile once (lazy singleton for uvicorn reload)."""
    global _compiled
    if _compiled is not None:
        return _compiled

    workflow = StateGraph(AgentState)
    workflow.add_node("intent", intent_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("crop", crop_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("reasoning", reasoning_node)

    workflow.add_edge(START, "intent")
    workflow.add_edge("intent", "weather")
    workflow.add_edge("weather", "crop")
    workflow.add_edge("crop", "knowledge")
    workflow.add_edge("knowledge", "reasoning")
    workflow.add_edge("reasoning", END)

    _compiled = workflow.compile()
    return _compiled


def reset_graph_cache() -> None:
    """Test hook."""
    global _compiled
    _compiled = None

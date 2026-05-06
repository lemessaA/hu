"""Knowledge base node — curated Ethiopia / CSA snippets (replace with vector DB later)."""
from __future__ import annotations

from typing import Any, Dict

from app.agent.nodes.intent import AgentState

KB_SNIPPETS = """
- Teff and maize are widely grown; timing planting with the belg/kiremt rains reduces water stress.
- Conservation agriculture (minimum tillage, mulch) helps soils hold moisture during dry spells.
- Rotate crops and remove infected plant debris to slow disease spread.
- For smallholders, low-cost actions (mulch, shade, timely weeding) often beat expensive inputs.
- If symptoms look severe, contact local extension with clear photos of leaves and stems.
"""


def knowledge_node(state: AgentState) -> Dict[str, Any]:
    if not state.get("needs_knowledge"):
        return {"knowledge_context": ""}
    return {"knowledge_context": KB_SNIPPETS.strip()}

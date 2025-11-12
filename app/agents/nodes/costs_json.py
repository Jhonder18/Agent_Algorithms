# app/agents/nodes/costs_json.py
from __future__ import annotations
from typing import TypedDict, Dict, Any
from app.services.llm import llm_json_call

class AgentState(TypedDict, total=False):
    ast: Dict[str, Any]
    costs: Dict[str, Any]

COSTS_SYS = """
Eres un analista de costos. A partir del AST (shape dado), devuelve JSON:

{
  "per_node": [ { "node_id": "...", "node_type":"...", "line_start": int|null, "line_end": int|null,
                  "code_snippet": str|null,
                  "cost": {"best": str, "avg": str, "worst": str},
                  "own_cost": {"best": str, "avg": str, "worst": str} | null,
                  "execution_count": null,
                  "loop_info": null | {"var": str, "start": str, "end": str} } ... ],
  "per_line": [ { "line_number": int, "code": str, "operations": [str,...],
                  "cost": {"best": str, "avg": str, "worst": str} } ... ],
  "total": { "best": str, "avg": str, "worst": str }
}

Usa notación simbólica con Sum(...) donde aplique.
Devuelve SOLO JSON válido.
"""

def costs_node(state: AgentState) -> Dict:
    ast_json = state.get("ast") or {}
    user = f"AST JSON:\n{ast_json}"
    data = llm_json_call(COSTS_SYS, user, temperature=0)
    return {"costs": data}

__all__ = ["costs_node"]

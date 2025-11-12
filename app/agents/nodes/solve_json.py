# app/agents/nodes/solve_json.py
from __future__ import annotations
from typing import TypedDict, Dict, Any
from app.services.llm import llm_json_call

class AgentState(TypedDict, total=False):
    input_text: str
    pseudocode: str
    validation: Dict[str, Any]
    ast: Dict[str, Any]
    costs: Dict[str, Any]
    solution: Dict[str, Any]
    result: Dict[str, Any]

SOLVE_SYS = """
Eres un algebraísta. Dado 'costs' con Sum(...), entrega:

{
  "steps": [],
  "steps_by_line": [],
  "exact": { "best": str, "avg": str, "worst": str },
  "big_o": { "best": str, "avg": str, "worst": str },
  "bounds": { "omega": str, "theta": str, "big_o": str }
}

Devuelve SOLO JSON válido, con expresiones algebraicas simples (usa ** para potencias).
"""

def solve_node(state: AgentState) -> Dict:
    costs_json = state.get("costs") or {}
    user = f"COSTS JSON:\n{costs_json}"
    sol = llm_json_call(SOLVE_SYS, user, temperature=0)

    # Empaquetar "result" con todo lo anterior (como pediste)
    result = {
        "input_text": state.get("input_text", ""),
        "validation": state.get("validation"),
        "ast": state.get("ast"),
        "costs": state.get("costs"),
        "solution": sol,
        "metadata": {
            "pipeline_stages": 5,
            "used_gemini_normalization": True,  # se puede ajustar basado en planner/normalize
            "input_type": "natural_language",
            "total_nodes_analyzed": (state.get("ast", {}).get("metadata", {}).get("total_nodes", 0)),
            "has_errors": False,
            "normalizations_applied": len((state.get("validation") or {}).get("normalizaciones") or []),
            "final_pseudocode": state.get("validation", {}).get("codigo_corregido") or state.get("pseudocode", "")
        }
    }
    return {"solution": sol, "result": result}

__all__ = ["solve_node"]

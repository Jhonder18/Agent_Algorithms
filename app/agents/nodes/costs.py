# app/agents/nodes/costs.py
from __future__ import annotations
from typing import Dict, Any

from app.services.llm import llm_json_call
from app.agents.state import AnalyzerState, update_metadata

COSTS_SYS = """
Eres un analista de costos. A partir del AST (shape dado), devuelve JSON:

{
  "per_node": [
    {
      "node_id": "...",
      "node_type":"...",
      "line_start": int|null,
      "line_end": int|null,
      "code_snippet": str|null,
      "cost": {"best": str, "avg": str, "worst": str},
      "own_cost": {"best": str, "avg": str, "worst": str} | null,
      "execution_count": null,
      "loop_info": null | {"var": str, "start": str, "end": str}
    }
    ...
  ],
  "per_line": [
    {
      "line_number": int,
      "code": str,
      "operations": [str,...],
      "cost": {"best": str, "avg": str, "worst": str}
    }
    ...
  ],
  "total": { "best": str, "avg": str, "worst": str }
}

Usa notación simbólica con Sum(...) donde aplique.
Devuelve SOLO JSON válido.
"""


def costs_node(state: AnalyzerState) -> Dict[str, Any]:
    ast_payload = state.get("ast") or {}
    ast_ok = bool(ast_payload.get("success") and ast_payload.get("ast"))

    if not ast_ok:
        error_msg = ast_payload.get("error") or "AST no disponible para calcular costos"
        empty_costs = {
            "per_node": [],
            "per_line": [],
            "total": {"best": "N/A", "avg": "N/A", "worst": "N/A"},
            "success": False,
            "error": error_msg,
        }
        meta_updates = update_metadata(
            state,
            costs_nodes=0,
            costs_lines=0,
            costs_error=error_msg,
        )
        return {"costs": empty_costs, **meta_updates}

    user = f"AST JSON:\n{ast_payload}"
    data = llm_json_call(COSTS_SYS, user, temperature=0)
    data["success"] = True
    data.setdefault("error", None)

    per_node = data.get("per_node") or []
    per_line = data.get("per_line") or []

    meta_updates = update_metadata(
        state,
        costs_nodes=len(per_node),
        costs_lines=len(per_line),
    )

    return {"costs": data, **meta_updates}


__all__ = ["costs_node"]

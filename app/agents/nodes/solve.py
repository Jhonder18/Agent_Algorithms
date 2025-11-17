# app/agents/nodes/solve.py
from __future__ import annotations
from typing import Dict, Any

from app.services.llm import llm_json_call
from app.agents.state import AnalyzerState, update_metadata

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


def solve_node(state: AnalyzerState) -> Dict[str, Any]:
    costs_json = state.get("costs") or {}
    user = f"COSTS JSON:\n{costs_json}"
    sol = llm_json_call(SOLVE_SYS, user, temperature=0)

    validation = state.get("validation") or {}
    ast_meta = (state.get("ast") or {}).get("metadata") or {}
    errores = validation.get("errores") or []
    normalizaciones = validation.get("normalizaciones") or []

    meta_fragment = update_metadata(
        state,
        pipeline_stages=5,
        has_errors=bool(errores),
        normalizations_applied=len(normalizaciones),
        final_pseudocode=validation.get("codigo_corregido")
        or state.get("pseudocode", ""),
        total_nodes_analyzed=ast_meta.get("total_nodes", 0),
    )
    final_meta = meta_fragment["metadata"]

    # Empaquetar "result" con todo lo anterior
    result = {
        "input_text": state.get("input_text", ""),
        "validation": validation,
        "ast": state.get("ast"),
        "costs": state.get("costs"),
        "solution": sol,
        "metadata": final_meta,
    }

    return {
        "solution": sol,
        "result": result,
        **meta_fragment,
    }


__all__ = ["solve_node"]

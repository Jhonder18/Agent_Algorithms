# app/agents/nodes/ast_tool_node.py
from __future__ import annotations
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from app.tools.ast_parser.ast_parser import ast_parse_lc
from app.agents.state import AnalyzerState, update_metadata


def _count_nodes(obj: Any) -> int:
    """Cuenta nodos en el AST dict para métricas rápidas."""
    if isinstance(obj, dict):
        return 1 + sum(_count_nodes(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(_count_nodes(item) for item in obj)
    return 0


def ast_node(state: AnalyzerState) -> Dict[str, Any]:
    """
    Nodo del grafo que invoca la Tool 'ast_parse' (StructuredTool) para construir el AST.
    Esto aparecerá en LangSmith como un 'Tool run' con sus inputs y outputs.
    """
    pseudo = (state.get("pseudocode") or "").strip()

    # Metadatos para LangSmith (agradables en Studio)
    cfg = RunnableConfig(tags=["tool", "ast", "lark"], run_name="AST Parser Tool")

    # Llamada a la tool; pasa por LangChain y queda trazado como Tool run
    result = ast_parse_lc.with_config(cfg).invoke({"pseudocode": pseudo})

    # result = {"ast": Program | None, "success": bool, "error": str | None}
    ast_obj = result.get("ast")
    ast_dict = ast_obj.to_dict() if ast_obj and hasattr(ast_obj, "to_dict") else None
    total_nodes = _count_nodes(ast_dict) if ast_dict else 0

    ast_payload = {
        "success": bool(result.get("success")),
        "ast": ast_dict,
        "ast_object": ast_obj,  # Guardar el objeto Program original para cost_model
        "metadata": {
            "source": "lark",
            "parser": "PseudocodeParser",
            "total_nodes": total_nodes,
        },
        "error": result.get("error"),
    }

    return {
        "ast": ast_payload,
        **update_metadata(state, parser="lark", total_nodes=total_nodes),
    }


__all__ = ["ast_node"]

# app/agents/nodes/ast_tool_node.py
from __future__ import annotations
from typing import Dict, Any, TypedDict, Optional
from langchain_core.runnables import RunnableConfig
from app.tools.ast_parser.ast_parser import ast_parse_lc


class AgentState(TypedDict, total=False):
    input_text: str
    pseudocode: str
    ast: Dict[str, Any]


def ast_node(state: AgentState) -> Dict[str, Any]:
    """
    Nodo del grafo que invoca la Tool 'ast_parse' (StructuredTool) para construir el AST.
    Esto aparecerá en LangSmith como un 'Tool run' con sus inputs y outputs.
    """
    pseudo = (state.get("pseudocode") or "").strip()

    # Metadatos para LangSmith (agradables en Studio)
    cfg = RunnableConfig(
        tags=["tool", "ast", "lark"],
        run_name="AST Parser Tool"
    )

    # Llamada a la tool; pasa por LangChain y queda trazado como Tool run
    result = ast_parse_lc.with_config(cfg).invoke({"pseudocode": pseudo})

    # result = {"ast": Program | None, "success": bool, "error": str | None}
    ast_obj = result.get("ast")
    ast_dict = ast_obj.to_dict() if ast_obj and hasattr(ast_obj, "to_dict") else None

    return {
        "ast": {
            "success": bool(result.get("success")),
            "ast": ast_dict,
            "metadata": {"source": "lark", "parser": "PseudocodeParser"},
            "error": result.get("error"),
        }
    }

__all__ = ["ast_node"]

# app/agents/nodes/ast_json.py
from __future__ import annotations
from typing import TypedDict, Dict, Any
from app.services.llm import llm_json_call

class AgentState(TypedDict, total=False):
    pseudocode: str
    validation: Dict[str, Any]
    ast: Dict[str, Any]

AST_SYS = """
Eres un generador de AST. Dado pseudocódigo, crea un JSON con shape:

{
  "success": bool,
  "ast": {
    "type": "Program",
    "functions": [ { "type":"Function", "name":"...", "params":[{"name":"A"},...], "body": { "type":"Block", "statements":[ ... ] } } ]
  } | null,
  "metadata": { "functions": int, "total_nodes": int },
  "error": null | str
}

Nodos permitidos:
- Program, Function, Block
- Assign, For, While, If, Return, ExprStmt
- Expresiones: Literal, Var, ArrayAccess, BinOp, Compare, Call
Devuelve SOLO JSON válido.
"""

def ast_node(state: AgentState) -> Dict:
    code = state.get("pseudocode") or ""
    user = f"INPUT PSEUDOCÓDIGO:\n{code}"
    data = llm_json_call(AST_SYS, user, temperature=0)
    return {"ast": data}

__all__ = ["ast_node"]

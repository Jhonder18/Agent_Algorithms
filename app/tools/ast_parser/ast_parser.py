# app/tools/ast_parser/ast_parser.py
from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from app.tools.ast_parser.parser_agent import get_parser_agent

class ASTInput(BaseModel):
    """Entrada para la tool 'ast_parse'."""
    pseudocode: str = Field(
        ...,
        description="Pseudocódigo a parsear con la gramática Lark del proyecto."
    )

def _ast_parse_impl(pseudocode: str) -> Dict[str, Any]:
    """
    Implementación real de la tool: invoca el ParserAgent (Lark + Transformer)
    y retorna un dict con keys: success, ast (objeto Program), error.
    """
    agent = get_parser_agent()
    return agent({"pseudocode": pseudocode})

# === NUEVO: función de compatibilidad para código legado ===
def build_ast(pseudocode: str) -> Dict[str, Any]:
    """
    Compatibilidad hacia atrás: construye y devuelve el AST como dict (Program.to_dict()).
    Lanza ValueError si no pudo parsear.
    """
    result = _ast_parse_impl(pseudocode)
    if result.get("success") and result.get("ast"):
        return result["ast"].to_dict()
    raise ValueError(result.get("error") or "AST build failed")

# Tool LangChain que aparecerá como "Tool run" en LangSmith
ast_parse_lc: StructuredTool = StructuredTool.from_function(
    name="ast_parse",
    description="Convierte pseudocódigo a un AST tipado usando la gramática Lark del proyecto.",
    func=lambda pseudocode: _ast_parse_impl(pseudocode),
    args_schema=ASTInput,
    return_direct=False,
)

__all__ = ["ast_parse_lc", "build_ast"]

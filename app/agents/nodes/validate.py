# app/agents/nodes/validate.py
from __future__ import annotations
from typing import TypedDict, Dict, Any
import re

ARROW = "🡨"

class AgentState(TypedDict, total=False):
    pseudocode: str
    validation: Dict[str, Any]

def _simple_normalize(code: str) -> tuple[str, list[str]]:
    changes = []
    new = code

    if "->" in new or "←" in new:
        new = new.replace("->", ARROW).replace("←", ARROW)
        changes.append("Reemplazo de asignación por flecha")

    # uniformizar keywords en minúscula
    for kw in ["BEGIN","END","FOR","WHILE","IF","ELSE","REPEAT","UNTIL","RETURN","AND","OR","NOT","DO","THEN"]:
        if kw in new:
            new = re.sub(rf"\b{kw}\b", kw.lower(), new)
            changes.append(f"Lowercase de '{kw}'")

    # asegurar newline final
    if not new.endswith("\n"):
        new += "\n"
        changes.append("Nueva línea añadida al final")

    return new, changes

def validate_node(state: AgentState) -> Dict:
    code = (state.get("pseudocode") or "").strip()
    era_algo = bool(re.search(r"\bbegin\b.*\bend\b", code, flags=re.I|re.S))
    corregido, normalizaciones = _simple_normalize(code)

    hints = {
        "parser_engine": "llm-free-pass",  # aquí puedes poner "lark-lalr" si luego usas tu parser real
        "language_hint": "es",
        "code_length": len(corregido),
        "line_count": corregido.count("\n")
    }

    validation = {
        "era_algoritmo_valido": era_algo,
        "codigo_corregido": corregido,
        "errores": [] if era_algo else ["Bloques begin/end no detectados"],
        "normalizaciones": normalizaciones,
        "hints": hints,
    }
    return {"validation": validation, "pseudocode": corregido}

__all__ = ["validate_node"]

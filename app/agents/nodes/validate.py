# app/agents/nodes/validate.py
from __future__ import annotations
from typing import Dict, Any
import re

from app.constants import ARROW
from app.agents.state import AnalyzerState, update_metadata


def _simple_normalize(code: str) -> tuple[str, list[str]]:
    changes = []
    new = code

    if "->" in new or "←" in new:
        new = new.replace("->", ARROW).replace("←", ARROW)
        changes.append("Reemplazo de asignación por flecha")

    # uniformizar keywords en minúscula
    for kw in [
        "BEGIN",
        "END",
        "FOR",
        "WHILE",
        "IF",
        "ELSE",
        "REPEAT",
        "UNTIL",
        "RETURN",
        "AND",
        "OR",
        "NOT",
        "DO",
        "THEN",
    ]:
        if kw in new:
            new = re.sub(rf"\b{kw}\b", kw.lower(), new)
            changes.append(f"Lowercase de '{kw}'")

    # asegurar newline final
    if not new.endswith("\n"):
        new += "\n"
        changes.append("Nueva línea añadida al final")

    return new, changes


def validate_node(state: AnalyzerState) -> Dict[str, Any]:
    code = (state.get("pseudocode") or "").strip()
    era_algo = bool(re.search(r"\bbegin\b.*\bend\b", code, flags=re.I | re.S))
    corregido, normalizaciones = _simple_normalize(code)

    hints = {
        "parser_engine": "llm-free-pass",  # cámbialo cuando uses el parser real
        "language_hint": "es",
        "code_length": len(corregido),
        "line_count": corregido.count("\n"),
    }

    validation = {
        "era_algoritmo_valido": era_algo,
        "codigo_corregido": corregido,
        "errores": [] if era_algo else ["Bloques begin/end no detectados"],
        "normalizaciones": normalizaciones,
        "hints": hints,
    }

    # Si nadie definió aún input_type (viene directo a validate), asumimos pseudocódigo
    meta_updates = update_metadata(
        state,
        input_type=(state.get("metadata") or {}).get("input_type", "pseudocode"),
    )

    return {"validation": validation, "pseudocode": corregido, **meta_updates}


__all__ = ["validate_node"]

# app/agents/state.py
from __future__ import annotations
from typing import TypedDict, Dict, Any


class AnalyzerState(TypedDict, total=False):
    """
    Estado compartido en todo el grafo de LangGraph.
    Todas las nodes leen/escriben sobre este shape.
    """

    # Entrada
    input_text: str        # Descripción NL o pseudocódigo directo
    pseudocode: str        # Pseudocódigo normalizado/corregido

    # Routing de complejidad
    mode: str              # 'iterative' o 'recursive'

    # Resultados intermedios
    validation: Dict[str, Any]
    ast: Dict[str, Any]
    costs: Dict[str, Any]         # Para flujo iterativo
    recurrence: Dict[str, Any]    # Para flujo recursivo
    solution: Dict[str, Any]

    # Resultado agregado
    result: Dict[str, Any]
    summary: str

    # Metadata global del pipeline
    metadata: Dict[str, Any]


def update_metadata(state: "AnalyzerState", **changes: Any) -> Dict[str, Any]:
    """
    Helper para nodos: fusiona metadata existente con cambios y devuelve un
    fragmento de estado listo para mergear en el grafo.

    Ejemplo:
        return {
            "pseudocode": code,
            **update_metadata(state, input_type="natural_language")
        }
    """
    meta: Dict[str, Any] = dict(state.get("metadata") or {})
    meta.update(changes)
    return {"metadata": meta}


__all__ = ["AnalyzerState", "update_metadata"]

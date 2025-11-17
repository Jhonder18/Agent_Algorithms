# app/agents/nodes/summarize.py
from __future__ import annotations
from typing import Dict, Any

from app.services.llm import get_llm
from app.agents.state import AnalyzerState, update_metadata

SUM_SYS = """
Eres un redactor técnico. Resume en 4-6 líneas:
- Qué hace el algoritmo
- Costes (O mejor/promedio/peor)
- Observaciones clave
Devuelve SOLO texto plano.
"""


def summarize_node(state: AnalyzerState) -> Dict[str, Any]:
    data = state.get("result") or {}
    llm = get_llm(temperature=0)
    msgs = [
        {"role": "system", "content": SUM_SYS},
        {"role": "user", "content": str(data)},
    ]
    summary = llm.invoke(msgs).content.strip()
    meta_fragment = update_metadata(state, has_summary=True)
    return {"summary": summary, **meta_fragment}


__all__ = ["summarize_node"]

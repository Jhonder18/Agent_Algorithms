# app/agents/nodes/summarize.py
from __future__ import annotations
from typing import TypedDict, Dict, Any
from app.services.llm import get_llm

class AgentState(TypedDict, total=False):
    result: Dict[str, Any]
    summary: str

SUM_SYS = """
Eres un redactor técnico. Resume en 4-6 líneas:
- Qué hace el algoritmo
- Costes (O mejor/promedio/peor)
- Observaciones clave
Devuelve SOLO texto plano.
"""

def summarize_node(state: AgentState) -> Dict:
    data = state.get("result") or {}
    llm = get_llm(temperature=0)
    msgs = [{"role":"system","content":SUM_SYS},{"role":"user","content":str(data)}]
    summary = llm.invoke(msgs).content.strip()
    return {"summary": summary}

__all__ = ["summarize_node"]

# app/agents/planner.py
from __future__ import annotations
from typing import Literal
import os, re

from app.agents.state import AnalyzerState

# Opcional: si quieres modo LLM para clasificar
try:
    from app.services.llm import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage
except Exception:  # pragma: no cover
    get_llm = None
    SystemMessage = HumanMessage = None  # evita fallo si no lo usas


def _get_raw_input_text(state: AnalyzerState) -> str:
    """
    Unifica de dónde sacamos el texto para clasificar:
    - prioriza input_text (descripción natural)
    - si no hay, usa pseudocode (para compatibilidad hacia atrás)
    """
    return (
        state.get("input_text")
        or state.get("pseudocode")
        or ""
    ).strip()


def planner_decide(state: AnalyzerState) -> Literal["normalize", "validate"]:
    """
    Devuelve:
      - "normalize" si el INPUT es lenguaje natural (NL)
      - "validate" si el INPUT ya parece pseudocódigo
    """
    text = _get_raw_input_text(state)
    mode = os.getenv("PLANNER_MODE", "heuristic").lower()

    if mode == "llm" and get_llm is not None:
        llm = get_llm(temperature=0)
        sys = SystemMessage(
            content=(
                "Clasifica el INPUT: responde SOLO 'normalize' "
                "si es lenguaje natural o 'validate' si ya es pseudocódigo."
            )
        )
        user = HumanMessage(content=f"INPUT:\n{text}")
        out = llm.invoke([sys, user]).content.strip().lower()
        # fallback robusto por si el modelo devuelve otra cosa
        return "validate" if "validate" in out else "normalize"

    # Heurística rápida (sin LLM)
    looks_pseudo = bool(
        re.search(
            r"\bbegin\b|\bend\b|←|->|\bfor\b|\bwhile\b|\bif\b|\brepeat\b|\buntil\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    return "validate" if looks_pseudo else "normalize"


__all__ = ["planner_decide"]

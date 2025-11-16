# app/agents/graph.py
from __future__ import annotations
from typing import Any, Dict, TypedDict, Optional

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END

# Nodos (ajusta los nombres si en tus archivos exportaste funciones con otro nombre)
from app.agents.nodes.normalize import normalize_node
from app.agents.nodes.validate import validate_node
from app.agents.nodes.ast_tool_node import ast_node
from app.agents.nodes.costs_json import costs_node
from app.agents.nodes.solve_json import solve_node
from app.agents.nodes.summarize import summarize_node

# (Opcional) Si ya tienes un router propio:
try:
    from app.agents.planner import planner_decide  # Debe devolver "normalize" o "validate"
except Exception:
    planner_decide = None


# ---------------------------
# Estado del grafo
# ---------------------------
class GraphState(TypedDict, total=False):
    # Entrada
    input_text: str      # Texto NL opcional
    pseudocode: str      # Pseudocódigo (si ya lo traes o lo produce normalize)

    # Resultados intermedios
    validation: Dict[str, Any]
    ast: Dict[str, Any]
    costs: Dict[str, Any]
    solution: Dict[str, Any]

    # Agregación final opcional
    result: Dict[str, Any]


# ---------------------------
# Router START -> normalize/validate
# ---------------------------
def _heuristic_router(state: GraphState) -> str:
    """Fallback simple si no existe planner_decide."""
    txt = (state.get("pseudocode")
           or state.get("input_text")
           or "")
    # Marcadores típicos de tu pseudo (🡨, begin/end, for/while/if/return/CALL, etc.)
    markers = ["🡨", "begin", "end", "for ", "while ", "if ", "CALL", "return", " then ", " do "]
    is_pseudo = any(m in txt for m in markers)
    return "validate" if is_pseudo else "normalize"


def route_from_start(state: GraphState) -> str:
    if planner_decide is not None:
        try:
            # Debe devolver exactamente "normalize" o "validate"
            decision = planner_decide(state)  # type: ignore[arg-type]
            return "normalize" if decision == "normalize" else "validate"
        except Exception:
            pass
    return _heuristic_router(state)


# ---------------------------
# Ensamblador del grafo
# ---------------------------
def build_graph():
    g = StateGraph(GraphState)

    # Registrar nodos
    g.add_node("normalize", normalize_node)  # NL -> pseudocode
    g.add_node("validate", validate_node)    # valida/corrige el pseudo
    g.add_node("ast", ast_node)              # Tool determinística (Lark) -> AST dict
    g.add_node("costs", costs_node)          # Costos por nodo/línea y totales
    g.add_node("solve", solve_node)          # Exact, Big-O, bounds, etc.
    g.add_node("summarize", summarize_node)  # Texto final (opcional)

    # Ruteo inicial: START -> normalize | validate
    g.add_conditional_edges(
        START,
        route_from_start,
        {"normalize": "normalize", "validate": "validate"},
    )

    # Flujo principal
    g.add_edge("normalize", "validate")
    g.add_edge("validate", "ast")
    g.add_edge("ast", "costs")
    g.add_edge("costs", "solve")
    g.add_edge("solve", "summarize")
    g.add_edge("summarize", END)

    return g.compile()

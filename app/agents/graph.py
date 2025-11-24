# app/agents/graph.py
from __future__ import annotations
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

from app.agents.state import AnalyzerState

from app.agents.nodes.generate_pseudo import generate_pseudo_node
from app.agents.nodes.validate import validate_node
from app.agents.nodes.ast_tool_node import ast_node
from app.agents.nodes.route_complexity import route_complexity_node
from app.agents.nodes.costs import costs_node
from app.agents.nodes.solve import solve_node
from app.agents.nodes.recurrence import recurrence_node
from app.agents.nodes.solve_recursive import solve_recursive_node
from app.agents.nodes.summarize import summarize_node

# (Opcional) Planner propio
try:
    from app.agents.planner import planner_decide  # Debe devolver "normalize" o "validate"
except Exception:  # pragma: no cover
    planner_decide = None


# ---------------------------
# Router START -> normalize/validate
# ---------------------------
def _heuristic_router(state: AnalyzerState) -> str:
    """Fallback simple si no existe planner_decide."""
    txt = (state.get("pseudocode") or state.get("input_text") or "")
    # Marcadores típicos de tu pseudo (🡨, begin/end, for/while/if/return/CALL, etc.)
    markers = [
        "🡨",
        "begin",
        "end",
        "for ",
        "while ",
        "if ",
        "CALL",
        "return",
        " then ",
        " do ",
    ]
    is_pseudo = any(m in txt for m in markers)
    return "validate" if is_pseudo else "normalize"


def route_from_start(state: AnalyzerState) -> str:
    """
    Determina si el input es lenguaje natural (normalize) o pseudocódigo (validate).
    Registra la decisión en metadata para trazabilidad.
    """
    decision = None
    route_method = "heuristic"
    
    if planner_decide is not None:
        try:
            # El planner también establece metadata.input_type si decide "validate"
            decision = planner_decide(state)  # type: ignore[arg-type]
            route_method = "planner"
            decision = "normalize" if decision == "normalize" else "validate"
        except Exception:
            pass
    
    if decision is None:
        decision = _heuristic_router(state)
        # Si usamos heurística y va a validate, establecer input_type
        if decision == "validate":
            if "metadata" not in state:
                state["metadata"] = {}
            state["metadata"]["input_type"] = "pseudocode"
            state["metadata"]["detected_by"] = "heuristic"
    
    # Registrar decisión de ruteo en metadata inicial
    if "metadata" not in state:
        state["metadata"] = {}
    state["metadata"]["initial_route"] = decision
    state["metadata"]["route_method"] = route_method
    
    return decision


# ---------------------------
# Router para bifurcar iterativo vs recursivo
# ---------------------------
def route_by_mode(state: AnalyzerState) -> str:
    """
    Determina el siguiente nodo según el modo:
    - 'iterative' -> costs (flujo actual)
    - 'recursive' -> recurrence (flujo recursivo)
    """
    mode = state.get("mode", "iterative")
    if mode == "recursive":
        return "recurrence"
    return "costs"


# ---------------------------
# Ensamblador del grafo
# ---------------------------
def build_graph():
    g = StateGraph(AnalyzerState)

    # Registrar nodos
    g.add_node("normalize", generate_pseudo_node)        # NL -> pseudocode (genera o normaliza)
    g.add_node("validate", validate_node)                # valida/corrige el pseudo
    g.add_node("ast", ast_node)                          # Tool determinística (Lark) -> AST dict
    g.add_node("route_complexity", route_complexity_node) # Detecta iterativo vs recursivo
    
    # Nodos para flujo iterativo (existente)
    g.add_node("costs", costs_node)                      # Costos por nodo/línea y totales
    g.add_node("solve", solve_node)                      # Exact, Big-O, bounds, etc.
    
    # Nodos para flujo recursivo (nuevo)
    g.add_node("recurrence", recurrence_node)            # Construye relación de recurrencia
    g.add_node("solve_recursive", solve_recursive_node)  # Resuelve recurrencia
    
    # Nodo común final
    g.add_node("summarize", summarize_node)              # Texto final (opcional)

    # Ruteo inicial: START -> normalize | validate
    g.add_conditional_edges(
        START,
        route_from_start,
        {"normalize": "normalize", "validate": "validate"},
    )

    # Flujo común inicial
    g.add_edge("normalize", "validate")
    g.add_edge("validate", "ast")
    g.add_edge("ast", "route_complexity")
    
    # Bifurcación según tipo de algoritmo
    g.add_conditional_edges(
        "route_complexity",
        route_by_mode,
        {
            "costs": "costs",           # Flujo iterativo
            "recurrence": "recurrence"  # Flujo recursivo
        }
    )
    
    # Rama iterativa (flujo existente)
    g.add_edge("costs", "solve")
    g.add_edge("solve", "summarize")
    
    # Rama recursiva (flujo nuevo)
    g.add_edge("recurrence", "solve_recursive")
    g.add_edge("solve_recursive", "summarize")
    
    # Salida común
    g.add_edge("summarize", END)

    return g.compile()

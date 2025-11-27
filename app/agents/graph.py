# app/agents/graph.py
from __future__ import annotations
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

from app.agents.state import AnalyzerState

from app.agents.nodes.generate_pseudo import generate_pseudo_node
from app.agents.nodes.validate import validate_node
from app.agents.nodes.ast_node import ast_node
from app.agents.nodes.route_complexity import route_complexity_node
from app.agents.nodes.costs import costs_node
from app.agents.nodes.solve import solve_node
from app.agents.nodes.recurrence import recurrence_node
from app.agents.nodes.solve_recursive import solve_recursive_node
from app.agents.nodes.result import summarize_node



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
    
    
    g.add_node("ast", ast_node)                          # Cambiar por el AST mas sencillo
    #g.add_node("route_complexity", route_complexity_node) # Detecta iterativo vs recursivo
    
    # Simplificar
    g.add_node("costs", costs_node)                      # Costos por nodo/línea y totales
    g.add_node("solve", solve_node)                      # Exact, Big-O, bounds, etc.
    
    # Await
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

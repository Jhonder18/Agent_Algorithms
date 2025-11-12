# app/agents/graph.py
from __future__ import annotations
from typing import TypedDict, Literal, Optional, Dict, Any
from langgraph.graph import StateGraph, END

from app.agents.planner import planner_decide
from app.agents.nodes.normalize import normalize_node
from app.agents.nodes.validate import validate_node
from app.agents.nodes.ast_json import ast_node
from app.agents.nodes.costs_json import costs_node
from app.agents.nodes.solve_json import solve_node
from app.agents.nodes.summarize import summarize_node

class AgentState(TypedDict, total=False):
    input_text: str
    route: Literal["normalize","validate"]
    pseudocode: Optional[str]
    validation: Dict[str, Any]
    ast: Dict[str, Any]
    costs: Dict[str, Any]
    solution: Dict[str, Any]
    result: Dict[str, Any]
    summary: Optional[str]
    error: Optional[str]

def start_node(state: AgentState) -> dict:
    return {}

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("start", start_node)
    g.add_node("normalize", normalize_node)
    g.add_node("validate", validate_node)
    g.add_node("ast", ast_node)
    g.add_node("costs", costs_node)
    g.add_node("solve", solve_node)
    g.add_node("summarize", summarize_node)

    g.set_entry_point("start")
    g.add_conditional_edges(
        "start",
        planner_decide,   # retorna "normalize" o "validate"
        {"normalize": "normalize", "validate": "validate"},
    )
    g.add_edge("normalize", "validate")
    g.add_edge("validate", "ast")
    g.add_edge("ast", "costs")
    g.add_edge("costs", "solve")
    g.add_edge("solve", "summarize")
    g.add_edge("summarize", END)

    return g.compile()

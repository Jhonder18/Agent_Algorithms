from app.agents.nodes import *
from app.agents.state import AnalyzerState
from langgraph.graph import StateGraph, START, END


def create_nodes(graph: StateGraph[AnalyzerState]) -> StateGraph[AnalyzerState]:
    graph.add_node("decicion_node", initial_decision_node)
    graph.add_node("code_description", code_description_node)
    graph.add_node("parse_code", parse_code_node)
    graph.add_node("validate_node", validate_node)
    graph.add_node("generate_ast", generate_ast_node)
    graph.add_node("calcular_costo_espacial_iterativo", costo_espacial_iterativo_node)
    graph.add_node("calcular_costo_temporal_iterativo", costo_temporal_iterativo_node)
    graph.add_node("calcular_costo_espacial_recursivo", recusive_espacial_node)
    graph.add_node("calcular_costo_temporal_recursivo", recusive_temporal_node)
    graph.add_node("preparacion_resultado", result_node)
    return graph


def create_edges(graph: StateGraph[AnalyzerState]) -> StateGraph[AnalyzerState]:
    graph.add_edge(START, "decicion_node")
    # recibe codigo o nl?
    def is_pseudocode(state: AnalyzerState) -> bool:
        return state.get("pseudocode") != ""

    graph.add_conditional_edges(
        "decicion_node",
        is_pseudocode,
        {
            True: "code_description",
            False: "parse_code",
        },
    )

    graph.add_edge("code_description", "validate_node")
    graph.add_edge("parse_code", "validate_node")
    graph.add_edge("validate_node", "generate_ast")
    # estatico o iterativo?
    def is_iterative(state: AnalyzerState) -> bool:
        return state.get("mode") == "iterativo"

    graph.add_conditional_edges(
        "generate_ast",
        is_iterative,
        {
            True: "calcular_costo_temporal_iterativo",
            False: "calcular_costo_temporal_recursivo",
        },
    )

    graph.add_edge(
        "calcular_costo_temporal_iterativo", "calcular_costo_espacial_iterativo"
    )
    graph.add_edge("calcular_costo_espacial_iterativo", "preparacion_resultado")

    graph.add_edge(
        "calcular_costo_temporal_recursivo", "calcular_costo_espacial_recursivo"
    )
    graph.add_edge("calcular_costo_espacial_recursivo", "preparacion_resultado")

    graph.add_edge("preparacion_resultado", END)
    return graph


def build_graph() -> StateGraph[AnalyzerState]:
    graph = StateGraph(AnalyzerState)

    graph = create_nodes(graph)
    graph = create_edges(graph) 

    return graph

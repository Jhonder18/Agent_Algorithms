"""
Definición del grafo de LangGraph para el analizador de complejidad.
Implementa flujos bifurcados para algoritmos iterativos y recursivos.
"""
from app.agents.nodes import *
from app.agents.state import AnalyzerState
from langgraph.graph import StateGraph, START, END


def create_nodes(graph: StateGraph[AnalyzerState]) -> StateGraph[AnalyzerState]:
    """
    Registra todos los nodos del grafo.
    
    Nodos compartidos:
        - decicion_node: Decide si entrada es NL o pseudocódigo
        - code_description: Genera descripción de pseudocódigo
        - parse_code: Convierte NL a pseudocódigo
        - validate_node: Valida y corrige sintaxis
        - generate_ast: Genera AST y detecta modo (iterativo/recursivo)
        - preparacion_resultado: Genera resultado final
    
    Nodos iterativos:
        - calcular_costo_temporal_iterativo
        - calcular_costo_espacial_iterativo
    
    Nodos recursivos:
        - build_recurrence: Construye ecuación de recurrencia
        - calcular_costo_temporal_recursivo: Aplica Master/Árbol/Iteración
        - calcular_costo_espacial_recursivo: Analiza pila y auxiliar
    """
    # Nodos compartidos
    graph.add_node("decicion_node", initial_decision_node)
    graph.add_node("code_description", code_description_node)
    graph.add_node("parse_code", parse_code_node)
    graph.add_node("validate_node", validate_node)
    graph.add_node("generate_ast", generate_ast_node)
    graph.add_node("preparacion_resultado", result_node)
    
    # Nodos iterativos
    graph.add_node("calcular_costo_temporal_iterativo", costo_temporal_iterativo_node)
    graph.add_node("calcular_costo_espacial_iterativo", costo_espacial_iterativo_node)
    
    # Nodos recursivos (NUEVO PIPELINE)
    graph.add_node("build_recurrence", build_recurrence_node)
    graph.add_node("calcular_costo_temporal_recursivo", recusive_temporal_node)
    graph.add_node("calcular_costo_espacial_recursivo", recusive_espacial_node)
    
    return graph


def create_edges(graph: StateGraph[AnalyzerState]) -> StateGraph[AnalyzerState]:
    """
    Define las conexiones entre nodos.
    
    Flujo principal:
        START → decicion_node → [code_description | parse_code] → validate_node
              → generate_ast → [ITERATIVO | RECURSIVO] → preparacion_resultado → END
    
    Flujo iterativo:
        generate_ast → costo_temporal_iterativo → costo_espacial_iterativo → resultado
    
    Flujo recursivo (NUEVO):
        generate_ast → build_recurrence → costo_temporal_recursivo 
                     → costo_espacial_recursivo → resultado
    """
    # Entrada inicial
    graph.add_edge(START, "decicion_node")
    
    # Decisión: ¿Es pseudocódigo o lenguaje natural?
    def is_pseudocode(state: AnalyzerState) -> bool:
        return state.get("pseudocode", "") != ""

    graph.add_conditional_edges(
        "decicion_node",
        is_pseudocode,
        {
            True: "code_description",
            False: "parse_code",
        },
    )

    # Ambos flujos convergen en validación
    graph.add_edge("code_description", "validate_node")
    graph.add_edge("parse_code", "validate_node")
    
    # Validación → Generación de AST
    graph.add_edge("validate_node", "generate_ast")
    
    # Decisión: ¿Iterativo o Recursivo?
    def route_by_mode(state: AnalyzerState) -> str:
        mode = state.get("mode", "iterativo")
        if mode == "recursivo":
            return "recursivo"
        return "iterativo"

    graph.add_conditional_edges(
        "generate_ast",
        route_by_mode,
        {
            "iterativo": "calcular_costo_temporal_iterativo",
            "recursivo": "build_recurrence",  # ← NUEVO: primero construye la recurrencia
        },
    )

    # ═══════════════════════════════════════════
    # FLUJO ITERATIVO
    # ═══════════════════════════════════════════
    graph.add_edge(
        "calcular_costo_temporal_iterativo", 
        "calcular_costo_espacial_iterativo"
    )
    graph.add_edge(
        "calcular_costo_espacial_iterativo", 
        "preparacion_resultado"
    )

    # ═══════════════════════════════════════════
    # FLUJO RECURSIVO (NUEVO PIPELINE)
    # ═══════════════════════════════════════════
    graph.add_edge(
        "build_recurrence",
        "calcular_costo_temporal_recursivo"
    )
    graph.add_edge(
        "calcular_costo_temporal_recursivo", 
        "calcular_costo_espacial_recursivo"
    )
    graph.add_edge(
        "calcular_costo_espacial_recursivo", 
        "preparacion_resultado"
    )

    # Final
    graph.add_edge("preparacion_resultado", END)
    
    return graph


def build_graph() -> StateGraph[AnalyzerState]:
    """
    Construye y retorna el grafo completo del analizador.
    
    Returns:
        StateGraph configurado con todos los nodos y edges.
    """
    graph = StateGraph(AnalyzerState)
    
    graph = create_nodes(graph)
    graph = create_edges(graph)

    return graph


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA DEL GRAFO (para referencia)
# ═══════════════════════════════════════════════════════════════════════════════
"""
                         ┌─────────────┐
                         │    START    │
                         └──────┬──────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │  decicion_node   │
                     └────────┬─────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
       ┌───────▼───────┐           ┌─────────▼─────────┐
       │ pseudocode!="" │           │ pseudocode == "" │
       │               │           │                   │
       │code_description│           │    parse_code    │
       └───────┬───────┘           └─────────┬─────────┘
               │                             │
               └──────────────┬──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  validate_node   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  generate_ast    │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
      ┌───────▼───────┐           ┌─────────▼─────────┐
      │ mode=iterativo│           │  mode=recursivo   │
      │               │           │                   │
      │costo_temporal │           │ build_recurrence  │ ← NUEVO
      │  _iterativo   │           └─────────┬─────────┘
      └───────┬───────┘                     │
              │                             ▼
              ▼                   ┌─────────────────────┐
      ┌───────────────┐           │ costo_temporal      │
      │costo_espacial │           │   _recursivo        │
      │  _iterativo   │           └─────────┬───────────┘
      └───────┬───────┘                     │
              │                             ▼
              │                   ┌─────────────────────┐
              │                   │ costo_espacial      │
              │                   │   _recursivo        │
              │                   └─────────┬───────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │preparacion_resultado│
                  └──────────┬─────────┘
                             │
                             ▼
                        ┌─────────┐
                        │   END   │
                        └─────────┘
"""

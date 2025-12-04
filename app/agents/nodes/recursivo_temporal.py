"""
Nodo para calcular la complejidad temporal de algoritmos recursivos.
Aplica múltiples métodos: Master Theorem, Árbol de Recursión, Iteración.
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import (
    AnalyzerState, 
    RecurrenceMethodResult,
    RecursionTreeAnalysis,
    RecursionTreeLevel,
    create_empty_ecuaciones
)
from app.agents.llms.gemini import get_gemini_model
from app.agents.llms.geminiWithTools import get_gemini_with_tools_model
from app.agents.tools.tools_recursivas import (
    resolver_recurrencia,
    generar_arbol_recurrencia,
    parse_recurrence,
    apply_master_theorem,
    calculate_recursion_tree_complexity,
    generate_recursion_tree_diagram
)


# ═══════════════════════════════════════════════════════════════════════════════
# MODELOS PYDANTIC
# ═══════════════════════════════════════════════════════════════════════════════

class TemporalAnalysisResult(BaseModel):
    """Resultado del análisis temporal."""
    
    best_case: str = Field(..., description="Complejidad en el mejor caso Ω()")
    average_case: str = Field(..., description="Complejidad en caso promedio Θ()")
    worst_case: str = Field(..., description="Complejidad en el peor caso O()")
    method_used: str = Field(..., description="Método principal usado para el análisis")
    detailed_steps: List[str] = Field(default_factory=list, description="Pasos detallados del análisis")
    justification: str = Field(..., description="Justificación matemática del resultado")


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Eres un experto en análisis de complejidad de algoritmos recursivos.
Tu tarea es analizar la ecuación de recurrencia y determinar la complejidad temporal.

## Métodos Disponibles (en orden de preferencia según el tipo)

### 1. Teorema Maestro (Master Theorem)
Aplica a: T(n) = aT(n/b) + f(n) donde a ≥ 1, b > 1

**Casos:**
- Caso 1: Si f(n) = O(n^c) donde c < log_b(a) → T(n) = Θ(n^(log_b(a)))
- Caso 2: Si f(n) = Θ(n^c) donde c = log_b(a) → T(n) = Θ(n^c · log n)
- Caso 3: Si f(n) = Ω(n^c) donde c > log_b(a) → T(n) = Θ(f(n))

### 2. Método del Árbol de Recursión
- Construir el árbol nivel por nivel
- Calcular costo por nivel
- Sumar todos los niveles
- Altura del árbol: log_b(n) para división, n para resta

### 3. Método de Iteración
- Expandir la recurrencia sucesivamente
- Identificar el patrón
- Sumar la serie resultante

### 4. Ecuación Característica
Para recurrencias lineales como Fibonacci:
- T(n) = T(n-1) + T(n-2) → Ecuación: x² = x + 1
- Raíces: φ = (1+√5)/2 ≈ 1.618
- Solución: T(n) = Θ(φⁿ)

## Clasificación de Recurrencias (ADA)

| Tipo | Forma | Métodos Aplicables |
|------|-------|-------------------|
| F0 | T(n) = T(n/b) + f(n) | Master, Árbol, Iteración |
| F1 | T(n) = aT(n/b) + f(n) | Master, Árbol |
| F4 | T(n) = T(n-b) + f(n) | Iteración, Árbol |
| F5 | T(n) = aT(n-b) + f(n) | Árbol, Característica |
| F6 | T(n) = T(n-1) + T(n-2) + f(n) | Característica |

## Ejemplos de Análisis

**Merge Sort: T(n) = 2T(n/2) + n**
- a=2, b=2, f(n)=n
- log_2(2) = 1, y f(n) = n = n^1
- Caso 2 del Master: T(n) = Θ(n log n)

**Búsqueda Binaria: T(n) = T(n/2) + 1**
- a=1, b=2, f(n)=1
- log_2(1) = 0, y f(n) = 1 = n^0
- Caso 2 del Master: T(n) = Θ(log n)

**Factorial: T(n) = T(n-1) + 1**
- Iteración: T(n) = T(n-1) + 1 = T(n-2) + 2 = ... = T(1) + (n-1)
- T(n) = Θ(n)

**Fibonacci: T(n) = T(n-1) + T(n-2) + 1**
- Ecuación característica: x² = x + 1
- T(n) = Θ(φⁿ) donde φ ≈ 1.618

Proporciona un análisis detallado paso a paso, mostrando el método utilizado.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_with_tools(recurrence: str, classification: str) -> Dict[str, Any]:
    """Usa las tools para analizar la recurrencia."""
    
    # Parsear la recurrencia
    params = parse_recurrence(recurrence)
    a, b, f_n = params["a"], params["b"], params["f_n"]
    rec_type = params["recurrence_type"]
    
    results = {
        "methods_applied": [],
        "best_result": "",
        "tree_diagram": "",
        "tree_analysis": {}
    }
    
    # 1. Intentar Master Theorem si aplica
    if classification in ["F0", "F1"]:
        master_result = apply_master_theorem(a, b, f_n)
        if master_result["applicable"]:
            results["methods_applied"].append({
                "method": "master",
                "steps": master_result["steps"],
                "result": master_result["result"],
                "applicable": True
            })
            results["best_result"] = master_result["result"]
    
    # 2. Árbol de Recursión (siempre aplicable)
    tree_result = calculate_recursion_tree_complexity(a, b, f_n)
    results["methods_applied"].append({
        "method": "recursion_tree",
        "steps": tree_result["steps"],
        "result": tree_result["result"],
        "applicable": True
    })
    results["tree_analysis"] = tree_result
    
    if not results["best_result"]:
        results["best_result"] = tree_result["result"]
    
    # 3. Generar diagrama Mermaid
    results["tree_diagram"] = generate_recursion_tree_diagram(a, b, f_n, 4)
    
    return results


def build_tree_levels(a: int, b: int, f_n: str, max_levels: int = 4) -> List[RecursionTreeLevel]:
    """Construye la lista de niveles del árbol de recursión."""
    levels = []
    
    for i in range(max_levels):
        if b > 1:
            nodes = a ** i
            size = f"n/{b**i}" if i > 0 else "n"
            cost = f_n.replace("n", f"({size})")
        else:
            nodes = a ** i
            size = f"n-{i}" if i > 0 else "n"
            cost = f_n
        
        total = f"{nodes} × {cost}"
        
        levels.append({
            "level": i,
            "num_nodes": nodes,
            "problem_size": size,
            "cost_per_node": cost,
            "total_level_cost": total
        })
    
    return levels


# ═══════════════════════════════════════════════════════════════════════════════
# NODO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def recusive_temporal_node(state: AnalyzerState) -> AnalyzerState:
    """
    Nodo que calcula la complejidad temporal de algoritmos recursivos.
    
    Input del estado:
        - recurrence: RecurrenceInfo con la ecuación
        - pseudocode: Para contexto adicional
    
    Output al estado:
        - ecuaciones: Con big_O_temporal, big_Omega_temporal, big_Theta_temporal
        - recurrence: Actualizado con methods_tried y final_solution
        - recursion_tree: Análisis del árbol de recursión
        - mermaid_diagram: Diagrama del árbol
        - razonamiento: Pasos agregados
    """
    # Obtener datos de la recurrencia
    recurrence = state.get("recurrence", {})
    recurrence_raw = recurrence.get("raw", "T(n) = T(n-1) + 1")
    classification = recurrence.get("classification", "F4")
    params = recurrence.get("parameters", {})
    
    # Inicializar ecuaciones si no existe
    if "ecuaciones" not in state:
        state["ecuaciones"] = create_empty_ecuaciones()
    
    # Inicializar razonamiento
    if "razonamiento" not in state:
        state["razonamiento"] = []
    
    state["razonamiento"].append("")
    state["razonamiento"].append("═══ FASE 2: Análisis de Complejidad Temporal ═══")
    state["razonamiento"].append(f"Ecuación a analizar: {recurrence_raw}")
    state["razonamiento"].append(f"Clasificación: {classification}")
    
    # Análisis usando tools
    a = params.get("a", 1)
    b = params.get("b", 1)
    f_n = params.get("f_n", "1")
    
    analysis = analyze_with_tools(recurrence_raw, classification)
    
    # Registrar métodos aplicados
    methods_tried = []
    for method in analysis["methods_applied"]:
        state["razonamiento"].append(f"\n--- Método: {method['method'].upper()} ---")
        for step in method["steps"]:
            state["razonamiento"].append(f"  • {step}")
        state["razonamiento"].append(f"  → Resultado: {method['result']}")
        
        methods_tried.append({
            "method": method["method"],
            "steps": method["steps"],
            "result": method["result"],
            "applicable": method["applicable"]
        })
    
    # Actualizar recurrence en el estado
    recurrence["methods_tried"] = methods_tried
    recurrence["best_method"] = methods_tried[0]["method"] if methods_tried else "unknown"
    recurrence["final_solution"] = analysis["best_result"]
    state["recurrence"] = recurrence
    
    # Extraer complejidades
    result = analysis["best_result"]
    
    # Para recursivos, generalmente O = Θ = Ω (complejidad ajustada)
    state["ecuaciones"]["big_O_temporal"] = result.replace("Θ", "O")
    state["ecuaciones"]["big_Theta_temporal"] = result
    state["ecuaciones"]["big_Omega_temporal"] = result.replace("Θ", "Ω")
    
    # Construir análisis del árbol de recursión
    tree_levels = build_tree_levels(a, b, f_n)
    
    tree_analysis: RecursionTreeAnalysis = {
        "levels": tree_levels,
        "height": analysis["tree_analysis"].get("height", "log(n)"),
        "total_nodes": f"{a}^h donde h = altura",
        "total_cost": result,
        "mermaid_diagram": analysis["tree_diagram"],
        "ascii_diagram": ""
    }
    state["recursion_tree"] = tree_analysis
    state["mermaid_diagram"] = analysis["tree_diagram"]
    
    # Resumen final
    state["razonamiento"].append("")
    state["razonamiento"].append("═══ RESULTADO TEMPORAL ═══")
    state["razonamiento"].append(f"✓ Mejor caso (Ω): {state['ecuaciones']['big_Omega_temporal']}")
    state["razonamiento"].append(f"✓ Caso promedio (Θ): {state['ecuaciones']['big_Theta_temporal']}")
    state["razonamiento"].append(f"✓ Peor caso (O): {state['ecuaciones']['big_O_temporal']}")
    state["razonamiento"].append(f"✓ Método usado: {recurrence['best_method']}")
    
    return state
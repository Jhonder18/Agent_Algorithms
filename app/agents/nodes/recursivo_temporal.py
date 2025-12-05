"""
Nodo para calcular la complejidad temporal de algoritmos recursivos.
Aplica múltiples métodos según la clasificación ADA_24A:
- Teorema Maestro: F0, F1
- Iteración: F4, F5, F0, F1
- Árbol de Recursión: F0, F1, F2, F3, F5, F6 (NO F4)
- Ecuación Característica: F4, F5, F6
- Sustitución: Todos
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
from app.agents.tools.tools_recursivas import (
    parse_recurrence,
    analyze_recurrence,
    get_applicable_methods,
    METHOD_PRIORITY,
    RecurrenceInfo
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

## Clasificación de Recurrencias (ADA_24A)

| Tipo | Forma | Descripción |
|------|-------|-------------|
| F0 | T(n) = T(n/b) + f(n) | DyV simple |
| F1 | T(n) = aT(n/b) + f(n) | DyV general (Teorema Maestro) |
| F2 | T(n) = T(n/b) + T(n/c) + f(n) | DyV múltiple |
| F3 | T(n) = ΣT(n/bᵢ) + f(n) | DyV generalizado |
| F4 | T(n) = T(n-b) + f(n) | RyV lineal |
| F5 | T(n) = aT(n-b) + f(n) | RysV exponencial |
| F6 | T(n) = aT(n-b) + cT(n-d) + f(n) | Fibonacci-like |

## Métodos Aplicables por Tipo

| Método | Aplica a | NO aplica a |
|--------|----------|-------------|
| Iteración | F4, F5, F0, F1 | F2, F3, F6 |
| Árbol de Recursión | F2, F3, F6, F5, F1, F0 | F4 |
| Teorema Maestro | F1, F0 | F2, F3, F4, F5, F6 |
| Sustitución | TODOS | - |
| Ecuación Característica | F5, F6, F4 | F0, F1, F2, F3 |

## Orden de Preferencia por Tipo

- F0: Teorema Maestro > Iteración > Árbol > Sustitución
- F1: Teorema Maestro > Iteración > Árbol > Sustitución
- F2: Árbol de Recursión > Sustitución
- F3: Árbol de Recursión > Sustitución
- F4: Ecuación Característica > Iteración > Sustitución
- F5: Ecuación Característica > Iteración > Árbol > Sustitución
- F6: Ecuación Característica > Árbol > Sustitución

## Ejemplos Importantes

**Fibonacci: T(n) = T(n-1) + T(n-2) + 1** (Tipo F6)
- ❌ NO usar iteración (no aplica a F6)
- ✅ Ecuación Característica: x² = x + 1 → T(n) = Θ(φⁿ) ≈ Θ(1.618ⁿ)

**Merge Sort: T(n) = 2T(n/2) + n** (Tipo F1)
- ✅ Teorema Maestro: a=2, b=2, f(n)=n → T(n) = Θ(n log n)

**Factorial: T(n) = T(n-1) + 1** (Tipo F4)
- ❌ NO usar Árbol de Recursión (solo tiene una rama)
- ✅ Ecuación Característica o Iteración → T(n) = Θ(n)

**Búsqueda Binaria: T(n) = T(n/2) + 1** (Tipo F0)
- ✅ Teorema Maestro: T(n) = Θ(log n)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_with_correct_methods(recurrence_raw: str, classification: str) -> Dict[str, Any]:
    """
    Analiza la recurrencia usando los métodos correctos según ADA_24A.
    
    Args:
        recurrence_raw: Ecuación de recurrencia como string
        classification: Tipo de recurrencia (F0-F6)
    
    Returns:
        Resultado del análisis con complejidad y diagrama Mermaid (si aplica)
    """
    # Realizar análisis completo
    analysis = analyze_recurrence(recurrence_raw)
    
    results = {
        "methods_applied": [],
        "best_result": "",
        "tree_diagram": None,  # Solo se incluye si el método es árbol de recursión
        "tree_analysis": {},
        "primary_method": ""
    }
    
    # Procesar todos los resultados
    for method_result in analysis.all_results:
        method_info = {
            "method": method_result.method,
            "steps": method_result.steps,
            "result": method_result.complexity or "",
            "applicable": method_result.applicable,
            "explanation": method_result.explanation
        }
        results["methods_applied"].append(method_info)
        
        # Si este método generó un diagrama Mermaid, guardarlo
        if method_result.mermaid_diagram:
            results["tree_diagram"] = method_result.mermaid_diagram
    
    # El resultado principal
    if analysis.primary_result:
        results["best_result"] = analysis.primary_result.complexity or ""
        results["primary_method"] = analysis.primary_result.method
        
        # Solo incluir el diagrama si el método principal es árbol de recursión
        if analysis.primary_result.method != "recursion_tree":
            results["tree_diagram"] = None
    
    return results


def build_tree_levels(info: RecurrenceInfo, max_levels: int = 4) -> List[Dict[str, Any]]:
    """Construye la lista de niveles del árbol de recursión."""
    levels = []
    
    a = int(info.a or 1)
    b = int(info.b or 2)
    f_n = info.f_n or "1"
    
    for i in range(max_levels):
        if info.is_division:
            nodes = a ** i
            size = f"n/{b**i}" if i > 0 else "n"
            cost = f_n.replace("n", f"({size})")
        else:
            nodes = a ** i
            size = f"n-{i*b}" if i > 0 else "n"
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
    
    Selecciona automáticamente el método correcto según la clasificación ADA_24A:
    - F0/F1 → Teorema Maestro
    - F2/F3 → Árbol de Recursión
    - F4 → Ecuación Característica o Iteración
    - F5 → Ecuación Característica
    - F6 (Fibonacci) → Ecuación Característica → Θ(φⁿ)
    
    Input del estado:
        - recurrence: RecurrenceInfo con la ecuación
        - pseudocode: Para contexto adicional
    
    Output al estado:
        - ecuaciones: Con big_O_temporal, big_Omega_temporal, big_Theta_temporal
        - recurrence: Actualizado con methods_tried y final_solution
        - recursion_tree: Análisis del árbol (solo si aplica)
        - mermaid_diagram: Diagrama del árbol (SOLO si el método es Árbol de Recursión)
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
    state["razonamiento"].append(f"Clasificación ADA: {classification}")
    
    # Obtener métodos aplicables según el tipo
    applicable_methods = METHOD_PRIORITY.get(classification, ["substitution"])
    state["razonamiento"].append(f"Métodos aplicables (en orden): {', '.join(applicable_methods)}")
    
    # Análisis usando las tools correctas
    analysis = analyze_with_correct_methods(recurrence_raw, classification)
    
    # Registrar métodos aplicados
    methods_tried = []
    for method in analysis["methods_applied"]:
        state["razonamiento"].append(f"\n--- Método: {method['method'].upper()} ---")
        if method['applicable']:
            for step in method["steps"]:
                state["razonamiento"].append(f"  • {step}")
            state["razonamiento"].append(f"  → Resultado: {method['result']}")
        else:
            state["razonamiento"].append(f"  ✗ No aplicable: {method['explanation']}")
        
        methods_tried.append({
            "method": method["method"],
            "steps": method["steps"],
            "result": method["result"],
            "applicable": method["applicable"]
        })
    
    # Actualizar recurrence en el estado
    recurrence["methods_tried"] = methods_tried
    recurrence["best_method"] = analysis["primary_method"]
    recurrence["final_solution"] = analysis["best_result"]
    state["recurrence"] = recurrence
    
    # Extraer complejidades
    result = analysis["best_result"] or "Θ(n)"
    
    # Para recursivos, generalmente O = Θ = Ω (complejidad ajustada)
    state["ecuaciones"]["big_O_temporal"] = result.replace("Θ", "O")
    state["ecuaciones"]["big_Theta_temporal"] = result
    state["ecuaciones"]["big_Omega_temporal"] = result.replace("Θ", "Ω")
    
    # Construir análisis del árbol de recursión SOLO si aplica
    if classification != "F4" and analysis.get("tree_diagram"):
        # Parsear para obtener info del árbol
        info = parse_recurrence(recurrence_raw)
        tree_levels = build_tree_levels(info)
        
        if info.is_division:
            height = f"log_{int(info.b)}(n)"
        else:
            height = f"n/{int(info.b)}"
        
        tree_analysis: RecursionTreeAnalysis = {
            "levels": tree_levels,
            "height": height,
            "total_nodes": f"Σ nodos en todos los niveles",
            "total_cost": result,
            "mermaid_diagram": analysis["tree_diagram"],
            "ascii_diagram": ""
        }
        state["recursion_tree"] = tree_analysis
        state["mermaid_diagram"] = analysis["tree_diagram"]
        state["razonamiento"].append(f"\n📊 Diagrama de árbol de recursión generado (método: {analysis['primary_method']})")
    else:
        # F4 no tiene árbol de recursión (es una línea, no un árbol)
        state["recursion_tree"] = None
        state["mermaid_diagram"] = None
        if classification == "F4":
            state["razonamiento"].append(f"\nℹ️ No se genera árbol de recursión para tipo F4 (estructura lineal, no árbol)")
        elif analysis["primary_method"] != "recursion_tree":
            state["razonamiento"].append(f"\nℹ️ Diagrama no generado (método usado: {analysis['primary_method']}, no árbol de recursión)")
    
    # Resumen final
    state["razonamiento"].append("")
    state["razonamiento"].append("═══ RESULTADO TEMPORAL ═══")
    state["razonamiento"].append(f"✓ Mejor caso (Ω): {state['ecuaciones']['big_Omega_temporal']}")
    state["razonamiento"].append(f"✓ Caso promedio (Θ): {state['ecuaciones']['big_Theta_temporal']}")
    state["razonamiento"].append(f"✓ Peor caso (O): {state['ecuaciones']['big_O_temporal']}")
    state["razonamiento"].append(f"✓ Método usado: {analysis['primary_method']}")
    state["razonamiento"].append(f"✓ Tipo de recurrencia: {classification}")
    
    return state

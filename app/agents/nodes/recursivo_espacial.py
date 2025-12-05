"""
Nodo para calcular la complejidad espacial de algoritmos recursivos.
Analiza profundidad de pila, variables locales y memoria auxiliar.
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AnalyzerState, SpaceAnalysis, create_empty_ecuaciones
from app.agents.llms.gemini import get_gemini_model
from app.agents.tools.tools_recursivas import parse_recurrence


# ═══════════════════════════════════════════════════════════════════════════════
# MODELOS PYDANTIC
# ═══════════════════════════════════════════════════════════════════════════════

class SpaceAnalysisResult(BaseModel):
    """Resultado del análisis espacial."""
    
    recursion_depth: str = Field(
        ..., 
        description="Profundidad máxima de la pila de recursión. Ej: 'O(n)', 'O(log n)'"
    )
    stack_frame_size: str = Field(
        ..., 
        description="Tamaño de cada frame en la pila. Ej: 'O(1)', 'O(n)'"
    )
    auxiliary_space: str = Field(
        ..., 
        description="Espacio auxiliar adicional usado. Ej: 'O(1)', 'O(n)'"
    )
    total_space: str = Field(
        ..., 
        description="Complejidad espacial total. Ej: 'O(n)', 'O(log n)', 'O(n log n)'"
    )
    explanation: str = Field(
        ..., 
        description="Explicación detallada del análisis espacial"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Eres un experto en análisis de complejidad espacial de algoritmos recursivos.

## Componentes del Espacio en Recursión

### 1. Profundidad de la Pila (Stack Depth)
- **Divide y Vencerás (n/b):** Profundidad = O(log_b n)
  - Binary Search: O(log n)
  - Merge Sort: O(log n)
  
- **Resta y Vencerás (n-1):** Profundidad = O(n)
  - Factorial: O(n)
  - Fibonacci (sin memoización): O(n)

### 2. Tamaño del Frame (Stack Frame)
- Variables locales por llamada
- Parámetros de la función
- Dirección de retorno
- Típicamente O(1) si no se crean estructuras grandes

### 3. Espacio Auxiliar
- Arreglos/listas creados durante la ejecución
- Merge Sort: O(n) para el arreglo temporal de merge
- Quick Sort: O(log n) versión optimizada, O(n) peor caso

## Fórmula General
**Espacio Total = Profundidad × Frame + Auxiliar**

## Ejemplos

**Merge Sort:**
- Profundidad: O(log n)
- Frame: O(1)
- Auxiliar: O(n) para el merge
- **Total: O(n)**

**Búsqueda Binaria:**
- Profundidad: O(log n)
- Frame: O(1)
- Auxiliar: O(1)
- **Total: O(log n)**

**Factorial:**
- Profundidad: O(n)
- Frame: O(1)
- Auxiliar: O(1)
- **Total: O(n)**

**Fibonacci (naive):**
- Profundidad: O(n) (rama más larga)
- Frame: O(1)
- Auxiliar: O(1)
- **Total: O(n)** (por la pila, aunque hay 2^n llamadas)

**Quick Sort:**
- Mejor/Promedio: O(log n) profundidad
- Peor: O(n) profundidad (lista ordenada)
- **Mejor: O(log n), Peor: O(n)**

## Importante
- En recursión, solo UNA rama está activa en la pila a la vez
- Aunque haya muchas llamadas (ej. 2^n en Fibonacci), la profundidad máxima es lo que importa
- Considera si el algoritmo es tail-recursive (puede optimizarse a O(1))
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_space_from_recurrence(recurrence: str, classification: str) -> Dict[str, Any]:
    """
    Analiza el espacio basándose en la recurrencia.
    Ahora usa RecurrenceInfo en lugar de diccionario.
    """
    info = parse_recurrence(recurrence)
    a = info.a or 1
    b = info.b or 1
    is_division = info.is_division
    rec_type = info.tipo  # F0, F1, F2, F3, F4, F5, F6
    
    result = {
        "recursion_depth": "",
        "stack_frame_size": "O(1)",
        "auxiliary_space": "O(1)",
        "total_space": "",
        "explanation": []
    }
    
    # Determinar profundidad según el tipo
    if rec_type in ["F0", "F1", "F2", "F3"]:  # Divide and Conquer
        result["recursion_depth"] = f"O(log_{int(b)}(n))" if b > 2 else "O(log n)"
        result["explanation"].append(f"La recursión divide el problema por {int(b)}, profundidad = log_{int(b)}(n)")
        
        # Para divide and conquer con múltiples llamadas, puede haber espacio auxiliar
        if a >= 2:
            result["auxiliary_space"] = "O(n)"  # Típico de merge sort
            result["explanation"].append("Algoritmos tipo merge requieren espacio auxiliar O(n)")
            result["total_space"] = "O(n)"
        else:
            result["total_space"] = "O(log n)"
            
    elif rec_type in ["F4", "F5"]:  # Decrease and Conquer
        result["recursion_depth"] = "O(n)"
        result["explanation"].append("La recursión resta una constante, profundidad = O(n)")
        result["total_space"] = "O(n)"
        
    elif rec_type == "F6":  # Fibonacci-like (was "multiple_recursive" or "decrease_and_lose")
        result["recursion_depth"] = "O(n)"
        result["explanation"].append("Tipo Fibonacci: profundidad = n (rama más larga)")
        result["explanation"].append("Aunque hay ~2^n llamadas totales, solo O(n) frames simultáneos")
        result["total_space"] = "O(n)"
    else:
        result["recursion_depth"] = "O(n)"
        result["total_space"] = "O(n)"
    
    return result


def detect_auxiliary_space(pseudocode: str) -> str:
    """
    Detecta si hay estructuras auxiliares en el código.
    """
    pseudocode_lower = pseudocode.lower()
    
    # Detectar creación de arreglos auxiliares
    if any(kw in pseudocode_lower for kw in ["merge", "temp", "auxiliar", "copia"]):
        return "O(n)"
    
    # Detectar creación de estructuras dinámicas
    if any(kw in pseudocode_lower for kw in ["new", "create", "alloc"]):
        return "O(n)"
    
    return "O(1)"


# ═══════════════════════════════════════════════════════════════════════════════
# NODO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def recusive_espacial_node(state: AnalyzerState) -> AnalyzerState:
    """
    Nodo que calcula la complejidad espacial de algoritmos recursivos.
    
    Input del estado:
        - recurrence: RecurrenceInfo con la ecuación
        - pseudocode: Para detectar estructuras auxiliares
    
    Output al estado:
        - ecuaciones: Con big_O_espacial, big_Omega_espacial, big_Theta_espacial
        - space_analysis: Análisis detallado del espacio
        - razonamiento: Pasos agregados
    """
    # Obtener datos
    recurrence = state.get("recurrence", {})
    recurrence_raw = recurrence.get("raw", "T(n) = T(n-1) + 1")
    classification = recurrence.get("classification", "F4")
    pseudocode = state.get("pseudocode", "")
    
    # Inicializar ecuaciones si no existe
    if "ecuaciones" not in state:
        state["ecuaciones"] = create_empty_ecuaciones()
    
    # Inicializar razonamiento
    if "razonamiento" not in state:
        state["razonamiento"] = []
    
    state["razonamiento"].append("")
    state["razonamiento"].append("═══ FASE 3: Análisis de Complejidad Espacial ═══")
    
    # Analizar espacio
    analysis = analyze_space_from_recurrence(recurrence_raw, classification)
    
    # Detectar espacio auxiliar del código
    aux_space = detect_auxiliary_space(pseudocode)
    if aux_space == "O(n)" and analysis["auxiliary_space"] == "O(1)":
        analysis["auxiliary_space"] = aux_space
        analysis["explanation"].append("Se detectó uso de estructuras auxiliares en el código")
        # Recalcular espacio total
        if "log" in analysis["recursion_depth"]:
            analysis["total_space"] = "O(n)"  # Dominado por auxiliar
    
    # Registrar análisis
    state["razonamiento"].append(f"Profundidad de pila: {analysis['recursion_depth']}")
    for exp in analysis["explanation"]:
        state["razonamiento"].append(f"  • {exp}")
    state["razonamiento"].append(f"Tamaño de frame: {analysis['stack_frame_size']}")
    state["razonamiento"].append(f"Espacio auxiliar: {analysis['auxiliary_space']}")
    
    # Guardar análisis
    space_analysis: SpaceAnalysis = {
        "recursion_depth": analysis["recursion_depth"],
        "stack_frame_size": analysis["stack_frame_size"],
        "auxiliary_space": analysis["auxiliary_space"],
        "total_space": analysis["total_space"]
    }
    state["space_analysis"] = space_analysis
    
    # Actualizar ecuaciones
    total = analysis["total_space"]
    state["ecuaciones"]["big_O_espacial"] = total.replace("Θ", "O")
    state["ecuaciones"]["big_Theta_espacial"] = total
    state["ecuaciones"]["big_Omega_espacial"] = total.replace("O", "Ω")
    
    # Resumen
    state["razonamiento"].append("")
    state["razonamiento"].append("═══ RESULTADO ESPACIAL ═══")
    state["razonamiento"].append(f"✓ Espacio total: {total}")
    state["razonamiento"].append(f"  - Pila: {analysis['recursion_depth']} × {analysis['stack_frame_size']}")
    state["razonamiento"].append(f"  - Auxiliar: {analysis['auxiliary_space']}")
    
    return state
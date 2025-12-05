# app/agents/state.py
"""
Estado del analizador de complejidad algorítmica.
Define todas las estructuras de datos que fluyen por el pipeline de LangGraph.
"""
from typing import TypedDict, Annotated, Literal, Dict, Any, Optional, List


# ═══════════════════════════════════════════════════════════════════════════════
# TIPOS PARA ANÁLISIS ITERATIVO
# ═══════════════════════════════════════════════════════════════════════════════

class Ecuaciones(TypedDict):
    """Ecuaciones de complejidad calculadas."""
    big_O_temporal: Annotated[str, "Notación Big-O temporal"]
    big_O_espacial: Annotated[str, "Notación Big-O espacial"]
    big_Theta_temporal: Annotated[str, "Notación Big-Theta temporal"]
    big_Theta_espacial: Annotated[str, "Notación Big-Theta espacial"]
    big_Omega_temporal: Annotated[str, "Notación Big-Omega temporal"]
    big_Omega_espacial: Annotated[str, "Notación Big-Omega espacial"]


class Notacion(TypedDict):
    """Notaciones asintóticas finales."""
    big_O_temporal: str
    big_O_espacial: str
    big_Theta_temporal: str
    big_Theta_espacial: str
    big_Omega_temporal: str
    big_Omega_espacial: str


# ═══════════════════════════════════════════════════════════════════════════════
# TIPOS PARA ANÁLISIS RECURSIVO
# ═══════════════════════════════════════════════════════════════════════════════

class RecurrenceMethodResult(TypedDict, total=False):
    """Resultado de aplicar un método de resolución de recurrencias."""
    method: Literal["master", "recursion_tree", "iteration", "characteristic", "substitution"]
    steps: List[str]           # Explicación paso a paso
    result: str                # Por ejemplo "T(n) = Θ(n log n)"
    applicable: bool           # Si el método fue aplicable
    diagram: Optional[str]     # Diagrama Mermaid (para árbol de recursión)


class RecurrenceParameters(TypedDict, total=False):
    """Parámetros extraídos de la ecuación de recurrencia."""
    a: int                     # Número de llamadas recursivas
    b: int                     # Factor de división del problema
    f_n: str                   # Trabajo no recursivo f(n)
    recurrence_type: Literal[
        "divide_and_conquer",  # T(n) = aT(n/b) + f(n)
        "decrease_and_conquer", # T(n) = T(n-b) + f(n)
        "decrease_and_lose",   # T(n) = aT(n-b) + f(n) con a > 1
        "multiple_recursive",  # T(n) = T(n-1) + T(n-2) + ... (tipo Fibonacci)
        "unknown"
    ]
    k: Optional[int]           # Para casos especiales (n^k en f(n))


class RecurrenceInfo(TypedDict, total=False):
    """Información completa de la recurrencia detectada."""
    raw: str                              # "T(n) = 2T(n/2) + n"
    base_cases: List[str]                 # ["T(1) = Θ(1)", "T(0) = 0"]
    variable: str                         # "n"
    parameters: RecurrenceParameters      # Parámetros extraídos
    classification: str                   # F0, F1, F2, ..., F6 según el PDF
    methods_tried: List[RecurrenceMethodResult]  # Todos los métodos intentados
    best_method: str                      # Método que dio mejor resultado
    final_solution: str                   # "T(n) = Θ(n log n)"


class RecursionTreeLevel(TypedDict):
    """Representa un nivel del árbol de recursión."""
    level: int                 # Número del nivel (0 = raíz)
    num_nodes: int             # Cantidad de nodos en este nivel
    problem_size: str          # Tamaño del problema (ej: "n/2^k")
    cost_per_node: str         # Costo por nodo
    total_level_cost: str      # Costo total del nivel


class RecursionTreeAnalysis(TypedDict, total=False):
    """Análisis completo del árbol de recursión."""
    levels: List[RecursionTreeLevel]
    height: str                # Altura del árbol (ej: "log₂(n)")
    total_nodes: str           # Número total de nodos
    total_cost: str            # Suma total de costos
    mermaid_diagram: str       # Diagrama en formato Mermaid
    ascii_diagram: str         # Diagrama en ASCII (alternativa)


class SpaceAnalysis(TypedDict, total=False):
    """Análisis de complejidad espacial para algoritmos recursivos."""
    recursion_depth: str       # Profundidad de la pila de recursión
    stack_frame_size: str      # Tamaño de cada frame
    auxiliary_space: str       # Espacio auxiliar adicional
    total_space: str           # Espacio total


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO PRINCIPAL DEL ANALIZADOR
# ═══════════════════════════════════════════════════════════════════════════════

class CostoLineaLineaMejor(TypedDict):
    lineas: Annotated[list[str], "Lista de líneas de código"]
    costos: Annotated[list[str], "Lista de costos asociados a cada línea"]

class CostoLineaLineaPeor(TypedDict):
    lineas: Annotated[list[str], "Lista de líneas de código"]
    costos: Annotated[list[str], "Lista de costos asociados a cada línea"]

class AnalyzerState(TypedDict, total=False):
    """
    Estado completo que fluye a través del pipeline de LangGraph.
    Contiene toda la información necesaria para el análisis de complejidad.
    """

    # ═══════════════════════════════════════════
    # ENTRADA
    # ═══════════════════════════════════════════
    nl_description: Annotated[str, "Descripción NL o pseudocódigo directo"]
    pseudocode: Annotated[str, "Pseudocódigo normalizado/corregido"]

    # ═══════════════════════════════════════════
    # ROUTING Y ANÁLISIS INTERMEDIO
    # ═══════════════════════════════════════════
    mode: Annotated[Literal["iterativo", "recursivo"], "'iterativo' o 'recursivo'"]
    ast: Annotated[Dict[str, Any], "Árbol sintáctico abstracto"]
    sumatoria: Annotated[str, "Expresión de sumatoria para flujo iterativo"]
    
    costos_mejor: Annotated[CostoLineaLineaMejor, "Costos línea a línea para caso mejor"]
    costos_peor: Annotated[CostoLineaLineaPeor, "Costos línea a línea para caso peor"]
    # Validación
    validation: Optional[Annotated[Dict[str, Any], "Validación del pseudocódigo"]]
    
    # ═══════════════════════════════════════════
    # ANÁLISIS RECURSIVO
    # ═══════════════════════════════════════════
    recurrence: Annotated[RecurrenceInfo, "Información de recurrencia para flujo recursivo"]
    recursion_tree: Annotated[RecursionTreeAnalysis, "Análisis del árbol de recursión"]
    space_analysis: Annotated[SpaceAnalysis, "Análisis de espacio para recursivos"]
    
    # ═══════════════════════════════════════════
    # RESULTADOS DE COMPLEJIDAD
    # ═══════════════════════════════════════════
    ecuaciones: Annotated[Ecuaciones, "Ecuaciones de complejidad calculadas"]
    notation: Annotated[Notacion, "Notaciones asintóticas finales"]
    
    # ═══════════════════════════════════════════
    # RESULTADO FINAL
    # ═══════════════════════════════════════════
    razonamiento: Annotated[List[str], "Pasos del razonamiento del análisis"]
    result: Annotated[str, "Análisis completo en lenguaje natural"]
    mermaid_diagram: Annotated[str, "Diagrama Mermaid del árbol/análisis"]


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def create_empty_ecuaciones() -> Ecuaciones:
    """Crea un diccionario de ecuaciones vacío."""
    return {
        "big_O_temporal": "",
        "big_O_espacial": "",
        "big_Theta_temporal": "",
        "big_Theta_espacial": "",
        "big_Omega_temporal": "",
        "big_Omega_espacial": "",
    }


def create_empty_recurrence() -> RecurrenceInfo:
    """Crea una estructura de recurrencia vacía."""
    return {
        "raw": "",
        "base_cases": [],
        "variable": "n",
        "parameters": {
            "a": 1,
            "b": 1,
            "f_n": "1",
            "recurrence_type": "unknown"
        },
        "classification": "",
        "methods_tried": [],
        "best_method": "",
        "final_solution": ""
    }
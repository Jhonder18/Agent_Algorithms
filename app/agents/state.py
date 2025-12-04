# app/agents/state.py
from typing import TypedDict, Annotated, Literal, Dict, Any, Optional

class Ecuaciones(TypedDict):
    big_O_temporal: Annotated[str, "Notación Big-O temporal"]
    big_O_espacial: Annotated[str, "Notación Big-O espacial"]
    big_Theta_temporal: Annotated[str, "Notación Big-Theta temporal"]
    big_Theta_espacial: Annotated[str, "Notación Big-Theta espacial"]
    big_Omega_temporal: Annotated[str, "Notación Big-Omega temporal"]
    big_Omega_espacial: Annotated[str, "Notación Big-Omega espacial"]

class Notacion(TypedDict):
    big_O_temporal: str
    big_O_espacial: str
    big_Theta_temporal: str
    big_Theta_espacial: str
    big_Omega_temporal: str
    big_Omega_espacial: str

class AnalyzerState(TypedDict, total=False):

    # Entrada
    nl_description: Annotated[str, "Descripción NL o pseudocódigo directo"]
    pseudocode: Annotated[str, "Pseudocódigo normalizado/corregido"]

    # Routing de complejidad
    mode: Annotated[Literal["iterative", "recursive"], "'iterative' o 'recursive'"]
    ast: Annotated[Dict[str, Any], "Árbol sintáctico abstracto"]
    sumatoria: Annotated[str, "Expresión de sumatoria para flujo iterativo/recursivo"]
    # Resultados intermedios
    validation: Optional[Annotated[Dict[str, Any], "Validación del pseudocódigo"]]
    recurrence: Annotated[Dict[str, Any], "Ecuaciones de recurrencias para flujo recursivo"]
    ecuaciones: Annotated[Ecuaciones, "Solución del análisis"]
    notation: Annotated[Notacion, "Notaciones de complejidad"]
    # Resultado agregado
    razonamiento: Annotated[list[str], "Razonamiento del análisis"]
    result: Annotated[Dict[str, Any], "Resultado en NL agregado del análisis"]
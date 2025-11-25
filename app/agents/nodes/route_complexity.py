# app/agents/nodes/route_complexity.py
"""
Nodo que determina si el algoritmo es iterativo o recursivo
y establece el modo de análisis correspondiente.
"""

from typing import Dict
from app.tools.recursion_detector import get_recursion_detector


def route_complexity_node(state: Dict) -> Dict:
    """
    Analiza el AST para determinar si contiene funciones recursivas.
    Establece el modo de análisis: 'iterative' o 'recursive'.
    
    Args:
        state: Estado del grafo que debe contener 'ast'
        
    Returns:
        Dict con 'mode' y metadata de recursividad añadida al AST
    """
    print("[ROUTE_COMPLEXITY] Analizando tipo de algoritmo...")
    
    ast_payload = state.get("ast")
    if not ast_payload:
        print("[ROUTE_COMPLEXITY] No se encontró AST en el estado")
        return {
            "mode": "iterative",
            "error": "No se encontró AST para analizar"
        }
    
    # El AST viene como un dict con estructura: {"ast": dict, "metadata": dict, ...}
    # Necesitamos acceder al campo "ast" dentro del payload
    if isinstance(ast_payload, dict):
        ast_dict = ast_payload.get("ast")
        if not ast_dict:
            # Si el AST es None (error de parsing), tratar como iterativo por defecto
            print("[ROUTE_COMPLEXITY] AST no disponible, tratando como iterativo por defecto")
            return {
                "mode": "iterative"
            }
    else:
        print(f"[ROUTE_COMPLEXITY] Tipo de payload no reconocido: {type(ast_payload)}")
        return {
            "mode": "iterative",
            "error": f"Tipo de payload no reconocido: {type(ast_payload)}"
        }
    
    # Detectar recursividad
    detector = get_recursion_detector()
    recursion_info = detector.detect(ast_dict)
    
    is_recursive = recursion_info["is_recursive"]
    recursive_functions = recursion_info["recursive_functions"]
    
    # Añadir metadata al payload del AST
    if "metadata" not in ast_payload:
        ast_payload["metadata"] = {}
    
    ast_payload["metadata"]["is_recursive"] = is_recursive
    ast_payload["metadata"]["recursive_functions"] = recursive_functions
    
    # Determinar el modo
    mode = "recursive" if is_recursive else "iterative"
    
    # Log para debugging
    if is_recursive:
        print(f"[ROUTE_COMPLEXITY] Detectadas {len(recursive_functions)} función(es) recursiva(s)")
        for func_info in recursive_functions:
            print(f"  - {func_info['name']}: {len(func_info['calls'])} llamada(s) recursiva(s)")
    else:
        print("[ROUTE_COMPLEXITY] No se detectó recursividad - usando flujo iterativo")
    
    return {
        "mode": mode,
        "ast": ast_payload  # Retornar el payload del AST actualizado con metadata
    }

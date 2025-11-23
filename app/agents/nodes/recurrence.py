# app/agents/nodes/recurrence.py
"""
Nodo para construir la relación de recurrencia a partir del AST recursivo.
"""

from typing import Dict
from app.tools.recurrence_analyzer import get_recurrence_analyzer


def recurrence_node(state: Dict) -> Dict:
    """
    Construye la relación de recurrencia a partir del AST con funciones recursivas.
    
    Args:
        state: Estado del grafo con AST y metadata de recursividad
        
    Returns:
        Dict con información de la recurrencia construida
    """
    print("[RECURRENCE_NODE] Construyendo relación de recurrencia...")
    
    ast_payload = state.get("ast")
    if not ast_payload:
        return {
            "recurrence": None,
            "success": False,
            "error": "No se encontró AST en el estado"
        }
    
    # Obtener el AST dict y metadata
    if isinstance(ast_payload, dict):
        ast_dict = ast_payload.get("ast")
        metadata = ast_payload.get("metadata", {})
    else:
        return {
            "recurrence": None,
            "success": False,
            "error": "Formato de AST no reconocido"
        }
    
    if not ast_dict:
        return {
            "recurrence": None,
            "success": False,
            "error": "AST no disponible"
        }
    
    # Obtener funciones recursivas
    recursive_functions = metadata.get("recursive_functions", [])
    
    if not recursive_functions:
        return {
            "recurrence": None,
            "success": False,
            "error": "No hay funciones recursivas para analizar"
        }
    
    print(f"[RECURRENCE_NODE] Analizando {len(recursive_functions)} función(es) recursiva(s)")
    
    # Analizar cada función recursiva
    analyzer = get_recurrence_analyzer()
    recurrences = []
    
    for func_info in recursive_functions:
        print(f"[RECURRENCE_NODE] Analizando: {func_info['name']}")
        result = analyzer.analyze(ast_dict, func_info)
        
        if result.get("success"):
            recurrence = result.get("recurrence", {})
            print(f"[RECURRENCE_NODE] OK Relacion construida: {recurrence.get('form', 'N/A')}")
            print(f"[RECURRENCE_NODE]   Patron: {recurrence.get('pattern_type', 'N/A')}")
            print(f"[RECURRENCE_NODE]   a={recurrence.get('a')}, b={recurrence.get('b')}, f(n)={recurrence.get('f_n')}")
            recurrences.append(result)
        else:
            print(f"[RECURRENCE_NODE] ERROR: {result.get('error', 'Desconocido')}")
            recurrences.append(result)
    
    # Por ahora, si hay múltiples funciones, tomamos la primera
    main_recurrence = recurrences[0] if recurrences else None
    
    return {
        "recurrence": main_recurrence,
        "all_recurrences": recurrences,
        "success": True
    }

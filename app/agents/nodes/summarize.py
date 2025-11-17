# app/agents/nodes/summarize.py
from __future__ import annotations
from typing import Dict, Any

from app.services.llm import get_llm
from app.agents.state import AnalyzerState, update_metadata

SUM_SYS = """
Eres un redactor técnico. Resume en 4-6 líneas:
- Qué hace el algoritmo (usa el NOMBRE DEL ALGORITMO que aparece en el pseudocódigo)
- Costes (O mejor/promedio/peor) basándote en los resultados del análisis
- Observaciones clave sobre la complejidad
Devuelve SOLO texto plano. NO inventes nombres de algoritmos, usa el nombre que aparece en el código.
"""


def summarize_node(state: AnalyzerState) -> Dict[str, Any]:
    # Extraer información relevante del estado
    pseudocode = state.get("pseudocode", "")
    ast_data = state.get("ast", {})
    costs = state.get("costs", {})
    solution = state.get("solution")
    
    # Validar que solution existe
    if not solution or not isinstance(solution, dict):
        solution = {}
    
    # Intentar extraer el nombre del algoritmo del AST
    algorithm_name = "el algoritmo"
    if ast_data and isinstance(ast_data, dict):
        ast_obj = ast_data.get("ast", {})
        if isinstance(ast_obj, dict) and "functions" in ast_obj:
            functions = ast_obj.get("functions", [])
            if functions and len(functions) > 0:
                algorithm_name = functions[0].get("name", "el algoritmo")
    
    # Construir contexto rico para el LLM
    context = f"""
NOMBRE DEL ALGORITMO: {algorithm_name}

PSEUDOCÓDIGO:
{pseudocode[:500]}

COMPLEJIDADES CALCULADAS:
{solution.get('big_o', {})}

COTAS ASINTÓTICAS:
{solution.get('bounds', {})}

COSTOS EXACTOS:
{solution.get('exact', {})}
"""
    
    llm = get_llm(temperature=0)
    msgs = [
        {"role": "system", "content": SUM_SYS},
        {"role": "user", "content": context},
    ]
    summary = llm.invoke(msgs).content.strip()
    meta_fragment = update_metadata(state, has_summary=True)
    return {"summary": summary, **meta_fragment}


__all__ = ["summarize_node"]

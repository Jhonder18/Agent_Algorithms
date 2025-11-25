"""
Nodo de resolución de series.
Recibe el JSON de costos con sumatorias y calcula los costos exactos y asintóticos (Big-O).
"""

from app.tools.series_solver import get_series_solver
from app.agents.state import AnalyzerState


def solve_node(state: AnalyzerState) -> dict:
    """
    Resuelve las sumatorias y calcula los costos exactos y asintóticos.
    
    Toma el JSON de costos con sumatorias y devuelve:
    - steps: pasos detallados de la resolución de cada sumatoria
    - exact_costs: costos exactos resueltos (best, avg, worst)
    - asymptotic_bounds: cotas asintóticas (Big-O)
    """
    costs_data = state["costs"]
    
    # Extraer el objeto CostsOut del resultado del nodo anterior
    costs_json = costs_data.get("costs") if isinstance(costs_data, dict) and "costs" in costs_data else costs_data
    
    # Obtener el solucionador de series
    solver = get_series_solver()
    
    # Ejecutar la resolución
    result = solver({"costs": costs_json})
    
    # Extraer solo la solución (sin el wrapper de success/error)
    if isinstance(result, dict) and "solution" in result:
        solve_json = result["solution"]
    else:
        solve_json = result
    
    return {"solution": solve_json}
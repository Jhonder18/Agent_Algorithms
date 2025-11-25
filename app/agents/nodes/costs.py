"""
Nodo de análisis de costos. 
Recibe el AST y el código fuente, y genera expresiones de costos con sumatorias.
"""

from app.tools.cost_model import get_cost_analyzer
from app.tools.ast_parser.ast_parser import ast_parse_lc
from app.agents.state import AnalyzerState


def costs_node(state: AnalyzerState) -> dict:
    """
    Analiza los costos del algoritmo a partir del AST.
    
    Toma el AST generado y el código normalizado, y devuelve un JSON con:
    - per_line: costos línea por línea
    - loops: información de sumatorias y bucles anidados
    - total_cost: expresión total de costos
    """
    pseudocode = state["pseudocode"]
    
    # Parsear el pseudocódigo para obtener el objeto Program
    parse_result = ast_parse_lc.invoke({"pseudocode": pseudocode})
    ast_obj = parse_result.get("ast")
    
    try:
        # Obtener el analizador de costos
        analyzer = get_cost_analyzer()
        
        # Ejecutar el análisis
        result = analyzer({"ast": ast_obj, "source_code": pseudocode})
        
        # Extraer solo los costos (sin el wrapper de success/error)
        if isinstance(result, dict) and "costs" in result:
            costs_json = result["costs"]
        else:
            costs_json = result
        
        return {"costs": costs_json}
    except Exception as e:
        # En caso de error, devolver estructura con error
        print(f"Error en costs_node: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"costs": None}

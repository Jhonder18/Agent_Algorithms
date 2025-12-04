# app/tools/recursion_detector/detector.py
"""
Detector de recursividad en el AST.
Analiza si una función tiene llamadas recursivas directas.
"""

from typing import Dict, List, Any, Optional


class RecursionDetector:
    """Detecta si un programa contiene funciones recursivas."""
    
    def __init__(self):
        self.recursive_functions = []
        self.current_function_name = None
    
    def detect(self, ast_dict: Dict) -> Dict[str, Any]:
        """
        Analiza el AST y detecta funciones recursivas.
        
        Returns:
            Dict con:
            - is_recursive: bool
            - recursive_functions: List[Dict] con info de cada función recursiva
        """
        self.recursive_functions = []
        
        if "functions" not in ast_dict:
            return {
                "is_recursive": False,
                "recursive_functions": []
            }
        
        functions = ast_dict["functions"]
        
        for func in functions:
            func_name = func.get("name")
            if not func_name:
                continue
            
            self.current_function_name = func_name
            recursive_calls = self._find_recursive_calls(func.get("body", {}))
            
            if recursive_calls:
                self.recursive_functions.append({
                    "name": func_name,
                    "calls": recursive_calls
                })
        
        return {
            "is_recursive": len(self.recursive_functions) > 0,
            "recursive_functions": self.recursive_functions
        }
    
    def _find_recursive_calls(self, node: Any, calls: Optional[List] = None) -> List[Dict]:
        """
        Busca llamadas recursivas en un nodo del AST.
        
        Args:
            node: Nodo del AST a analizar
            calls: Lista acumuladora de llamadas encontradas
            
        Returns:
            Lista de diccionarios con información de cada llamada recursiva
        """
        if calls is None:
            calls = []
        
        if not isinstance(node, dict):
            return calls
        
        # Verificar si es un nodo Call o CallStatement
        node_type = node.get("type")
        if node_type in ["Call", "CallStatement"]:
            # En el AST actual, el nombre de la función está directamente en el campo "name"
            call_name = node.get("name")
            if call_name == self.current_function_name:
                # Es una llamada recursiva
                call_info = {
                    "line": node.get("line_start", 0),
                    "args": self._extract_arg_names(node.get("args", []))
                }
                calls.append(call_info)
        
        # Recorrer recursivamente todos los hijos del nodo
        for key, value in node.items():
            if isinstance(value, dict):
                self._find_recursive_calls(value, calls)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._find_recursive_calls(item, calls)
        
        return calls
    
    def _extract_arg_names(self, args: List[Dict]) -> List[str]:
        """
        Extrae representaciones en texto de los argumentos de una llamada.
        
        Args:
            args: Lista de nodos de argumentos
            
        Returns:
            Lista de strings representando cada argumento
        """
        result = []
        for arg in args:
            if not isinstance(arg, dict):
                result.append(str(arg))
                continue
            
            arg_type = arg.get("type")
            
            if arg_type == "Var":
                result.append(arg.get("name", "?"))
            elif arg_type == "Literal":
                result.append(str(arg.get("value", "?")))
            elif arg_type == "BinOp":
                # Para operaciones binarias, crear una representación simple
                left = self._extract_arg_names([arg.get("left", {})])[0] if arg.get("left") else "?"
                right = self._extract_arg_names([arg.get("right", {})])[0] if arg.get("right") else "?"
                op = arg.get("op", "?")
                result.append(f"{left}{op}{right}")
            elif arg_type == "ArrayAccess":
                array = arg.get("array", {})
                index = arg.get("index", {})
                array_name = array.get("name", "?") if isinstance(array, dict) else "?"
                index_str = self._extract_arg_names([index])[0] if index else "?"
                result.append(f"{array_name}[{index_str}]")
            else:
                result.append("?")
        
        return result


def get_recursion_detector() -> RecursionDetector:
    """Retorna una instancia del detector de recursividad."""
    return RecursionDetector()

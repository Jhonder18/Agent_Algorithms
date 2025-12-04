# app/tools/recurrence_analyzer/analyzer.py
"""
Analizador de recurrencias para algoritmos recursivos.
Construye la relación de recurrencia T(n) a partir del AST.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import copy


class RecurrencePattern:
    """Representa un patrón de recurrencia identificado."""
    
    def __init__(self, name: str, a: int, b: Optional[int], f_n: str, form: str, pattern_type: str):
        self.name = name
        self.a = a  # número de llamadas recursivas
        self.b = b  # factor de división (None para decremental)
        self.f_n = f_n  # trabajo no recursivo
        self.form = form  # forma textual T(n) = ...
        self.pattern_type = pattern_type  # 'divide_conquer', 'decremental', 'fibonacci_like', etc.


class RecurrenceAnalyzer:
    """Analiza el AST y construye la relación de recurrencia."""
    
    def __init__(self):
        self.current_function = None
        self.recursive_calls = []
        self.non_recursive_cost = 0
        self.base_case_cost = "O(1)"
        self.full_ast = None  # Guardar el AST completo para buscar funciones auxiliares
    
    def analyze(self, ast_dict: Dict, recursive_function: Dict) -> Dict[str, Any]:
        """
        Analiza una función recursiva y construye su relación de recurrencia.
        
        Args:
            ast_dict: El AST completo del programa
            recursive_function: Info de la función recursiva desde el detector
            
        Returns:
            Dict con la relación de recurrencia y su análisis
        """
        # Guardar el AST completo para poder buscar funciones auxiliares
        self.full_ast = ast_dict
        
        func_name = recursive_function["name"]
        calls = recursive_function["calls"]
        
        print(f"[RECURRENCE_ANALYZER] Analizando función: {func_name}")
        
        # Buscar la función en el AST
        func_ast = self._find_function_in_ast(ast_dict, func_name)
        if not func_ast:
            return {
                "success": False,
                "error": f"No se encontró la función {func_name} en el AST"
            }
        
        # Analizar las llamadas recursivas
        num_calls = len(calls)
        recurrence_info = self._analyze_recursive_calls(calls, func_ast)
        
        # Analizar el trabajo no recursivo
        non_recursive_work = self._estimate_non_recursive_work(func_ast, func_name)
        
        # Identificar el patrón de recurrencia
        pattern = self._identify_pattern(num_calls, recurrence_info, non_recursive_work)
        
        # Construir la relación de recurrencia
        recurrence_form = self._build_recurrence_form(pattern)
        
        return {
            "success": True,
            "function_name": func_name,
            "pattern": pattern,
            "recurrence": {
                "a": pattern["a"],
                "b": pattern["b"],
                "f_n": pattern["f_n"],
                "form": recurrence_form,
                "pattern_type": pattern["pattern_type"]
            },
            "calls_info": calls,
            "base_case": self._find_base_case(func_ast)
        }
    
    def _find_function_in_ast(self, ast_dict: Dict, func_name: str) -> Optional[Dict]:
        """Encuentra una función específica en el AST."""
        functions = ast_dict.get("functions", [])
        for func in functions:
            if func.get("name") == func_name:
                return func
        return None
    
    def _analyze_recursive_calls(self, calls: List[Dict], func_ast: Dict) -> Dict[str, Any]:
        """
        Analiza las llamadas recursivas para determinar cómo reducen el problema.
        
        Returns:
            Dict con información sobre la reducción del problema
        """
        if not calls:
            return {"reduction_type": "none"}
        
        # Examinar los argumentos de todas las llamadas
        all_args_str = " ".join(" ".join(str(a) for a in call["args"]) for call in calls)
        
        # Detectar división explícita
        if any(marker in all_args_str for marker in ["/", "//", "/2", "/ 2"]):
            return {
                "reduction_type": "divide",
                "factor": 2,
                "description": "Divide el problema a la mitad"
            }
        
        # Detectar uso de punto medio (búsqueda binaria, merge sort)
        has_medio = any(keyword in all_args_str.lower() for keyword in ["medio", "mid", "middle"])
        has_range_params = any(keyword in all_args_str.lower() for keyword in ["left", "right", "izq", "der", "inicio", "fin"])
        
        if has_medio and (has_range_params or "-1" in all_args_str or "+1" in all_args_str):
            return {
                "reduction_type": "divide",
                "factor": 2,
                "description": "Divide el problema usando un punto medio (búsqueda binaria o merge sort)"
            }
        
        # Detectar decremental simple (n-1)
        if "-1" in all_args_str and not has_medio:
            # Verificar que no sea búsqueda binaria (que también tiene -1 pero en índices)
            if not has_range_params:
                return {
                    "reduction_type": "decremental",
                    "amount": 1,
                    "description": "Reduce el problema en 1 (factorial, suma recursiva)"
                }
        
        return {
            "reduction_type": "unknown",
            "description": "Patrón de reducción no identificado"
        }
    
    def _estimate_non_recursive_work(self, func_ast: Dict, func_name: str) -> str:
        """
        Calcula la complejidad del trabajo no recursivo usando el CostAnalyzer.
        Elimina las llamadas recursivas y analiza el resto del código.
        
        Returns:
            String representando la complejidad (ej: "O(1)", "O(n)", "O(n^2)")
        """
        try:
            # Crear una copia del AST de la función sin las llamadas recursivas
            func_ast_copy = copy.deepcopy(func_ast)
            
            self._remove_recursive_calls_from_ast(func_ast_copy, func_name)
            
            # Convertir el dict del AST a objetos de AST
            from app.tools.ast_parser.ast_nodes import Program, Function
            
            # Necesitamos incluir funciones auxiliares que sean llamadas
            # Buscar todas las funciones auxiliares en el AST original
            auxiliary_functions = self._find_auxiliary_functions(func_ast_copy, func_name)
            
            # Crear una función temporal para análisis
            # El CostAnalyzer necesita un Program con una Function
            all_functions = [func_ast_copy] + auxiliary_functions
            temp_program_dict = {
                "type": "Program",
                "functions": all_functions
            }
            
            # Convertir a objeto Program
            temp_program = self._dict_to_ast_object(temp_program_dict)
            
            if not temp_program or not temp_program.functions:
                return self._estimate_by_loop_count(func_ast)
            
            # Usar el CostAnalyzer
            from app.tools.cost_model.analyzer import get_cost_analyzer
            analyzer = get_cost_analyzer()
            
            costs = analyzer.analyze(temp_program)
            
            if not costs or not costs.total:
                return self._estimate_by_loop_count(func_ast)
            
            # Extraer el Big-O del worst case
            worst_cost = costs.total.worst
            
            # Simplificar a notación Big-O
            big_o = self._extract_big_o_from_cost(worst_cost)
            
            print(f"[RECURRENCE_ANALYZER] Trabajo no recursivo calculado: {big_o} (de expresión: {worst_cost})")
            
            return big_o
            
        except Exception as e:
            print(f"[RECURRENCE_ANALYZER] Error al calcular trabajo no recursivo: {e}")
            # Fallback al método simple
            return self._estimate_by_loop_count(func_ast)
    
    def _estimate_by_loop_count(self, func_ast: Dict) -> str:
        """Método de fallback: contar bucles."""
        body = func_ast.get("body", {})
        loops = self._count_loops(body)
        
        if loops == 0:
            return "O(1)"
        elif loops == 1:
            return "O(n)"
        elif loops == 2:
            return "O(n^2)"
        else:
            return f"O(n^{loops})"
    
    def _count_loops(self, node: Any) -> int:
        """Cuenta bucles en un nodo del AST."""
        if not isinstance(node, dict):
            return 0
        
        count = 0
        node_type = node.get("type")
        
        if node_type in ["For", "While"]:
            count = 1
            # Buscar bucles anidados
            if node_type == "For":
                body = node.get("body", {})
            else:
                body = node.get("body", {})
            count += self._count_loops(body)
        
        # Recorrer otros nodos
        for key, value in node.items():
            if key != "body" and isinstance(value, dict):
                count += self._count_loops(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        count += self._count_loops(item)
        
        return count
    
    def _identify_pattern(self, num_calls: int, recurrence_info: Dict, work: str) -> Dict[str, Any]:
        """
        Identifica el patrón de recurrencia basándose en el análisis.
        
        Returns:
            Dict con a, b, f(n), y tipo de patrón
        """
        reduction_type = recurrence_info.get("reduction_type", "unknown")
        
        # Patrón: Divide and Conquer
        if reduction_type == "divide":
            factor = recurrence_info.get("factor", 2)
            return {
                "a": num_calls,
                "b": factor,
                "f_n": work,
                "pattern_type": "divide_and_conquer",
                "description": f"Divide y conquista: {num_calls} subproblema(s) de tamaño n/{factor}"
            }
        
        # Patrón: Decremental (n-1)
        elif reduction_type == "decremental":
            amount = recurrence_info.get("amount", 1)
            return {
                "a": num_calls,
                "b": None,  # No es división, es resta
                "f_n": work,
                "pattern_type": "decremental",
                "description": f"Decremental: {num_calls} llamada(s) con n-{amount}"
            }
        
        # Patrón especial: Fibonacci-like (2 llamadas decrementales)
        elif num_calls == 2 and reduction_type == "decremental":
            return {
                "a": 2,
                "b": None,
                "f_n": work,
                "pattern_type": "fibonacci_like",
                "description": "Patrón tipo Fibonacci: T(n-1) + T(n-2)"
            }
        
        # Patrón desconocido
        else:
            return {
                "a": num_calls,
                "b": None,
                "f_n": work,
                "pattern_type": "unknown",
                "description": "Patrón de recurrencia no estándar"
            }
    
    def _build_recurrence_form(self, pattern: Dict) -> str:
        """
        Construye la forma textual de la recurrencia.
        
        Returns:
            String como "T(n) = 2T(n/2) + O(n)"
        """
        a = pattern["a"]
        b = pattern["b"]
        f_n = pattern["f_n"]
        pattern_type = pattern["pattern_type"]
        
        if pattern_type == "divide_and_conquer":
            if a == 1:
                return f"T(n) = T(n/{b}) + {f_n}"
            else:
                return f"T(n) = {a}T(n/{b}) + {f_n}"
        
        elif pattern_type == "decremental":
            if a == 1:
                return f"T(n) = T(n-1) + {f_n}"
            else:
                return f"T(n) = {a}T(n-1) + {f_n}"
        
        elif pattern_type == "fibonacci_like":
            return f"T(n) = T(n-1) + T(n-2) + {f_n}"
        
        else:
            return f"T(n) = {a}T(?) + {f_n}"
    
    def _find_base_case(self, func_ast: Dict) -> Dict[str, Any]:
        """
        Identifica el caso base de la recursión.
        
        Returns:
            Dict con información del caso base
        """
        body = func_ast.get("body", {})
        
        # Buscar el primer if que retorna sin llamadas recursivas
        base_if = self._find_base_case_if(body)
        
        if base_if:
            return {
                "condition": "detectado",
                "cost": "O(1)",
                "description": "Caso base con retorno constante"
            }
        
        return {
            "condition": "no detectado",
            "cost": "O(1)",
            "description": "Se asume caso base constante"
        }
    
    def _find_base_case_if(self, node: Any) -> Optional[Dict]:
        """Busca el if del caso base."""
        if not isinstance(node, dict):
            return None
        
        if node.get("type") == "If":
            # Verificar si el then_block tiene un return
            then_block = node.get("then_block", {})
            if self._has_return(then_block):
                return node
        
        # Buscar en statements del bloque
        if node.get("type") == "Block":
            statements = node.get("statements", [])
            for stmt in statements:
                result = self._find_base_case_if(stmt)
                if result:
                    return result
        
        return None
    
    def _has_return(self, node: Any) -> bool:
        """Verifica si un nodo contiene un return."""
        if not isinstance(node, dict):
            return False
        
        if node.get("type") == "Return":
            return True
        
        if node.get("type") == "Block":
            statements = node.get("statements", [])
            return any(self._has_return(stmt) for stmt in statements)
        
        return False
    
    def _remove_recursive_calls_from_ast(self, node: Any, func_name: str) -> None:
        """
        Elimina las llamadas recursivas del AST (modifica in-place).
        Reemplaza las llamadas recursivas con statements vacíos.
        """
        if not isinstance(node, dict):
            return
        
        node_type = node.get("type")
        
        # Si es un bloque, filtrar sus statements
        if node_type == "Block":
            statements = node.get("statements", [])
            filtered_statements = []
            
            for stmt in statements:
                # Si es una llamada recursiva, omitirla
                if self._is_recursive_call(stmt, func_name):
                    continue
                # Si es un return con llamada recursiva, convertir a return simple
                elif stmt.get("type") == "Return":
                    value = stmt.get("value")
                    if value and self._contains_recursive_call(value, func_name):
                        # Omitir el return recursivo
                        continue
                
                # Recursivamente limpiar el statement
                self._remove_recursive_calls_from_ast(stmt, func_name)
                filtered_statements.append(stmt)
            
            node["statements"] = filtered_statements
        
        # Recorrer recursivamente otros nodos
        for key, value in list(node.items()):
            if key == "statements":
                continue  # Ya procesado arriba
            if isinstance(value, dict):
                self._remove_recursive_calls_from_ast(value, func_name)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._remove_recursive_calls_from_ast(item, func_name)
    
    def _is_recursive_call(self, node: Dict, func_name: str) -> bool:
        """Verifica si un nodo es una llamada recursiva directa."""
        if not isinstance(node, dict):
            return False
        
        node_type = node.get("type")
        if node_type in ["Call", "CallStatement"]:
            return node.get("name") == func_name
        
        return False
    
    def _contains_recursive_call(self, node: Any, func_name: str) -> bool:
        """Verifica si un nodo contiene una llamada recursiva en cualquier lugar."""
        if not isinstance(node, dict):
            return False
        
        if self._is_recursive_call(node, func_name):
            return True
        
        # Buscar recursivamente
        for key, value in node.items():
            if isinstance(value, dict):
                if self._contains_recursive_call(value, func_name):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and self._contains_recursive_call(item, func_name):
                        return True
        
        return False
    
    def _dict_to_ast_object(self, ast_dict: Dict) -> Any:
        """
        Convierte un dict de AST a objetos de AST.
        Usa el parser existente para reconstruir los objetos.
        """
        try:
            from app.tools.ast_parser.ast_nodes import (
                Program, Function, Block, 
                For, While, If, Assign, Return, ExprStmt,
                Var, Literal, BinOp, Compare, ArrayAccess
            )
            
            if ast_dict.get("type") == "Program":
                functions = [self._dict_to_function(f) for f in ast_dict.get("functions", [])]
                return Program(functions=functions)
            
            return None
            
        except Exception as e:
            print(f"[RECURRENCE_ANALYZER] Error convirtiendo dict a AST: {e}")
            return None
    
    def _dict_to_function(self, func_dict: Dict) -> Any:
        """Convierte un dict de función a objeto Function."""
        from app.tools.ast_parser.ast_nodes import Function, Param
        
        name = func_dict.get("name", "")
        params_list = func_dict.get("params", [])
        
        # Los parámetros pueden ser dicts o strings
        params = []
        for p in params_list:
            if isinstance(p, dict):
                params.append(Param(name=p.get("name", "")))
            elif isinstance(p, str):
                params.append(Param(name=p))
            else:
                params.append(Param(name="x"))
        
        body = self._dict_to_stmt(func_dict.get("body", {}))
        
        return Function(name=name, params=params, body=body)
    
    def _dict_to_stmt(self, stmt_dict: Dict) -> Any:
        """Convierte un dict de statement a objeto Statement."""
        from app.tools.ast_parser.ast_nodes import (
            Block, For, While, If, Assign, Return, ExprStmt
        )
        
        stmt_type = stmt_dict.get("type", "")
        
        if stmt_type == "Block":
            statements = [self._dict_to_stmt(s) for s in stmt_dict.get("statements", [])]
            return Block(statements=statements)
        
        elif stmt_type == "For":
            # var puede ser un string o un dict
            var_data = stmt_dict.get("var", "i")
            if isinstance(var_data, dict):
                var = var_data.get("name", "i")
            else:
                var = str(var_data)
            
            start = self._dict_to_expr(stmt_dict.get("start", {}))
            end = self._dict_to_expr(stmt_dict.get("end", {}))
            body = self._dict_to_stmt(stmt_dict.get("body", {}))
            return For(var=var, start=start, end=end, body=body)
        
        elif stmt_type == "While":
            cond = self._dict_to_expr(stmt_dict.get("cond", {}))
            body = self._dict_to_stmt(stmt_dict.get("body", {}))
            return While(cond=cond, body=body)
        
        elif stmt_type == "If":
            cond = self._dict_to_expr(stmt_dict.get("cond", {}))
            then_block = self._dict_to_stmt(stmt_dict.get("then_block", {}))
            else_block = self._dict_to_stmt(stmt_dict.get("else_block")) if stmt_dict.get("else_block") else None
            return If(cond=cond, then_block=then_block, else_block=else_block)
        
        elif stmt_type == "Assign":
            target = self._dict_to_expr(stmt_dict.get("target", {}))
            value = self._dict_to_expr(stmt_dict.get("value", {}))
            return Assign(target=target, value=value)
        
        elif stmt_type == "Return":
            value = self._dict_to_expr(stmt_dict.get("value")) if stmt_dict.get("value") else None
            return Return(value=value)
        
        elif stmt_type == "ExprStmt":
            expr = self._dict_to_expr(stmt_dict.get("expr", {}))
            return ExprStmt(expr=expr)
        
        # Default: return a simple block
        return Block(statements=[])
    
    def _dict_to_expr(self, expr_dict: Any) -> Any:
        """Convierte un dict de expresión a objeto Expression."""
        if not isinstance(expr_dict, dict):
            return None
        
        from app.tools.ast_parser.ast_nodes import (
            Var, Literal, BinOp, Compare, ArrayAccess
        )
        
        expr_type = expr_dict.get("type", "")
        
        if expr_type == "Var":
            return Var(name=expr_dict.get("name", "x"))
        
        elif expr_type == "Literal":
            return Literal(value=expr_dict.get("value", 0))
        
        elif expr_type == "BinOp":
            left = self._dict_to_expr(expr_dict.get("left", {}))
            right = self._dict_to_expr(expr_dict.get("right", {}))
            op = expr_dict.get("op", "+")
            return BinOp(left=left, op=op, right=right)
        
        elif expr_type == "Compare":
            left = self._dict_to_expr(expr_dict.get("left", {}))
            right = self._dict_to_expr(expr_dict.get("right", {}))
            op = expr_dict.get("op", "==")
            return Compare(left=left, op=op, right=right)
        
        elif expr_type == "ArrayAccess":
            array = self._dict_to_expr(expr_dict.get("array", {}))
            index = self._dict_to_expr(expr_dict.get("index", {}))
            return ArrayAccess(array=array, index=index)
        
        # Default
        return Var(name="x")
    
    def _extract_big_o_from_cost(self, cost_str: str) -> str:
        """
        Extrae la notación Big-O de una expresión de costo.
        Ejemplos: "n" -> "O(n)", "n**2" -> "O(n^2)", "1" -> "O(1)"
        """
        if not cost_str or cost_str == "0":
            return "O(1)"
        
        cost_str = str(cost_str).strip()
        
        # Si ya está en formato O(...)
        if cost_str.startswith("O("):
            return cost_str
        
        # Detectar patrones comunes
        if "**2" in cost_str or "^2" in cost_str:
            return "O(n^2)"
        elif "**3" in cost_str or "^3" in cost_str:
            return "O(n^3)"
        elif "*n" in cost_str or "n*" in cost_str or " n" in cost_str:
            return "O(n)"
        # Detectar expresiones con variables de rango (right - left es O(n))
        elif "right" in cost_str or "left" in cost_str or "end" in cost_str or "start" in cost_str:
            return "O(n)"
        elif cost_str in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "c"]:
            return "O(1)"
        elif "n" in cost_str.lower():
            # Tiene n pero no es cuadrático
            return "O(n)"
        else:
            # Si hay solo constantes, es O(1)
            try:
                float(cost_str)
                return "O(1)"
            except:
                return "O(1)"
    
    def _find_auxiliary_functions(self, func_ast_cleaned: Dict, current_func_name: str) -> List[Dict]:
        """
        Encuentra todas las funciones auxiliares llamadas desde func_ast_cleaned.
        Busca en el AST completo (self.full_ast) las definiciones de esas funciones.
        
        Returns:
            Lista de AST de funciones auxiliares
        """
        if not self.full_ast:
            return []
        
        # Encontrar todas las llamadas a funciones en el AST limpio
        called_functions = set()
        self._collect_function_calls(func_ast_cleaned, called_functions)
        
        # Excluir la función actual (que ya está incluida)
        called_functions.discard(current_func_name)
        
        # Buscar las definiciones de esas funciones en el AST completo
        auxiliary_funcs = []
        all_functions = self.full_ast.get("functions", [])
        
        for aux_name in called_functions:
            for func in all_functions:
                if func.get("name") == aux_name:
                    auxiliary_funcs.append(func)
                    print(f"[RECURRENCE_ANALYZER] Función auxiliar encontrada: {aux_name}")
                    break
        
        return auxiliary_funcs
    
    def _collect_function_calls(self, node: Any, collected: set) -> None:
        """Recolecta recursivamente nombres de todas las funciones llamadas."""
        if not isinstance(node, dict):
            return
        
        node_type = node.get("type")
        
        # Si es una llamada, agregar el nombre
        if node_type in ["Call", "CallStatement"]:
            func_name = node.get("name")
            if func_name:
                collected.add(func_name)
        
        # Recursión en todos los hijos
        for key, value in node.items():
            if isinstance(value, dict):
                self._collect_function_calls(value, collected)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._collect_function_calls(item, collected)


def get_recurrence_analyzer() -> RecurrenceAnalyzer:
    """Retorna una instancia del analizador de recurrencias."""
    return RecurrenceAnalyzer()

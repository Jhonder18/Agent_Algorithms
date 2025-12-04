from typing import List, Dict, Any, Tuple, Optional
import re


class SimpleASTParser:
    """Parser simple que procesa pseudocódigo línea por línea"""
    
    def __init__(self):
        self.functions = []
        self.current_function = None
        self.function_calls = {}
        
    def parse(self, pseudocode: str) -> List[Dict]:
        """Parsea el pseudocódigo y genera el AST"""
        lines = pseudocode.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Ignorar líneas vacías y comentarios
            if not line or line.startswith('►'):
                i += 1
                continue
            
            # Detectar definición de función
            if self._is_function_def(line):
                i = self._parse_function(lines, i)
            else:
                i += 1
                
        return self.functions
    
    def _is_function_def(self, line: str) -> bool:
        """Detecta si una línea es una definición de función"""
        # Debe tener paréntesis y no ser una llamada, if, while o for
        if '(' not in line or ')' not in line:
            return False
        if any(keyword in line.lower() for keyword in ['call', 'if', 'while', 'for']):
            return False
        return True
    
    def _parse_function(self, lines: List[str], start_idx: int) -> int:
        """Parsea una función completa"""
        line = lines[start_idx].strip()
        
        # Extraer nombre y parámetros
        match = re.match(r'(\w+)\s*\((.*?)\)', line)
        if not match:
            return start_idx + 1
            
        func_name = match.group(1)
        params_str = match.group(2)
        
        self.current_function = func_name
        self.function_calls[func_name] = []
        
        # Parsear parámetros
        variables = self._parse_parameters(params_str)
        
        # Buscar el begin
        i = start_idx + 1
        while i < len(lines) and 'begin' not in lines[i].strip().lower():
            i += 1
        
        if i >= len(lines):
            return start_idx + 1
            
        i += 1  # Saltar el begin
        
        # Parsear el cuerpo hasta encontrar el end correspondiente
        body_lines = []
        depth = 1
        
        while i < len(lines) and depth > 0:
            line = lines[i].strip().lower()
            if line == 'begin':
                depth += 1
            elif line == 'end':
                depth -= 1
                if depth == 0:
                    break
            body_lines.append(lines[i])
            i += 1
        
        # Construir el código
        code = self._parse_body(body_lines, variables)
        
        # Crear la estructura de la función
        func_structure = {
            func_name: {
                "variables": variables,
                "code": code
            }
        }
        
        self.functions.append(func_structure)
        self.current_function = None
        
        return i + 1
    
    def _parse_parameters(self, params_str: str) -> List[Tuple[str, str]]:
        """Parsea los parámetros de una función"""
        variables = []
        
        if not params_str.strip():
            return variables
        
        params = [p.strip() for p in params_str.split(',')]
        
        for param in params:
            # Detectar arrays: nombre[dimension]
            array_match = re.match(r'(\w+)\[([^\]]+)\]', param)
            if array_match:
                var_name = array_match.group(1)
                dimension = f"[{array_match.group(2)}]"
                variables.append((var_name, dimension))
            else:
                # Variable escalar
                var_name = param.strip()
                if var_name:
                    variables.append((var_name, ""))
        
        return variables
    
    def _parse_body(self, lines: List[str], variables: List[Tuple[str, str]]) -> Dict:
        """Parsea el cuerpo de una función o bloque"""
        code = {}
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Ignorar líneas vacías y comentarios
            if not line or line.startswith('►'):
                i += 1
                continue
            
            line_lower = line.lower()
            
            # Detectar declaraciones de variables (líneas que solo tienen nombre[dim])
            if self._is_var_declaration(line):
                var_info = self._extract_var_from_declaration(line)
                if var_info:
                    variables.append(var_info)
                i += 1
                continue
            
            # Detectar for loop
            if line_lower.startswith('for'):
                result, new_i = self._parse_for_loop(lines, i)
                if result:
                    code.update(result)
                i = new_i
                continue
            
            # Detectar while loop
            if line_lower.startswith('while'):
                result, new_i = self._parse_while_loop(lines, i)
                if result:
                    code.update(result)
                i = new_i
                continue
            
            # Detectar if statement
            if line_lower.startswith('if'):
                result, new_i = self._parse_if_statement(lines, i)
                if result:
                    # Añadir tanto el if como el else si existe
                    for key, value in result.items():
                        code[key] = value
                i = new_i
                continue
            
            # Detectar llamada a función
            if line_lower.startswith('call'):
                func_call = self._parse_function_call(line)
                if func_call:
                    code["func_call"] = func_call
                i += 1
                continue
            
            i += 1
        
        return code
    
    def _is_var_declaration(self, line: str) -> bool:
        """Detecta si una línea es una declaración de variable"""
        # Una declaración de variable es una línea que tiene formato nombre[dim] sin operadores
        if '🡨' in line or 'call' in line.lower():
            return False
        
        # Verificar si tiene formato de array sin nada más
        return bool(re.match(r'^\w+\[[^\]]+\]$', line.strip()))
    
    def _extract_var_from_declaration(self, line: str) -> Optional[Tuple[str, str]]:
        """Extrae información de variable de una declaración"""
        match = re.match(r'^(\w+)\[([^\]]+)\]$', line.strip())
        if match:
            return (match.group(1), f"[{match.group(2)}]")
        return None
    
    def _parse_for_loop(self, lines: List[str], start_idx: int) -> Tuple[Dict, int]:
        """Parsea un bucle for"""
        line = lines[start_idx].strip()
        
        # Extraer la expresión 'to': for i 🡨 1 to n do
        match = re.search(r'to\s+([^\s]+)', line, re.IGNORECASE)
        if not match:
            return {}, start_idx + 1
        
        to_expr = match.group(1).replace('do', '').strip()
        
        # Buscar el begin
        i = start_idx + 1
        while i < len(lines) and 'begin' not in lines[i].strip().lower():
            i += 1
        
        if i >= len(lines):
            return {}, start_idx + 1
        
        i += 1  # Saltar el begin
        
        # Extraer el cuerpo del for
        body_lines = []
        depth = 1
        
        while i < len(lines) and depth > 0:
            line_lower = lines[i].strip().lower()
            if line_lower == 'begin':
                depth += 1
            elif line_lower == 'end':
                depth -= 1
                if depth == 0:
                    break
            body_lines.append(lines[i])
            i += 1
        
        # Parsear el cuerpo
        body_code = self._parse_body(body_lines, [])
        
        key = ("for", to_expr)
        return {key: body_code}, i + 1
    
    def _parse_while_loop(self, lines: List[str], start_idx: int) -> Tuple[Dict, int]:
        """Parsea un bucle while"""
        line = lines[start_idx].strip()
        
        # Extraer la condición: while (condicion) do
        match = re.search(r'while\s+\(?([^)]+)\)?', line, re.IGNORECASE)
        if not match:
            return {}, start_idx + 1
        
        condition = match.group(1).strip().replace('do', '').replace(')', '').strip()
        
        # Buscar el begin
        i = start_idx + 1
        while i < len(lines) and 'begin' not in lines[i].strip().lower():
            i += 1
        
        if i >= len(lines):
            return {}, start_idx + 1
        
        i += 1  # Saltar el begin
        
        # Extraer el cuerpo
        body_lines = []
        depth = 1
        
        while i < len(lines) and depth > 0:
            line_lower = lines[i].strip().lower()
            if line_lower == 'begin':
                depth += 1
            elif line_lower == 'end':
                depth -= 1
                if depth == 0:
                    break
            body_lines.append(lines[i])
            i += 1
        
        body_code = self._parse_body(body_lines, [])
        
        key = ("while", condition)
        return {key: body_code}, i + 1
    
    def _parse_if_statement(self, lines: List[str], start_idx: int) -> Tuple[Dict, int]:
        """Parsea una declaración if"""
        line = lines[start_idx].strip()
        
        # Extraer la condición: if (condicion) then
        match = re.search(r'if\s+\(?([^)]+)\)?', line, re.IGNORECASE)
        if not match:
            return {}, start_idx + 1
        
        condition = match.group(1).strip().replace('then', '').replace(')', '').strip()
        
        # Buscar el begin del then
        i = start_idx + 1
        while i < len(lines) and 'begin' not in lines[i].strip().lower():
            i += 1
        
        if i >= len(lines):
            return {}, start_idx + 1
        
        i += 1  # Saltar el begin
        
        # Extraer el cuerpo del then
        then_lines = []
        depth = 1
        
        while i < len(lines) and depth > 0:
            line_lower = lines[i].strip().lower()
            if line_lower == 'begin':
                depth += 1
            elif line_lower == 'end':
                depth -= 1
                if depth == 0:
                    break
            then_lines.append(lines[i])
            i += 1
        
        then_code = self._parse_body(then_lines, [])
        
        i += 1  # Saltar el end
        
        # Crear el resultado con el if
        result = {}
        key = ("if", condition)
        result[key] = then_code
        
        # Verificar si hay else
        if i < len(lines) and lines[i].strip().lower().startswith('else'):
            i += 1  # Saltar else
            
            # Buscar el begin del else
            while i < len(lines) and 'begin' not in lines[i].strip().lower():
                i += 1
            
            if i < len(lines):
                i += 1  # Saltar el begin
                
                else_lines = []
                depth = 1
                
                while i < len(lines) and depth > 0:
                    line_lower = lines[i].strip().lower()
                    if line_lower == 'begin':
                        depth += 1
                    elif line_lower == 'end':
                        depth -= 1
                        if depth == 0:
                            break
                    else_lines.append(lines[i])
                    i += 1
                
                else_code = self._parse_body(else_lines, [])
                # Añadir el else al resultado
                result["else"] = else_code
                i += 1  # Saltar el end del else
        
        return result, i
    
    def _parse_function_call(self, line: str) -> Optional[Tuple[str, List[Tuple[str, str]]]]:
        """Parsea una llamada a función"""
        # CALL func_name(arg1, arg2, ...)
        match = re.search(r'call\s+(\w+)\s*\((.*?)\)', line, re.IGNORECASE)
        if not match:
            return None
        
        func_name = match.group(1)
        args_str = match.group(2)
        
        # Registrar la llamada para detectar recursividad
        if self.current_function:
            self.function_calls[self.current_function].append(func_name)
        
        # Parsear argumentos
        args = []
        if args_str.strip():
            arg_list = [a.strip() for a in args_str.split(',')]
            
            for arg in arg_list:
                # Detectar arrays: nombre[dimension]
                array_match = re.match(r'(\w+)\[([^\]]+)\]', arg)
                if array_match:
                    var_name = array_match.group(1)
                    dimension = f"[{array_match.group(2)}]"
                    args.append((var_name, dimension))
                else:
                    # Variable escalar
                    var_name = arg.strip()
                    if var_name:
                        args.append((var_name, ""))
        
        return (func_name, args)
    
    def is_recursive(self) -> bool:
        """Determina si alguna función es recursiva"""
        for func_name, calls in self.function_calls.items():
            if func_name in calls:
                return True
        return False


def generate_ast(pseudocode: str) -> Dict[str, List]:
    """Genera el AST a partir del pseudocódigo normalizado."""
    
    parser = SimpleASTParser()
    
    try:
        # Parsear el pseudocódigo
        estructura_codigo = parser.parse(pseudocode)
        
        # Crear el output
        ast_output = {
            "ast": estructura_codigo
        }
        
    except Exception as e:
        # Si hay error en el parsing, guardar el error
        print(f"Error al parsear: {e}")
        ast_output = {
            "ast": []
        }
    
    return ast_output
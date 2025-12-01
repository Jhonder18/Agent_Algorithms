import re
from typing import Dict, List, Tuple, Any

def parse_pseudocode(input_text: str) -> List[Dict]:
    lines = input_text.strip().split('\n')
    functions = []
    current_function = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detectar declaración de función
        if line and not line.startswith('#') and '(' in line and ')' in line and i + 1 < len(lines) and lines[i + 1].strip() == 'begin':
            func_match = re.match(r'(\w+)\((.*?)\)', line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                
                current_function = {
                    func_name: {
                        "variables": parse_variables(params),
                        "code": {}
                    }
                }
                i += 2  # Saltar 'begin'
                i = parse_block(lines, i, current_function[func_name]["code"])
                functions.append(current_function)
                current_function = None
        i += 1
    
    return functions

def parse_variables(params: str) -> List[Tuple[str, str]]:
    if not params.strip():
        return []
    
    variables = []
    for param in params.split(','):
        param = param.strip()
        if '[' in param:
            match = re.match(r'(\w+)(\[.*?\])', param)
            if match:
                variables.append((match.group(1), match.group(2)))
        else:
            variables.append((param, ""))
    return variables

def parse_block(lines: List[str], start_idx: int, parent_dict: Dict) -> int:
    i = start_idx
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line == 'end':
            return i + 1
        
        # FOR
        if line.startswith('for'):
            match = re.search(r'for\s+\w+\s+🡨\s+\d+\s+to\s+(.+?)\s+do', line)
            if match:
                iterations = match.group(1).strip()
                key = ("for", iterations)
                parent_dict[key] = {}
                i = parse_block(lines, i + 2, parent_dict[key])  # Saltar 'begin'
                continue
        
        # WHILE
        if line.startswith('while'):
            match = re.search(r'while\s+\((.*?)\)\s+do', line)
            if match:
                condition = match.group(1).strip()
                key = ("while", condition)
                parent_dict[key] = {}
                i = parse_block(lines, i + 2, parent_dict[key])
                continue
        
        # IF
        if line.startswith('If'):
            match = re.search(r'If\s+\((.*?)\)\s+then', line)
            if match:
                condition = match.group(1).strip()
                key = ("if", condition)
                parent_dict[key] = {}
                i = parse_block(lines, i + 2, parent_dict[key])
                continue
        
        # ELSE
        if line == 'else':
            parent_dict["else"] = {}
            i = parse_block(lines, i + 2, parent_dict["else"])
            continue
        
        # CALL
        if line.startswith('CALL'):
            match = re.search(r'CALL\s+(\w+)\((.*?)\)', line)
            if match:
                func_name = match.group(1)
                params = match.group(2)
                parent_dict["func_call"] = (func_name, parse_variables(params))
        
        i += 1
    
    return i

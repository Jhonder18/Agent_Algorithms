"""
Herramientas (Tools) para el análisis de algoritmos recursivos.
Implementa resolución de recurrencias y generación de diagramas.
"""
from langchain.tools import tool
from sympy import symbols, Function, rsolve, simplify, log, sqrt, Rational, oo
from sympy import sympify, Symbol, Pow
from typing import Dict, Any, List, Optional
import re
import math


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES Y CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

# Clasificación de ecuaciones según el PDF ADA_24A
RECURRENCE_TYPES = {
    "F0": "T(n) = T(n/b) + f(n)",           # DyV simple
    "F1": "T(n) = aT(n/b) + f(n)",          # DyV general (Master Theorem)
    "F2": "T(n) = T(n/b) + T(n/c) + f(n)",  # DyV múltiple
    "F3": "T(n) = T(n/b) + ... + T(n/z) + f(n)",  # DyV múltiple generalizado
    "F4": "T(n) = T(n-b) + f(n)",           # RyV (Resta y Vencerás)
    "F5": "T(n) = aT(n-b) + f(n)",          # RysV (Resta y serás Vencido)
    "F6": "T(n) = aT(n-b) + cT(n-d) + f(n)", # RysV generalizado (Fibonacci)
}

# Métodos aplicables a cada tipo
METHOD_APPLICABILITY = {
    "iteration": ["F4", "F5", "F0", "F1"],
    "recursion_tree": ["F2", "F3", "F6", "F5", "F1", "F0"],
    "master": ["F1", "F0"],
    "substitution": ["F5", "F6", "F4", "F2", "F3", "F1", "F0"],
    "characteristic": ["F5", "F6", "F4"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def parse_recurrence(recurrence: str) -> Dict[str, Any]:
    """
    Parsea una ecuación de recurrencia y extrae sus parámetros.
    
    Ejemplos soportados:
    - "T(n) = 2T(n/2) + n"      -> a=2, b=2, f_n="n", tipo=divide_and_conquer
    - "T(n) = T(n-1) + 1"       -> a=1, b=1, f_n="1", tipo=decrease_and_conquer
    - "T(n) = T(n-1) + T(n-2)"  -> tipo=multiple_recursive (Fibonacci)
    - "T(n) = 2T(n-1) + 1"      -> a=2, b=1, f_n="1", tipo=decrease_and_lose
    """
    result = {
        "a": 1,
        "b": 1,
        "f_n": "1",
        "recurrence_type": "unknown",
        "classification": "unknown"
    }
    
    # Normalizar la entrada
    rec = recurrence.replace(" ", "").lower()
    
    # Patrón para T(n) = aT(n/b) + f(n) [Divide and Conquer]
    dyv_pattern = r't\(n\)=(\d*)t\(n/(\d+)\)\+(.+)'
    match = re.match(dyv_pattern, rec)
    if match:
        a = int(match.group(1)) if match.group(1) else 1
        b = int(match.group(2))
        f_n = match.group(3)
        result.update({
            "a": a,
            "b": b,
            "f_n": f_n,
            "recurrence_type": "divide_and_conquer",
            "classification": "F1" if a > 1 else "F0"
        })
        return result
    
    # Patrón para T(n) = aT(n-b) + f(n) [Decrease and Conquer/Lose]
    ryv_pattern = r't\(n\)=(\d*)t\(n-(\d+)\)\+(.+)'
    match = re.match(ryv_pattern, rec)
    if match:
        a = int(match.group(1)) if match.group(1) else 1
        b = int(match.group(2))
        f_n = match.group(3)
        rec_type = "decrease_and_lose" if a > 1 else "decrease_and_conquer"
        classification = "F5" if a > 1 else "F4"
        result.update({
            "a": a,
            "b": b,
            "f_n": f_n,
            "recurrence_type": rec_type,
            "classification": classification
        })
        return result
    
    # Patrón para Fibonacci: T(n) = T(n-1) + T(n-2) + f(n)
    fib_pattern = r't\(n\)=t\(n-1\)\+t\(n-2\)(?:\+(.+))?'
    match = re.match(fib_pattern, rec)
    if match:
        f_n = match.group(1) if match.group(1) else "0"
        result.update({
            "a": 2,  # Dos llamadas recursivas (una con n-1, otra con n-2)
            "b": 1,
            "f_n": f_n,
            "recurrence_type": "multiple_recursive",
            "classification": "F6"
        })
        return result
    
    return result


def classify_f_n(f_n: str, b: int) -> Dict[str, Any]:
    """
    Clasifica f(n) para determinar qué caso del Master Theorem aplica.
    Retorna el exponente k tal que f(n) = O(n^k) o identificadores especiales.
    """
    f_n = f_n.lower().strip()
    
    # Casos comunes
    if f_n in ["1", "c", "o(1)", "θ(1)"]:
        return {"type": "constant", "k": 0}
    
    if f_n in ["n", "o(n)", "θ(n)"]:
        return {"type": "linear", "k": 1}
    
    if f_n in ["n^2", "n*n", "o(n^2)", "θ(n^2)"]:
        return {"type": "quadratic", "k": 2}
    
    if "log" in f_n and "n" in f_n:
        if f_n in ["logn", "log(n)", "o(logn)", "θ(logn)"]:
            return {"type": "logarithmic", "k": 0, "log_factor": 1}
        if f_n in ["nlogn", "n*logn", "n*log(n)", "o(nlogn)", "θ(nlogn)"]:
            return {"type": "linearithmic", "k": 1, "log_factor": 1}
    
    # Intentar parsear n^k
    power_match = re.match(r'n\^(\d+)', f_n)
    if power_match:
        return {"type": "polynomial", "k": int(power_match.group(1))}
    
    return {"type": "unknown", "k": None}


def apply_master_theorem(a: int, b: int, f_n: str) -> Dict[str, Any]:
    """
    Aplica el Teorema Maestro para resolver T(n) = aT(n/b) + f(n).
    
    Casos del Master Theorem:
    1. Si f(n) = O(n^c) donde c < log_b(a): T(n) = Θ(n^(log_b(a)))
    2. Si f(n) = Θ(n^c) donde c = log_b(a): T(n) = Θ(n^c * log(n))
    3. Si f(n) = Ω(n^c) donde c > log_b(a): T(n) = Θ(f(n))
    """
    result = {
        "applicable": True,
        "case": 0,
        "steps": [],
        "result": ""
    }
    
    # Calcular log_b(a)
    log_b_a = math.log(a, b) if b > 1 else 0
    result["steps"].append(f"Paso 1: Identificamos a={a}, b={b}, f(n)={f_n}")
    result["steps"].append(f"Paso 2: Calculamos log_b(a) = log_{b}({a}) = {log_b_a:.4f}")
    
    # Clasificar f(n)
    f_info = classify_f_n(f_n, b)
    k = f_info.get("k")
    
    if k is None:
        result["applicable"] = False
        result["steps"].append(f"No se pudo clasificar f(n) = {f_n} automáticamente")
        return result
    
    result["steps"].append(f"Paso 3: f(n) = {f_n} tiene orden n^{k}")
    
    # Determinar el caso
    epsilon = 0.0001  # Tolerancia para comparaciones
    
    if k < log_b_a - epsilon:
        # Caso 1
        result["case"] = 1
        complexity = f"n^(log_{b}({a}))"
        if log_b_a == int(log_b_a):
            complexity = f"n^{int(log_b_a)}"
        result["result"] = f"Θ({complexity})"
        result["steps"].append(f"Paso 4: Como {k} < {log_b_a:.4f}, aplica Caso 1 del Master Theorem")
        result["steps"].append(f"Paso 5: Por lo tanto T(n) = {result['result']}")
        
    elif abs(k - log_b_a) < epsilon:
        # Caso 2
        result["case"] = 2
        if k == 0:
            result["result"] = "Θ(log n)"
        elif k == 1:
            result["result"] = "Θ(n log n)"
        else:
            result["result"] = f"Θ(n^{k} log n)"
        result["steps"].append(f"Paso 4: Como {k} ≈ {log_b_a:.4f}, aplica Caso 2 del Master Theorem")
        result["steps"].append(f"Paso 5: Por lo tanto T(n) = {result['result']}")
        
    else:
        # Caso 3
        result["case"] = 3
        result["result"] = f"Θ({f_n})"
        result["steps"].append(f"Paso 4: Como {k} > {log_b_a:.4f}, aplica Caso 3 del Master Theorem")
        result["steps"].append(f"Paso 5: Por lo tanto T(n) = {result['result']}")
    
    return result


def solve_by_iteration(a: int, b: int, f_n: str, rec_type: str) -> Dict[str, Any]:
    """
    Resuelve la recurrencia por el método de iteración/expansión.
    """
    result = {
        "applicable": True,
        "steps": [],
        "result": ""
    }
    
    if rec_type == "decrease_and_conquer":
        # T(n) = T(n-b) + f(n)
        result["steps"].append(f"T(n) = T(n-{b}) + {f_n}")
        result["steps"].append(f"T(n-{b}) = T(n-{2*b}) + {f_n}")
        result["steps"].append(f"...")
        result["steps"].append(f"Sustituyendo: T(n) = T(n-k·{b}) + k·{f_n}")
        result["steps"].append(f"La recursión termina cuando n - k·{b} = caso base")
        result["steps"].append(f"Por lo tanto k = n/{b} iteraciones")
        
        if f_n in ["1", "c", "o(1)"]:
            result["result"] = "Θ(n)"
        elif f_n in ["n", "o(n)"]:
            result["result"] = "Θ(n²)"
        else:
            result["result"] = f"Θ(n · {f_n})"
            
    elif rec_type == "divide_and_conquer":
        # T(n) = aT(n/b) + f(n)
        result["steps"].append(f"T(n) = {a}T(n/{b}) + {f_n}")
        result["steps"].append(f"T(n/{b}) = {a}T(n/{b**2}) + f(n/{b})")
        result["steps"].append(f"...")
        result["steps"].append(f"Expandiendo k niveles: T(n) = {a}^k · T(n/{b}^k) + Σ {a}^i · f(n/{b}^i)")
        result["steps"].append(f"La recursión termina cuando n/{b}^k = 1, es decir k = log_{b}(n)")
        
        # Aplicar Master Theorem para el resultado final
        master = apply_master_theorem(a, b, f_n)
        if master["applicable"]:
            result["result"] = master["result"]
        else:
            result["result"] = f"Θ(n^(log_{b}({a}))) o Θ({f_n}) dependiendo de f(n)"
    
    return result


def generate_recursion_tree_diagram(a: int, b: int, f_n: str, levels: int = 4) -> str:
    """
    Genera un diagrama Mermaid del árbol de recursión.
    """
    lines = ["graph TD"]
    lines.append("    classDef level0 fill:#e1f5fe")
    lines.append("    classDef level1 fill:#b3e5fc")
    lines.append("    classDef level2 fill:#81d4fa")
    lines.append("    classDef level3 fill:#4fc3f7")
    
    node_id = 0
    
    def get_node_id():
        nonlocal node_id
        node_id += 1
        return f"N{node_id}"
    
    def add_level(parent_id: str, size: str, level: int, parent_label: str = None):
        if level >= levels:
            return
        
        current_id = get_node_id()
        label = f"T({size})"
        cost = f_n.replace("n", f"({size})")
        
        if parent_id:
            lines.append(f"    {parent_id} --> {current_id}[\"{label}<br/>costo: {cost}\"]")
        else:
            lines.append(f"    {current_id}[\"{label}<br/>costo: {cost}\"]")
        
        lines.append(f"    class {current_id} level{min(level, 3)}")
        
        # Generar hijos
        if level < levels - 1:
            for i in range(a):
                if b > 1:
                    child_size = f"{size}/{b}"
                else:
                    child_size = f"{size}-1"
                add_level(current_id, child_size, level + 1)
    
    add_level(None, "n", 0)
    
    # Agregar resumen de costos por nivel
    lines.append("")
    lines.append("    subgraph Costos[\"Costo por Nivel\"]")
    for i in range(min(levels, 4)):
        if b > 1:
            nodes_at_level = a ** i
            size = f"n/{b**i}" if i > 0 else "n"
        else:
            nodes_at_level = a ** i
            size = f"n-{i}" if i > 0 else "n"
        cost = f"{nodes_at_level} × {f_n.replace('n', size)}"
        lines.append(f"        L{i}[\"Nivel {i}: {cost}\"]")
    lines.append("    end")
    
    return "\n".join(lines)


def calculate_recursion_tree_complexity(a: int, b: int, f_n: str) -> Dict[str, Any]:
    """
    Calcula la complejidad usando el método del árbol de recursión.
    """
    result = {
        "steps": [],
        "levels": [],
        "height": "",
        "total_cost": "",
        "result": ""
    }
    
    # Altura del árbol
    if b > 1:
        result["height"] = f"log_{b}(n)"
        result["steps"].append(f"Altura del árbol: h = log_{b}(n)")
    else:
        result["height"] = "n"
        result["steps"].append(f"Altura del árbol: h = n (decrece de 1 en 1)")
    
    # Costo por nivel
    result["steps"].append(f"En cada nivel i, hay {a}^i nodos")
    
    f_info = classify_f_n(f_n, b)
    k = f_info.get("k", 0)
    
    if b > 1:
        result["steps"].append(f"El tamaño del problema en nivel i es n/{b}^i")
        result["steps"].append(f"Costo por nodo en nivel i: f(n/{b}^i)")
        result["steps"].append(f"Costo total nivel i: {a}^i × f(n/{b}^i)")
        
        # Sumar todos los niveles
        result["steps"].append(f"Costo total = Σ(i=0 a log_{b}(n)) de {a}^i × f(n/{b}^i)")
        
        # Determinar resultado según la relación a vs b^k
        log_b_a = math.log(a, b)
        
        if k < log_b_a:
            result["result"] = f"Θ(n^{log_b_a:.2f})"
        elif abs(k - log_b_a) < 0.01:
            result["result"] = f"Θ(n^{k} × log n)"
        else:
            result["result"] = f"Θ({f_n})"
    else:
        result["steps"].append(f"El tamaño del problema en nivel i es n-i")
        result["steps"].append(f"Costo total = Σ(i=0 a n) de {a}^i × {f_n}")
        
        if a == 1:
            if k == 0:
                result["result"] = "Θ(n)"
            else:
                result["result"] = f"Θ(n × {f_n})"
        else:
            result["result"] = f"Θ({a}^n)"
            result["steps"].append(f"Serie geométrica con razón {a} → crecimiento exponencial")
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# TOOLS DE LANGCHAIN
# ═══════════════════════════════════════════════════════════════════════════════

@tool
def resolver_recurrencia(recurrencia: str) -> Dict[str, Any]:
    """
    Resuelve una ecuación de recurrencia usando múltiples métodos.
    
    Args:
        recurrencia: Ecuación en formato "T(n) = aT(n/b) + f(n)" o similar.
    
    Returns:
        Dict con:
        - classification: Tipo de recurrencia (F0-F6)
        - parameters: a, b, f(n) extraídos
        - methods: Lista de métodos aplicados con sus resultados
        - best_result: Mejor solución encontrada
    
    Ejemplos de entrada:
    - "T(n) = 2T(n/2) + n"      (Merge Sort)
    - "T(n) = T(n/2) + 1"       (Binary Search)
    - "T(n) = T(n-1) + 1"       (Factorial)
    - "T(n) = T(n-1) + T(n-2)"  (Fibonacci)
    - "T(n) = 2T(n-1) + 1"      (Torres de Hanoi)
    """
    # Parsear la recurrencia
    params = parse_recurrence(recurrencia)
    
    result = {
        "recurrence": recurrencia,
        "classification": params["classification"],
        "parameters": {
            "a": params["a"],
            "b": params["b"],
            "f_n": params["f_n"],
            "type": params["recurrence_type"]
        },
        "methods": [],
        "best_result": ""
    }
    
    a, b, f_n = params["a"], params["b"], params["f_n"]
    rec_type = params["recurrence_type"]
    classification = params["classification"]
    
    # Intentar cada método según la clasificación
    
    # 1. Master Theorem (solo para F0, F1)
    if classification in METHOD_APPLICABILITY["master"]:
        master_result = apply_master_theorem(a, b, f_n)
        result["methods"].append({
            "method": "master",
            "applicable": master_result["applicable"],
            "steps": master_result["steps"],
            "result": master_result["result"]
        })
        if master_result["applicable"]:
            result["best_result"] = master_result["result"]
    
    # 2. Método de Iteración
    if classification in METHOD_APPLICABILITY["iteration"]:
        iter_result = solve_by_iteration(a, b, f_n, rec_type)
        result["methods"].append({
            "method": "iteration",
            "applicable": iter_result["applicable"],
            "steps": iter_result["steps"],
            "result": iter_result["result"]
        })
        if not result["best_result"]:
            result["best_result"] = iter_result["result"]
    
    # 3. Árbol de Recursión
    if classification in METHOD_APPLICABILITY["recursion_tree"]:
        tree_result = calculate_recursion_tree_complexity(a, b, f_n)
        result["methods"].append({
            "method": "recursion_tree",
            "applicable": True,
            "steps": tree_result["steps"],
            "result": tree_result["result"],
            "height": tree_result["height"]
        })
        if not result["best_result"]:
            result["best_result"] = tree_result["result"]
    
    # Casos especiales
    if rec_type == "multiple_recursive":
        # Fibonacci-like: T(n) = T(n-1) + T(n-2) + O(1) → O(φ^n)
        phi = (1 + math.sqrt(5)) / 2
        result["methods"].append({
            "method": "characteristic",
            "applicable": True,
            "steps": [
                "Ecuación característica: x² = x + 1",
                f"Raíces: φ = (1+√5)/2 ≈ {phi:.4f}, ψ = (1-√5)/2",
                "Solución general: T(n) = c₁φⁿ + c₂ψⁿ",
                f"Término dominante: Θ(φⁿ) ≈ Θ({phi:.4f}ⁿ)"
            ],
            "result": "Θ(φⁿ) ≈ Θ(1.618ⁿ)"
        })
        result["best_result"] = "Θ(φⁿ) ≈ Θ(1.618ⁿ)"
    
    return result


@tool
def generar_arbol_recurrencia(recurrencia: str, niveles: int = 4) -> Dict[str, Any]:
    """
    Genera un diagrama del árbol de recursión en formato Mermaid.
    
    Args:
        recurrencia: Ecuación de recurrencia.
        niveles: Número de niveles a mostrar (default: 4).
    
    Returns:
        Dict con:
        - mermaid_diagram: Código Mermaid del diagrama
        - analysis: Análisis del árbol (altura, costo por nivel, etc.)
    """
    params = parse_recurrence(recurrencia)
    a, b, f_n = params["a"], params["b"], params["f_n"]
    
    # Generar diagrama
    mermaid = generate_recursion_tree_diagram(a, b, f_n, niveles)
    
    # Análisis
    analysis = calculate_recursion_tree_complexity(a, b, f_n)
    
    return {
        "mermaid_diagram": mermaid,
        "analysis": {
            "height": analysis["height"],
            "steps": analysis["steps"],
            "total_complexity": analysis["result"]
        }
    }


@tool  
def detectar_tipo_recurrencia(pseudocode: str) -> Dict[str, Any]:
    """
    Analiza pseudocódigo y detecta el tipo de recurrencia.
    
    Args:
        pseudocode: Código en pseudocódigo.
    
    Returns:
        Dict con información sobre la recurrencia detectada.
    """
    result = {
        "is_recursive": False,
        "recursive_calls": [],
        "base_cases": [],
        "recurrence_equation": "",
        "classification": ""
    }
    
    lines = pseudocode.strip().split('\n')
    func_name = None
    
    # Detectar nombre de la función
    for line in lines:
        line = line.strip()
        if '(' in line and ')' in line and 'begin' not in line.lower():
            if not any(kw in line.lower() for kw in ['if', 'while', 'for', 'call']):
                match = re.match(r'(\w+)\s*\(', line)
                if match:
                    func_name = match.group(1)
                    break
    
    if not func_name:
        return result
    
    # Buscar llamadas recursivas y casos base
    for line in lines:
        line_lower = line.lower().strip()
        
        # Buscar llamadas recursivas
        if 'call' in line_lower and func_name.lower() in line_lower:
            result["is_recursive"] = True
            # Extraer argumentos de la llamada
            call_match = re.search(rf'call\s+{func_name}\s*\(([^)]+)\)', line, re.IGNORECASE)
            if call_match:
                args = call_match.group(1)
                result["recursive_calls"].append(args)
        
        # Buscar casos base (return con condición simple)
        if 'return' in line_lower:
            if any(base in line_lower for base in ['= 1', '= 0', '<= 1', '<= 0', '== 1', '== 0']):
                result["base_cases"].append(line.strip())
    
    # Clasificar tipo de recurrencia
    if result["is_recursive"]:
        calls = result["recursive_calls"]
        num_calls = len(calls)
        
        # Detectar patrón de división
        has_division = any('/' in c for c in calls)
        has_subtraction = any('-' in c for c in calls)
        
        if has_division:
            if num_calls == 1:
                result["classification"] = "F0"
                result["recurrence_equation"] = "T(n) = T(n/b) + f(n)"
            else:
                result["classification"] = "F1"
                result["recurrence_equation"] = f"T(n) = {num_calls}T(n/b) + f(n)"
        elif has_subtraction:
            if num_calls == 1:
                result["classification"] = "F4"
                result["recurrence_equation"] = "T(n) = T(n-1) + f(n)"
            elif num_calls == 2:
                result["classification"] = "F6"
                result["recurrence_equation"] = "T(n) = T(n-1) + T(n-2) + f(n)"
            else:
                result["classification"] = "F5"
                result["recurrence_equation"] = f"T(n) = {num_calls}T(n-1) + f(n)"
    
    return result


@tool
def calcular_espacio_recursivo(recurrencia: str, variables_locales: int = 1) -> Dict[str, Any]:
    """
    Calcula la complejidad espacial de un algoritmo recursivo.
    
    Args:
        recurrencia: Ecuación de recurrencia.
        variables_locales: Número de variables locales por llamada.
    
    Returns:
        Dict con análisis de espacio.
    """
    params = parse_recurrence(recurrencia)
    a, b = params["a"], params["b"]
    rec_type = params["recurrence_type"]
    
    result = {
        "stack_depth": "",
        "frame_size": f"O({variables_locales})",
        "auxiliary_space": "O(1)",
        "total_space": "",
        "explanation": []
    }
    
    if rec_type == "divide_and_conquer":
        result["stack_depth"] = f"O(log_{b}(n))"
        result["explanation"].append(f"La profundidad de recursión es log_{b}(n) porque dividimos por {b}")
        
        if a == 1:
            result["total_space"] = f"O(log n)"
        else:
            result["total_space"] = f"O(log n)"  # Solo se mantiene un camino activo
            result["explanation"].append("Aunque hay múltiples ramas, solo una está activa a la vez en la pila")
            
    elif rec_type in ["decrease_and_conquer", "decrease_and_lose"]:
        result["stack_depth"] = "O(n)"
        result["explanation"].append("La profundidad de recursión es O(n) porque restamos una constante")
        
        if a == 1:
            result["total_space"] = "O(n)"
        else:
            result["total_space"] = "O(n)"  # Por la pila
            result["explanation"].append("El espacio está dominado por la profundidad de la pila")
            
    elif rec_type == "multiple_recursive":
        result["stack_depth"] = "O(n)"
        result["total_space"] = "O(n)"
        result["explanation"].append("Fibonacci-like: profundidad O(n) aunque tiene múltiples ramas")
    
    return result

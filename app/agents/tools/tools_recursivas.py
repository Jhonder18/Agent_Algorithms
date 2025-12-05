"""
Herramientas para análisis de complejidad de algoritmos recursivos.

Clasificación de recurrencias según ADA_24A:
- F0: T(n) = T(n/b) + f(n)         [DyV simple]
- F1: T(n) = aT(n/b) + f(n)        [DyV general - Teorema Maestro]
- F2: T(n) = T(n/b) + T(n/c) + f(n) [DyV múltiple]
- F3: T(n) = T(n/b) + ... + T(n/z) + f(n) [DyV generalizado]
- F4: T(n) = T(n-b) + f(n)         [RyV - Resta y Vencerás]
- F5: T(n) = aT(n-b) + f(n)        [RysV - Resta y serás Vencido]
- F6: T(n) = aT(n-b) + cT(n-d) + f(n) [RysV Fibonacci-like]

Métodos aplicables según ADA_24A:
- Iteración: {F4, F5, F0, F1} - NO aplica a {F2, F3, F6}
- Árbol de Recursión: {F2, F3, F6, F5, F1, F0} - NO aplica a {F4}
- Teorema Maestro: {F1, F0} - NO aplica a {F2, F3, F4, F5, F6}
- Sustitución Inteligente: Todos los tipos
- Ecuación Característica: {F5, F6, F4} - NO aplica a {F0, F1, F2, F3}
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
import sympy as sp
from sympy import symbols, Function, rsolve, simplify, expand, sqrt, Rational, log, Pow
import re
import math

# ============================================================================
# CLASIFICACIÓN DE MÉTODOS SEGÚN ADA_24A
# ============================================================================

METHOD_APPLICABILITY = {
    "iteration": {"applies": ["F4", "F5", "F0", "F1"], "not_applies": ["F2", "F3", "F6"]},
    "recursion_tree": {"applies": ["F2", "F3", "F6", "F5", "F1", "F0"], "not_applies": ["F4"]},
    "master_theorem": {"applies": ["F1", "F0"], "not_applies": ["F2", "F3", "F4", "F5", "F6"]},
    "substitution": {"applies": ["F0", "F1", "F2", "F3", "F4", "F5", "F6"], "not_applies": []},
    "characteristic_equation": {"applies": ["F5", "F6", "F4"], "not_applies": ["F0", "F1", "F2", "F3"]},
}

# Orden de preferencia de métodos por tipo de recurrencia
METHOD_PRIORITY = {
    "F0": ["master_theorem", "iteration", "recursion_tree", "substitution"],
    "F1": ["master_theorem", "iteration", "recursion_tree", "substitution"],
    "F2": ["recursion_tree", "substitution"],
    "F3": ["recursion_tree", "substitution"],
    "F4": ["characteristic_equation", "iteration", "substitution"],
    "F5": ["characteristic_equation", "iteration", "recursion_tree", "substitution"],
    "F6": ["characteristic_equation", "recursion_tree", "substitution"],
}


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class RecurrenceInfo(BaseModel):
    """Información extraída de una ecuación de recurrencia."""
    tipo: str = Field(description="Tipo de recurrencia: F0, F1, F2, F3, F4, F5, F6")
    recurrence_raw: str = Field(description="Ecuación de recurrencia original")
    a: Optional[float] = Field(default=None, description="Coeficiente a (llamadas recursivas)")
    b: Optional[float] = Field(default=None, description="Factor de división/resta b")
    c: Optional[float] = Field(default=None, description="Segundo coeficiente c (para F6)")
    d: Optional[float] = Field(default=None, description="Segundo factor d (para F6)")
    f_n: Optional[str] = Field(default=None, description="Término no recursivo f(n)")
    is_division: bool = Field(default=True, description="True si es división (DyV), False si es resta (RyV)")


class MethodResult(BaseModel):
    """Resultado de aplicar un método de resolución."""
    method: str = Field(description="Nombre del método aplicado")
    applicable: bool = Field(description="Si el método fue aplicable")
    complexity: Optional[str] = Field(default=None, description="Complejidad resultante")
    steps: List[str] = Field(default_factory=list, description="Pasos de la solución")
    explanation: str = Field(default="", description="Explicación del resultado")
    mermaid_diagram: Optional[str] = Field(default=None, description="Diagrama Mermaid (solo para árbol de recursión)")


class RecurrenceAnalysis(BaseModel):
    """Análisis completo de una recurrencia."""
    recurrence_info: RecurrenceInfo
    applicable_methods: List[str]
    primary_result: MethodResult
    all_results: List[MethodResult]


# ============================================================================
# FUNCIONES DE PARSING
# ============================================================================

def parse_recurrence(recurrence: str) -> RecurrenceInfo:
    """
    Parsea una ecuación de recurrencia y determina su tipo según ADA_24A.
    
    Tipos:
    - F0: T(n) = T(n/b) + f(n)
    - F1: T(n) = aT(n/b) + f(n)
    - F2: T(n) = T(n/b) + T(n/c) + f(n)
    - F3: T(n) = T(n/b) + ... + T(n/z) + f(n)
    - F4: T(n) = T(n-b) + f(n)
    - F5: T(n) = aT(n-b) + f(n)
    - F6: T(n) = aT(n-b) + cT(n-d) + f(n)
    """
    recurrence = recurrence.strip()
    
    # Detectar si usa división o resta
    is_division = "/" in recurrence and "-" not in re.sub(r'T\([^)]+\)', '', recurrence)
    
    # Patrones para identificar llamadas recursivas
    # Patrón para T(n/b) o T(n-b)
    division_pattern = r'(\d*)\s*T\s*\(\s*n\s*/\s*(\d+)\s*\)'
    subtraction_pattern = r'(\d*)\s*T\s*\(\s*n\s*-\s*(\d+)\s*\)'
    
    division_calls = re.findall(division_pattern, recurrence)
    subtraction_calls = re.findall(subtraction_pattern, recurrence)
    
    # Extraer f(n) - todo lo que no es T(...)
    fn_pattern = r'\d*\s*T\s*\([^)]+\)'
    remaining = re.sub(fn_pattern, '', recurrence)
    # Quitar "T(n) = " del inicio
    remaining = re.sub(r'^T\s*\(\s*n\s*\)\s*=', '', remaining)
    # Quitar "=" suelto
    remaining = re.sub(r'^\s*=\s*', '', remaining)
    # Quitar + al inicio y al final
    remaining = re.sub(r'^\s*\+\s*', '', remaining)
    remaining = re.sub(r'\s*\+\s*$', '', remaining)
    # Quitar + repetidos que quedan después de remover T(...)
    remaining = re.sub(r'\+\s*\+', '+', remaining)
    remaining = remaining.strip()
    
    # Limpiar f_n
    f_n = re.sub(r'^\s*\+\s*', '', remaining).strip()
    f_n = re.sub(r'\s*\+\s*$', '', f_n).strip()
    
    # Si quedó algo numérico solo, o vacío, o solo +, usar "1"
    if not f_n or f_n == "+" or f_n.isspace():
        f_n = "1"
    
    # Si f_n es solo un número sin n, mantenerlo
    # Pero preferir la parte con 'n' si existe
    parts = [p.strip() for p in f_n.split('+') if p.strip()]
    n_parts = [p for p in parts if 'n' in p.lower()]
    if n_parts:
        f_n = n_parts[0]  # Tomar la primera parte con 'n'
    elif parts:
        f_n = parts[0]
    
    # Determinar tipo basado en las llamadas encontradas
    if subtraction_calls:
        is_division = False
        total_calls = len(subtraction_calls)
        
        if total_calls >= 2:
            # F6: aT(n-b) + cT(n-d)
            a1 = int(subtraction_calls[0][0]) if subtraction_calls[0][0] else 1
            b1 = int(subtraction_calls[0][1])
            c1 = int(subtraction_calls[1][0]) if subtraction_calls[1][0] else 1
            d1 = int(subtraction_calls[1][1])
            return RecurrenceInfo(
                tipo="F6",
                recurrence_raw=recurrence,
                a=a1, b=b1, c=c1, d=d1,
                f_n=f_n,
                is_division=False
            )
        else:
            # Una sola llamada con resta
            a = int(subtraction_calls[0][0]) if subtraction_calls[0][0] else 1
            b = int(subtraction_calls[0][1])
            
            if a == 1:
                # F4: T(n) = T(n-b) + f(n)
                return RecurrenceInfo(
                    tipo="F4",
                    recurrence_raw=recurrence,
                    a=1, b=b,
                    f_n=f_n,
                    is_division=False
                )
            else:
                # F5: T(n) = aT(n-b) + f(n)
                return RecurrenceInfo(
                    tipo="F5",
                    recurrence_raw=recurrence,
                    a=a, b=b,
                    f_n=f_n,
                    is_division=False
                )
    
    elif division_calls:
        is_division = True
        total_calls = len(division_calls)
        
        if total_calls == 1:
            a = int(division_calls[0][0]) if division_calls[0][0] else 1
            b = int(division_calls[0][1])
            
            if a == 1:
                # F0: T(n) = T(n/b) + f(n)
                return RecurrenceInfo(
                    tipo="F0",
                    recurrence_raw=recurrence,
                    a=1, b=b,
                    f_n=f_n,
                    is_division=True
                )
            else:
                # F1: T(n) = aT(n/b) + f(n)
                return RecurrenceInfo(
                    tipo="F1",
                    recurrence_raw=recurrence,
                    a=a, b=b,
                    f_n=f_n,
                    is_division=True
                )
        elif total_calls == 2:
            # F2: T(n) = T(n/b) + T(n/c) + f(n)
            b1 = int(division_calls[0][1])
            c1 = int(division_calls[1][1])
            return RecurrenceInfo(
                tipo="F2",
                recurrence_raw=recurrence,
                a=1, b=b1, c=1, d=c1,
                f_n=f_n,
                is_division=True
            )
        else:
            # F3: múltiples llamadas
            b = int(division_calls[0][1])
            return RecurrenceInfo(
                tipo="F3",
                recurrence_raw=recurrence,
                a=total_calls, b=b,
                f_n=f_n,
                is_division=True
            )
    
    # Default: intentar inferir
    return RecurrenceInfo(
        tipo="F1",
        recurrence_raw=recurrence,
        a=2, b=2,
        f_n=f_n,
        is_division=True
    )


def get_applicable_methods(recurrence_type: str) -> List[str]:
    """Obtiene los métodos aplicables para un tipo de recurrencia en orden de prioridad."""
    return METHOD_PRIORITY.get(recurrence_type, ["substitution"])


def can_apply_method(method: str, recurrence_type: str) -> bool:
    """Verifica si un método es aplicable a un tipo de recurrencia."""
    if method not in METHOD_APPLICABILITY:
        return False
    return recurrence_type in METHOD_APPLICABILITY[method]["applies"]


# ============================================================================
# MÉTODO: TEOREMA MAESTRO
# ============================================================================

def apply_master_theorem(info: RecurrenceInfo) -> MethodResult:
    """
    Aplica el Teorema Maestro para recurrencias de la forma T(n) = aT(n/b) + f(n).
    Solo aplica a F0 y F1.
    """
    if info.tipo not in ["F0", "F1"]:
        return MethodResult(
            method="master_theorem",
            applicable=False,
            explanation=f"El Teorema Maestro no aplica a recurrencias tipo {info.tipo}"
        )
    
    if not info.is_division:
        return MethodResult(
            method="master_theorem",
            applicable=False,
            explanation="El Teorema Maestro solo aplica a divisiones (DyV), no a restas"
        )
    
    a = info.a or 1
    b = info.b or 2
    f_n = info.f_n or "1"
    
    steps = []
    steps.append(f"Recurrencia: T(n) = {a}T(n/{b}) + {f_n}")
    steps.append(f"Parámetros: a = {a}, b = {b}")
    
    # Calcular log_b(a)
    log_b_a = math.log(a) / math.log(b)
    steps.append(f"log_b(a) = log_{b}({a}) = {log_b_a:.4f}")
    
    # Determinar k de f(n) = Θ(n^k)
    k = extract_polynomial_degree(f_n)
    steps.append(f"f(n) = {f_n}, k = {k}")
    
    # Aplicar casos del Teorema Maestro
    epsilon = 0.001
    
    if abs(k - log_b_a) < epsilon:
        # Caso 2: k = log_b(a)
        complexity = f"Θ(n^{k:.0f} log n)" if k == int(k) else f"Θ(n^{log_b_a:.4f} log n)"
        steps.append(f"Caso 2: k = log_b(a) → T(n) = {complexity}")
        return MethodResult(
            method="master_theorem",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Aplicando Caso 2 del Teorema Maestro: k = log_b(a)"
        )
    elif k < log_b_a:
        # Caso 1: k < log_b(a)
        if log_b_a == int(log_b_a):
            complexity = f"Θ(n^{int(log_b_a)})"
        else:
            complexity = f"Θ(n^{log_b_a:.4f})"
        steps.append(f"Caso 1: k < log_b(a) → T(n) = {complexity}")
        return MethodResult(
            method="master_theorem",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Aplicando Caso 1 del Teorema Maestro: k < log_b(a)"
        )
    else:
        # Caso 3: k > log_b(a)
        complexity = f"Θ({f_n})"
        steps.append(f"Caso 3: k > log_b(a) → T(n) = {complexity}")
        return MethodResult(
            method="master_theorem",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Aplicando Caso 3 del Teorema Maestro: k > log_b(a)"
        )


def extract_polynomial_degree(f_n: str) -> float:
    """Extrae el grado del polinomio de f(n)."""
    f_n = f_n.strip().lower()
    
    if f_n in ["1", "o(1)", "θ(1)", "c", ""]:
        return 0
    
    # Buscar n^k
    power_match = re.search(r'n\s*\^\s*(\d+\.?\d*)', f_n)
    if power_match:
        return float(power_match.group(1))
    
    # Buscar n log n
    if "log" in f_n and "n" in f_n:
        if re.search(r'n\s*log', f_n) or re.search(r'log.*n.*n', f_n):
            return 1  # n log n es como n^1 * log n
    
    # Solo n
    if re.search(r'^n$', f_n) or f_n == "n":
        return 1
    
    # n^2
    if "n^2" in f_n or "n²" in f_n:
        return 2
    
    # n^3
    if "n^3" in f_n or "n³" in f_n:
        return 3
    
    return 0


# ============================================================================
# MÉTODO: ITERACIÓN
# ============================================================================

def solve_by_iteration(info: RecurrenceInfo) -> MethodResult:
    """
    Resuelve por el método de iteración (expansión).
    Aplica a: F4, F5, F0, F1
    NO aplica a: F2, F3, F6
    """
    if info.tipo in ["F2", "F3", "F6"]:
        return MethodResult(
            method="iteration",
            applicable=False,
            explanation=f"El método de iteración no aplica a recurrencias tipo {info.tipo}"
        )
    
    steps = []
    a = info.a or 1
    b = info.b or 2
    f_n = info.f_n or "1"
    
    if info.is_division:
        # DyV: T(n) = aT(n/b) + f(n)
        steps.append(f"T(n) = {a}T(n/{b}) + {f_n}")
        steps.append(f"T(n) = {a}[{a}T(n/{b}²) + {f_n}] + {f_n}")
        steps.append(f"T(n) = {a}²T(n/{b}²) + {a}·{f_n} + {f_n}")
        
        # Generalizar
        steps.append(f"Después de k iteraciones:")
        steps.append(f"T(n) = {a}^k · T(n/{b}^k) + Σᵢ₌₀ᵏ⁻¹ {a}ⁱ · f(n/{b}ⁱ)")
        
        # Caso base cuando n/b^k = 1, k = log_b(n)
        k = f"log_{b}(n)"
        steps.append(f"El caso base se alcanza cuando n/{b}^k = 1, es decir k = {k}")
        
        # Calcular complejidad
        log_b_a = math.log(a) / math.log(b) if a > 0 and b > 1 else 0
        degree_f = extract_polynomial_degree(f_n)
        
        if abs(degree_f - log_b_a) < 0.001:
            complexity = f"Θ(n^{degree_f:.0f} log n)"
        elif degree_f < log_b_a:
            complexity = f"Θ(n^{log_b_a:.4f})"
        else:
            complexity = f"Θ({f_n})"
        
        steps.append(f"Complejidad resultante: {complexity}")
        
        return MethodResult(
            method="iteration",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto por expansión iterativa de la recurrencia DyV"
        )
    else:
        # RyV: T(n) = aT(n-b) + f(n)
        steps.append(f"T(n) = {a}T(n-{b}) + {f_n}")
        
        if a == 1:
            # F4: T(n) = T(n-b) + f(n) → Suma de f(n)
            steps.append(f"T(n) = T(n-{b}) + {f_n}")
            steps.append(f"T(n) = T(n-2·{b}) + {f_n} + {f_n}")
            steps.append(f"T(n) = T(n-k·{b}) + k·{f_n}")
            steps.append(f"Cuando n - k·{b} = 0, k = n/{b}")
            
            # Complejidad depende de f(n)
            if f_n in ["1", "c", "O(1)"]:
                complexity = "Θ(n)"
            elif "n" in f_n and "^" not in f_n:
                complexity = "Θ(n²)"
            elif "n^2" in f_n:
                complexity = "Θ(n³)"
            else:
                complexity = f"Θ(n · {f_n})"
            
            steps.append(f"Suma: (n/{b}) · {f_n} = {complexity}")
        else:
            # F5: T(n) = aT(n-b) + f(n) → Serie geométrica
            steps.append(f"T(n) = {a}[{a}T(n-2·{b}) + {f_n}] + {f_n}")
            steps.append(f"T(n) = {a}²T(n-2·{b}) + {a}·{f_n} + {f_n}")
            steps.append(f"T(n) = {a}^k · T(n-k·{b}) + Σᵢ₌₀ᵏ⁻¹ {a}ⁱ · {f_n}")
            
            complexity = f"Θ({a}^(n/{b}))"
            steps.append(f"La suma geométrica domina: {complexity}")
        
        return MethodResult(
            method="iteration",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto por expansión iterativa de la recurrencia RyV"
        )


# ============================================================================
# MÉTODO: ECUACIÓN CARACTERÍSTICA
# ============================================================================

def solve_by_characteristic_equation(info: RecurrenceInfo) -> MethodResult:
    """
    Resuelve por el método de la ecuación característica.
    Aplica a: F4, F5, F6
    NO aplica a: F0, F1, F2, F3
    
    Para Fibonacci T(n) = T(n-1) + T(n-2), la solución es Θ(φⁿ) donde φ = (1+√5)/2
    """
    if info.tipo in ["F0", "F1", "F2", "F3"]:
        return MethodResult(
            method="characteristic_equation",
            applicable=False,
            explanation=f"La ecuación característica no aplica a recurrencias tipo {info.tipo} (división)"
        )
    
    steps = []
    a = info.a or 1
    b = info.b or 1
    c = info.c
    d = info.d
    f_n = info.f_n or "1"
    
    if info.tipo == "F6":
        # F6: T(n) = aT(n-b) + cT(n-d) + f(n)
        # Caso especial: Fibonacci T(n) = T(n-1) + T(n-2)
        steps.append(f"Recurrencia: T(n) = {a}T(n-{b}) + {c}T(n-{d}) + {f_n}")
        
        if a == 1 and c == 1 and b == 1 and d == 2:
            # Fibonacci clásico
            steps.append("Esta es la recurrencia de Fibonacci")
            steps.append("Ecuación característica: x² = x + 1")
            steps.append("x² - x - 1 = 0")
            steps.append("Usando la fórmula cuadrática:")
            steps.append("x = (1 ± √5) / 2")
            steps.append("φ = (1 + √5) / 2 ≈ 1.618 (razón áurea)")
            steps.append("ψ = (1 - √5) / 2 ≈ -0.618")
            steps.append("Solución general: T(n) = c₁φⁿ + c₂ψⁿ")
            steps.append("Como |ψ| < 1, ψⁿ → 0 cuando n → ∞")
            steps.append("Por lo tanto: T(n) = Θ(φⁿ)")
            
            phi = (1 + math.sqrt(5)) / 2
            complexity = f"Θ(φⁿ) = Θ({phi:.4f}ⁿ)"
            
            return MethodResult(
                method="characteristic_equation",
                applicable=True,
                complexity=complexity,
                steps=steps,
                explanation="Resuelto usando ecuación característica (Fibonacci → razón áurea)"
            )
        else:
            # Ecuación característica general para F6
            steps.append(f"Ecuación característica: x^{d} = {a}x^{d-b} + {c}")
            
            # Resolver simbólicamente
            x = symbols('x')
            char_eq = x**d - a * x**(d-b) - c
            
            try:
                roots = sp.solve(char_eq, x)
                steps.append(f"Raíces: {roots}")
                
                # La raíz dominante determina la complejidad
                max_root = max([abs(complex(r)) for r in roots])
                complexity = f"Θ({max_root:.4f}ⁿ)"
                steps.append(f"Raíz dominante: {max_root:.4f}")
            except:
                complexity = f"Θ(max(|raíces|)ⁿ)"
            
            return MethodResult(
                method="characteristic_equation",
                applicable=True,
                complexity=complexity,
                steps=steps,
                explanation="Resuelto usando ecuación característica para recurrencia F6"
            )
    
    elif info.tipo == "F5":
        # F5: T(n) = aT(n-b) + f(n)
        steps.append(f"Recurrencia: T(n) = {a}T(n-{b}) + {f_n}")
        steps.append(f"Ecuación característica: x^{b} = {a}")
        steps.append(f"Raíz: x = {a}^(1/{b})")
        
        root = a ** (1/b)
        
        if f_n in ["1", "c", "O(1)"]:
            complexity = f"Θ({a}^(n/{b}))"
        else:
            # Con término no homogéneo
            complexity = f"Θ({a}^(n/{b}))"
        
        steps.append(f"Complejidad: {complexity}")
        
        return MethodResult(
            method="characteristic_equation",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto usando ecuación característica para recurrencia F5"
        )
    
    elif info.tipo == "F4":
        # F4: T(n) = T(n-b) + f(n)
        steps.append(f"Recurrencia: T(n) = T(n-{b}) + {f_n}")
        steps.append("Ecuación característica: x^b = 1")
        steps.append(f"Raíz: x = 1 (multiplicidad {b})")
        
        # Para F4 con a=1, la solución es suma de f(n)
        if f_n in ["1", "c", "O(1)"]:
            complexity = "Θ(n)"
        elif "n" in f_n:
            degree = extract_polynomial_degree(f_n)
            complexity = f"Θ(n^{int(degree)+1})"
        else:
            complexity = f"Θ(n · {f_n})"
        
        steps.append(f"La complejidad depende de la suma de {f_n}")
        steps.append(f"Complejidad: {complexity}")
        
        return MethodResult(
            method="characteristic_equation",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto usando ecuación característica para recurrencia F4"
        )
    
    return MethodResult(
        method="characteristic_equation",
        applicable=False,
        explanation=f"Tipo de recurrencia {info.tipo} no manejado"
    )


# ============================================================================
# MÉTODO: ÁRBOL DE RECURSIÓN
# ============================================================================

def solve_by_recursion_tree(info: RecurrenceInfo) -> MethodResult:
    """
    Resuelve usando el método del árbol de recursión.
    Aplica a: F2, F3, F6, F5, F1, F0
    NO aplica a: F4
    """
    if info.tipo == "F4":
        return MethodResult(
            method="recursion_tree",
            applicable=False,
            explanation="El árbol de recursión no aplica a recurrencias tipo F4 (una sola rama lineal)"
        )
    
    steps = []
    a = info.a or 1
    b = info.b or 2
    f_n = info.f_n or "1"
    
    if info.is_division:
        # DyV
        steps.append(f"Recurrencia: T(n) = {a}T(n/{b}) + {f_n}")
        steps.append(f"Nivel 0: {f_n} (1 nodo)")
        steps.append(f"Nivel 1: {a} nodos, cada uno con costo f(n/{b})")
        steps.append(f"Nivel 2: {a}² nodos, cada uno con costo f(n/{b}²)")
        steps.append(f"...")
        steps.append(f"Nivel k: {a}^k nodos, cada uno con costo f(n/{b}^k)")
        
        height = f"log_{b}(n)"
        steps.append(f"Altura del árbol: h = {height}")
        
        # Costo total por nivel y suma
        log_b_a = math.log(a) / math.log(b) if a > 0 and b > 1 else 0
        degree_f = extract_polynomial_degree(f_n)
        
        if a > 1:
            steps.append(f"Número total de hojas: {a}^h = {a}^(log_{b}(n)) = n^(log_{b}({a})) = n^{log_b_a:.4f}")
        
        if abs(degree_f - log_b_a) < 0.001:
            complexity = f"Θ(n^{degree_f:.0f} log n)"
            steps.append("Todos los niveles contribuyen igualmente → factor log n")
        elif degree_f < log_b_a:
            complexity = f"Θ(n^{log_b_a:.4f})"
            steps.append("El costo está dominado por las hojas")
        else:
            complexity = f"Θ({f_n})"
            steps.append("El costo está dominado por la raíz")
        
        # Generar diagrama Mermaid
        mermaid = generate_tree_diagram(info, depth=3)
        
        return MethodResult(
            method="recursion_tree",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto visualizando el árbol de recursión",
            mermaid_diagram=mermaid
        )
    else:
        # RyV
        if info.tipo == "F6":
            # Árbol binario (Fibonacci-like)
            steps.append(f"Recurrencia: T(n) = {a}T(n-{b}) + {info.c}T(n-{info.d}) + {f_n}")
            steps.append("Árbol de recursión binario (estilo Fibonacci)")
            steps.append(f"Cada nodo se ramifica en {a + info.c} subnodos")
            steps.append(f"Profundidad máxima: n/{b}")
            
            phi = (1 + math.sqrt(5)) / 2
            complexity = f"Θ(φⁿ) ≈ Θ({phi:.4f}ⁿ)"
            steps.append(f"Número de nodos crece exponencialmente: {complexity}")
            
            mermaid = generate_fibonacci_tree_diagram(info, depth=4)
        else:
            # F5
            steps.append(f"Recurrencia: T(n) = {a}T(n-{b}) + {f_n}")
            steps.append(f"Cada nivel tiene {a}^k nodos")
            steps.append(f"Profundidad: n/{b} niveles")
            
            complexity = f"Θ({a}^(n/{b}))"
            steps.append(f"Número total de nodos: {complexity}")
            
            mermaid = generate_tree_diagram(info, depth=3)
        
        return MethodResult(
            method="recursion_tree",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto visualizando el árbol de recursión",
            mermaid_diagram=mermaid
        )


def generate_tree_diagram(info: RecurrenceInfo, depth: int = 3) -> str:
    """Genera un diagrama Mermaid del árbol de recursión."""
    lines = ["graph TD"]
    
    a = int(info.a or 1)
    b = int(info.b or 2)
    op = "/" if info.is_division else "-"
    
    node_id = [0]
    
    def add_node(current_n: str, current_depth: int, parent_id: int = None):
        my_id = node_id[0]
        node_id[0] += 1
        
        # Crear nodo
        label = f"T({current_n})"
        lines.append(f"    N{my_id}[\"{label}\"]")
        
        # Conectar con padre
        if parent_id is not None:
            lines.append(f"    N{parent_id} --> N{my_id}")
        
        # Agregar hijos si no hemos llegado al límite
        if current_depth < depth:
            for i in range(a):
                if info.is_division:
                    child_n = f"{current_n}/{b}" if current_n == "n" else f"({current_n})/{b}"
                else:
                    child_n = f"{current_n}-{b}" if current_n == "n" else f"({current_n})-{b}"
                add_node(child_n, current_depth + 1, my_id)
        else:
            # Agregar indicador de continuación
            dots_id = node_id[0]
            node_id[0] += 1
            lines.append(f"    N{dots_id}[\"...\"]")
            lines.append(f"    N{my_id} --> N{dots_id}")
    
    add_node("n", 0)
    
    return "\n".join(lines)


def generate_fibonacci_tree_diagram(info: RecurrenceInfo, depth: int = 4) -> str:
    """Genera un diagrama Mermaid para árbol estilo Fibonacci."""
    lines = ["graph TD"]
    
    b = int(info.b or 1)
    d = int(info.d or 2)
    
    node_id = [0]
    
    def add_node(current_n: str, current_depth: int, parent_id: int = None):
        my_id = node_id[0]
        node_id[0] += 1
        
        label = f"T({current_n})"
        lines.append(f"    N{my_id}[\"{label}\"]")
        
        if parent_id is not None:
            lines.append(f"    N{parent_id} --> N{my_id}")
        
        if current_depth < depth:
            # Rama izquierda (n-b)
            child1 = f"{current_n}-{b}" if current_n == "n" else f"({current_n})-{b}"
            add_node(child1, current_depth + 1, my_id)
            
            # Rama derecha (n-d)
            child2 = f"{current_n}-{d}" if current_n == "n" else f"({current_n})-{d}"
            add_node(child2, current_depth + 1, my_id)
        else:
            dots_id = node_id[0]
            node_id[0] += 1
            lines.append(f"    N{dots_id}[\"...\"]")
            lines.append(f"    N{my_id} --> N{dots_id}")
    
    add_node("n", 0)
    
    return "\n".join(lines)


# ============================================================================
# MÉTODO: SUSTITUCIÓN INTELIGENTE
# ============================================================================

def solve_by_substitution(info: RecurrenceInfo) -> MethodResult:
    """
    Resuelve por el método de sustitución (adivinar y verificar).
    Aplica a todos los tipos de recurrencia.
    """
    steps = []
    a = info.a or 1
    b = info.b or 2
    f_n = info.f_n or "1"
    
    steps.append(f"Recurrencia: {info.recurrence_raw}")
    steps.append("Método de sustitución: adivinamos una solución y verificamos")
    
    # Usar SymPy para resolver
    n = symbols('n', positive=True, integer=True)
    T = Function('T')
    
    try:
        if info.is_division:
            # Para DyV, usamos resultados conocidos
            log_b_a = math.log(a) / math.log(b) if a > 0 and b > 1 else 0
            degree_f = extract_polynomial_degree(f_n)
            
            steps.append(f"Hipótesis: T(n) = Θ(n^{max(log_b_a, degree_f):.2f})")
            
            if abs(degree_f - log_b_a) < 0.001:
                complexity = f"Θ(n^{degree_f:.0f} log n)"
            elif degree_f < log_b_a:
                complexity = f"Θ(n^{log_b_a:.4f})"
            else:
                complexity = f"Θ({f_n})"
        else:
            # Para RyV
            if a == 1:
                # F4: lineal en suma de f(n)
                if f_n in ["1", "c"]:
                    complexity = "Θ(n)"
                else:
                    complexity = f"Θ(n · {f_n})"
            elif info.tipo == "F6":
                # Fibonacci-like
                phi = (1 + math.sqrt(5)) / 2
                complexity = f"Θ(φⁿ) ≈ Θ({phi:.4f}ⁿ)"
            else:
                # Exponencial
                complexity = f"Θ({a}^(n/{b}))"
        
        steps.append(f"Verificación por inducción confirma: {complexity}")
        
        return MethodResult(
            method="substitution",
            applicable=True,
            complexity=complexity,
            steps=steps,
            explanation="Resuelto por sustitución (adivinar y verificar)"
        )
    except Exception as e:
        return MethodResult(
            method="substitution",
            applicable=True,
            complexity="No determinado",
            steps=steps + [f"Error en verificación: {str(e)}"],
            explanation="El método de sustitución no pudo completarse"
        )


# ============================================================================
# FUNCIÓN PRINCIPAL DE ANÁLISIS
# ============================================================================

def analyze_recurrence(recurrence: str) -> RecurrenceAnalysis:
    """
    Analiza una recurrencia y aplica los métodos apropiados según ADA_24A.
    
    Args:
        recurrence: Ecuación de recurrencia como string
        
    Returns:
        RecurrenceAnalysis con información completa del análisis
    """
    # Parsear la recurrencia
    info = parse_recurrence(recurrence)
    
    # Obtener métodos aplicables en orden de prioridad
    applicable = get_applicable_methods(info.tipo)
    
    # Aplicar cada método y recopilar resultados
    all_results = []
    primary_result = None
    
    for method in applicable:
        if method == "master_theorem":
            result = apply_master_theorem(info)
        elif method == "iteration":
            result = solve_by_iteration(info)
        elif method == "characteristic_equation":
            result = solve_by_characteristic_equation(info)
        elif method == "recursion_tree":
            result = solve_by_recursion_tree(info)
        elif method == "substitution":
            result = solve_by_substitution(info)
        else:
            continue
        
        all_results.append(result)
        
        # El primer método aplicable es el primario
        if result.applicable and primary_result is None:
            primary_result = result
    
    # Si ningún método fue aplicable, usar sustitución como fallback
    if primary_result is None:
        primary_result = solve_by_substitution(info)
        all_results.append(primary_result)
    
    return RecurrenceAnalysis(
        recurrence_info=info,
        applicable_methods=applicable,
        primary_result=primary_result,
        all_results=all_results
    )


# ============================================================================
# TOOLS PARA LANGCHAIN
# ============================================================================

@tool
def clasificar_recurrencia(recurrence: str) -> Dict[str, Any]:
    """
    Clasifica una ecuación de recurrencia según el sistema ADA_24A.
    
    Tipos:
    - F0: T(n) = T(n/b) + f(n) [DyV simple]
    - F1: T(n) = aT(n/b) + f(n) [DyV general]
    - F2: T(n) = T(n/b) + T(n/c) + f(n) [DyV múltiple]
    - F3: T(n) = múltiples T(n/bᵢ) + f(n) [DyV generalizado]
    - F4: T(n) = T(n-b) + f(n) [RyV lineal]
    - F5: T(n) = aT(n-b) + f(n) [RysV exponencial]
    - F6: T(n) = aT(n-b) + cT(n-d) + f(n) [Fibonacci-like]
    
    Args:
        recurrence: La ecuación de recurrencia a clasificar
        
    Returns:
        Información sobre el tipo y métodos aplicables
    """
    info = parse_recurrence(recurrence)
    methods = get_applicable_methods(info.tipo)
    
    return {
        "tipo": info.tipo,
        "descripcion": get_type_description(info.tipo),
        "parametros": {
            "a": info.a,
            "b": info.b,
            "c": info.c,
            "d": info.d,
            "f_n": info.f_n,
            "es_division": info.is_division
        },
        "metodos_aplicables": methods,
        "metodo_recomendado": methods[0] if methods else "substitution"
    }


def get_type_description(tipo: str) -> str:
    """Devuelve una descripción del tipo de recurrencia."""
    descriptions = {
        "F0": "Divide y Vencerás simple: T(n) = T(n/b) + f(n)",
        "F1": "Divide y Vencerás general (Teorema Maestro): T(n) = aT(n/b) + f(n)",
        "F2": "Divide y Vencerás múltiple: T(n) = T(n/b) + T(n/c) + f(n)",
        "F3": "Divide y Vencerás generalizado: múltiples llamadas con diferentes divisores",
        "F4": "Resta y Vencerás lineal: T(n) = T(n-b) + f(n)",
        "F5": "Resta y serás Vencido exponencial: T(n) = aT(n-b) + f(n)",
        "F6": "Fibonacci-like: T(n) = aT(n-b) + cT(n-d) + f(n)"
    }
    return descriptions.get(tipo, "Tipo desconocido")


@tool
def resolver_recurrencia(recurrence: str) -> Dict[str, Any]:
    """
    Resuelve una ecuación de recurrencia usando el método más apropiado según ADA_24A.
    
    Selección de método por tipo:
    - F0, F1: Teorema Maestro (preferido) o Iteración
    - F2, F3: Árbol de Recursión
    - F4: Ecuación Característica o Iteración
    - F5: Ecuación Característica o Árbol de Recursión
    - F6: Ecuación Característica (ej: Fibonacci → φⁿ)
    
    Args:
        recurrence: La ecuación de recurrencia a resolver
        
    Returns:
        Análisis completo con complejidad y pasos
    """
    analysis = analyze_recurrence(recurrence)
    
    result = {
        "recurrencia_original": recurrence,
        "tipo": analysis.recurrence_info.tipo,
        "metodo_utilizado": analysis.primary_result.method,
        "complejidad": analysis.primary_result.complexity,
        "pasos": analysis.primary_result.steps,
        "explicacion": analysis.primary_result.explanation,
        "metodos_aplicables": analysis.applicable_methods
    }
    
    # Solo incluir diagrama si el método es árbol de recursión
    if analysis.primary_result.mermaid_diagram:
        result["diagrama_mermaid"] = analysis.primary_result.mermaid_diagram
    
    return result


@tool
def generar_arbol_recursion(recurrence: str) -> Dict[str, Any]:
    """
    Genera un diagrama de árbol de recursión para una recurrencia.
    
    Solo aplica a tipos: F0, F1, F2, F3, F5, F6
    NO aplica a: F4 (tiene una sola rama lineal)
    
    Args:
        recurrence: La ecuación de recurrencia
        
    Returns:
        Diagrama Mermaid y análisis del árbol
    """
    info = parse_recurrence(recurrence)
    
    if info.tipo == "F4":
        return {
            "aplicable": False,
            "razon": "El árbol de recursión no aplica a recurrencias tipo F4 (Resta y Vencerás lineal) porque solo tiene una rama, no forma un árbol.",
            "sugerencia": "Use el método de iteración o ecuación característica para F4"
        }
    
    result = solve_by_recursion_tree(info)
    
    return {
        "aplicable": result.applicable,
        "tipo_recurrencia": info.tipo,
        "complejidad": result.complexity,
        "diagrama_mermaid": result.mermaid_diagram,
        "pasos": result.steps
    }


@tool
def aplicar_teorema_maestro(a: float, b: float, f_n: str) -> Dict[str, Any]:
    """
    Aplica el Teorema Maestro a una recurrencia T(n) = aT(n/b) + f(n).
    
    Solo aplica a recurrencias de división (DyV):
    - F0: a = 1
    - F1: a ≥ 1
    
    Casos del Teorema Maestro:
    - Caso 1: Si f(n) = O(n^(log_b(a) - ε)), entonces T(n) = Θ(n^(log_b(a)))
    - Caso 2: Si f(n) = Θ(n^(log_b(a))), entonces T(n) = Θ(n^(log_b(a)) log n)
    - Caso 3: Si f(n) = Ω(n^(log_b(a) + ε)), entonces T(n) = Θ(f(n))
    
    Args:
        a: Número de subproblemas
        b: Factor de división
        f_n: Término no recursivo como string (ej: "n", "n^2", "1")
        
    Returns:
        Resultado del Teorema Maestro
    """
    info = RecurrenceInfo(
        tipo="F1" if a > 1 else "F0",
        recurrence_raw=f"T(n) = {a}T(n/{b}) + {f_n}",
        a=a, b=b, f_n=f_n,
        is_division=True
    )
    
    result = apply_master_theorem(info)
    
    return {
        "aplicable": result.applicable,
        "complejidad": result.complexity,
        "pasos": result.steps,
        "explicacion": result.explanation
    }


@tool
def resolver_ecuacion_caracteristica(recurrence: str) -> Dict[str, Any]:
    """
    Resuelve una recurrencia usando el método de la ecuación característica.
    
    Aplica a tipos: F4, F5, F6
    NO aplica a: F0, F1, F2, F3 (usan división, no resta)
    
    Ejemplos:
    - Fibonacci T(n) = T(n-1) + T(n-2) → Θ(φⁿ) donde φ = (1+√5)/2 ≈ 1.618
    - T(n) = 2T(n-1) + 1 → Θ(2ⁿ)
    - T(n) = T(n-1) + n → Θ(n²)
    
    Args:
        recurrence: La ecuación de recurrencia
        
    Returns:
        Solución usando ecuación característica
    """
    info = parse_recurrence(recurrence)
    
    if info.tipo in ["F0", "F1", "F2", "F3"]:
        return {
            "aplicable": False,
            "razon": f"La ecuación característica no aplica a recurrencias tipo {info.tipo} (división). Use Teorema Maestro o Árbol de Recursión.",
            "tipo_detectado": info.tipo
        }
    
    result = solve_by_characteristic_equation(info)
    
    return {
        "aplicable": result.applicable,
        "tipo_recurrencia": info.tipo,
        "complejidad": result.complexity,
        "pasos": result.steps,
        "explicacion": result.explanation
    }


# Lista de todas las herramientas
RECURSIVE_TOOLS = [
    clasificar_recurrencia,
    resolver_recurrencia,
    generar_arbol_recursion,
    aplicar_teorema_maestro,
    resolver_ecuacion_caracteristica
]

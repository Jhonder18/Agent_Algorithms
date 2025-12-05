"""
Nodo para construir la ecuación de recurrencia a partir del AST.
Este es el primer nodo del flujo recursivo.
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AnalyzerState, RecurrenceInfo, RecurrenceParameters
from app.agents.llms.gemini import get_gemini_model


# ═══════════════════════════════════════════════════════════════════════════════
# MODELOS PYDANTIC PARA STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

class RecurrenceExtraction(BaseModel):
    """Modelo para la extracción de recurrencia por el LLM."""
    
    recurrence_equation: str = Field(
        ...,
        description="La ecuación de recurrencia en formato T(n) = ... Por ejemplo: T(n) = 2T(n/2) + n"
    )
    base_cases: List[str] = Field(
        default_factory=list,
        description="Lista de casos base. Por ejemplo: ['T(1) = 1', 'T(0) = 0']"
    )
    num_recursive_calls: int = Field(
        ...,
        description="Número de llamadas recursivas (valor de 'a')"
    )
    division_factor: int = Field(
        default=1,
        description="Factor por el que se divide n (valor de 'b'). Si es resta, poner 1."
    )
    subtraction_factor: int = Field(
        default=0,
        description="Valor que se resta a n en cada llamada. 0 si es división."
    )
    non_recursive_work: str = Field(
        ...,
        description="El trabajo no recursivo f(n). Por ejemplo: 'n', '1', 'n^2', 'log n'"
    )
    recurrence_type: str = Field(
        ...,
        description="Tipo: 'divide_and_conquer', 'decrease_and_conquer', 'decrease_and_lose', 'multiple_recursive'"
    )
    explanation: str = Field(
        ...,
        description="Breve explicación de cómo se identificó la recurrencia"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Eres un experto en análisis de algoritmos recursivos. Tu tarea es analizar el pseudocódigo proporcionado y extraer la ecuación de recurrencia que describe su complejidad temporal.

## Tipos de Recurrencias (según clasificación ADA)

### Divide y Vencerás (DyV)
- F0: T(n) = T(n/b) + f(n)           → Una llamada recursiva con división
- F1: T(n) = aT(n/b) + f(n)          → Múltiples llamadas con división
- F2: T(n) = T(n/b) + T(n/c) + f(n)  → Divisiones diferentes

### Resta y Vencerás (RyV)
- F4: T(n) = T(n-b) + f(n)           → Una llamada recursiva con resta
- F5: T(n) = aT(n-b) + f(n)          → Múltiples llamadas con resta (exponencial)
- F6: T(n) = T(n-1) + T(n-2) + f(n)  → Tipo Fibonacci

## Instrucciones

1. Identifica la función recursiva principal
2. Cuenta cuántas llamadas recursivas hay (valor 'a')
3. Determina cómo cambia el parámetro n:
   - Si se divide (n/2, n/3, etc.) → es DyV, determina 'b'
   - Si se resta (n-1, n-2, etc.) → es RyV
4. Identifica el trabajo no recursivo f(n):
   - Operaciones fuera de las llamadas recursivas
   - Bucles, asignaciones, comparaciones, etc.
5. Identifica los casos base (condiciones de parada)

## Ejemplos

**Merge Sort:**
```
mergeSort(A, p, r)
begin
    if p < r then
    begin
        q 🡨 (p + r) / 2
        CALL mergeSort(A, p, q)
        CALL mergeSort(A, q+1, r)
        CALL merge(A, p, q, r)
    end
end
```
→ T(n) = 2T(n/2) + n  (a=2, b=2, f(n)=n por el merge)

**Búsqueda Binaria:**
```
binarySearch(A, p, r, x)
begin
    if p <= r then
    begin
        q 🡨 (p + r) / 2
        if A[q] = x then return q
        if A[q] > x then CALL binarySearch(A, p, q-1, x)
        else CALL binarySearch(A, q+1, r, x)
    end
end
```
→ T(n) = T(n/2) + 1  (a=1, b=2, f(n)=1)

**Factorial:**
```
factorial(n)
begin
    if n <= 1 then return 1
    return n * CALL factorial(n-1)
end
```
→ T(n) = T(n-1) + 1  (resta y vencerás, f(n)=1)

**Fibonacci:**
```
fib(n)
begin
    if n <= 1 then return n
    return CALL fib(n-1) + CALL fib(n-2)
end
```
→ T(n) = T(n-1) + T(n-2) + 1  (tipo F6, exponencial)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def classify_recurrence(a: int, b: int, is_division: bool, is_multiple: bool) -> str:
    """Clasifica la recurrencia según el PDF ADA_24A."""
    if is_division:
        if a == 1:
            return "F0"
        else:
            return "F1"
    else:  # Resta
        if is_multiple:
            return "F6"  # Tipo Fibonacci
        elif a > 1:
            return "F5"  # Resta y serás vencido
        else:
            return "F4"  # Resta y vencerás


def get_recurrence_type_name(classification: str) -> str:
    """Obtiene el nombre del tipo de recurrencia."""
    names = {
        "F0": "Divide y Vencerás (simple)",
        "F1": "Divide y Vencerás (general)",
        "F2": "Divide y Vencerás (múltiple)",
        "F3": "Divide y Vencerás (generalizado)",
        "F4": "Resta y Vencerás",
        "F5": "Resta y Serás Vencido",
        "F6": "Tipo Fibonacci (múltiple recursivo)"
    }
    return names.get(classification, "Desconocido")


# ═══════════════════════════════════════════════════════════════════════════════
# NODO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def build_recurrence_node(state: AnalyzerState) -> AnalyzerState:
    """
    Nodo que construye la ecuación de recurrencia a partir del pseudocódigo.
    
    Input del estado:
        - pseudocode: El código a analizar
        - ast: El árbol sintáctico (opcional, para contexto adicional)
    
    Output al estado:
        - recurrence: RecurrenceInfo con la ecuación y parámetros
        - razonamiento: Pasos del análisis agregados
    """
    pseudocode = state.get("pseudocode", "")
    ast = state.get("ast", {})
    
    # Inicializar razonamiento si no existe
    if "razonamiento" not in state:
        state["razonamiento"] = []
    
    state["razonamiento"].append("═══ FASE 1: Construcción de Ecuación de Recurrencia ═══")
    
    # Obtener modelo LLM con structured output
    gemini = get_gemini_model()
    llm_structured = gemini.with_structured_output(RecurrenceExtraction)
    
    # Crear mensajes
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    human_message = HumanMessage(
        content=f"""Analiza el siguiente pseudocódigo y extrae la ecuación de recurrencia:

```
{pseudocode}
```

AST (para contexto adicional):
{ast}

Por favor, identifica:
1. La ecuación de recurrencia T(n) = ...
2. Los casos base
3. Los parámetros a, b, f(n)
4. El tipo de recurrencia"""
    )
    
    # Invocar LLM
    try:
        extraction: RecurrenceExtraction = llm_structured.invoke([system_message, human_message])
        
        # Determinar si es división o resta
        is_division = extraction.division_factor > 1
        is_multiple = "+" in extraction.recurrence_equation and extraction.recurrence_equation.count("T(") > 2
        
        # Clasificar
        classification = classify_recurrence(
            extraction.num_recursive_calls,
            extraction.division_factor if is_division else extraction.subtraction_factor,
            is_division,
            is_multiple
        )
        
        # Construir RecurrenceInfo
        recurrence_info: RecurrenceInfo = {
            "raw": extraction.recurrence_equation,
            "base_cases": extraction.base_cases,
            "variable": "n",
            "parameters": {
                "a": extraction.num_recursive_calls,
                "b": extraction.division_factor if is_division else extraction.subtraction_factor,
                "f_n": extraction.non_recursive_work,
                "recurrence_type": extraction.recurrence_type,
            },
            "classification": classification,
            "methods_tried": [],
            "best_method": "",
            "final_solution": ""
        }
        
        state["recurrence"] = recurrence_info
        
        # Agregar al razonamiento
        state["razonamiento"].append(f"✓ Ecuación detectada: {extraction.recurrence_equation}")
        state["razonamiento"].append(f"✓ Casos base: {', '.join(extraction.base_cases)}")
        state["razonamiento"].append(f"✓ Parámetros: a={extraction.num_recursive_calls}, b={extraction.division_factor}, f(n)={extraction.non_recursive_work}")
        state["razonamiento"].append(f"✓ Clasificación: {classification} - {get_recurrence_type_name(classification)}")
        state["razonamiento"].append(f"✓ Explicación: {extraction.explanation}")
        
    except Exception as e:
        # En caso de error, crear recurrencia por defecto
        state["recurrence"] = {
            "raw": "T(n) = T(n-1) + O(1)",
            "base_cases": ["T(1) = O(1)"],
            "variable": "n",
            "parameters": {
                "a": 1,
                "b": 1,
                "f_n": "1",
                "recurrence_type": "decrease_and_conquer"
            },
            "classification": "F4",
            "methods_tried": [],
            "best_method": "",
            "final_solution": ""
        }
        state["razonamiento"].append(f"⚠ Error al extraer recurrencia: {str(e)}")
        state["razonamiento"].append("✓ Usando recurrencia por defecto: T(n) = T(n-1) + O(1)")
    
    return state

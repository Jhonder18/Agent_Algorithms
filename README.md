# Agent Algorithms - Analizador de Complejidad Algorítmica

Sistema de análisis automático de complejidad temporal de algoritmos mediante agentes inteligentes con LangGraph.

## 🎯 Características

- **Análisis de algoritmos iterativos y recursivos**: Soporte completo para ambos paradigmas
- **Detección automática de recursión**: Identifica funciones recursivas en el código
- **Construcción de relaciones de recurrencia**: Genera T(n) = aT(n/b) + f(n)
- **Análisis profundo de f(n)**: Calcula trabajo no recursivo incluyendo funciones auxiliares
- **Análisis estático de código**: Parser personalizado con Lark para pseudocódigo
- **Cálculo de complejidades**: Best, Average y Worst case con notación Big-O
- **Resolución de series**: Sympy para resolver sumatorias anidadas
- **Análisis por línea**: Costos detallados línea por línea
- **Soporte completo**: for, while, if-else, bucles anidados
- **API REST**: FastAPI con endpoints para análisis
- **Resumen inteligente**: LLM genera explicaciones del análisis

## 📋 Requisitos

- Python 3.11 o superior
- Dependencias principales:
  - FastAPI 0.121.1
  - LangGraph 1.0.3
  - Sympy 1.14.1
  - Lark 1.1.9+

## 🚀 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Jhonder18/Agent_Algorithms.git
   cd Agent_Algorithms
   ```

2. Crea y activa el entorno virtual:
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicia el servidor:
   ```bash
   uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
   ```

## 📁 Estructura del Proyecto

```
app/
├── api.py                  # API REST con FastAPI
├── agents/
│   ├── graph.py           # Grafo de LangGraph con flujo bifurcado
│   ├── state.py           # Definición del estado
│   ├── planner.py         # Planificador de rutas
│   └── nodes/             # Nodos del grafo
│       ├── normalize.py   # Normalización de entrada
│       ├── validate.py    # Validación y reparación
│       ├── ast_json.py    # Generación de AST
│       ├── route_complexity.py  # Routing iterativo/recursivo
│       ├── recurrence.py  # Construcción de recurrencias (T(n))
│       ├── solve_recursive.py   # Resolución de recurrencias
│       ├── costs_json.py  # Análisis de costos (iterativos)
│       ├── solve_json.py  # Resolución de series (iterativos)
│       └── summarize.py   # Resumen con LLM
├── tools/
│   ├── ast_parser/        # Parser de pseudocódigo
│   ├── cost_model/        # Analizador de costos mejorado (CallStatement)
│   ├── recursion_detector/  # Detector de funciones recursivas
│   ├── recurrence_analyzer/ # Analizador de relaciones de recurrencia
│   └── series_solver/     # Solucionador de series
└── services/
    └── llm.py             # Cliente LLM

test_comprehensive.py      # Suite de pruebas (iterativos)
test_recurrence_builder.py # Tests de recurrencias
test_merge_with_merge_function.py  # Test merge sort con f(n) = O(n)
ALGORITMOS_TEST.md        # Lista de algoritmos de prueba
```

## 🔬 Uso

### API REST

```bash
# Analizar pseudocódigo
curl -X POST http://127.0.0.1:8000/api/v2/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"burbuja(A, n)\nbegin\n    for i 🡨 1 to n-1 do\n    begin\n        for j 🡨 1 to n-i do\n        begin\n            if (A[j] > A[j+1]) then\n            begin\n                temp 🡨 A[j]\n                A[j] 🡨 A[j+1]\n                A[j+1] 🡨 temp\n            end\n        end\n    end\nend"}'
```

### Tests

```bash
# Suite completa (10 algoritmos)
python test_comprehensive.py

# Test específico
python test_insertion_debug.py
```

## 📊 Ejemplo de Análisis

**Entrada**: Ordenamiento por inserción
```
insercion(A, n)
begin
    for i 🡨 2 to n do
    begin
        clave 🡨 A[i]
        j 🡨 i - 1
        while (j > 0 and A[j] > clave) do
        begin
            A[j+1] 🡨 A[j]
            j 🡨 j - 1
        end
        A[j+1] 🡨 clave
    end
end
```

**Salida**:
- **Complejidad**: Best O(n), Average O(n²), Worst O(n²)
- **Costos exactos**: 
  - Best: `8*n - 7`
  - Worst: `(3*n² + 19*n - 20)/2`
- **Por línea**: Sumatorias anidadas para while dentro de for
- **Resumen**: Explicación generada por LLM

## 🧪 Tests Disponibles

### Algoritmos Iterativos (10 tests)

El proyecto incluye 10 algoritmos de prueba en `ALGORITMOS_TEST.md`:

1. Búsqueda Lineal - O(n)
2. Ordenamiento Burbuja - O(n²)
3. Ordenamiento por Inserción - O(n²)
4. Ordenamiento por Selección - O(n²)
5. Suma de Matriz - O(n*m)
6. Búsqueda con While - O(n)
7. Merge de Arrays Ordenados - O(n)
8. Máximo en Array - O(n)
9. Contar Pares - O(n)
10. Búsqueda de Par de Suma - O(n²)

### Algoritmos Recursivos (Tests de recurrencia)

```bash
python test_recurrence_builder.py
```

Tests incluidos:
1. **Binary Search** - `T(n) = 2T(n/2) + O(1)` - Divide y conquista
2. **Factorial** - `T(n) = T(n-1) + O(1)` - Decremental
3. **Merge Sort** - `T(n) = 2T(n/2) + O(n)` - Divide y conquista con merge

**Test adicional con función auxiliar:**
```bash
python test_merge_with_merge_function.py
```
- Verifica detección correcta de f(n) = O(n) cuando hay función merge explícita

## 🔧 Características Técnicas

### Parser (Lark LALR)
- Soporta: for, while, if-else, asignaciones, return, CALL
- Símbolo de asignación: 🡨 (U+1F868)
- Arrays unidimensionales: `A[i]`
- Reconoce tanto `Call` como `CallStatement` para llamadas a funciones

### Flujo Bifurcado (Routing)
- **route_complexity_node**: Determina si el algoritmo es iterativo o recursivo
- **Flujo iterativo**: ast → costs → solve → summarize
- **Flujo recursivo**: ast → recurrence → solve_recursive → summarize
- Routing automático basado en detección de recursión

### Detector de Recursión
- Identifica funciones que se llaman a sí mismas
- Extrae información de llamadas recursivas (línea, argumentos)
- Distingue entre Call y CallStatement

### Analizador de Recurrencias
- Construye relaciones T(n) = aT(n/b) + f(n)
- Detecta patrones: divide_and_conquer, decremental, fibonacci_like
- Identifica división del problema (n/2, n-1, etc.)
- **Análisis profundo de f(n)**:
  - Elimina llamadas recursivas del AST
  - Detecta funciones auxiliares (como merge en merge sort)
  - Usa CostAnalyzer para calcular trabajo no recursivo
  - Extrae Big-O de expresiones simbólicas

### Analizador de Costos (Mejorado)
- Análisis estático del AST
- Tracking de bucles anidados
- Diferenciación best/avg/worst case
- Manejo de condiciones (if con probabilidad 0.5)
- **Nuevo**: Soporte para `CallStatement`
- **Nuevo**: Heurística para estimar costos de llamadas a funciones
  - Detecta argumentos de rango (left, right) → O(n)
  - Detecta arrays + rangos → O(n)

### Solucionador de Series
- Resolución simbólica con Sympy
- Simplificación algebraica
- Extracción de Big-O automática
- Cálculo de cotas asintóticas (Ω, Θ, O)

## 🛠️ Notas Técnicas

### Algoritmos Iterativos
- **Serialización**: LangGraph requiere JSON, los objetos Python se convierten con `to_dict()`
- **While anidados**: Detecta variable del for padre para límite superior
- **Mejor caso del while**: Evalúa condición una vez, no entra al cuerpo
- **Limitaciones**: No soporta matrices bidimensionales `A[i][j]`

### Algoritmos Recursivos
- **Detección automática**: El sistema identifica recursión y cambia de flujo
- **Relaciones de recurrencia**: Se construyen automáticamente analizando el AST
- **f(n) preciso**: Incluye análisis de funciones auxiliares mediante conversión AST → objetos
- **Patrones soportados**:
  - Divide y conquista: T(n) = aT(n/b) + f(n)
  - Decremental: T(n) = T(n-k) + f(n)
  - Fibonacci-like: T(n) = T(n-1) + T(n-2) + f(n)
- **Fallback robusto**: Si falla el análisis profundo, usa conteo de bucles

## 📝 Dependencias Actualizadas

Ver `requirements.txt` para la lista completa. Principales:
- fastapi==0.121.1
- langgraph==1.0.3
- sympy==1.14.1
- lark==1.1.9
- pydantic==2.11.0

## 🤝 Contribución

Rama activa: `fix-structure`

## 📄 Licencia

Este proyecto es desarrollado como parte de un proyecto universitario.
  ```bash
  uv pip freeze > uv.lock
  ```
- Para más información sobre uv: https://github.com/astral-sh/uv

# Agent Algorithms - Analizador de Complejidad Algorítmica

Sistema de análisis automático de complejidad temporal de algoritmos mediante agentes inteligentes con LangGraph.

## 🎯 Características

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
│   ├── graph.py           # Grafo de LangGraph
│   ├── state.py           # Definición del estado
│   ├── planner.py         # Planificador de rutas
│   └── nodes/             # Nodos del grafo
│       ├── normalize.py   # Normalización de entrada
│       ├── validate.py    # Validación y reparación
│       ├── ast_json.py    # Generación de AST
│       ├── costs_json.py  # Análisis de costos
│       ├── solve_json.py  # Resolución de series
│       └── summarize.py   # Resumen con LLM
├── tools/
│   ├── ast_parser/        # Parser de pseudocódigo
│   ├── cost_model/        # Analizador de costos
│   └── series_solver/     # Solucionador de series
└── services/
    └── llm.py             # Cliente LLM

test_comprehensive.py      # Suite de pruebas
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

## 🔧 Características Técnicas

### Parser (Lark LALR)
- Soporta: for, while, if-else, asignaciones, return
- Símbolo de asignación: 🡨 (U+1F868)
- Arrays unidimensionales: `A[i]`

### Analizador de Costos
- Análisis estático del AST
- Tracking de bucles anidados
- Diferenciación best/avg/worst case
- Manejo de condiciones (if con probabilidad 0.5)

### Solucionador de Series
- Resolución simbólica con Sympy
- Simplificación algebraica
- Extracción de Big-O automática
- Cálculo de cotas asintóticas (Ω, Θ, O)

## 🛠️ Notas Técnicas

- **Serialización**: LangGraph requiere JSON, los objetos Python se convierten con `to_dict()`
- **While anidados**: Detecta variable del for padre para límite superior
- **Mejor caso del while**: Evalúa condición una vez, no entra al cuerpo
- **Limitaciones**: No soporta matrices bidimensionales `A[i][j]`

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

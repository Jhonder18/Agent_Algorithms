# 📚 Agent Algorithms - Documentación Completa

## Analizador Automático de Complejidad Algorítmica con Agentes Inteligentes

---

## 📋 Tabla de Contenidos

1. [Propósito del Proyecto](#-propósito-del-proyecto)
2. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
3. [Arquitectura del Sistema](#-arquitectura-del-sistema)
4. [Estructura del Proyecto](#-estructura-del-proyecto)
5. [Flujo del Pipeline](#-flujo-del-pipeline)
6. [Componentes Principales](#-componentes-principales)
7. [Estado del Analizador](#-estado-del-analizador)
8. [Nodos del Grafo](#-nodos-del-grafo)
9. [Herramientas (Tools)](#-herramientas-tools)
10. [Prompts del Sistema](#-prompts-del-sistema)
11. [API REST](#-api-rest)
12. [Instalación y Configuración](#-instalación-y-configuración)
13. [Ejemplos de Uso](#-ejemplos-de-uso)
14. [Algoritmos Soportados](#-algoritmos-soportados)

---

## 🎯 Propósito del Proyecto

**Agent Algorithms** es un sistema de análisis automático de complejidad algorítmica que utiliza **agentes inteligentes** basados en LLMs (Large Language Models) orquestados mediante **LangGraph**.

### Objetivos Principales

| Objetivo | Descripción |
|----------|-------------|
| **Análisis Automático** | Calcular complejidad temporal y espacial de algoritmos |
| **Soporte Dual** | Manejar algoritmos iterativos y recursivos |
| **Entrada Flexible** | Aceptar pseudocódigo o descripciones en lenguaje natural |
| **Notación Asintótica** | Generar Big-O (Ω), Big-Omega (Θ), y Big-Theta (O) |
| **Explicaciones** | Producir análisis detallados en lenguaje natural |

### Características Clave

- ✅ **Análisis de algoritmos iterativos y recursivos**
- ✅ **Detección automática del tipo de algoritmo** (iterativo vs recursivo)
- ✅ **Generación de AST** (Árbol de Sintaxis Abstracta)
- ✅ **Conversión a expresiones de sumatoria** para análisis matemático
- ✅ **Resolución simbólica** con SymPy
- ✅ **Validación y corrección de sintaxis** asistida por LLM
- ✅ **API REST** para integración con otros sistemas
- ✅ **Interfaz de desarrollo** con LangGraph Studio

---

## 🛠 Tecnologías Utilizadas

### Stack Principal

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | ≥3.12 | Lenguaje base |
| **LangGraph** | ≥0.2.45 | Orquestación de agentes |
| **LangChain** | ≥0.3.10 | Framework de LLM |
| **Google Gemini** | gemini-2.5-flash-lite | Modelo LLM |
| **FastAPI** | ≥0.115.0 | API REST |
| **SymPy** | Latest | Resolución simbólica |
| **Lark** | Latest | Parsing de gramáticas |
| **Pydantic** | ≥2.9.0 | Validación de datos |

### Dependencias Secundarias

```toml
[project]
dependencies = [
    "google-genai",
    "python-dotenv",
    "sympy",
    "lark",
    "langchain",
    "langchain-google-genai",
    "langgraph",
    "langsmith",
    "fastapi[standard]",
    "matplotlib>=3.10.7",
    "ipython>=9.7.0",
]
```

---

## 🏗 Arquitectura del Sistema

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         ENTRADA                                  │
│    ┌──────────────────┐    ┌──────────────────────────┐         │
│    │ Lenguaje Natural │ OR │     Pseudocódigo         │         │
│    └────────┬─────────┘    └────────────┬─────────────┘         │
└─────────────┼───────────────────────────┼───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH PIPELINE                            │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐     │
│  │  Decision   │───▶│   Validate   │───▶│   Generate AST  │     │
│  │    Node     │    │     Node     │    │      Node       │     │
│  └─────────────┘    └──────────────┘    └────────┬────────┘     │
│                                                   │              │
│                          ┌────────────────────────┼──────┐       │
│                          ▼                        ▼      │       │
│               ┌──────────────────┐    ┌──────────────────┐      │
│               │    ITERATIVO     │    │    RECURSIVO     │      │
│               │  Temporal/Espacial│    │ Temporal/Espacial│      │
│               └────────┬─────────┘    └────────┬─────────┘      │
│                        │                       │                 │
│                        └───────────┬───────────┘                 │
│                                    ▼                             │
│                         ┌──────────────────┐                     │
│                         │  Result Node     │                     │
│                         │  (Resumen LLM)   │                     │
│                         └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SALIDA                                   │
│  • Pseudocódigo validado                                        │
│  • AST estructurado                                              │
│  • Ecuaciones de complejidad (Big-O, Ω, Θ)                      │
│  • Notaciones asintóticas                                        │
│  • Análisis en lenguaje natural                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Patrón de Diseño

El sistema implementa el patrón **State Machine** mediante LangGraph:

1. **Estado Compartido**: `AnalyzerState` TypedDict que viaja por todos los nodos
2. **Nodos Funcionales**: Cada nodo es una función pura que transforma el estado
3. **Edges Condicionales**: Routing dinámico basado en el contenido del estado
4. **Orquestación**: LangGraph maneja el flujo y la ejecución

---

## 📁 Estructura del Proyecto

```
Agent_Algorithms/
│
├── 📄 main.py                    # Punto de entrada principal
├── 📄 langgraph.json             # Configuración de LangGraph
├── 📄 pyproject.toml             # Dependencias del proyecto
├── 📄 requirements.txt           # Dependencias (pip)
├── 📄 test.py                    # Tests básicos
│
├── 📁 app/                       # Módulo principal
│   ├── 📄 __init__.py
│   ├── 📄 api.py                 # API REST con FastAPI
│   ├── 📄 constants.py           # Constantes globales
│   │
│   ├── 📁 agents/                # Agentes LangGraph
│   │   ├── 📄 graph.py           # Definición del grafo
│   │   ├── 📄 state.py           # Estado del analizador
│   │   │
│   │   ├── 📁 nodes/             # Nodos del grafo
│   │   │   ├── 📄 initial_decision.py
│   │   │   ├── 📄 code_description.py
│   │   │   ├── 📄 parse_nl_code.py
│   │   │   ├── 📄 validate.py
│   │   │   ├── 📄 ast_node.py
│   │   │   ├── 📄 iterativo_temporal.py
│   │   │   ├── 📄 iterativo_espacial.py
│   │   │   ├── 📄 recursivo_temporal.py
│   │   │   ├── 📄 recursivo_espacial.py
│   │   │   └── 📄 result.py
│   │   │
│   │   ├── 📁 llms/              # Configuración de LLMs
│   │   │   ├── 📄 gemini.py
│   │   │   └── 📄 geminiWithTools.py
│   │   │
│   │   ├── 📁 prompts/           # Prompts del sistema
│   │   │   ├── 📄 SINTAXE.md
│   │   │   ├── 📄 NL_TO_CODE.md
│   │   │   ├── 📄 GENERAR_RESULT.md
│   │   │   └── 📁 iterativos/
│   │   │       ├── 📁 temporal/
│   │   │       └── 📁 espacial/
│   │   │
│   │   ├── 📁 tools/             # Herramientas de LangChain
│   │   │   ├── 📄 tools_iterativas.py
│   │   │   └── 📄 tools_recursivas.py
│   │   │
│   │   └── 📁 utils/             # Utilidades
│   │       ├── 📄 generate_ast.py
│   │       └── 📄 generate_sum.py
│   │
│   ├── 📁 tools/                 # Herramientas de análisis
│   │   ├── 📁 ast_parser/        # Parser de pseudocódigo
│   │   ├── 📁 cost_model/        # Modelo de costos
│   │   ├── 📁 recurrence_analyzer/
│   │   ├── 📁 recursion_detector/
│   │   └── 📁 series_solver/     # Resolutor de series
│   │
│   └── 📁 services/              # Servicios
│       └── 📄 llm.py
│
└── 📁 docs/                      # Documentación
    └── 📄 ARCHITECTURE.md
```

---

## 🔄 Flujo del Pipeline

### Diagrama de Flujo Detallado

```
                    ┌─────────────┐
                    │    START    │
                    └──────┬──────┘
                           │
                           ▼
                ┌──────────────────┐
                │  decicion_node   │ ← Determina si es pseudocódigo o NL
                └────────┬─────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼───────┐       ┌─────────▼─────────┐
    │pseudocode!="" │       │ pseudocode == ""  │
    │               │       │                   │
    │code_description│       │   parse_code     │ ← Convierte NL a código
    └───────┬───────┘       └─────────┬─────────┘
            │                         │
            └────────────┬────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  validate_node   │ ← Valida y corrige sintaxis
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  generate_ast    │ ← Genera AST + detecta modo
                └────────┬─────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼───────┐       ┌─────────▼─────────┐
    │mode="iterativo"│       │ mode="recursivo" │
    │               │       │                   │
    │costo_temporal │       │ costo_temporal    │
    │  _iterativo   │       │   _recursivo      │
    └───────┬───────┘       └─────────┬─────────┘
            │                         │
            ▼                         ▼
    ┌───────────────┐       ┌─────────────────┐
    │costo_espacial │       │ costo_espacial  │
    │  _iterativo   │       │   _recursivo    │
    └───────┬───────┘       └─────────┬───────┘
            │                         │
            └────────────┬────────────┘
                         │
                         ▼
              ┌────────────────────┐
              │preparacion_resultado│ ← Genera resumen final
              └──────────┬─────────┘
                         │
                         ▼
                    ┌─────────┐
                    │   END   │
                    └─────────┘
```

### Descripción de Cada Paso

| Paso | Nodo | Función | Descripción |
|------|------|---------|-------------|
| 1 | `decicion_node` | `initial_decision_node` | Clasifica entrada como "pseudocódigo" o "lenguaje_natural" |
| 2a | `code_description` | `code_description_node` | Si es pseudocódigo, genera descripción NL |
| 2b | `parse_code` | `parse_code_node` | Si es NL, convierte a pseudocódigo |
| 3 | `validate_node` | `validate_node` | Valida sintaxis y corrige errores |
| 4 | `generate_ast` | `generate_ast_node` | Genera AST y determina modo (iterativo/recursivo) |
| 5a | `calcular_costo_temporal_iterativo` | `costo_temporal_iterativo_node` | Calcula Big-O, Ω, Θ temporal |
| 5b | `calcular_costo_temporal_recursivo` | `recusive_temporal_node` | (TODO) Análisis recursivo temporal |
| 6a | `calcular_costo_espacial_iterativo` | `costo_espacial_iterativo_node` | Calcula Big-O, Ω, Θ espacial |
| 6b | `calcular_costo_espacial_recursivo` | `recusive_espacial_node` | (TODO) Análisis recursivo espacial |
| 7 | `preparacion_resultado` | `result_node` | Genera análisis final en NL |

---

## 🔧 Componentes Principales

### 1. Grafo Principal (`graph.py`)

```python
from langgraph.graph import StateGraph, START, END

def build_graph() -> StateGraph[AnalyzerState]:
    graph = StateGraph(AnalyzerState)
    graph = create_nodes(graph)  # Añade todos los nodos
    graph = create_edges(graph)  # Define las conexiones
    return graph
```

**Funciones de Routing:**

```python
# Determina si la entrada es pseudocódigo
def is_pseudocode(state: AnalyzerState) -> bool:
    return state.get("pseudocode") != ""

# Determina si el algoritmo es iterativo
def is_iterative(state: AnalyzerState) -> bool:
    return state.get("mode") == "iterativo"
```

### 2. Configuración LLM (`gemini.py`)

```python
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite"), 
        api_key=os.environ["GOOGLE_API_KEY"]
    )
```

### 3. Parser de AST (`generate_ast.py`)

El parser procesa pseudocódigo línea por línea y genera un AST estructurado:

```python
class SimpleASTParser:
    def parse(self, pseudocode: str) -> List[Dict]:
        # Parsea funciones, loops, condicionales
        # Retorna estructura jerárquica
```

**Estructuras Soportadas:**
- Definiciones de funciones
- Bucles `for` y `while`
- Condicionales `if-else`
- Asignaciones con `🡨`
- Llamadas a funciones con `CALL`
- Arrays unidimensionales `A[i]`

### 4. Generador de Sumatorias (`generate_sum.py`)

Convierte el AST en expresiones matemáticas para SymPy:

```python
def convertir_a_sumatoria(codigo: list) -> str:
    # Ejemplo de salida:
    # "T_bubbleSort(n) = Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1))"
```

---

## 📊 Estado del Analizador

### Definición del Estado (`state.py`)

```python
class AnalyzerState(TypedDict, total=False):
    # ═══════════════════════════════════════════
    # ENTRADA
    # ═══════════════════════════════════════════
    nl_description: str    # Descripción en lenguaje natural
    pseudocode: str        # Pseudocódigo normalizado

    # ═══════════════════════════════════════════
    # ROUTING Y ANÁLISIS INTERMEDIO
    # ═══════════════════════════════════════════
    mode: Literal["iterative", "recursive"]  # Tipo de algoritmo
    ast: Dict[str, Any]                      # Árbol sintáctico
    sumatoria: str                           # Expresión matemática
    validation: Dict[str, Any]               # Resultado de validación
    recurrence: Dict[str, Any]               # Ecuaciones de recurrencia

    # ═══════════════════════════════════════════
    # RESULTADOS DE COMPLEJIDAD
    # ═══════════════════════════════════════════
    ecuaciones: Ecuaciones     # Ecuaciones calculadas
    notation: Notacion         # Notaciones finales

    # ═══════════════════════════════════════════
    # RESULTADO FINAL
    # ═══════════════════════════════════════════
    razonamiento: list[str]    # Pasos del análisis
    result: Dict[str, Any]     # Análisis en lenguaje natural
```

### Tipos Auxiliares

```python
class Ecuaciones(TypedDict):
    big_O_temporal: str       # O(n²)
    big_O_espacial: str       # O(1)
    big_Theta_temporal: str   # Θ(n²)
    big_Theta_espacial: str   # Θ(1)
    big_Omega_temporal: str   # Ω(n)
    big_Omega_espacial: str   # Ω(1)

class Notacion(TypedDict):
    big_O_temporal: str
    big_O_espacial: str
    big_Theta_temporal: str
    big_Theta_espacial: str
    big_Omega_temporal: str
    big_Omega_espacial: str
```

---

## 🔌 Nodos del Grafo

### 1. `initial_decision_node`

**Archivo:** `nodes/initial_decision.py`

**Propósito:** Clasifica la entrada como pseudocódigo o lenguaje natural.

```python
class typeInput(BaseModel):
    type_input: Literal["lenguaje_natural", "pseudocódigo"]

def initial_decision_node(state: AnalyzerState) -> AnalyzerState:
    # Usa Gemini para clasificar
    # Si es pseudocódigo: mueve nl_description → pseudocode
    # Si es NL: deja pseudocode vacío
```

### 2. `code_description_node`

**Archivo:** `nodes/code_description.py`

**Propósito:** Genera una descripción en lenguaje natural del pseudocódigo.

```python
def code_description_node(state: AnalyzerState) -> AnalyzerState:
    # Input: pseudocode
    # Output: nl_description (descripción generada)
```

### 3. `parse_code_node`

**Archivo:** `nodes/parse_nl_code.py`

**Propósito:** Convierte descripción en lenguaje natural a pseudocódigo.

### 4. `validate_node`

**Archivo:** `nodes/validate.py`

**Propósito:** Valida y corrige la sintaxis del pseudocódigo.

```python
class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str]

class CodeFixed(BaseModel):
    code: str

def validate_node(state: AnalyzerState) -> AnalyzerState:
    # 1. Valida usando SINTAXE.md como referencia
    # 2. Si hay errores, corrige usando NL_TO_CODE.md
    # 3. Itera hasta que sea válido
```

### 5. `generate_ast_node`

**Archivo:** `nodes/ast_node.py`

**Propósito:** Genera el AST y clasifica el algoritmo.

```python
class TipoCodigo(BaseModel):
    tipo: Literal["recursivo", "iterativo"]

def generate_ast_node(state: AnalyzerState) -> AnalyzerState:
    # 1. Clasifica como iterativo o recursivo (LLM)
    # 2. Genera AST con SimpleASTParser
    # 3. Convierte a sumatoria
    # Output: ast, mode, sumatoria
```

### 6. `costo_temporal_iterativo_node`

**Archivo:** `nodes/iterativo_temporal.py`

**Propósito:** Calcula complejidad temporal para algoritmos iterativos.

```python
def costo_temporal_iterativo_node(state: AnalyzerState) -> AnalyzerState:
    # Usa 3 prompts: CASO_PROMEDIO, MEJOR_CASO, PEOR_CASO
    # Llama a Gemini con tool resolver_sumatorias
    # Output: ecuaciones.big_O_temporal, big_Omega_temporal, big_Theta_temporal
```

### 7. `costo_espacial_iterativo_node`

**Archivo:** `nodes/iterativo_espacial.py`

**Propósito:** Calcula complejidad espacial para algoritmos iterativos.

### 8. `recusive_temporal_node` / `recusive_espacial_node`

**Archivos:** `nodes/recursivo_temporal.py`, `nodes/recursivo_espacial.py`

**Estado:** TODO - Pendiente de implementación

### 9. `result_node`

**Archivo:** `nodes/result.py`

**Propósito:** Genera el análisis final en lenguaje natural.

```python
class NotacionesYAnalisis(BaseModel):
    analisis: str              # Análisis completo en NL
    big_O_temporal: str
    big_O_espacial: str
    big_Theta_temporal: str
    big_Theta_espacial: str
    big_Omega_temporal: str
    big_Omega_espacial: str

def result_node(state: AnalyzerState) -> AnalyzerState:
    # Usa GENERAR_RESULT.md como prompt
    # Input: pseudocode, ast, ecuaciones
    # Output: result, notation
```

---

## 🔨 Herramientas (Tools)

### `resolver_sumatorias`

**Archivo:** `agents/tools/tools_iterativas.py`

```python
from langchain.tools import tool
from sympy import sympify

@tool
def resolver_sumatorias(sumatoria: str) -> str:
    """
    Resuelve sumatorias matemáticas usando SymPy.
    
    Ejemplo:
    Input: "Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1))"
    Output: "n*(n-1)/2"
    """
    expr = sympify(sumatoria)
    return expr.doit()
```

**Uso en el Pipeline:**
- Los nodos de cálculo de costos invocan a Gemini con esta tool
- Gemini decide cuándo llamar a la tool
- La tool resuelve expresiones simbólicas

---

## 📝 Prompts del Sistema

### 1. `SINTAXE.md` - Validación de Sintaxis

**Propósito:** Definir las reglas de sintaxis para validación.

**Contenido clave:**
- Estructuras de control: `FOR`, `WHILE`, `REPEAT`, `IF`
- Símbolo de asignación: `🡨`
- Comentarios: `►`
- Operadores: booleanos, relacionales, matemáticos
- Subrutinas y llamadas con `CALL`

### 2. `NL_TO_CODE.md` - Conversión NL → Pseudocódigo

**Propósito:** Guía para convertir lenguaje natural a pseudocódigo válido.

**Incluye:**
- Ejemplos de cada estructura
- Convenciones de formato
- Reglas de indentación

### 3. `GENERAR_RESULT.md` - Generación de Análisis

**Propósito:** Generar el análisis final completo.

**Secciones del análisis:**
1. Resumen ejecutivo
2. Análisis de complejidad
3. Análisis estructural
4. Optimización

### 4. Prompts de Casos (iterativos/)

```
prompts/iterativos/
├── temporal/
│   ├── CASO_PROMEDIO.md
│   ├── MEJOR_CASO.md
│   └── PEOR_CASO.md
└── espacial/
    ├── CASO_PROMEDIO.md
    ├── MEJOR_CASO.md
    └── PEOR_CASO.md
```

---

## 🌐 API REST

### Endpoint Principal

```
POST /api/v2/analyze
```

**Request:**
```json
{
  "text": "bubbleSort(A, n)\nbegin\n    for i 🡨 1 to n-1 do\n    begin\n        for j 🡨 1 to n-i do\n        begin\n            if (A[j] > A[j+1]) then\n            begin\n                temp 🡨 A[j]\n                A[j] 🡨 A[j+1]\n                A[j+1] 🡨 temp\n            end\n        end\n    end\nend",
  "language_hint": "es"
}
```

**Response:**
```json
{
  "nl_description": "Algoritmo de ordenamiento burbuja...",
  "pseudocode": "bubbleSort(A, n)...",
  "mode": "iterativo",
  "ast": [...],
  "sumatoria": "T_bubbleSort(n) = Sum(...)",
  "ecuaciones": {
    "big_O_temporal": "O(n²)",
    "big_O_espacial": "O(1)",
    "big_Theta_temporal": "Θ(n²)",
    "big_Theta_espacial": "Θ(1)",
    "big_Omega_temporal": "Ω(n)",
    "big_Omega_espacial": "Ω(1)"
  },
  "notation": {...},
  "result": "Análisis completo del algoritmo..."
}
```

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

### Serialización JSON

La API incluye una función `make_json_serializable` que convierte:
- Tuplas como claves de diccionario → strings (`("for", "n")` → `"for:n"`)
- Objetos SymPy → strings
- Tipos no primitivos → representación string

---

## ⚙ Instalación y Configuración

### Requisitos Previos

- Python 3.12+
- Cuenta de Google Cloud con API de Gemini habilitada

### Pasos de Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/Jhonder18/Agent_Algorithms.git
cd Agent_Algorithms

# 2. Crear entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Instalar dependencias
# Opción A: Con uv (recomendado)
uv pip install -r pyproject.toml

# Opción B: Con pip
pip install .

# 4. Configurar variables de entorno
# Crear archivo .env
echo "GOOGLE_API_KEY=tu_api_key_aqui" > .env
echo "GEMINI_MODEL=gemini-2.5-flash-lite" >> .env
```

### Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `GOOGLE_API_KEY` | API Key de Google Gemini | ✅ Sí |
| `GEMINI_MODEL` | Modelo a usar | No (default: gemini-2.5-flash-lite) |
| `LANGSMITH_TRACING` | Habilitar tracing | No |
| `LANGSMITH_API_KEY` | API Key de LangSmith | No |
| `LANGSMITH_PROJECT` | Proyecto en LangSmith | No |

### Ejecución

```bash
# Opción 1: API con Uvicorn
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000

# Opción 2: LangGraph Dev (Studio)
langgraph dev

# Opción 3: Script principal
python main.py
```

---

## 📌 Ejemplos de Uso

### Ejemplo 1: Bubble Sort (Iterativo)

**Input:**
```
bubbleSort(A[n], n)
begin
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 1 to n-i do
        begin
            if (A[j] > A[j+1]) then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end
```

**Análisis Esperado:**
- **Complejidad Temporal:** O(n²), Θ(n²), Ω(n)
- **Complejidad Espacial:** O(1), Θ(1), Ω(1)
- **Tipo:** Iterativo (doble bucle anidado)

### Ejemplo 2: Búsqueda Lineal

**Input:**
```
busquedaLineal(A[n], n, x)
begin
    for i 🡨 1 to n do
    begin
        if (A[i] = x) then
        begin
            return i
        end
    end
    return -1
end
```

**Análisis Esperado:**
- **Mejor caso:** O(1) - elemento en primera posición
- **Peor caso:** O(n) - elemento no existe
- **Caso promedio:** O(n/2) = O(n)

### Ejemplo 3: Desde Lenguaje Natural

**Input:**
```
"Implementa un algoritmo que ordene un arreglo usando el método de inserción"
```

**Proceso:**
1. `decicion_node` → Detecta "lenguaje_natural"
2. `parse_code` → Genera pseudocódigo de Insertion Sort
3. `validate_node` → Valida sintaxis
4. `generate_ast` → Genera AST, detecta "iterativo"
5. Nodos de costo → Calculan O(n²)
6. `result_node` → Genera explicación

---

## 📊 Algoritmos Soportados

### Algoritmos Iterativos ✅

| Algoritmo | Complejidad Temporal | Complejidad Espacial |
|-----------|---------------------|---------------------|
| Búsqueda Lineal | O(n) | O(1) |
| Bubble Sort | O(n²) | O(1) |
| Insertion Sort | O(n²) | O(1) |
| Selection Sort | O(n²) | O(1) |
| Suma de Matriz | O(n×m) | O(1) |
| Merge de Arrays | O(n) | O(n) |
| Máximo en Array | O(n) | O(1) |
| Búsqueda de Par | O(n²) | O(1) |

### Algoritmos Recursivos 🚧 (En Desarrollo)

| Algoritmo | Estado |
|-----------|--------|
| Binary Search | TODO |
| Merge Sort | TODO |
| Quick Sort | TODO |
| Factorial | TODO |
| Fibonacci | TODO |

---

## 🔮 Roadmap

### Funcionalidades Pendientes

- [ ] Implementar análisis recursivo completo
- [ ] Agregar soporte para Master Theorem
- [ ] Implementar detector de patrones de recurrencia
- [ ] Añadir análisis de complejidad amortizada
- [ ] Soportar matrices bidimensionales `A[i][j]`
- [ ] Añadir más algoritmos de prueba
- [ ] Mejorar UI con LangGraph Studio

---

## 📄 Licencia

Este proyecto es desarrollado como parte de un proyecto universitario.

**Repositorio:** https://github.com/Jhonder18/Agent_Algorithms

**Rama activa:** `feats/JuanManoel/Agent`

---

*Documentación generada el 4 de diciembre de 2025*

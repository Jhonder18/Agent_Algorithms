# Agent Algorithms – Arquitectura y Flujos

Este documento resume cómo está organizada la aplicación, qué agentes intervienen en cada etapa del pipeline y qué pruebas conviene ejecutar para validar cambios.

## Visión general

- **Tecnologías clave:** FastAPI para el servicio HTTP, LangGraph para orquestar los nodos del pipeline, Lark para el parser determinístico de pseudocódigo y un proveedor LLM (Gemini por defecto) para normalización, validación asistida, cálculos de costos y resúmenes.
- **Entrada principal:** peticiones `POST /api/v2/analyze` con texto o pseudocódigo. El request inicial se transforma en un estado `AnalyzerState` que viaja por LangGraph.
- **Salida:** un diccionario con el pseudocódigo corregido, AST, costos, solución de complejidad y metadatos; opcionalmente se adjunta un resumen natural en la última etapa.

## Flujo del pipeline

1. **Router START → normalize|validate**
   - `route_from_start` usa el `planner` (LLM opcional) o una heurística en `_heuristic_router`.
   - Criterio: presencia de keywords como `begin`, `for`, `if` o el símbolo `🡨`.

2. **normalize (`app/agents/nodes/normalize.py`)**
   - Detecta si el texto ya es pseudocódigo canónico (keywords en inglés, `begin/end`, flecha `🡨`).
   - Si no lo es, llama a `get_llm` con un prompt estricto que exige estructuras bien formadas, flechas correctas, bloques `begin/end` en loops y condicionales, etc.
   - Devuelve `pseudocode` y marca metadatos `input_type`, `used_normalization`.

3. **validate (`app/agents/nodes/validate.py`)**
   - Aplica `_simple_normalize` (flechas, keywords a minúscula, `CALL` en mayúsculas, newline final) y `_ensure_balanced_blocks` para añadir `end` faltantes.
   - Ejecuta el parser Lark mediante `get_parser_agent().parser.parse`.
   - Si falla, `_repair_with_llm` recibe el error de Lark + gramática completa. Tras la respuesta del LLM se vuelve a balancear `begin/end` y se reintenta con Lark.
   - Registra normalizaciones (incluyendo resúmenes del LLM) y devuelve `validation` + el pseudocódigo corregido.

4. **ast (`app/agents/nodes/ast_tool_node.py`)**
   - Invoca la herramienta estructurada `ast_parse_lc` (LangChain StructuredTool) que interna­mente usa `ParserAgent`.
   - El AST se construye con los nodos tipados de `app/tools/ast_parser/ast_nodes.py`, con soporte para:
     - Sentencias (`Assign`, `If`, `While`, `For`, `CallStatement`, `VarDeclaration`, `ActionStatement`, etc.).
     - Expresiones (`Call`, `ArrayAccess`, `ArrayLiteral`, `BinOp`, `UnOp`, `Compare`, `Literal`).
   - Se adjunta `metadata` con el número total de nodos para uso posterior.

5. **costs (`app/agents/nodes/costs.py`)**
   - Si el AST no existe o llega con `success=False`, el nodo corta la ejecución y devuelve costos vacíos (`success=False`, `error` descriptivo). Esto evita pedir al LLM cálculos inventados.
   - Cuando hay AST válido, se llama a `llm_json_call` con un prompt que exige:
     - Costos por nodo (`per_node`) con `line_start/end`, `cost` y `own_cost`.
     - Costos por línea (`per_line`) con operaciones simbólicas.
     - Totales agregados (`total`).
   - Los resultados incluyen `success=True` y metadatos `costs_nodes`, `costs_lines`.

6. **solve (`app/agents/nodes/solve.py`)**
   - Si `costs.success` es falso, se retorna un bloque con `N/A` y el error propagado.
   - En caso contrario, el prompt `SOLVE_SYS` pide pasos algebráicos y cotas (`exact`, `big_o`, `bounds`).
   - El nodo empaqueta `result` con todo lo calculado y actualiza metadatos (`final_pseudocode`, `total_nodes_analyzed`, etc.).

7. **summarize (`app/agents/nodes/summarize.py`)**
   - Opcional; usa el LLM para generar un resumen técnico de 4-6 líneas basado en `state["result"]`.

El flujo finaliza en `END` y la respuesta JSON se envía de vuelta al cliente FastAPI.

## Arquitectura de carpetas relevantes

```
app/
├── api.py                # FastAPI con /api/v2/analyze y /health
├── agents/
│   ├── graph.py          # Construye el StateGraph y rutas
│   ├── planner.py        # Decide normalize vs validate (heurístico o LLM)
│   ├── nodes/            # Nodos normalize, validate, ast, costs, solve, summarize
│   └── state.py          # TypedDict AnalyzerState + helper update_metadata
├── constants.py          # Define ARROW (🡨) y otras constantes globales
├── services/llm.py       # get_llm, strip_code_fences y llm_json_call
└── tools/ast_parser/
    ├── ast_nodes.py      # Definición del IR tipado
    ├── parser_agent.py   # Lark + Transformer + Singleton
    ├── ast_parser.py     # StructuredTool + compatibilidad build_ast
    └── grammar/          # Gramática Lark (*.lark)
```

## Lógica de parsing y transformación

- `grammar.lark` define la sintaxis de pseudocódigo (procedimientos, bucles, condicionales, asignaciones, llamadas, arrays, literales, comentarios con `►`, etc.).
- `PseudocodeToASTTransformer` convierte los árboles de Lark en nodos Python, conservando `line_start/line_end` gracias a `propagate_positions=True`.
- El módulo crea un `ParserAgent` singleton para evitar recargar la gramática en cada llamada; `get_parser_agent` mueve todo el parsing a memoria compartida.
- `create_toolkit()` expone `ast_parse_lc`, permitiendo integrar la tool en LangGraph o en cualquier agente LangChain que soporte herramientas.

## Estrategia de robustez

- **Balance de bloques:** `_ensure_balanced_blocks` añade `end` faltantes tras normalización o reparación con LLM.
- **Validaciones en cadena:** cada nodo comprueba que el paso anterior haya tenido éxito antes de continuar, anotando `success`/`error` en la carga útil.
- **LLM JSON fallback:** `llm_json_call` intenta volver a pedir al modelo un JSON válido si el primero falla al parsearse.
- **Metadatos centralizados:** `update_metadata` evita duplicar lógica al propagar información a través del estado global.

## Casos de prueba recomendados

1. **Pseudocódigo válido sin intervención LLM**
   - Input: algoritmo clásico (ej. burbuja) ya canónico.
   - Expectativa: `normalize.used_normalization=False`, `validation.era_algoritmo_valido=True`, `costs.success=True`, `solve.success=True`.

2. **Texto en lenguaje natural**
   - Input: descripción en español.
   - Verificar que `normalize` invoque al LLM, genere pseudocódigo con flechas `🡨` y se agregue `metadata.used_normalization=True`.

3. **Pseudocódigo con `begin/end` faltantes**
   - Input: loops o condicionales sin `end` de cierre.
   - Asegurar que `_ensure_balanced_blocks` añada los cierres antes de pasar a Lark y que `normalizaciones` registre la acción.

4. **Errores de sintaxis complejos**
   - Input: pseudocódigo con `repeat` mal formado, `CALL` en minúsculas o literales de arreglos.
   - Verificar que tras la reparación con LLM, `validation.parser_ok=True` y que el AST incluya nodos `CallStatement`, `ArrayLiteral`, etc.

5. **Fallos controlados**
   - Forzar un error en el parser (por ejemplo, símbolos ajenos a la gramática) y comprobar que:
     - `validation.errores` documente el fallo.
     - `costs_node` devuelva `success=False` sin invocar al LLM.
     - `solve_node` propague `N/A` y el mensaje de error.

6. **Integración API**
   - Ejecutar `python main.py` (Uvicorn) y hacer requests reales contra `/api/v2/analyze` para confirmar que se reciben todos los campos (`validation`, `ast`, `costs`, `solution`, `metadata`, `summary`).

Para automatizar, puedes mockear `get_llm` con el `provider=stub` (`LLM_PROVIDER=stub`) y así simular respuestas deterministas durante pruebas unitarias o integración ligera.


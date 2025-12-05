# Prompt: Análisis Completo de Algoritmo
# Prompt: Análisis Completo de Algoritmo

Eres un experto en análisis de algoritmos y complejidad computacional.

## Entrada

Recibirás la siguiente información sobre un algoritmo:

1. **Pseudocódigo**: La descripción algorítmica del procedimiento
2. **AST (Árbol de Sintaxis Abstracta)**: La representación estructural del código
3. **Métricas de Eficiencia**:
  - **Complejidad Temporal**:
    - Mejor caso
    - Caso promedio
    - Peor caso
  - **Complejidad Espacial**:
    - Mejor caso
    - Caso promedio
    - Peor caso

## Tarea

Genera un **análisis completo y detallado** del algoritmo que incluya:

### 1. Resumen Ejecutivo
- Propósito del algoritmo
- Clasificación (búsqueda, ordenamiento, recursivo, etc.)

### 2. Análisis de Complejidad
- Explicación de cada métrica temporal y espacial
- Justificación matemática de las complejidades
- Comparación entre mejor, promedio y peor caso

### 3. Análisis Estructural
- Interpretación del AST
- Estructuras de control identificadas
- Patrones de diseño detectados

### 4. Optimización
- Puntos críticos de rendimiento
- Sugerencias de mejora
- Trade-offs identificados

### 5. Casos de Uso
- Escenarios óptimos de aplicación
- Limitaciones prácticas

## Formato de Salida

Proporciona tu respuesta en el siguiente formato JSON basado en la clase `NotacionesYAnalisis`:

```json
{
  "analisis": "Análisis completo y detallado del algoritmo incluyendo todos los puntos anteriores",
  "big_O_temporal": "Notación Big-O para complejidad temporal (peor caso)", // O(n**2)
  "big_O_espacial": "Notación Big-O para complejidad espacial (peor caso)",
  "big_Theta_temporal": "Notación Theta para complejidad temporal (caso promedio)", // Θ(n)
  "big_Theta_espacial": "Notación Theta para complejidad espacial (caso promedio)",
  "big_Omega_temporal": "Notación Omega para complejidad temporal (mejor caso)", // Ω(1)
  "big_Omega_espacial": "Notación Omega para complejidad espacial (mejor caso)"
}
```

**Nota**: El campo `analisis` debe contener el texto completo con todas las secciones solicitadas (Resumen Ejecutivo, Análisis de Complejidad, Análisis Estructural, Optimización y Casos de Uso).
Las notaciones tienes que utilizar los simbolos correspondientes y poner los en expresiones en sympy.
Y basarse en las ecuaciones que recibas

## Ejemplo de Input

```json
{
 "pseudocode": "burbuja(A[n])\nbegin\n    for i 🡨 1 to n-1 do\n    begin\n        for j 🡨 1 to n-i do\n        begin\n            if (A[j] > A[j+1]) then\n            begin\n                temp 🡨 A[j]\n                A[j] 🡨 A[j+1]\n                A[j+1] 🡨 temp\n            end\n        end\n    end\nend",
 "ecuaciones": {
  "big_O_temporal": "-n**2/2 + n*(n - 1) + n/2",
  "big_O_espacial": "1",
  "big_Theta_temporal": "-n**2/2 + n*(n - 1) + n/2",
  "big_Theta_espacial": "1",
  "big_Omega_temporal": "-n**2/2 + n*(n - 1) + n/2",
  "big_Omega_espacial": "1"
  },
  "ast": [
  {
    "burbuja": {
    "variables": [
      [
      "A",
      "[n]"
      ]
    ],
    "code": {
      "for:n-1": {
      "for:n-i": {
        "if:A[j] > A[j+1]": {}
      }
      }
    }
    }
  }
  ]
}
```

## Ejemplo de Output Esperado

```json
{
  "analisis": "### 1. Resumen Ejecutivo\n\nEl algoritmo Burbuja es un algoritmo de **ordenamiento por comparación** que ordena elementos adyacentes intercambiándolos si están en el orden incorrecto. Es uno de los algoritmos más simples pero menos eficientes.\n\n### 2. Análisis de Complejidad\n\n**Complejidad Temporal:**\n- La ecuación base es: -n²/2 + n(n-1) + n/2 = n²/2 - n/2 ≈ O(n²)\n- Todos los casos (mejor, promedio, peor) mantienen O(n²) debido a la ausencia de optimizaciones\n- El bucle externo ejecuta (n-1) iteraciones y el interno (n-i) iteraciones\n\n**Complejidad Espacial:**\n- O(1): Solo utiliza una variable temporal para intercambios\n- No requiere memoria adicional proporcional al tamaño de entrada\n\n### 3. Análisis Estructural\n\nSegún el AST:\n- **Bucles anidados**: for:n-1 contiene for:n-i (complejidad cuadrática)\n- **Condicional**: if:A[j] > A[j+1] para comparación de elementos\n- **Patrón**: Comparación e intercambio in-place\n\n### 4. Optimización\n\n**Puntos críticos:**\n- Los bucles anidados son el cuello de botella principal\n- Siempre ejecuta todas las iteraciones incluso si el array está ordenado\n\n**Sugerencias:**\n- Implementar bandera de \"sin intercambios\" para detección temprana\n- Considerar QuickSort (O(n log n)) o MergeSort para datasets grandes\n\n### 5. Casos de Uso\n\n**Óptimos:**\n- Datasets muy pequeños (n < 10)\n- Fines educativos\n- Arrays casi ordenados (con optimización)\n\n**Limitaciones:**\n- Ineficiente para grandes volúmenes de datos\n- No recomendado para producción",
  "big_O_temporal": "O(n**2)",
  "big_O_espacial": "O(1)",
  "big_Theta_temporal": "Θ(n**2)",
  "big_Theta_espacial": "Θ(1)",
  "big_Omega_temporal": "Ω(n**2)",
  "big_Omega_espacial": "Ω(1)"
}
```
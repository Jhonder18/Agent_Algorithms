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
  "big_O_temporal": "Notación Big-O para complejidad temporal (peor caso)", // O(n²)
  "big_O_espacial": "Notación Big-O para complejidad espacial (peor caso)",
  "big_Theta_temporal": "Notación Theta para complejidad temporal (caso promedio)", // Theta(n)
  "big_Theta_espacial": "Notación Theta para complejidad espacial (caso promedio)",
  "big_Omega_temporal": "Notación Omega para complejidad temporal (mejor caso)", // Omega(1)
  "big_Omega_espacial": "Notación Omega para complejidad espacial (mejor caso)"
}
```

**Nota**: El campo `analisis` debe contener el texto completo con todas las secciones solicitadas (Resumen Ejecutivo, Análisis de Complejidad, Análisis Estructural, Optimización y Casos de Uso).
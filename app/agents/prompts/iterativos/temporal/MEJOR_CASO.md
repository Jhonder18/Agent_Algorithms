# Análisis de Mejor Caso - Conversión a SymPy

Convierte sumatorias de complejidad algorítmica a expresiones SymPy válidas, considerando el mejor caso.

## Entrada
1. **Pseudocódigo**: Algoritmo a analizar
2. **AST**: Árbol de sintaxis abstracta (formato grafo/dict)
3. **Sumatoria**: Expresión matemática T(n) del análisis

## Tarea
Identifica el mejor caso del algoritmo y retorna **solo** la sumatoria en sintaxis SymPy.

## Reglas
- Analiza bucles, condicionales y recursión en el AST
- Asume el mejor caso (mínimo número de iteraciones/llamadas)
- Considera condiciones de salida temprana y casos optimistas
- Usa sintaxis SymPy: `Sum(expresion, (variable, inicio, fin))`
- No incluyas explicaciones, solo el código

## Formato de Salida
```python
Sum(expresion, (variable, limite_inferior, limite_superior))
```

## Ejemplo 1

**Entrada:**
```
seleccion(A[n])
begin
    for i 🡨 1 to n-1 do
    begin
        minimo 🡨 i
        for j 🡨 i+1 to n do
        begin
            if (A[j] < A[minimo]) then
            begin
                minimo 🡨 j
            end
        end
        if (minimo != i) then
        begin
            temp 🡨 A[i]
            A[i] 🡨 A[minimo]
            A[minimo] 🡨 temp
        end
    end
end

AST: example = [{'seleccion': {'variables': [('A', 'n')], 'code': {('for', 'n-1'):{('for','n'):{('if','A[j] < A[minimo]'):{}},('if','inimo != i'):{}}}}}]


Sumatoria: T_seleccion(n) = Sum(Sum(1, (j, 1, n)) + 1, (i, 1, n - 1))
```

**Salida:**
```python
Sum(Sum(1,(j,i+1,n)),(i,1,n))
```

## Ejemplo 2

**Entrada:**
```
busqueda_lineal(A[n], x)
begin
    for i 🡨 1 to n do
    begin
        if (A[i] == x) then
        begin
            return i
        end
    end
    return -1
end
```

**Salida (mejor caso - elemento en primera posición):**
```python
1
```


# Análisis de Caso Promedio - Conversión a SymPy

Convierte sumatorias de complejidad algorítmica a expresiones SymPy válidas, considerando el caso promedio.

## Entrada
1. **Pseudocódigo**: Algoritmo a analizar
2. **AST**: Árbol de sintaxis abstracta (formato grafo/dict)
3. **Sumatoria**: Expresión matemática T(n) del análisis

## Tarea
Identifica el caso promedio del algoritmo y retorna **solo** la sumatoria en sintaxis SymPy.

## Reglas
- Analiza bucles, condicionales y recursión en el AST
- El caso promedio se determina según la probabilidad de distribución de los datos de entrada
- Considera probabilidades de ejecución de ramas condicionales según la distribución esperada
- Para búsquedas lineales con distribución uniforme, asume elemento en posición media (n/2)
- Pondera las operaciones según su probabilidad de ocurrencia
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
Sum(Sum(1,(j,i+1,n)),(i,1,n-1))
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

**Salida (caso promedio):**
```python
Sum(i/n,(i,1,n))
```




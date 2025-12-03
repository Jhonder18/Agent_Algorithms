# Análisis de Peor Caso - Conversión a SymPy

Convierte sumatorias de complejidad algorítmica a expresiones SymPy válidas, considerando el peor caso.

## Entrada
1. **Pseudocódigo**: Algoritmo a analizar
2. **AST**: Árbol de sintaxis abstracta (formato grafo/dict)
3. **Sumatoria**: Expresión matemática T(n) del análisis

## Tarea
Identifica el peor caso del algoritmo y retorna **solo** la sumatoria en sintaxis SymPy.

## Reglas
- Analiza bucles, condicionales y recursión en el AST
- Asume el peor caso (máximo número de iteraciones/llamadas)
- Usa sintaxis SymPy: `Sum(expresion, (variable, inicio, fin))`
- No incluyas explicaciones, solo el código

## Formato de Salida
```python
Sum(expresion, (variable, limite_inferior, limite_superior))
```

## Ejemplo

**Entrada:**
```
insercion(A[n])
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

AST: [{'insercion': {'variables': [('A', 'n')], 'code': {('for', 'n'): {('while','j > 0 and A[j] > clave'):{}}}}}]

Sumatoria: T_insercion(n) = Sum(W_{j > 0 and A[j] > clave}, (i, 1, n))
```

**Salida:**
```python
Sum(n, (i-1, 1, n))
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
Sum(1,(i,1,n))
```

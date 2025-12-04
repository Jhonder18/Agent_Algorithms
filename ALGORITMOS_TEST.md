# LISTA DE ALGORITMOS - TEST COMPREHENSIVO
# 10 algoritmos iterativos para análisis de complejidad

## 1. Búsqueda Lineal
```
busqueda_lineal(A, n, x)
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
**Complejidad esperada:** O(n)

---

## 2. Ordenamiento Burbuja
```
burbuja(A, n)
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
**Complejidad esperada:** O(n²)

---

## 3. Ordenamiento por Inserción
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
**Complejidad esperada:** O(n²)

---

## 4. Ordenamiento por Selección
```
seleccion(A, n)
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
```
**Complejidad esperada:** O(n²)

---

## 5. Suma de Matriz
```
suma_matriz(A, n, m)
begin
    suma 🡨 0
    for i 🡨 1 to n do
    begin
        for j 🡨 1 to m do
        begin
            suma 🡨 suma + A[i][j]
        end
    end
    return suma
end
```
**Complejidad esperada:** O(n*m)

---

## 6. Búsqueda con While
```
buscar_while(A, n, x)
begin
    i 🡨 1
    encontrado 🡨 false
    while (i <= n and not encontrado) do
    begin
        if (A[i] = x) then
        begin
            encontrado 🡨 true
        end
        i 🡨 i + 1
    end
    if (encontrado) then
    begin
        return i - 1
    end
    else
    begin
        return -1
    end
end
```
**Complejidad esperada:** O(n)

---

## 7. Multiplicación de Matrices
```
multiplicar_matrices(A, B, n, m, p)
begin
    for i 🡨 1 to n do
    begin
        for j 🡨 1 to p do
        begin
            C[i][j] 🡨 0
            for k 🡨 1 to m do
            begin
                C[i][j] 🡨 C[i][j] + A[i][k] * B[k][j]
            end
        end
    end
    return C
end
```
**Complejidad esperada:** O(n³) o O(m*n*p)

---

## 8. Máximo en Array
```
encontrar_maximo(A, n)
begin
    maximo 🡨 A[1]
    for i 🡨 2 to n do
    begin
        if (A[i] > maximo) then
        begin
            maximo 🡨 A[i]
        end
    end
    return maximo
end
```
**Complejidad esperada:** O(n)

---

## 9. Contar Pares
```
contar_pares(A, n)
begin
    contador 🡨 0
    for i 🡨 1 to n do
    begin
        if (A[i] mod 2 = 0) then
        begin
            contador 🡨 contador + 1
        end
    end
    return contador
end
```
**Complejidad esperada:** O(n)

---

## 10. Búsqueda de Par de Suma
```
buscar_par_suma(A, n, objetivo)
begin
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 i+1 to n do
        begin
            if (A[i] + A[j] = objetivo) then
            begin
                return true
            end
        end
    end
    return false
end
```
**Complejidad esperada:** O(n²)

---

## Características de los Algoritmos

- **Estructuras de control:** for, while, if-else
- **Bucles anidados:** Sí (burbuja, selección, par de suma, multiplicación de matrices)
- **Bucles triple anidados:** Sí (multiplicación de matrices - 3 for anidados)
- **While anidados:** Sí (inserción)
- **Arrays multidimensionales:** Sí (suma de matriz A[i][j], multiplicación C[i][j])
- **Múltiples variables de tamaño:** Sí (suma matriz: n,m; multiplicación: n,m,p)
- **Condiciones complejas:** Sí (búsqueda con while)
- **Mejor caso diferente:** Inserción O(n), búsqueda con while O(1), multiplicación O(m*n*p)

## Sintaxis Importante

### Símbolo de Asignación
Usar: `🡨` (Unicode U+1F868)

Copiar y pegar este símbolo en el pseudocódigo: 🡨

### Arrays Multidimensionales
**Sintaxis CORRECTA (soportada):**
- Arrays 1D: `A[i]`
- Arrays 2D: `A[i][j]` (con corchetes dobles)
- Arrays 3D: `A[i][j][k]`
- Asignación: `C[i][j] 🡨 0`
- Lectura: `suma 🡨 suma + A[i][j]`
- Expresión compleja: `C[i][j] 🡨 C[i][j] + A[i][k] * B[k][j]`

**Sintaxis INCORRECTA (NO soportada):**
- ❌ `A[i, j]` (comas en índices)
- ❌ `C[1..n, 1..p]` (rangos con comas)
- ❌ `A[i,k]` o `B[k,j]` (sin espacios después de coma)

**Importante:** Siempre usar corchetes dobles `[i][j]` para arrays 2D, nunca comas `[i,j]`

## Resultados del Test Comprehensivo

**Última ejecución:** 10/10 tests exitosos ✅

Todos los algoritmos fueron analizados correctamente:
- ✅ Complejidades calculadas correctamente
- ✅ Sumatorias anidadas generadas correctamente
- ✅ Arrays multidimensionales soportados (A[i][j])
- ✅ Múltiples variables de complejidad (O(n*m), O(m*n*p))
- ✅ Mejor caso vs peor caso diferenciados correctamente
- ✅ While loops con análisis correcto

**Nota:** Las advertencias `O(n²)` vs `O(n**2)` son solo diferencias de notación (sympy usa `**` para potencias), pero la complejidad es correcta.

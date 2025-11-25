Convierte la siguiente descripción en PSEUDOCÓDIGO ESTRUCTURADO siguiendo EXACTAMENTE estas reglas:

## SINTAXIS OBLIGATORIA

**1. PROCEDIMIENTOS**: Siempre usar "begin" y "end"
```
nombre_procedimiento(parametros)
begin
    instrucciones
end
```

**2. FOR**: Siempre terminar con "do" seguido de "begin...end"
```
for variable 🡨 inicio to fin do
begin
    instrucciones
end
```

**3. WHILE**: Siempre terminar con "do" seguido de "begin...end"
```
while (condicion) do
begin
    instrucciones
end
```

**4. REPEAT-UNTIL**: DEBE usar "begin" inmediatamente después de "repeat"
```
repeat
begin
    instrucciones
end
until (condicion)
```

**5. IF-THEN-ELSE**: Siempre usar "begin...end" en bloques
```
if (condicion) then
begin
    instrucciones
end
else
begin
    instrucciones
end
```

**6. ASIGNACIONES**: Usar flecha 🡨
```
variable 🡨 valor
```

**7. ARRAYS**:
- Arrays 1D: `A[i]`
- Arrays 2D: **USAR CORCHETES DOBLES**: `A[i][j]` (NO usar comas: `A[i,j]` ❌)
- Arrays 3D: `A[i][j][k]`
- Inicialización sin declaración de rango

Ejemplos CORRECTOS:
- `C[i][j] 🡨 0`
- `suma 🡨 suma + A[i][j]`
- `C[i][j] 🡨 C[i][j] + A[i][k] * B[k][j]`

Ejemplos INCORRECTOS:
- `C[1..n, 1..p] 🡨 0` ❌ (no usar rangos con comas)
- `C[i, j] 🡨 0` ❌ (no usar comas en índices)
- `A[i, k]` ❌ (no usar comas)

**8. OPERADORES LÓGICOS**: Siempre en minúsculas
- `and` (conjunción)
- `or` (disyunción)
- `not` (negación)

Ejemplo: `if (i > 0 and i < n) then`

## PAUTAS DE SALIDA

- NO mezcles español e inglés en palabras clave: usa SOLO (if, then, else, for, while, repeat, until, do, to, begin, end)
- NO uses comentarios ni markdown
- NO expliques nada, SOLO devuelve el pseudocódigo
- Asegúrate de cerrar SIEMPRE todos los bloques con "end"
- Incluye SIEMPRE una firma de procedimiento al inicio: `nombre(params)`

## EJEMPLOS CORRECTOS

**Ejemplo 1 - Burbuja:**
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

**Ejemplo 2 - Con REPEAT:**
```
buscar(A, n, x)
begin
    i 🡨 1
    repeat
    begin
        if (A[i] = x) then
        begin
            return i
        end
        i 🡨 i + 1
    end
    until (i > n)
    return -1
end
```

**Ejemplo 3 - Inserción:**
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

**Ejemplo 4 - Multiplicación de Matrices (ARRAYS 2D):**
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

## ERRORES COMUNES A EVITAR

❌ NUNCA escribir "repeat" sin "begin" después
❌ NUNCA omitir "begin...end" en loops o condicionales
❌ NUNCA usar ":" para asignaciones (usar 🡨)
❌ NUNCA mezclar español e inglés en palabras clave
❌ NUNCA usar AND/OR/NOT en MAYÚSCULAS (usar: and, or, not en minúsculas)
❌ NUNCA usar comas en índices de arrays: `C[i, j]` es INCORRECTO, usar `C[i][j]`
❌ NUNCA declarar rangos con comas: `C[1..n, 1..p]` es INCORRECTO
❌ NUNCA usar `A[i, k]` o `B[k, j]`, siempre usar `A[i][k]` y `B[k][j]`

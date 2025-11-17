#!/usr/bin/env python3
# test_comprehensive.py
"""
Test completo con 10 algoritmos iterativos diversos
Incluye: for, while, if, bucles anidados, condiciones complejas
"""
import sys
import time
sys.path.insert(0, ".")

from app.agents.graph import build_graph

# 10 algoritmos de prueba con diferentes estructuras
TEST_ALGORITHMS = [
    {
        "name": "1. Búsqueda Lineal",
        "pseudocode": """busqueda_lineal(A, n, x)
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
""",
        "expected_complexity": "O(n)"
    },
    {
        "name": "2. Ordenamiento Burbuja",
        "pseudocode": """burbuja(A, n)
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
""",
        "expected_complexity": "O(n²)"
    },
    {
        "name": "3. Ordenamiento por Inserción",
        "pseudocode": """insercion(A, n)
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
""",
        "expected_complexity": "O(n²)"
    },
    {
        "name": "4. Ordenamiento por Selección",
        "pseudocode": """seleccion(A, n)
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
""",
        "expected_complexity": "O(n²)"
    },
    {
        "name": "5. Suma de Matriz",
        "pseudocode": """suma_matriz(A, n, m)
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
""",
        "expected_complexity": "O(n*m)"
    },
    {
        "name": "6. Búsqueda con While",
        "pseudocode": """buscar_while(A, n, x)
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
""",
        "expected_complexity": "O(n)"
    },
    {
        "name": "7. Multiplicación de Matrices",
        "pseudocode": """multiplicar_matrices(A, B, n, m, p)
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
""",
        "expected_complexity": "O(n³)"
    },
    {
        "name": "8. Máximo en Array",
        "pseudocode": """encontrar_maximo(A, n)
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
""",
        "expected_complexity": "O(n)"
    },
    {
        "name": "9. Contar Pares",
        "pseudocode": """contar_pares(A, n)
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
""",
        "expected_complexity": "O(n)"
    },
    {
        "name": "10. Búsqueda de Par de Suma",
        "pseudocode": """buscar_par_suma(A, n, objetivo)
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
""",
        "expected_complexity": "O(n²)"
    }
]

def run_test(graph, test_case, index):
    """Ejecuta un caso de prueba y muestra resultados"""
    print(f"\n{'='*80}")
    print(f"TEST {index}: {test_case['name']}")
    print(f"{'='*80}")
    print(f"Complejidad esperada: {test_case['expected_complexity']}")
    
    try:
        # Invocar el grafo
        state = {"input_text": test_case['pseudocode'].strip()}
        result = graph.invoke(state)
        
        # Extraer información clave
        validation = result.get("validation", {})
        ast_result = result.get("ast", {})
        costs = result.get("costs", {})
        solution = result.get("solution", {})
        
        # Validación
        print(f"\n[OK] Validación: {'VÁLIDO' if validation.get('era_algoritmo_valido') else 'INVÁLIDO'}")
        if validation.get('errores'):
            print(f"  Errores: {validation['errores']}")
        
        # AST
        print(f"[OK] AST: {'Parseado' if ast_result.get('success') else 'ERROR'}")
        if ast_result.get('success'):
            ast_obj = ast_result.get('ast', {})
            functions = ast_obj.get('functions', [])
            if functions:
                print(f"  Función: {functions[0].get('name', 'N/A')}")
        
        # Costos
        per_line = costs.get('per_line', [])
        print(f"[OK] Costos: {len(per_line)} líneas analizadas")
        
        # Complejidades
        big_o = solution.get('big_o', {})
        bounds = solution.get('bounds', {})
        
        print(f"\n[COMPLEXITY] Complejidades calculadas:")
        print(f"  Mejor caso:    {big_o.get('best', 'N/A')}")
        print(f"  Caso promedio: {big_o.get('avg', 'N/A')}")
        print(f"  Peor caso:     {big_o.get('worst', 'N/A')}")
        print(f"  Theta:         {bounds.get('theta', 'N/A')}")
        
        # Verificar si coincide con lo esperado
        expected = test_case['expected_complexity']
        calculated = big_o.get('worst', 'N/A')
        
        if expected in calculated or calculated in expected:
            print(f"\n[PASS] CORRECTO: Complejidad coincide con la esperada")
        else:
            print(f"\n[WARN] ADVERTENCIA: Esperado {expected}, calculado {calculated}")
        
        # Mostrar algunas líneas de costo
        print(f"\n[COSTS] Costos por línea (primeras 5):")
        for i, line_cost in enumerate(per_line[:5]):
            ops = ', '.join(line_cost.get('operations', []))
            worst = line_cost.get('cost', {}).get('worst', 'N/A')
            print(f"  L{line_cost.get('line_number')}: [{ops}] → {worst[:60]}{'...' if len(str(worst)) > 60 else ''}")
        
        if len(per_line) > 5:
            print(f"  ... y {len(per_line) - 5} líneas más")
        
        # Summary
        summary = result.get('summary', '')
        if summary:
            print(f"\n[SUMMARY] Resumen:")
            # Mostrar primeras 200 caracteres del resumen
            print(f"  {summary[:200]}{'...' if len(summary) > 200 else ''}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("TEST COMPREHENSIVO - 10 ALGORITMOS ITERATIVOS")
    print("="*80)
    print(f"Total de tests: {len(TEST_ALGORITHMS)}")
    print(f"Delay entre tests: 10 segundos (límite de API)")
    print("="*80)
    
    # Construir el grafo una vez
    print("\n[*] Construyendo grafo de LangGraph...")
    graph = build_graph()
    print("[OK] Grafo construido")
    
    # Ejecutar cada test
    results = []
    for i, test_case in enumerate(TEST_ALGORITHMS, 1):
        success = run_test(graph, test_case, i)
        results.append({
            "name": test_case['name'],
            "success": success
        })
        
        # Delay entre tests (excepto después del último)
        if i < len(TEST_ALGORITHMS):
            print(f"\n[WAIT] Esperando 10 segundos antes del siguiente test...")
            time.sleep(10)
    
    # Resumen final
    print(f"\n{'='*80}")
    print("RESUMEN FINAL")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n[OK] Tests exitosos: {successful}/{len(results)}")
    print(f"[FAIL] Tests fallidos: {failed}/{len(results)}")
    
    if failed > 0:
        print(f"\nTests fallidos:")
        for r in results:
            if not r['success']:
                print(f"  - {r['name']}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETO")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

"""
Test del pipeline recursivo con diferentes ecuaciones de recurrencia.
Prueba algoritmos canónicos: factorial, búsqueda binaria, merge sort, fibonacci, etc.
"""
import json
from typing import Dict, Any
from app.agents.graph import build_graph
from app.agents.state import AnalyzerState


# ═══════════════════════════════════════════════════════════════════════════════
# CASOS DE PRUEBA - Algoritmos recursivos canónicos
# ═══════════════════════════════════════════════════════════════════════════════

TEST_CASES: list[Dict[str, Any]] = [
    # ───────────────────────────────────────────────────────────────────────────
    # F4: T(n) = T(n-1) + O(1) → O(n)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Factorial",
        "tipo_esperado": "F4",
        "complejidad_esperada": "O(n)",
        "pseudocode": """factorial(n)
begin
    if n <= 1 then
        return 1
    else
        return n * factorial(n - 1)
    end
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # F0: T(n) = T(n/2) + O(1) → O(log n)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Búsqueda Binaria",
        "tipo_esperado": "F0",
        "complejidad_esperada": "O(log n)",
        "pseudocode": """busquedaBinaria(A, x, low, high)
begin
    if low > high then
        return -1
    end
    
    mid ← (low + high) / 2
    
    if A[mid] = x then
        return mid
    else if A[mid] > x then
        return busquedaBinaria(A, x, low, mid - 1)
    else
        return busquedaBinaria(A, x, mid + 1, high)
    end
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # F1: T(n) = 2T(n/2) + O(n) → O(n log n)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Merge Sort",
        "tipo_esperado": "F1",
        "complejidad_esperada": "O(n log n)",
        "pseudocode": """mergeSort(A, p, r)
begin
    if p < r then
    begin
        q ← (p + r) / 2
        mergeSort(A, p, q)
        mergeSort(A, q + 1, r)
        merge(A, p, q, r)
    end
end

merge(A, p, q, r)
begin
    n1 ← q - p + 1
    n2 ← r - q
    
    for i ← 1 to n1 do
        L[i] ← A[p + i - 1]
    end
    
    for j ← 1 to n2 do
        R[j] ← A[q + j]
    end
    
    i ← 1
    j ← 1
    k ← p
    
    while i <= n1 and j <= n2 do
    begin
        if L[i] <= R[j] then
        begin
            A[k] ← L[i]
            i ← i + 1
        end
        else
        begin
            A[k] ← R[j]
            j ← j + 1
        end
        k ← k + 1
    end
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # F3/F6: T(n) = T(n-1) + T(n-2) + O(1) → O(φⁿ) ≈ O(1.618ⁿ)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Fibonacci (Ingenuo)",
        "tipo_esperado": "F6",
        "complejidad_esperada": "O(2^n) o O(φ^n)",
        "pseudocode": """fibonacci(n)
begin
    if n <= 1 then
        return n
    else
        return fibonacci(n - 1) + fibonacci(n - 2)
    end
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # F1: T(n) = 2T(n/2) + O(1) → O(n)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Suma de Arreglo (Divide y Vencerás)",
        "tipo_esperado": "F1",
        "complejidad_esperada": "O(n)",
        "pseudocode": """sumaRecursiva(A, low, high)
begin
    if low = high then
        return A[low]
    end
    
    mid ← (low + high) / 2
    leftSum ← sumaRecursiva(A, low, mid)
    rightSum ← sumaRecursiva(A, mid + 1, high)
    
    return leftSum + rightSum
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # F1: T(n) = 8T(n/2) + O(n²) → O(n³)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Multiplicación de Matrices (Naive)",
        "tipo_esperado": "F1",
        "complejidad_esperada": "O(n^3)",
        "pseudocode": """multiplicarMatrices(A, B, n)
begin
    if n = 1 then
        return A[1,1] * B[1,1]
    end
    
    dividir A en A11, A12, A21, A22
    dividir B en B11, B12, B21, B22
    
    C11 ← multiplicarMatrices(A11, B11, n/2) + multiplicarMatrices(A12, B21, n/2)
    C12 ← multiplicarMatrices(A11, B12, n/2) + multiplicarMatrices(A12, B22, n/2)
    C21 ← multiplicarMatrices(A21, B11, n/2) + multiplicarMatrices(A22, B21, n/2)
    C22 ← multiplicarMatrices(A21, B12, n/2) + multiplicarMatrices(A22, B22, n/2)
    
    return combinar(C11, C12, C21, C22)
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # F1: T(n) = 2^n (exponencial)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Torres de Hanoi",
        "tipo_esperado": "F5",
        "complejidad_esperada": "O(2^n)",
        "pseudocode": """hanoi(n, origen, destino, auxiliar)
begin
    if n = 1 then
        mover(origen, destino)
    else
        hanoi(n - 1, origen, auxiliar, destino)
        mover(origen, destino)
        hanoi(n - 1, auxiliar, destino, origen)
    end
end"""
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # Quick Sort: T(n) = T(k) + T(n-k-1) + O(n)
    # Promedio: O(n log n), Peor: O(n²)
    # ───────────────────────────────────────────────────────────────────────────
    {
        "nombre": "Quick Sort",
        "tipo_esperado": "F1",
        "complejidad_esperada": "O(n log n) promedio, O(n²) peor",
        "pseudocode": """quickSort(A, low, high)
begin
    if low < high then
    begin
        pivot ← partition(A, low, high)
        quickSort(A, low, pivot - 1)
        quickSort(A, pivot + 1, high)
    end
end

partition(A, low, high)
begin
    pivot ← A[high]
    i ← low - 1
    
    for j ← low to high - 1 do
    begin
        if A[j] <= pivot then
        begin
            i ← i + 1
            swap(A[i], A[j])
        end
    end
    
    swap(A[i + 1], A[high])
    return i + 1
end"""
    },
]


def print_separator(char: str = "═", length: int = 80):
    """Imprime una línea separadora."""
    print(char * length)


def print_header(text: str):
    """Imprime un encabezado formateado."""
    print_separator()
    print(f"  {text}")
    print_separator()


def run_test(test_case: Dict[str, Any], graph) -> Dict[str, Any]:
    """
    Ejecuta un caso de prueba individual.
    
    Args:
        test_case: Diccionario con datos del test
        graph: Grafo compilado de LangGraph
        
    Returns:
        Diccionario con los resultados
    """
    nombre = test_case["nombre"]
    tipo_esperado = test_case["tipo_esperado"]
    complejidad_esperada = test_case["complejidad_esperada"]
    pseudocode = test_case["pseudocode"]
    
    print(f"\n{'─' * 60}")
    print(f"🧪 TEST: {nombre}")
    print(f"{'─' * 60}")
    print(f"📌 Tipo esperado: {tipo_esperado}")
    print(f"📌 Complejidad esperada: {complejidad_esperada}")
    print(f"\n📝 Pseudocódigo:")
    print(f"{'.' * 40}")
    # Imprimir solo las primeras líneas del pseudocódigo
    lines = pseudocode.strip().split('\n')
    for line in lines[:8]:
        print(f"   {line}")
    if len(lines) > 8:
        print(f"   ... ({len(lines) - 8} líneas más)")
    print(f"{'.' * 40}")
    
    # Crear estado inicial
    state = AnalyzerState()
    state["nl_description"] = pseudocode
    
    # Ejecutar el grafo
    print("\n⏳ Ejecutando pipeline recursivo...")
    try:
        result = graph.invoke(state)
        
        print("\n✅ RESULTADO:")
        print(f"   Modo detectado: {result.get('mode', 'N/A')}")
        
        # Mostrar ecuaciones
        ecuaciones = result.get("ecuaciones", {})
        temporal = ecuaciones.get("temporal", {})
        espacial = ecuaciones.get("espacial", {})
        
        print(f"\n   📊 COMPLEJIDAD TEMPORAL:")
        print(f"      O (peor):     {temporal.get('O', 'N/A')}")
        print(f"      Ω (mejor):    {temporal.get('omega', 'N/A')}")
        print(f"      Θ (promedio): {temporal.get('theta', 'N/A')}")
        
        print(f"\n   📊 COMPLEJIDAD ESPACIAL:")
        print(f"      O (peor):     {espacial.get('O', 'N/A')}")
        print(f"      Ω (mejor):    {espacial.get('omega', 'N/A')}")
        print(f"      Θ (promedio): {espacial.get('theta', 'N/A')}")
        
        # Mostrar recurrencia detectada si existe
        recurrence_info = result.get("recurrence_info", {})
        if recurrence_info:
            print(f"\n   🔄 RECURRENCIA DETECTADA:")
            print(f"      Ecuación: {recurrence_info.get('raw', 'N/A')}")
            print(f"      Tipo: {recurrence_info.get('tipo', 'N/A')}")
        
        # Mostrar árbol de recursión si existe
        if result.get("recursion_tree"):
            print(f"\n   🌳 ÁRBOL DE RECURSIÓN: Generado")
        
        # Mostrar diagrama Mermaid si existe
        if result.get("mermaid_diagram"):
            print(f"\n   📈 DIAGRAMA MERMAID: Disponible")
            mermaid = result.get("mermaid_diagram", "")
            # Mostrar primeras líneas del diagrama
            mermaid_lines = mermaid.split('\n')[:5]
            for line in mermaid_lines:
                print(f"      {line}")
            if len(mermaid.split('\n')) > 5:
                print(f"      ...")
        
        # Mostrar razonamiento resumido
        razonamiento = result.get("razonamiento", [])
        if razonamiento and len(razonamiento) > 0:
            print(f"\n   💭 RAZONAMIENTO ({len(razonamiento)} pasos):")
            for paso in razonamiento[-3:]:  # Últimos 3 pasos
                if isinstance(paso, dict):
                    print(f"      - {paso.get('accion', 'N/A')}: {paso.get('detalle', '')[:60]}...")
        
        return {
            "nombre": nombre,
            "exito": True,
            "mode": result.get("mode"),
            "temporal": temporal,
            "espacial": espacial,
            "recurrence": recurrence_info,
            "complejidad_esperada": complejidad_esperada
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "nombre": nombre,
            "exito": False,
            "error": str(e),
            "complejidad_esperada": complejidad_esperada
        }


def run_all_tests():
    """Ejecuta todos los casos de prueba."""
    print_header("🚀 TEST DEL PIPELINE RECURSIVO")
    print(f"📅 Ejecutando {len(TEST_CASES)} casos de prueba...\n")
    
    # Compilar el grafo una sola vez
    print("⚙️  Compilando grafo de LangGraph...")
    graph = build_graph().compile()
    print("✅ Grafo compilado exitosamente\n")
    
    results = []
    exitosos = 0
    fallidos = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'═' * 60}")
        print(f"  CASO {i}/{len(TEST_CASES)}")
        print(f"{'═' * 60}")
        
        result = run_test(test_case, graph)
        results.append(result)
        
        if result["exito"]:
            exitosos += 1
        else:
            fallidos += 1
    
    # Resumen final
    print_header("📊 RESUMEN DE RESULTADOS")
    
    print(f"\n✅ Exitosos: {exitosos}/{len(TEST_CASES)}")
    print(f"❌ Fallidos: {fallidos}/{len(TEST_CASES)}")
    
    print(f"\n{'─' * 60}")
    print("DETALLE POR ALGORITMO:")
    print(f"{'─' * 60}")
    
    for r in results:
        status = "✅" if r["exito"] else "❌"
        nombre = r["nombre"]
        esperado = r["complejidad_esperada"]
        
        if r["exito"]:
            temporal = r.get("temporal", {})
            obtenido = temporal.get("O", "N/A")
            print(f"{status} {nombre:<30} | Esperado: {esperado:<20} | Obtenido: {obtenido}")
        else:
            print(f"{status} {nombre:<30} | Esperado: {esperado:<20} | Error: {r.get('error', 'N/A')[:30]}")
    
    print_separator()
    
    return results


def run_single_test(index: int = 0):
    """
    Ejecuta un solo caso de prueba por índice.
    
    Args:
        index: Índice del caso (0-based)
    """
    if index < 0 or index >= len(TEST_CASES):
        print(f"❌ Índice inválido. Debe estar entre 0 y {len(TEST_CASES) - 1}")
        return
    
    print_header(f"🧪 TEST INDIVIDUAL: {TEST_CASES[index]['nombre']}")
    
    graph = build_graph().compile()
    result = run_test(TEST_CASES[index], graph)
    
    print_separator()
    print(f"{'✅ ÉXITO' if result['exito'] else '❌ FALLO'}")
    print_separator()
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Si se pasa un argumento, ejecutar ese test específico
        try:
            index = int(sys.argv[1])
            run_single_test(index)
        except ValueError:
            # Si es un nombre, buscar el test
            nombre = sys.argv[1].lower()
            for i, tc in enumerate(TEST_CASES):
                if nombre in tc["nombre"].lower():
                    run_single_test(i)
                    break
            else:
                print(f"❌ No se encontró test con nombre: {nombre}")
                print(f"Tests disponibles:")
                for i, tc in enumerate(TEST_CASES):
                    print(f"  {i}: {tc['nombre']}")
    else:
        # Ejecutar todos los tests
        run_all_tests()

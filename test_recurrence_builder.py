# test_recurrence_builder.py
"""
Test para verificar la construcción de relaciones de recurrencia.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.graph import build_graph


def test_binary_search_recurrence():
    """Test construcción de recurrencia para búsqueda binaria."""
    print("\n" + "="*70)
    print("TEST: Construcción de Recurrencia - Búsqueda Binaria")
    print("="*70)
    
    pseudocode = """
function binary_search(A, x, left, right)
begin
    if left > right then
        return -1
    medio ← (left + right) / 2
    if A[medio] = x then
        return medio
    else if A[medio] > x then
        return binary_search(A, x, left, medio - 1)
    else
        return binary_search(A, x, medio + 1, right)
end
"""
    
    graph = build_graph()
    result = graph.invoke({
        "input_text": pseudocode,
        "pseudocode": pseudocode
    })
    
    print(f"\n{'='*70}")
    print("RESULTADOS:")
    print(f"{'='*70}")
    
    recurrence = result.get("recurrence")
    if recurrence:
        if recurrence.get("success"):
            rec_data = recurrence.get("recurrence", {})
            print(f"✓ Función: {recurrence.get('function_name')}")
            print(f"✓ Relación: {rec_data.get('form')}")
            print(f"✓ Tipo de patrón: {rec_data.get('pattern_type')}")
            print(f"✓ Parámetros:")
            print(f"    a (llamadas): {rec_data.get('a')}")
            print(f"    b (división): {rec_data.get('b')}")
            print(f"    f(n) (trabajo): {rec_data.get('f_n')}")
            
            pattern = recurrence.get("pattern", {})
            print(f"✓ Descripción: {pattern.get('description', 'N/A')}")
            
            base = recurrence.get("base_case", {})
            print(f"✓ Caso base: {base.get('description', 'N/A')}")
            
            return True
        else:
            print(f"✗ Error: {recurrence.get('error')}")
            return False
    else:
        print("✗ No se generó información de recurrencia")
        return False


def test_factorial_recurrence():
    """Test construcción de recurrencia para factorial."""
    print("\n" + "="*70)
    print("TEST: Construcción de Recurrencia - Factorial")
    print("="*70)
    
    pseudocode = """
function factorial(n)
begin
    if n <= 1 then
        return 1
    return n * factorial(n - 1)
end
"""
    
    graph = build_graph()
    result = graph.invoke({
        "input_text": pseudocode,
        "pseudocode": pseudocode
    })
    
    print(f"\n{'='*70}")
    print("RESULTADOS:")
    print(f"{'='*70}")
    
    recurrence = result.get("recurrence")
    if recurrence and recurrence.get("success"):
        rec_data = recurrence.get("recurrence", {})
        print(f"✓ Función: {recurrence.get('function_name')}")
        print(f"✓ Relación: {rec_data.get('form')}")
        print(f"✓ Tipo de patrón: {rec_data.get('pattern_type')}")
        print(f"✓ Parámetros:")
        print(f"    a (llamadas): {rec_data.get('a')}")
        print(f"    b (división): {rec_data.get('b')}")
        print(f"    f(n) (trabajo): {rec_data.get('f_n')}")
        return True
    else:
        print(f"✗ Error o sin datos")
        return False


def test_merge_sort_recurrence():
    """Test construcción de recurrencia para merge sort."""
    print("\n" + "="*70)
    print("TEST: Construcción de Recurrencia - Merge Sort")
    print("="*70)
    
    pseudocode = """
function merge_sort(A, left, right)
begin
    if left >= right then
    begin
        x 🡨 1
    end
    medio 🡨 (left + right) / 2
    CALL merge_sort(A, left, medio)
    CALL merge_sort(A, medio + 1, right)
end
"""
    
    graph = build_graph()
    result = graph.invoke({
        "input_text": pseudocode,
        "pseudocode": pseudocode
    })
    
    print(f"\n{'='*70}")
    print("RESULTADOS:")
    print(f"{'='*70}")
    
    recurrence = result.get("recurrence")
    if recurrence and recurrence.get("success"):
        rec_data = recurrence.get("recurrence", {})
        print(f"✓ Función: {recurrence.get('function_name')}")
        print(f"✓ Relación: {rec_data.get('form')}")
        print(f"✓ Tipo de patrón: {rec_data.get('pattern_type')}")
        print(f"✓ Parámetros:")
        print(f"    a (llamadas): {rec_data.get('a')}")
        print(f"    b (división): {rec_data.get('b')}")
        print(f"    f(n) (trabajo): {rec_data.get('f_n')}")
        
        # Merge sort debe ser 2T(n/2) + O(n)
        expected_a = 2
        expected_b = 2
        actual_a = rec_data.get('a')
        actual_b = rec_data.get('b')
        
        if actual_a == expected_a and actual_b == expected_b:
            print(f"✓ Parámetros correctos para merge sort!")
        else:
            print(f"⚠ Esperado: a={expected_a}, b={expected_b}")
            print(f"  Obtenido: a={actual_a}, b={actual_b}")
        
        return True
    else:
        print(f"✗ Error o sin datos")
        return False


if __name__ == "__main__":
    results = []
    
    try:
        results.append(("Búsqueda Binaria", test_binary_search_recurrence()))
        results.append(("Factorial", test_factorial_recurrence()))
        results.append(("Merge Sort", test_merge_sort_recurrence()))
        
        print("\n" + "="*70)
        print("RESUMEN DE TESTS")
        print("="*70)
        
        for name, passed in results:
            status = "✓ PASÓ" if passed else "✗ FALLÓ"
            print(f"{status:15} {name}")
        
        all_passed = all(r[1] for r in results)
        
        if all_passed:
            print("\n" + "="*70)
            print("TODOS LOS TESTS DE RECURRENCIA PASARON ✓")
            print("="*70)
        else:
            print("\nAlgunos tests fallaron")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

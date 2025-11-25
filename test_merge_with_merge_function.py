# test_merge_with_merge_function.py
"""
Test para verificar que f(n) se calcula correctamente cuando hay función auxiliar merge.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.graph import build_graph


def test_merge_sort_with_merge():
    """Test merge sort con función merge que hace trabajo O(n)."""
    print("\n" + "="*70)
    print("TEST: Merge Sort con función merge()")
    print("="*70)
    
    pseudocode = """
function merge(A, left, medio, right)
begin
    for i from left to right do
    begin
        temp[i] <- A[i]
    end
end

function merge_sort(A, left, right)
begin
    if left >= right then
    begin
        return
    end
    medio <- (left + right) / 2
    CALL merge_sort(A, left, medio)
    CALL merge_sort(A, medio + 1, right)
    CALL merge(A, left, medio, right)
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
        print(f"Funcion: {recurrence.get('function_name')}")
        print(f"Relacion: {rec_data.get('form')}")
        print(f"Patron: {rec_data.get('pattern_type')}")
        print(f"Parametros:")
        print(f"    a (llamadas): {rec_data.get('a')}")
        print(f"    b (division): {rec_data.get('b')}")
        print(f"    f(n) (trabajo): {rec_data.get('f_n')}")
        
        # Verificar que detectó el trabajo O(n) de merge
        f_n = rec_data.get('f_n', '')
        if 'n' in f_n.lower() and '1' not in f_n:
            print(f"\nEXITO: Se detectó correctamente el trabajo O(n) de la función merge!")
            return True
        else:
            print(f"\nADVERTENCIA: Se esperaba f(n) = O(n), pero se obtuvo {f_n}")
            print("Esto puede deberse a que aún falta integrar el CostAnalyzer completamente.")
            return False
    else:
        print(f"Error o sin datos")
        return False


if __name__ == "__main__":
    test_merge_sort_with_merge()

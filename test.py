from app.agents.graph import build_graph
from app.agents.state import AnalyzerState


state = AnalyzerState()
state["nl_description"] = """burbuja(A, n)
begin
    for i ← 1 to n - 1 do
    begin
        for j ← 1 to n - 1 do
        begin
            if (A[j] > A[j + 1]) then
            begin
                temp ← A[j]
                A[j] ← A[j + 1]
                A[j + 1] ← temp
            end
        end
    end
end"""
graph = build_graph().compile()

out = graph.invoke(state)

print("RESULTADO FINAL")
print(out["result"])
print("NOTACIONES")
print(out["notation"])
print("ECUACIONES")
print(out["ecuaciones"])
print("COSTOS MEJOR CASO")
print(out["costos_mejor"])
print("COSTOS PEOR CASO")
print(out["costos_peor"])
from app.agents.graph import build_graph
from app.agents.state import AnalyzerState


state = AnalyzerState()
state["nl_description"] = """burbuja(A[n])
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

result = graph.invoke(state)

print("Resultado final:")
print(result)
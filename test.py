from app.agents.graph import build_graph
from app.agents.state import AnalyzerState


state = AnalyzerState()
state["nl_description"] = """dame el algoritmo del fibonacci recursivo"""
graph = build_graph().compile()

for event in graph.stream(state):
    print(state.keys(state))
    print(event)

# print("RESULTADO FINAL")
# print(out["result"])
# print("NOTACIONES")
# print(out["notation"])
# print("ECUACIONES")
# print(out["ecuaciones"])
# print("COSTOS MEJOR CASO")
# print(out["costos_mejor"])
# print("COSTOS PEOR CASO")
# print(out["costos_peor"])
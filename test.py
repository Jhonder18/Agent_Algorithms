from app.agents.graph import build_graph
from app.agents.state import AnalyzerState


state = AnalyzerState()
state["nl_description"] = """Genere un algoritmo de busqueda binaria"""
graph = build_graph().compile()

result = graph.invoke(state)

print("Resultado final:")
print(result)
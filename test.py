from app.agents.graph import build_graph
from app.agents.state import AnalyzerState
import json

state = AnalyzerState()
state["nl_description"] = "Genere un codigo iterativo de finonacci"
graph = build_graph().compile()

for event in graph.stream(state):
    print()
    print(json.dumps(event, indent=2, ensure_ascii=False))
    print()

from app.agents.tools.tools_iterativas import resolver_sumatorias
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState
from app.agents.llms.geminiWithTools import get_gemini_with_tools_model

def costo_espacial_iterativo_node(state: AnalyzerState) -> AnalyzerState:
    """
    Calcula la sumatoria dada y retorna su resultado simplificado
    """
    prompts = []
    folder = "./app/agents/prompts/iterativos/espacial"
    files = [f"{folder}/CASO_PROMEDIO.md",f"{folder}/MEJOR_CASO.md",f"{folder}/PEOR_CASO.md"]
    for file in files:
        with open(file, "r") as f:
            prompts.append(f.read())
    for prompt in prompts:
        gemini = get_gemini_with_tools_model([resolver_sumatorias])
        system_message = SystemMessage(content=prompt)
        human_message = HumanMessage(content=f"Calcule la complejidad espacial de esto: {state['pseudocode']}\n\nAST: {state['ast']}\n\n") # type: ignore
        messages = [system_message, human_message]
        result = gemini.invoke(messages)
        print("Resultado de la complejidad espacial:")
        print(result)
        if "CASO_PROMEDIO" in prompt:
            state["solution"]["big_O_espacial"] = result # type: ignore
        elif "MEJOR_CASO" in prompt:
            state["solution"]["big_Theta_espacial"] = result # type: ignore
        elif "PEOR_CASO" in prompt:
            state["solution"]["big_Omega_espacial"] = result # type: ignore
    return state
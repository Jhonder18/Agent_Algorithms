from app.agents.tools.tools_iterativas import resolver_sumatorias
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState
from app.agents.llms.geminiWithTools import get_gemini_with_tools_model

def calcular_costo_temporal(state: AnalyzerState) -> AnalyzerState:
    """
    Calcula la sumatoria dada y retorna su resultado simplificado
    """
    prompts = []
    folder = "./app/agents/prompts/iterativos/temporal"
    files = [f"{folder}/CASO_PROMEDIO.md",f"{folder}/MEJOR_CASO.md",f"{folder}/PEOR_CASO.md"]
    for file in files:
        with open(file, "r") as f:
            prompts.append(f.read())
    context = {
        "code": state["pseudocode"], # type: ignore
        "ast": state["ast"], # type: ignore
        "sumatoria": state["sumatoria"] # type: ignore
    }
    for prompt in prompts:
        gemini = get_gemini_with_tools_model([resolver_sumatorias])
        system_message = SystemMessage(content=prompt)
        human_message = HumanMessage(content="Calcule la complejidad temporal de esto: {code}\n\nAST: {ast}\n\nSumatoria: {sumatoria}".format(**context))
        messages = [system_message, human_message]
        result = str(gemini.invoke(messages).content)
        if "CASO_PROMEDIO" in prompt:
            state["solution"]["big_O_temporal"] = result # type: ignore
        elif "MEJOR_CASO" in prompt:
            state["solution"]["big_Theta_temporal"] = result # type: ignore
        elif "PEOR_CASO" in prompt:
            state["solution"]["big_Omega_temporal"] = result # type: ignore
    return state
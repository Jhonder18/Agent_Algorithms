from app.agents.tools.tools_iterativas import resolver_sumatorias
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState
from app.agents.llms.geminiWithTools import get_gemini_with_tools_model


def costo_espacial_iterativo_node(state: AnalyzerState) -> AnalyzerState:
    """
    Calcula la sumatoria dada y retorna su resultado simplificado
    """
    print("Calculando costo espacial iterativo...")  # type: ignore --- IGNORE ---
    
    # Initialize solution if it doesn't exist
    if "solution" not in state:
        state["solution"] = {  # type: ignore
            "big_O_temporal": "",
            "big_O_espacial": "",
            "big_Theta_temporal": "",
            "big_Theta_espacial": "",
            "big_Omega_temporal": "",
            "big_Omega_espacial": "",
        }
    
    prompts = []
    folder = "./app/agents/prompts/iterativos/espacial"
    files = [
        f"{folder}/CASO_PROMEDIO.md",
        f"{folder}/MEJOR_CASO.md",
        f"{folder}/PEOR_CASO.md",
    ]
    for file in files:
        with open(file, "r") as f:
            prompts.append(f.read())
    for i in range(len(prompts)):
        gemini = get_gemini_with_tools_model([resolver_sumatorias])
        system_message = SystemMessage(content=prompts[i])
        human_message = HumanMessage(content=f"Calcule la complejidad espacial de esto: {state['pseudocode']}\n\nAST: {state['ast']}\n\n")  # type: ignore
        messages = [system_message, human_message]
        response = gemini.invoke(messages)
        # Si el modelo llamó a una tool, ejecutarla
        if hasattr(response, "tool_calls") and response.tool_calls:
            result = resolver_sumatorias.invoke(response.tool_calls[0]["args"])
        else:
            result = response.content

        if i==2:
            print("O e", result)  # type: ignore --- IGNORE ---
            state["solution"]["big_O_espacial"] = result  # type: ignore
        elif i==1:
            print("Omega e", result)  # type: ignore --- IGNORE ---
            state["solution"]["big_Omega_espacial"] = result  # type: ignore
        elif i==0:
            print("Theta e", result)  # type: ignore --- IGNORE ---
            state["solution"]["big_Theta_espacial"] = result  # type: ignore
    return state

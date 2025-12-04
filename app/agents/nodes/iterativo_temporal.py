from app.agents.tools.tools_iterativas import resolver_sumatorias
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState
from app.agents.llms.geminiWithTools import get_gemini_with_tools_model
from app.agents.state import AnalyzerState

def costo_temporal_iterativo_node(state: AnalyzerState) -> AnalyzerState:
    """
    Calcula la sumatoria dada y retorna su resultado simplificado
    """
    
    # Initialize ecuaciones if it doesn't exist
    if "ecuaciones" not in state:
        state["ecuaciones"] = {  # type: ignore
            "big_O_temporal": "",
            "big_O_espacial": "",
            "big_Theta_temporal": "",
            "big_Theta_espacial": "",
            "big_Omega_temporal": "",
            "big_Omega_espacial": "",
        }
    
    prompts = []
    folder = "./app/agents/prompts/iterativos/temporal"
    files = [
        f"{folder}/CASO_PROMEDIO.md",
        f"{folder}/MEJOR_CASO.md",
        f"{folder}/PEOR_CASO.md",
    ]
    for file in files:
        with open(file, "r") as f:
            prompts.append(f.read())
    context = {
        "code": state["pseudocode"],  # type: ignore
        "ast": state["ast"],  # type: ignore
        "sumatoria": state["sumatoria"],  # type: ignore
    }
    gemini = get_gemini_with_tools_model([resolver_sumatorias])

    
    # Execute prompts iteratively
    results = []
    for i, prompt in enumerate(prompts):
        system_message = SystemMessage(content=prompt)
        human_message = HumanMessage(
            content=f"Calcule la complejidad temporal de esto: {context['code']}\n\nSumatoria: {context['sumatoria']}"
        )
        messages = [system_message, human_message]
        response = gemini.invoke(messages)

        # Si el modelo llamó a una tool, ejecutarla
        if hasattr(response, "tool_calls") and response.tool_calls:
            result = resolver_sumatorias.invoke(response.tool_calls[0]["args"])
        else:
            result = response.content
        
        results.append((i, result))
    
    # Process results
    for i, result in results:
        if i == 2:
            state["ecuaciones"]["big_O_temporal"] = result  # type: ignore
        elif i == 1:
            state["ecuaciones"]["big_Omega_temporal"] = result  # type: ignore
        elif i == 0:
            state["ecuaciones"]["big_Theta_temporal"] = result  # type: ignore

    return state

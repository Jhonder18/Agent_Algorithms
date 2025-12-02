from app.agents.tools.tools_iterativas import resolver_sumatorias
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState
from app.agents.llms.geminiWithTools import get_gemini_with_tools_model
from concurrent.futures import ThreadPoolExecutor, as_completed

def costo_temporal_iterativo_node(state: AnalyzerState) -> AnalyzerState:
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
    def process_prompt(prompt):
        gemini = get_gemini_with_tools_model([resolver_sumatorias])
        system_message = SystemMessage(content=prompt)
        human_message = HumanMessage(content=f"Calcule la complejidad temporal de esto: {context['code']}\n\nSumatoria: {context['sumatoria']}")
        messages = [system_message, human_message]
        result = str(gemini.invoke(messages).content)
        print(result)
        if "CASO_PROMEDIO" in prompt:
            return ("big_O_temporal", result)
        elif "MEJOR_CASO" in prompt:
            return ("big_Omega_temporal", result)
        elif "PEOR_CASO" in prompt:
            return ("big_Theta_temporal", result)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in prompts]
        
        for future in as_completed(futures):
            result = future.result() # type: ignore
            if result is not None:
                key, value = result
                state["solution"][key] = value # type: ignore
    return state
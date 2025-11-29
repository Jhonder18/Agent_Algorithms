from app.agents.llms.gemini import get_gemini_model
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState

def result_node(state: AnalyzerState) -> AnalyzerState:
    """
    Genera un resumen en lenguaje natural del análisis realizado.
    """
    gemini = get_gemini_model()
    PROMPT = ""
    with open("./app/agents/prompts/GENERAR_RESULT.md", "r") as f:
        PROMPT = f.read()
    system_message = SystemMessage(content=PROMPT)
    human_message = HumanMessage(content=f"El análisis realizado tiene los siguientes resultados:\n\n{state['pseudocode']},{state['ast']},{state['solution']}") # type: ignore
    messages = [system_message, human_message]
    response = gemini.invoke(messages)
    state["result"] = str(response.content)  # type: ignore
    return state
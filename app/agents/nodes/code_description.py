from app.agents.state import AnalyzerState
from app.agents.llms.gemini import get_gemini_model
from langchain_core.messages import SystemMessage, HumanMessage



def code_description_node(state: AnalyzerState) -> AnalyzerState:
    """
    Genera una descripción del código basado en el pseudocódigo normalizado.
    """
    pseudocode = state.get("pseudocode", "")
    gemini = get_gemini_model()
    PROMPT = "Genere una descripcion corta y concisa del siguiente pseudocódigo que mandara el usuario"
    system_message = SystemMessage(content=PROMPT)
    human_message = HumanMessage(content=pseudocode)
    llm_response = gemini.invoke([system_message, human_message])
    description = str(llm_response.content)
    state["nl_description"] = description
    return state
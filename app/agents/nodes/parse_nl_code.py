from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.llms.gemini import get_gemini_model
from app.agents.state import AnalyzerState


# https://towardsdev.com/built-with-langgraph-3-structured-outputs-4707284be57e
class ParceCode(BaseModel):
    """
    Clase para normalizar el código fuente en una representación intermedia.
    """

    code: str = Field(
        ...,
        description="El pseudocodigo. resultado de la transformacion de natural language a pseudocodigo.",
    )


def ParseCode(state: AnalyzerState) -> AnalyzerState:
    """
    Normaliza el estado del analizador asegurando que todas las claves esperadas estén presentes.
    Si alguna clave falta, se inicializa con un valor predeterminado.
    """
    gemini = get_gemini_model()
    PROMPT = ""
    with open("app/agents/prompt_templates/normalize_state.txt", "r") as f:
        PROMPT = f.read()
    system_message = SystemMessage(content=PROMPT)
    human_message = HumanMessage(content=state["nl_description"]) # type: ignore
    llm_structured_output = gemini.with_structured_output(ParceCode)
    response = llm_structured_output.invoke([system_message, human_message])
    state["pseudocode"] = response.code  # type: ignore
    return state

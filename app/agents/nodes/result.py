from pydantic import BaseModel, Field
from app.agents.llms.gemini import get_gemini_model
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AnalyzerState


class NotacionesYAnalisis(BaseModel):
    analisis: str = Field(
        ...,
        description="El analisis completo en lenguaje natural. muestra el codigo, las ecuaciones y las notaciones asintoticas",
    )
    big_O_temporal: str = Field(
        ..., description="Notación Big O para el análisis temporal"
    )
    big_O_espacial: str = Field(
        ..., description="Notación Big O para el análisis espacial"
    )
    big_Theta_temporal: str = Field(
        ..., description="Notación Big Theta para el análisis temporal"
    )
    big_Theta_espacial: str = Field(
        ..., description="Notación Big Theta para el análisis espacial"
    )
    big_Omega_temporal: str = Field(
        ..., description="Notación Big Omega para el análisis temporal"
    )
    big_Omega_espacial: str


def result_node(state: AnalyzerState) -> AnalyzerState:
    """
    Genera un resumen en lenguaje natural del análisis realizado.
    """
    gemini = get_gemini_model()
    gemini_structured = gemini.with_structured_output(NotacionesYAnalisis)
    PROMPT = ""
    with open("./app/agents/prompts/GENERAR_RESULT.md", "r") as f:
        PROMPT = f.read()
    system_message = SystemMessage(content=PROMPT)
    human_message = HumanMessage(content=f"El análisis realizado tiene los siguientes resultados:\n\n{state['pseudocode']}\n\n{state['ast']}\n\n{state['ecuaciones']}")  # type: ignore
    messages = [system_message, human_message]
    response = gemini_structured.invoke(messages)
    state["result"] = response.analisis  # type: ignore
    state["notation"] = {
        "big_O_temporal": response.big_O_temporal,  # type: ignore
        "big_O_espacial": response.big_O_espacial,  # type: ignore
        "big_Theta_temporal": response.big_Theta_temporal,  # type: ignore
        "big_Theta_espacial": response.big_Theta_espacial,  # type: ignore
        "big_Omega_temporal": response.big_Omega_temporal,  # type: ignore
        "big_Omega_espacial": response.big_Omega_espacial,  # type: ignore
    }
    return state

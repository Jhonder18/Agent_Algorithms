from app.agents.state import AnalyzerState
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.llms.gemini import get_gemini_model
from typing import Literal


class typeInput(BaseModel):
    """
    Clase para normalizar el código fuente en una representación intermedia.
    """

    type_input: Literal["lenguaje_natural", "pseudocódigo"] = Field(
        ..., description="Dice si el input es en lenguaje natural o pseudocódigo."
    )


def initial_decision_node(state: AnalyzerState) -> AnalyzerState:
    """
    Decide si el input es en lenguaje natural o pseudocódigo.
    """
    gemini = get_gemini_model()
    PROMPT = "Diga si el siguiente texto es pseudocódigo o una peticion para hacer un codigo en lenguaje natural. Responda solo con 'lenguaje_natural' o 'pseudocódigo'"
    system_message = SystemMessage(content=PROMPT)
    human_message = HumanMessage(content=state["nl_description"])  # type: ignore
    llm_structured_output = gemini.with_structured_output(typeInput)
    response = llm_structured_output.invoke([system_message, human_message])
    if response.type_input == "pseudocódigo":  # type: ignore
        state["pseudocode"] = state["nl_description"] # type: ignore
        state["nl_description"] = ""
    else:
        state["pseudocode"] = ""
    return state

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


def decision(input: str) -> AnalyzerState:
    """
    Decide si el input es en lenguaje natural o pseudocódigo.
    """
    gemini = get_gemini_model()
    PROMPT = "Diga si el siguiente texto es pseudocódigo o lenguaje natural. Responda solo con 'lenguaje_natural' o 'pseudocódigo'"
    system_message = SystemMessage(content=PROMPT)
    human_message = HumanMessage(content=input)
    llm_structured_output = gemini.with_structured_output(typeInput)
    response = llm_structured_output.invoke([system_message, human_message])
    state: AnalyzerState = {}
    if response.type_input == "pseudocódigo":  # type: ignore
        state["pseudocode"] = input
        state["nl_description"] = ""
    else:
        state["nl_description"] = input
        state["pseudocode"] = ""
    return state

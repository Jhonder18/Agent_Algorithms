from pydantic import BaseModel
from app.agents.llms.gemini import get_gemini_model
from app.agents.state import AnalyzerState
from langchain_core.messages import SystemMessage, HumanMessage

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str]

# https://towardsdev.com/built-with-langgraph-3-structured-outputs-4707284be57e
class CodeFixed(BaseModel):
    """
    Clase para normalizar el código fuente en una representación intermedia.
    """
    code: str


def validate_node(state: AnalyzerState) -> AnalyzerState:
    """
    Nodo para validar el pseudocódigo proporcionado en el estado del analizador.
    Se ejecutra antes de generar el AST y puede corregir errores menores en el pseudocódigo.
    """ 
    code = state["pseudocode"]  # type: ignore
    PROMPT_VALIDATE = ""
    with open("./app/agents/prompts/SINTAXE.md", "r") as f:
        PROMPT_VALIDATE = f.read()
    gemini_validate = get_gemini_model()
    system_message = SystemMessage(content=PROMPT_VALIDATE)
    human_message = HumanMessage(content=code)
    output_validated = gemini_validate.with_structured_output(ValidationResult)
    response = output_validated.invoke([system_message, human_message])
    PROMPT_FIX = ""
    with open("./app/agents/prompts/NL_TO_CODE.md", "r") as f:
        PROMPT_FIX = f.read()
    gemini_fix = get_gemini_model()
    output_fix = gemini_fix.with_structured_output(CodeFixed)
    while not response.is_valid: # type: ignore
        system_message = SystemMessage(content=PROMPT_FIX)
        human_message_fix = HumanMessage(content=f"este es un codigo para {state['nl_description']}, por favor arregle la sintaxe:\n {code}") # type: ignore
        response = output_fix.invoke([system_message, human_message_fix])
        code = response.code  # type: ignore
        human_message = HumanMessage(content=code)
        response = output_validated.invoke([system_message, human_message])
    state["pseudocode"] = code  # type: ignore
    return state
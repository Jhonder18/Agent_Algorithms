from app.agents.state import AnalyzerState
from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Tuple
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.llms.gemini import get_gemini_model
from app.agents.utils.process_ast import convertir_a_sumatoria

# Tupla: (nombre, dimension)
Variable = Tuple[str, str]

# Para func_call: (nombre_funcion, [(var,dim),...])
FunctionCall = Tuple[str, List[Variable]]


class FunctionStructure(BaseModel):
    variables: List[Variable]
    code: Dict[Any, Any]   # claves pueden ser tuplas reales o strings


class ASTOutput(BaseModel):
    tipo: Literal["recursivo", "iterativo"]
    ast: List[Dict[str, FunctionStructure]]


def generate_ast(state: AnalyzerState) -> AnalyzerState:
    """Genera el AST a partir del pseudocódigo normalizado en el estado."""
    system_prompt = ""
    # Leer el prompt del sistema
    with open("./app/agents/prompts/GENERAR_AST.md", "r") as f:
        system_prompt = f.read()

    pseudocode = state["pseudocode"]  # type: ignore

    # Obtener el modelo LLM con structured output
    llm = get_gemini_model().with_structured_output(ASTOutput)

    # Generar el AST usando el LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"Genere el AST a partir del siguiente pseudocódigo:\n\n{pseudocode}"
        ),
    ]

    ast_output = llm.invoke(messages)

    # Convertir el output a diccionario para almacenar en el estado
    state["ast"] = ast_output.ast  # type: ignore
    state["mode"] = ast_output.tipo  # type: ignore
    state["sumatoria"] = convertir_a_sumatoria(state["ast"]) 
    return state

from app.agents.state import AnalyzerState
from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Tuple
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.llms.gemini import get_gemini_model
from app.agents.utils.process_ast import convertir_a_sumatoria
from app.agents.utils.generate_ast import parse_pseudocode


class TipoCodigo(BaseModel):
    tipo: Literal["recursivo", "iterativo"]


def generate_ast_node(state: AnalyzerState) -> AnalyzerState:
    """Genera el AST a partir del pseudocódigo normalizado en el estado."""
    system_prompt = "CLASSIFIQUE EL SIGUIENTE PSEUDOCÓDIGO COMO 'recursivo' O 'iterativo'"
    # Leer el prompt del sistema

    pseudocode = state["pseudocode"]  # type: ignore

    # Obtener el modelo LLM con structured output
    llm = get_gemini_model().with_structured_output(TipoCodigo)

    # Generar el AST usando el LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"{pseudocode}"
        ),
    ]

    output = llm.invoke(messages)
    # Convertir el output a diccionario para almacenar en el estado
    state["ast"] = parse_pseudocode(state["pseudocode"])  # type: ignore
    state["mode"] = output.tipo  # type: ignore
    state["sumatoria"] = convertir_a_sumatoria(state["ast"]) 
    return state

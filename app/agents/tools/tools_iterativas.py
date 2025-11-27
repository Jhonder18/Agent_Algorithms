from langchain.tools import tool
from sympy import sympify

@tool
def resolver_sumatorias(sumatoria: str) -> str:
    """
    Tool responsable de resolver sumatorias dadas en notación matemática en sympy.
    """
    expr = sympify(sumatoria)
    return expr.doit()
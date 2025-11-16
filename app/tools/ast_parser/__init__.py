from typing import List
from langchain_core.tools import BaseTool
from .ast_parser import build_ast

def create_toolkit() -> List[BaseTool]:
    return [build_ast]

from typing import List
from langchain_core.tools import BaseTool
from .ast_parser import ast_parse_lc

def create_toolkit() -> List[BaseTool]:
    return [ast_parse_lc]

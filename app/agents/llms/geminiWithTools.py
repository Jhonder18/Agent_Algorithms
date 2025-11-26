from app.agents.llms.gemini import get_gemini_model
from collections.abc import Callable
from langchain_core.language_models import (
    LanguageModelInput,
)
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.prebuilt import ToolNode


def get_gemini_with_tools_model(
    tools: list[Callable],
) -> Runnable[LanguageModelInput, AIMessage]:
    model = get_gemini_model()
    gemini_with_tools = model.bind_tools(tools)
    return gemini_with_tools


def get_gemini_tool_model(tools: list[Callable], name: str) -> ToolNode:
    tools_node = ToolNode(tools, name=name)
    return tools_node
    
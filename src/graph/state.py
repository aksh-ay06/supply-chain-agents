from __future__ import annotations
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_agents: list[str]
    agent_outputs: dict[str, str]
    final_report: str

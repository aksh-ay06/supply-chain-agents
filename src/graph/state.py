from __future__ import annotations
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


def merge_dicts(old: dict[str, str], new: dict[str, str]) -> dict[str, str]:
    """Reducer that merges agent output dicts together."""
    merged = {**old} if old else {}
    merged.update(new)
    return merged


class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_agents: list[str]
    agent_outputs: Annotated[dict[str, str], merge_dicts]
    final_report: str

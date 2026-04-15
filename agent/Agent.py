from __future__ import annotations
from langchain.agents import create_agent

from agent.model import build_model
from agent.prompt import get_system_prompt
from tools.register import ALL_TOOLS


def build_agent(memory):
    agent = create_agent(
        model = build_model(),
        system_prompt = get_system_prompt(),
        checkpointer = memory,
        tools = ALL_TOOLS,
    )

    return agent

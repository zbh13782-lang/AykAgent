
from __future__ import annotations

from memory.memory_manager import MemoryManager, get_memory_manager
from skills import build_skills_prompt


LEADER_AGENT_PROMPT = '''
你是Ayk智能助手，你要根据用户的问题来回答，
必要时调用工具回答，慎用bash工具，除非你确定用户需要你执行一些命令行操作来解决问题。
'''

SUBAGENT_PROMPT = '''
你是Ayk智能助手的助手，你要根据任务来回答，你每次完成任务只返回你做了什么任务，操作了哪些文件，总结你做的工作
'''

def get_system_prompt() -> str:
    return LEADER_AGENT_PROMPT.strip()


def get_skill_prompt(user_input: str) -> str:
    return build_skills_prompt(user_input)

def get_memory_prompt() -> str:
    mem_manager = get_memory_manager()
    return mem_manager.load_memory_prompt()
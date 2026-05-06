from langchain_core.tools import tool

from memory.memory_manager import get_memory_manager

mem_manager = get_memory_manager()


@tool("save_memory")
def save_memory(name, description, mem_type, content) -> str:
    """
    记录一条记忆，只有当这个这条记忆很重要或者用户明确提出要记忆的东西，比如用户的个人信息，用户明确纠正过你的问题（不是聚焦某一个具体问题，
    而是你的行为或者思想问题），你的 回答规范 或者 回答风格 问题。
    另外不是 每条重要的记忆或者用户指出来的东西 都有记忆的必要，只有你觉得这条消息重要到 1 周或者更久之后还会有用才能记录

    name:记忆的名字
    description:记忆的简要描述，不要太长，方便你快速回忆起这条记忆的内容
    mem_type:记忆类型，必须是"user", "feedback", "reference"其中之一，user表示用户的个人信息，feedback表示用户明确指出你的问题或者需要改进的地方，reference表示其他重要的信息或者知识点
    content:详细的需要记忆的内容
    """
    return mem_manager.save_memory(name, description, mem_type, content)


@tool("recall_memory")
def recall_memory(name):
    """
    回忆一条记忆，输入记忆的名字，返回这条记忆的内容，如果没有找到这条记忆，返回空
    Args:
        name:记忆的名字
    """
    mem = mem_manager.memories.get(name)
    if mem:
        return mem["content"]
    else:
        return ""

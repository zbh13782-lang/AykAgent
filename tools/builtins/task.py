from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from agent.model import build_model
from prompts.prompt import SUBAGENT_PROMPT
from langchain_core.messages import HumanMessage

from utils.text import extract_text


#这里面子agent有自己的记忆，最终子智能体返回了总结的结果,invoke即可，不用流，其实子agent设置为异步是对的

#但我对于子agent有些疑惑：
#子agent做的事情要是做 的 太差，父agent会干预吗？
#对于这个问题，我的做法是：让子智能体告诉父亲自己干了什么，父亲去自己审核一下
#子agent创建出来的目的是想要一个干净的上下文，但太干净的上下文有时候是好的，有时候不太理想
#这个问题，本质上还是context工程了，要给子智能体他的定位，他的任务，他要返回什么

@tool("run_subagent")
def run_subagent(prompt:str) -> str:
    """
    分配一个任务给子智能体来做，他会根据你提供的任务描述来完成任务，并返回结果。你可以使用这个工具来让子智能体执行一些特定的任务，比如分析数据、生成内容等。
    但子智能体完成任务之后你必须审查一遍是否满足你的要求，如果不满足，你再自己去做这个任务。
    Args:
        prompt:你要分配给子智能体的任务描述
    """
    from tools.register import SUBAGENT_TOOLS

    memory = MemorySaver()
    subagent = create_agent(
        checkpointer=memory,
        system_prompt=SUBAGENT_PROMPT,
        model=build_model(),
        name="subagent",
        tools=SUBAGENT_TOOLS
    )

    result = subagent.invoke(
        {"messages": [HumanMessage(prompt)]},
        config={"configurable": {"thread_id": "subagent"}},
    )

    ai_message = result["messages"][-1]
    return extract_text(ai_message.content)





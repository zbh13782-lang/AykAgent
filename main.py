import asyncio
import os
import uuid

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage


from agent.model import build_model
from prompts.prompt import get_skill_prompt, get_system_prompt
from tools.register import PARENT_TOOLS
from utils.text import extract_text
from memory.memory_manager import get_memory_manager
from memory.checkpointer import make_checkpointer

mem_manager = get_memory_manager()


def _resolve_thread_id() -> str:
    """确定本次运行使用的 thread_id。

    优先级：环境变量 THREAD_ID > 随机 UUID。
    这样多次启动或多用户场景不会串会话；需要复用历史会话时显式传 THREAD_ID 即可。
    """
    env_thread_id = os.getenv("THREAD_ID")
    if env_thread_id and env_thread_id.strip():
        return env_thread_id.strip()
    return f"session-{uuid.uuid4()}"


async def main():
    mem_manager.load_all()
    thread_id = _resolve_thread_id()
    print(f"[session] thread_id={thread_id}")

    async with make_checkpointer() as short_memory:
        agent = create_agent(
            model=build_model(),
            checkpointer=short_memory,
            system_prompt=get_system_prompt(),
            tools=PARENT_TOOLS,
            name="leader"
        )
        while True:
            try:
                user_input = await asyncio.to_thread(input, "You> ")
            except EOFError:
                print("\nDetected EOF on stdin, exiting.")
                break
            except KeyboardInterrupt:
                print("\nInterrupted by user, exiting.")
                break

            if user_input.strip() == "exit":
                break

            skill_prompt = get_skill_prompt(user_input)

            messages = [HumanMessage(user_input)]
            if skill_prompt:
                messages.insert(0, SystemMessage(skill_prompt))

            print("AI> ", end="", flush=True)
            printed_anything = False

            async for chunk in agent.astream(
                {"messages": messages},
                config={"configurable": {"thread_id": thread_id}},
                stream_mode="messages",
            ):
                message = chunk[0] if isinstance(chunk, tuple) else chunk
                message_type = getattr(message, "type", "")
                if message_type not in {"ai", "AIMessageChunk"}:
                    continue

                text = extract_text(getattr(message, "content", ""))
                if text:
                    print(text, end="", flush=True)
                    printed_anything = True

            if not printed_anything:
                result = await agent.ainvoke(
                    {"messages": messages},
                    config={"configurable": {"thread_id": thread_id}},
                )
                ai_message = result["messages"][-1]
                print(extract_text(ai_message.content), end="")

            print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")

import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage


from langgraph.checkpoint.memory import MemorySaver

from agent.model import build_model
from prompts.prompt import get_skill_prompt, get_system_prompt
from tools.register import PARENT_TOOLS
from utils.text import extract_text
from memory.memory_manager import get_memory_manager

short_memory = MemorySaver()

mem_manager = get_memory_manager()

async def main():
    mem_manager.load_all()
    agent = create_agent(
        model=build_model(),
        checkpointer=short_memory,
        system_prompt=get_system_prompt(),
        tools=PARENT_TOOLS,
        name="leader"
    )
    while True:
        user_input = await asyncio.to_thread(input, "You> ")
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
            config={"configurable": {"thread_id": "user1"}},
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
                config={"configurable": {"thread_id": "user1"}},
            )
            ai_message = result["messages"][-1]
            print(extract_text(ai_message.content), end="")

        print()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage


from langgraph.checkpoint.memory import MemorySaver

from agent.model import build_model
from prompts.prompt import get_system_prompt
from tools.register import PARENT_TOOLS
from utils.text import extract_text

memory = MemorySaver()


async def main():
    agent = create_agent(
        model=build_model(),
        checkpointer=memory,
        system_prompt=get_system_prompt(),
        tools=PARENT_TOOLS,
        name="leader"
    )

    while True:
        user_input = await asyncio.to_thread(input, "You> ")
        if user_input.strip() == "exit":
            break

        print("AI> ", end="", flush=True)
        printed_anything = False

        async for chunk in agent.astream(
            {"messages": [HumanMessage(user_input)]},
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
                {"messages": [HumanMessage(user_input)]},
                config={"configurable": {"thread_id": "user1"}},
            )
            ai_message = result["messages"][-1]
            print(extract_text(ai_message.content), end="")

        print()

if __name__ == "__main__":
    asyncio.run(main())
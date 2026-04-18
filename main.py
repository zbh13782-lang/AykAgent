import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage


from langgraph.checkpoint.memory import MemorySaver

from agent.model import build_model
from memory.checkpointer import make_checkpointer
from prompts.prompt import get_skill_prompt, get_system_prompt
from tools.register import PARENT_TOOLS
from utils.text import extract_text
from memory.memory_manager import get_memory_manager
from memory.short_memory_manager import ShortMemoryManager
from utils.thread_id import get_thread_id


mem_manager = get_memory_manager()
short_mem_manager = ShortMemoryManager()

async def main():
    mem_manager.load_all()
    
    #只有一个用户，这个的作用其实就是新会话
    thread_id = get_thread_id()
    print(f"[session] thread_id: {thread_id}")
    await short_mem_manager.ainit()

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

            if user_input.strip().lower() == "/compact":
                compacted = await short_mem_manager.force_compact(
                    thread_id,
                    saver=short_memory,
                    reason="manual-command",
                )
                if compacted is None:
                    print("AI> 当前没有可压缩的新内容（或未启用 Redis 短期记忆）。")
                else:
                    print(
                        "AI> 已完成短期记忆压缩: "
                        f"[{compacted.compressed_from}, {compacted.compressed_to}) / "
                        f"total={compacted.total_events}, reason={compacted.reason}"
                    )
                continue

            await short_mem_manager.maybe_compact(
                thread_id,
                saver=short_memory,
                reason="auto-before-turn",
            )

            skill_prompt = get_skill_prompt(user_input)
            summary_prompt = await short_mem_manager.get_summary_prompt(thread_id)

            messages = [HumanMessage(user_input)]
            if summary_prompt:
                messages.insert(0, SystemMessage(summary_prompt))
            if skill_prompt:
                messages.insert(0, SystemMessage(skill_prompt))

            await short_mem_manager.append_event(thread_id, "user", user_input)

            print("AI> ", end="", flush=True)
            printed_anything = False
            ai_text_buffer: list[str] = []

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
                    ai_text_buffer.append(text)

            if not printed_anything:
                result = await agent.ainvoke(
                    {"messages": messages},
                    config={"configurable": {"thread_id": thread_id}},
                )
                ai_message = result["messages"][-1]
                ai_text = extract_text(ai_message.content)
                print(ai_text, end="")
                ai_text_buffer.append(ai_text)

            await short_mem_manager.append_event(thread_id, "ai", "".join(ai_text_buffer))
            await short_mem_manager.maybe_compact(
                thread_id,
                saver=short_memory,
                reason="auto-after-turn",
            )

            print()

    await short_mem_manager.aclose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        
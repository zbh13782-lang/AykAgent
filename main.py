from langchain_core.messages import HumanMessage

from agent.Agent import build_agent
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

def main():
    agent = build_agent(memory)

    while True:
        user_input = input("You> ")
        if user_input.strip() == "exit":
            break
        result = agent.invoke(
            {"messages": [HumanMessage(user_input)]},
            config={"configurable": {"thread_id": "user1"}}
        )
        ai_message = result["messages"][-1]
        print(f"AI> {ai_message.content}")

if __name__ == "__main__":
    main()
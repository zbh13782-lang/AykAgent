from agent.graph import build_react_graph
from langchain_core.messages import HumanMessage

# 测试工具调用是否被记录和传递
graph = build_react_graph()

messages = []

# 第一轮：要求AI调用工具
print("=== 第一轮对话 ===")
messages.append(HumanMessage(content="请查看当前目录"))
result1 = graph.invoke({"messages": messages})
messages = result1["messages"]

print(f"Messages数量: {len(messages)}")
for i, msg in enumerate(messages):
    msg_type = msg.__class__.__name__
    print(f"  {i}: {msg_type}", end="")
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f" → 调用工具: {[tc.get('name') for tc in msg.tool_calls]}")
    else:
        print()

# 第二轮：验证AI是否记得工具调用
print("\n=== 第二轮对话 ===")
messages.append(HumanMessage(content="刚才你调用了什么工具"))
result2 = graph.invoke({"messages": messages})
messages = result2["messages"]

print(f"Messages数量: {len(messages)}")
for i, msg in enumerate(messages):
    msg_type = msg.__class__.__name__
    content = getattr(msg, "content", "")[:50] if hasattr(msg, "content") else ""
    print(f"  {i}: {msg_type}", end="")
    if content:
        print(f" → {content}...")
    elif hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f" → 调用工具: {[tc.get('name') for tc in msg.tool_calls]}")
    else:
        print()

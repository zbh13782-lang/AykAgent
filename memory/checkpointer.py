"""
短期记忆 checkpointer 工厂。

根据 CHECKPOINTER_BACKEND 环境变量选择：
- "memory"  (默认): 进程内存储 (langgraph.checkpoint.memory.MemorySaver)
- "redis" : Redis 存储 (langgraph-checkpoint-redis, AsyncRedisSaver)

统一对外暴露为 async context manager，main.py 用 `async with` 即可拿到 saver。
"""

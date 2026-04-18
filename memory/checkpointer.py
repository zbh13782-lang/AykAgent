"""
短期记忆 checkpointer 工厂。

根据 CHECKPOINTER_BACKEND 环境变量选择：
- "memory": 进程内存储 (langgraph.checkpoint.memory.MemorySaver)
- "redis" : Redis 存储 (langgraph-checkpoint-redis, AsyncRedisSaver)

统一对外暴露为 async context manager，main.py 用 `async with` 即可拿到 saver。
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from config import get_settings


@asynccontextmanager
async def make_checkpointer() -> AsyncIterator[BaseCheckpointSaver]:
    settings = get_settings()

    backend = settings.checkpointer.strip().lower()
    if backend == "memory":
        yield MemorySaver()
        return

    if backend == "redis":

        from langgraph.checkpoint.redis.aio import AsyncRedisSaver

        ttl_config : dict | None = None
        if settings.short_memory_ttl and settings.short_memory_ttl > 0:
            ttl_config = {
                "default_ttl": settings.short_memory_ttl / 60,
                "refresh_on_read" : True
            }

        async with AsyncRedisSaver.from_conn_string(
            settings.build_redis_url(),
            ttl = ttl_config
        ) as saver:
            await saver.asetup()
            yield saver

        return

    raise ValueError(
        f"Unsupported CHECKPOINTERER={settings.checkpointer!r}; "
        f"expected 'memory' or 'redis'."
    )
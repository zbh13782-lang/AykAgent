"""
短期记忆 checkpointer 工厂。

根据 CHECKPOINTER_BACKEND 环境变量选择：
- "memory"  (默认): 进程内存储 (langgraph.checkpoint.memory.MemorySaver)
- "redis" : Redis 存储 (langgraph-checkpoint-redis, AsyncRedisSaver)

统一对外暴露为 async context manager，main.py 用 `async with` 即可拿到 saver。
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from config import get_settings


@asynccontextmanager
async def make_checkpointer() -> AsyncIterator[BaseCheckpointSaver]:
    """按配置创建并管理 checkpointer 生命周期。

    - memory 后端：直接 yield 一个 MemorySaver 实例。
    - redis 后端：创建 AsyncRedisSaver，按 SHORT_MEMORY_TTL 设置默认 TTL（秒 -> 分钟），
      首次创建所需索引，退出时自动断开连接。
    """
    settings = get_settings()
    backend = (settings.checkpointer_backend or "memory").strip().lower()

    if backend == "memory":
        yield MemorySaver()
        return

    if backend == "redis":
        # 延迟导入，避免 memory 后端场景强依赖 redis 相关包
        from langgraph.checkpoint.redis.aio import AsyncRedisSaver

        ttl_config: dict | None = None
        if settings.short_memory_ttl and settings.short_memory_ttl > 0:
            # langgraph-checkpoint-redis 的 default_ttl 单位为分钟
            ttl_config = {
                "default_ttl": settings.short_memory_ttl / 60,
                "refresh_on_read": True,
            }

        async with AsyncRedisSaver.from_conn_string(
            settings.build_redis_url(), ttl=ttl_config
        ) as saver:
            # 首次使用需要创建索引（幂等，重复调用安全）
            await saver.asetup()
            yield saver
        return

    raise ValueError(
        f"Unsupported CHECKPOINTER_BACKEND={settings.checkpointer_backend!r}; "
        f"expected 'memory' or 'redis'."
    )

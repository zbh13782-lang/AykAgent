"""短期记忆压缩管理模块。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agent.model import build_model
from config import get_settings
from utils.text import extract_text


@dataclass
class CompactResult:
    compressed_from: int
    compressed_to: int
    total_events: int
    reason: str
    summary_chars: int


class ShortMemoryManager:
    def __init__(self) -> None:
        settings = get_settings()
        backend = (settings.checkpointer or "memory").strip().lower()
        self.enabled = backend == "redis"
        self.redis_url = settings.build_redis_url()
        self.compact_turns = max(
            50, settings.short_memory_compact_turns
        )  # 对话轮次数量到达这个阈值，自动触发压缩
        self.compact_chars = max(
            50000, settings.short_memory_compact_chars
        )  # 字符数量到达，自动触发压缩
        self.keep_turns = max(
            5, settings.short_memory_compact_keep_turns
        )  # 保留最近5条数据不压缩，保持语义

        self._redis: Any | None = None
        self._model: Any | None = None

    async def ainit(self) -> None:
        if not self.enabled or self._redis is not None:
            return
        import redis.asyncio as redis

        self._redis = redis.from_url(self.redis_url, decode_responses=True)

    async def aclose(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    def _events_key(self, thread_id: str) -> str:
        return f"shortmem:{thread_id}:events"

    def _meta_key(self, thread_id: str) -> str:
        return f"shortmem:{thread_id}:meta"

    async def append_event(self, thread_id: str, role: str, content: str) -> None:
        if not self.enabled:
            return
        text = (content or "").strip()
        if not text:
            return
        await self.ainit()
        payload = {
            "role": role,
            "content": text,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        await self._redis.rpush(
            self._events_key(thread_id), json.dumps(payload, ensure_ascii=False)
        )

    async def get_summary_prompt(self, thread_id: str) -> str | None:
        if not self.enabled:
            return None
        await self.ainit()
        meta = await self._redis.hgetall(self._meta_key(thread_id))
        summary = (meta.get("summary") or "").strip()
        if not summary:
            return None
        compressed_until = int(meta.get("compressed_until") or 0)
        return (
            "[短期记忆摘要已压缩]\n"
            f"{summary}\n"
            f"[压缩标记] 已压缩事件区间: [0, {compressed_until})，该区间禁止重复压缩。"
        )

    async def maybe_compact(
        self, thread_id: str, saver: Any, reason: str = "auto"
    ) -> CompactResult | None:
        if not self.enabled:
            return None
        await self.ainit()
        should_compact = await self._should_compact(thread_id)
        if not should_compact:
            return None
        return await self.force_compact(thread_id, saver=saver, reason=reason)

    async def force_compact(
        self, thread_id: str, saver: Any, reason: str = "manual"
    ) -> CompactResult | None:
        if not self.enabled:
            return None
        await self.ainit()

        events_key = self._events_key(thread_id)
        meta_key = self._meta_key(thread_id)

        total_events = int(await self._redis.llen(events_key))
        if total_events <= 0:
            return None

        meta = await self._redis.hgetall(meta_key)
        compressed_until = int(meta.get("compressed_until") or 0)

        target_end = max(compressed_until, total_events - self.keep_turns)
        if target_end <= compressed_until:
            return None

        raw_events = await self._redis.lrange(
            events_key, compressed_until, target_end - 1
        )
        if not raw_events:
            return None

        old_summary = (meta.get("summary") or "").strip()
        new_summary = await self._summarize(old_summary, raw_events)
        now = datetime.now(timezone.utc).isoformat()

        await self._redis.hset(
            meta_key,
            mapping={
                "summary": new_summary,
                "compressed_until": str(target_end),
                "last_reason": reason,
                "last_compacted_at": now,
            },
        )

        if saver is not None and hasattr(saver, "adelete_thread"):
            await saver.adelete_thread(thread_id)

        return CompactResult(
            compressed_from=compressed_until,
            compressed_to=target_end,
            total_events=total_events,
            reason=reason,
            summary_chars=len(new_summary),
        )

    async def _should_compact(self, thread_id: str) -> bool:
        events_key = self._events_key(thread_id)
        meta_key = self._meta_key(thread_id)

        total_events = int(await self._redis.llen(events_key))
        if total_events <= self.keep_turns:
            return False

        compressed_until = int(
            await self._redis.hget(meta_key, "compressed_until") or 0
        )
        uncompressed_count = max(0, total_events - compressed_until)
        if uncompressed_count >= self.compact_turns:
            return True

        raw_events = await self._redis.lrange(events_key, compressed_until, -1)
        total_chars = 0
        for row in raw_events:
            try:
                payload = json.loads(row)
                total_chars += len((payload.get("content") or "").strip())
            except (json.JSONDecodeError, TypeError):
                continue
            if total_chars >= self.compact_chars:
                return True

        return False

    async def _summarize(self, old_summary: str, raw_events: list[str]) -> str:
        lines: list[str] = []
        for row in raw_events:
            try:
                payload = json.loads(row)
            except (json.JSONDecodeError, TypeError):
                continue
            role = str(payload.get("role") or "unknown").strip()
            content = str(payload.get("content") or "").strip()
            if not content:
                continue
            lines.append(f"[{role}] {content}")

        if not lines:
            return old_summary

        system = SystemMessage(
            "你是智能对话摘要助手。请在保留关键事实的前提下输出简洁摘要，"
            "并明确：用户偏好、待办事项、未决问题、已做决策。"
            "输出中文纯文本，避免冗余，长度控制在 5000 字以内。"
        )
        human = HumanMessage(
            "历史摘要（可能为空）：\n"
            f"{old_summary or '(空)'}\n\n"
            "请将以下新增对话合并到历史摘要中：\n"
            f"{chr(10).join(lines)}"
        )
        if self._model is None:
            self._model = build_model()
        response = await self._model.ainvoke([system, human])
        text = extract_text(getattr(response, "content", "")).strip()
        if not text:
            return old_summary
        return text[:5000]

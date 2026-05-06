from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    workdir: str | None = Field(default_factory=lambda: os.getenv("WORKDIR"))

    openai_api_key: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    openai_chat_model: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_CHAT_MODEL")
    )
    openai_base_url: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL")
    )
    # tavily搜索服务
    tavily_api_key: str | None = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY")
    )
    # 短期记忆方式，可选redis或内存
    checkpointer: str | None = Field(default_factory=lambda: os.getenv("CHECKPOINTER"))
    # redis配置
    redis_url: str | None = Field(default_factory=lambda: os.getenv("REDIS_URL"))
    redis_host: str = Field(
        default_factory=lambda: os.getenv("REDIS_HOST", "127.0.0.1")
    )
    redis_port: int = Field(
        default_factory=lambda: int(os.getenv("REDIS_PORT", "6379"))
    )
    redis_db: int = Field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    redis_password: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_PASSWORD")
    )
    short_memory_ttl: int | None = Field(
        default_factory=lambda: int(os.getenv("SHORT_MEMORY_TTL", "0"))
    )
    short_memory_compact_turns: int = Field(
        default_factory=lambda: int(os.getenv("SHORT_MEMORY_COMPACT_TURNS", "50"))
    )
    short_memory_compact_chars: int = Field(
        default_factory=lambda: int(os.getenv("SHORT_MEMORY_COMPACT_CHARS", "50000"))
    )
    short_memory_compact_keep_turns: int = Field(
        default_factory=lambda: int(os.getenv("SHORT_MEMORY_COMPACT_KEEP_TURNS", "5"))
    )

    thread_id: str | None = Field(
        default_factory=lambda: int(os.getenv("THREAD_ID", ""))
    )

    # MCP 配置（可选）
    mcp_enable_github: bool = Field(
        default_factory=lambda: _env_bool("MCP_ENABLE_GITHUB", False)
    )
    mcp_github_url: str | None = Field(
        default_factory=lambda: os.getenv("MCP_GITHUB_URL")
    )
    mcp_github_token: str | None = Field(
        default_factory=lambda: os.getenv("MCP_GITHUB_TOKEN")
    )
    mcp_github_tool_allowlist: str | None = Field(
        default_factory=lambda: os.getenv("MCP_GITHUB_TOOL_ALLOWLIST")
    )

    @property
    def mcp_github_allowlist(self) -> list[str]:
        raw = self.mcp_github_tool_allowlist
        if not raw:
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    def build_redis_url(self) -> str:
        """拼装 Redis 连接 URL：显式 REDIS_URL 优先，否则由 host/port/db/password 拼装。"""
        if self.redis_url:
            return self.redis_url
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # 如果 WORKDIR 没配，回退到当前工作目录
    @property
    def resolved_workdir(self) -> Path:
        raw_workdir = self.workdir
        if not raw_workdir:
            return Path.cwd().resolve()

        configured = Path(raw_workdir).expanduser()
        if not configured.is_absolute():
            configured = (Path.cwd() / configured).resolve()

        return configured.resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

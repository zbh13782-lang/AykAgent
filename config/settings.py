from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    workdir: str | None = Field(default_factory=lambda: os.getenv("WORKDIR"))

    openai_api_key: str | None = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_chat_model: str | None = Field(default_factory=lambda: os.getenv("OPENAI_CHAT_MODEL"))
    openai_base_url: str | None = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))

    tavily_api_key: str | None = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY"))

    #如果 WORKDIR 没配，回退到当前工作目录
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

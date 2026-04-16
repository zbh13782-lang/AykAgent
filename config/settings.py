from __future__ import annotations

import os

from anyio.functools import lru_cache
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

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

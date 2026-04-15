from __future__ import annotations

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

WORKDIR = os.getcwd()


#SKILL_PATH = os.path.join(WORKDIR, "skills")

def build_model() -> ChatOpenAI:
    model_name = os.getenv("OPENAI_CHAT_MODEL")
    model_base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("❌ OPENAI_API_KEY 未配置")
    if not model_name:
        raise RuntimeError("❌ OPENAI_CHAT_MODEL 未配置")
    if not model_base_url:
        raise RuntimeError("❌ OPENAI_BASE_URL 未配置")

    return ChatOpenAI(
        model=model_name,
        base_url=model_base_url,
        api_key=api_key,
        temperature=0
    )

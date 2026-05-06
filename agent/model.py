from __future__ import annotations

from langchain_openai import ChatOpenAI

from config.settings import get_settings


# SKILL_PATH = os.path.join(WORKDIR, "skills")

settings = get_settings()


def build_model() -> ChatOpenAI:
    model_name = settings.openai_chat_model
    model_base_url = settings.openai_base_url
    api_key = settings.openai_api_key

    if not api_key:
        raise RuntimeError("❌ OPENAI_API_KEY 未配置")
    if not model_name:
        raise RuntimeError("❌ OPENAI_CHAT_MODEL 未配置")
    if not model_base_url:
        raise RuntimeError("❌ OPENAI_BASE_URL 未配置")

    return ChatOpenAI(
        model=model_name, base_url=model_base_url, api_key=api_key, temperature=0
    )

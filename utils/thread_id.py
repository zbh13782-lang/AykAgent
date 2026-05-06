import uuid

from config import get_settings


def get_thread_id():
    settings = get_settings()
    env_thread_id = settings.thread_id
    if env_thread_id and env_thread_id != "":
        return env_thread_id.strip()
    return f"session-{uuid.uuid4()}"

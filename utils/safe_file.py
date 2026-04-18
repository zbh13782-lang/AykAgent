from pathlib import Path

from config.settings import get_settings


def safe_path(p: str) -> Path:
    workdir = get_settings().resolved_workdir
    path = (workdir / p).resolve()
    if not path.is_relative_to(workdir):
        raise ValueError(f"Path escape workspace : {p}")
    return path

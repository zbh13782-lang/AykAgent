from pathlib import Path


def safe_path(p: str) -> Path:
    workdir = Path.cwd().resolve()
    path = (workdir / p).resolve()
    if not path.is_relative_to(workdir):
        raise ValueError(f"Path escape workspace : {p}")
    return path
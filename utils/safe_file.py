from pathlib import Path
import os
def safe_path(p:str) -> Path:
    workdir = os.getcwd()
    path = (workdir / p).resolve()
    if not path.is_relative_to(workdir):
        raise ValueError(f"Path escape workspace : {p}")
    return path
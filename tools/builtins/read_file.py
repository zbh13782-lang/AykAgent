from langchain_core.tools import tool

from utils.safe_file import safe_path


@tool("read_file")
def read_file(p: str, limit: int = 0) -> str:
    """
    读取文件内容，可以指定行数限制，超过部分会被省略。
    Args:
        p:读取文件路径
        limit:要读取的行数限制，超过部分会被省略
    """
    try:
        path = safe_path(p).read_text(encoding="utf-8")
        lines = path.split("\n")
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

from langchain_core.tools import tool

from utils.safe_file import safe_path


@tool("write_file")
def write_file(p:str,content:str) -> str:
    """
    写入文件内容，如果文件不存在会创建，如果文件存在会覆盖
    Args:
        p:文件路径
        content:你要写入的内容
    """
    try:
        path = safe_path(p)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Successfully edited {path}"
    except Exception as e:
        return f"Error:{e}"


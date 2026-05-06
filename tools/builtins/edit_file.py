from langchain_core.tools import tool

from utils.safe_file import safe_path


@tool
def edit_file(p: str, old_text: str, new_text: str) -> str:
    """
    编辑文件，但必须准确指定文件里面的老内容，然后用新内容替换掉
    Args:
        p:文件路径
        old_text:要替换掉的老内容
        new_text:要替换成的新内容，可以为空
    """
    try:
        path = safe_path(p)
        content = path.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error:Text not found in {path}"
        path.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Successfully edited {path}"
    except Exception as e:
        return f"Error:{e}"

from __future__ import annotations
import re
from functools import lru_cache
from pathlib import Path

from config import get_settings
settings = get_settings()

'''
记忆模块，记忆用户偏好，个人信息，用户明确要记录的东西，用户明确指出的错误类型
'''

def parse_frontmatter(text: str) -> dict | None:
    """
    memory.md解析工具，
    例如：
    ---
    name: prefer_tabs
    description: 用户偏好使用 tab 缩进
    type: user
    ---
    Always use tabs for indentation.

    返回{
            "content": "Always use tabs for indentation.",
            "name": "prefer_tabs",
            "description": "用户偏好使用 tab 缩进",
            "type": "user"
        }
    """

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return None
    header, body = match.group(1), match.group(2)
    result = {"content": body.strip()}
    for line in header.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result

#获取默认的manager方法(路径默认)，只实现一次
@lru_cache(maxsize=1)
def get_memory_manager():
    return MemoryManager()

class MemoryManager:
    def __init__(self, memory_dir: str | Path | None = None) -> None:
        if memory_dir is None:
            self.memory_dir = settings.resolved_workdir / "memory"
        else:
            self.memory_dir = Path(memory_dir)
        self.memory_index = self.memory_dir / "MEMORY.md"
        self.memory_types = ("user", "feedback", "reference")
        self.memory_index_max_len = 200
        self.memories = {}

    def load_all(self):
        self.memories = {}
        for md_file in sorted(self.memory_dir.glob("*.md")):
            if md_file.name == "MEMORY.md":
                continue
            parsed = parse_frontmatter(md_file.read_text(encoding="utf-8"))
            if parsed:
                name = parsed.get("name")
                if not name:
                    continue
                self.memories[name] = {
                    "description": parsed.get("description", ""),
                    "type": parsed.get("type", "reference"),
                    "content": parsed.get("content", ""),
                    "file": md_file.name,
                }

        print(f"Loaded {len(self.memories)} memories from {self.memory_dir}")

    def rebuild_index(self):
        lines = ["# Memory Index", ""]
        for name, mem in self.memories.items():
            lines.append(f"- {name}: {mem['description']} [{mem['type']}]")
            if len(lines) > self.memory_index_max_len:
                lines.append("...")
                break
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_index.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def save_memory(self, name: str, description: str, mem_type: str, content: str) -> str:
        """
        新建一个记忆,更新index
        """
        if mem_type not in self.memory_types:
            return f"Error: type must be one of {self.memory_types}"

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", name.lower())
        if not safe_name:
            return "Error: invalid memory name"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        frontmatter = (
            f"---\n"
            f"name: {name}\n"
            f"description: {description}\n"
            f"type: {mem_type}\n"
            f"---\n"
            f"{content}\n"
        )
        file_name = f"{safe_name}.md"
        file_path = self.memory_dir / file_name
        file_path.write_text(frontmatter, encoding="utf-8")


        self.memories[name] = {
            "description": description,
            "type": mem_type,
            "content": content,
            "file": file_name,
        }

        #更新索引
        self.rebuild_index()

        try:
            display_path = file_path.relative_to(settings.resolved_workdir)
        except ValueError:
            display_path = file_path

        return f"Saved memory '{name}' [{mem_type}] to {display_path}"

    def load_memory_prompt(self):
        if not self.memories:
            return ""
        sections = []
        sections.append("# Memories")
        sections.append("---")

        for mem_type in self.memory_types:
            typed = {k: v for k, v in self.memories.items() if v["type"] == mem_type}
            if not typed:
                continue
            sections.append(f"## [{mem_type}]")
            for name, mem in typed.items():
                sections.append(f"### {name}: {mem['description']}")
        return "\n".join(sections)


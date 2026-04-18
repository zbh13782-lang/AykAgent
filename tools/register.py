from __future__ import annotations

from tools.builtins.memory_tools import *
from tools.builtins.task import run_subagent
from tools.builtins.edit_file import edit_file
from tools.builtins.read_file import read_file
from tools.builtins.run_bash import run_bash
from tools.builtins.web_search import web_search
from tools.builtins.write_file import write_file
from tools.mcp.github_tools import get_github_mcp_tools

builtin_tools = [run_bash,read_file,edit_file,write_file,web_search,save_memory,recall_memory]

ALL_TOOLS = builtin_tools

PARENT_TOOLS = ALL_TOOLS + [run_subagent]

SUBAGENT_TOOLS = ALL_TOOLS


async def get_parent_tools() -> list:
	"""父智能体工具清单：内置工具 + 可选 MCP 工具 + 子智能体工具。"""
	mcp_tools = await get_github_mcp_tools()
	return ALL_TOOLS + mcp_tools + [run_subagent]
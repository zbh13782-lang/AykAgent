from __future__ import annotations

import logging
from collections.abc import Sequence

from config.settings import get_settings

logger = logging.getLogger(__name__)

try:
	from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:  # pragma: no cover - 可选依赖缺失
	MultiServerMCPClient = None  # type: ignore[assignment]



_github_client: MultiServerMCPClient | None = None
_github_tools_cache: list | None = None


async def get_github_mcp_tools() -> list:
	"""加载 GitHub Remote MCP 工具，不可用时返回空列表。"""
	global _github_client, _github_tools_cache

	if _github_tools_cache is not None:
		return _github_tools_cache

	settings = get_settings()

	if not settings.mcp_enable_github:
		_github_tools_cache = []
		return _github_tools_cache

	if MultiServerMCPClient is None:
		logger.warning("未安装 langchain-mcp-adapters，已跳过 GitHub MCP 工具加载。")
		_github_tools_cache = []
		return _github_tools_cache


	if not settings.mcp_github_url:
		_github_tools_cache = []
		return _github_tools_cache

	server_config: dict[str, dict] = {
		"github": {
			"transport": "streamable_http",
			"url": settings.mcp_github_url,
		}
	}

	headers: dict[str, str] = {}
	if settings.mcp_github_token:
		headers["Authorization"] = f"Bearer {settings.mcp_github_token}"

	if headers:
		server_config["github"]["headers"] = headers

	try:
		_github_client = MultiServerMCPClient(server_config)
		tools: Sequence = await _github_client.get_tools()
		loaded_tools = list(tools)
	except Exception as exc:
		logger.exception("GitHub MCP 工具加载失败，已降级为仅内置工具: %s", exc)
		_github_tools_cache = []
		return _github_tools_cache

	allowlist = set(settings.mcp_github_allowlist)
	if allowlist:
		loaded_tools = [tool for tool in loaded_tools if getattr(tool, "name", "") in allowlist]

	logger.info("GitHub MCP 工具加载完成：%s 个", len(loaded_tools))
	_github_tools_cache = loaded_tools
	return _github_tools_cache

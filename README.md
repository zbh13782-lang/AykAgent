# AykAgent

一个基于 LangChain 和 LangGraph 的智能 AI 智能体系统，具备记忆管理、工具调用和技能扩展能力。
目前接入了多种工具

## 特性

- 🤖 **智能对话**: 基于 OpenAI GPT 模型的自然语言交互
- 🧠 **记忆管理**: 支持短期和长期记忆，自动记忆压缩
- 🛠️ **工具系统**: 可扩展的工具调用能力
- 📚 **技能系统**: 灵活的技能提示机制
- 💾 **会话持久化**: 基于 Redis 的检查点机制
- 🔍 **网络搜索**: 集成 Tavily 搜索 API
- 📝 **子任务分配**: 支持将任务分配给子智能体执行
- 🔗 **GitHub MCP 集成**: 可选接入 GitHub Remote MCP Server

## 系统要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip
- Redis（可选，用于短期记忆持久化；也可使用内置内存模式）
- Docker & Docker Compose（可选，用于快速启动 Redis）

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/zbh13782-lang/AykAgent.git
cd AykAgent
```

2. 创建虚拟环境并安装依赖（推荐使用 uv）：
```bash
uv sync
```

或使用标准 pip：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

pip install -e .
```

## 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API 密钥：
```env
# OpenAI 配置（必须）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Tavily 搜索 API (可选，用于网络搜索功能)
TAVILY_API_KEY=your_tavily_api_key_here

# 工作目录 (可选，默认为当前目录)
WORKDIR=./Aykagent

# 短期记忆后端：memory（内置）或 redis
CHECKPOINTER=redis

# Redis 配置（CHECKPOINTER=redis 时使用）
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 短期记忆配置（可选），以下为默认值
SHORT_MEMORY_COMPACT_TURNS=50
SHORT_MEMORY_COMPACT_CHARS=50000
SHORT_MEMORY_COMPACT_KEEP_TURNS=5
SHORT_MEMORY_TTL=3600
```

## 快速开始

### 最简启动（无 Redis）

如果你只想快速体验，可以使用内置内存作为短期记忆后端，无需 Redis：

1. 在 `.env` 中设置：
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
CHECKPOINTER=memory
```

2. 启动程序：
```bash
python main.py
```

3. 开始对话：
```
You> 你好，请介绍一下你自己
You> 帮我读取当前目录下的文件列表
You> 搜索一下 Python 最新版本的特性
You> exit
```

### 使用 Redis 持久化会话（推荐）

1. 启动 Redis（使用项目内置的 docker-compose）：
```bash
docker compose up -d
```

2. 配置 `.env`（确保 `CHECKPOINTER=redis` 及 Redis 连接信息正确）。

3. 启动程序：
```bash
python main.py
```

### 交互命令

| 命令 | 说明 |
|------|------|
| 直接输入消息 | 与 AI 智能体对话 |
| `exit` | 退出程序 |
| `/compact` | 手动触发短期记忆压缩（当前会话） |

## 接入 GitHub Remote MCP Server

项目已支持按环境变量动态加载 GitHub MCP 工具。默认关闭，不影响现有内置工具。

在 `.env` 中启用并配置（一定要配置好 token，同时管理好你的 token 权限！）：

> `MCP_GITHUB_URL` 默认官方地址为 `https://api.githubcopilot.com/mcp/`

```env
MCP_ENABLE_GITHUB=true
MCP_GITHUB_URL=https://api.githubcopilot.com/mcp/
MCP_GITHUB_TOKEN=<你的 GitHub Bearer Token>
MCP_GITHUB_TOOL_ALLOWLIST=tool_a,tool_b   # 可选，限制暴露的工具名
```

说明：
- 若 `MCP_ENABLE_GITHUB=false`（默认），则只使用内置工具。
- 若配置了 `MCP_GITHUB_TOOL_ALLOWLIST`，仅会加载名单中的 MCP 工具。请确保 token 权限与工具所需权限匹配，否则调用时会报错。

## 内置工具

| 工具名 | 说明 |
|--------|------|
| `read_file` | 读取文件内容 |
| `write_file` | 写入文件内容 |
| `edit_file` | 编辑文件（替换指定内容） |
| `run_bash` | 执行 bash 命令 |
| `web_search` | 网络搜索（使用 Tavily API） |
| `save_memory` | 保存长期记忆 |
| `recall_memory` | 回忆长期记忆 |
| `run_subagent` | 分配任务给子智能体执行 |

## 项目结构

```
AykAgent/
├── Aykagent/       # Ayk 智能助手主入口
├── agent/          # 智能体核心逻辑
│   ├── model.py    # 模型构建
│   └── Agent.py    # 智能体定义
├── tools/          # 工具系统
│   ├── register.py # 工具注册
│   ├── builtins/   # 内置工具
│   │   ├── task.py         # 子任务分配
│   │   ├── memory_tools.py # 记忆管理工具
│   │   ├── edit_file.py    # 文件编辑
│   │   ├── run_bash.py     # Bash 命令执行
│   │   ├── read_file.py    # 文件读取
│   │   ├── web_search.py   # 网络搜索
│   │   └── write_file.py   # 文件写入
│   └── mcp/        # MCP 客户端
│       └── github_tools.py # GitHub MCP 工具集成
├── skills/         # 技能系统
│   ├── loader.py   # 技能加载器
│   └── feng-ge/    # 风格技能示例
├── memory/         # 记忆管理
│   ├── memory_manager.py       # 长期记忆管理
│   ├── short_memory_manager.py # 短期记忆管理
│   └── checkpointer.py         # 检查点管理
├── prompts/        # 提示词模板
│   └── prompt.py   # 提示词生成
├── config/         # 配置文件
│   ├── __init__.py
│   └── settings.py # 配置管理
├── utils/          # 工具函数
│   ├── text.py     # 文本处理
│   ├── thread_id.py # 线程ID生成
│   └── safe_file.py # 安全文件操作
├── main.py         # 主程序入口
├── tests/          # 测试文件
├── docker-compose.yml # Docker Redis 配置
├── pyproject.toml  # 项目配置
└── .env.example    # 环境变量示例
```

## 常见问题

**Q: 启动时提示 `❌ OPENAI_API_KEY 未配置`**

A: 请确认 `.env` 文件已正确创建并填入了 `OPENAI_API_KEY`。检查是否在项目根目录下执行 `python main.py`。

**Q: 不想使用 Redis，有没有更简单的方式？**

A: 在 `.env` 中设置 `CHECKPOINTER=memory` 即可使用内置内存作为短期记忆后端，无需安装 Redis。注意：使用内存模式时，会话数据在程序退出后不会保留。

**Q: `web_search` 工具不可用？**

A: 网络搜索功能需要 Tavily API Key。在 `.env` 中配置 `TAVILY_API_KEY` 后即可使用。可在 [Tavily 官网](https://tavily.com/) 免费申请。

**Q: 如何添加自定义技能？**

A: 在 `skills/` 目录下创建新的技能文件夹，参考 `skills/feng-ge/` 的结构编写技能提示词文件，技能加载器会自动识别并加载。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交 Issue

- 报告 Bug 时，请提供复现步骤、Python 版本、错误信息等信息
- 提交功能建议时，请描述使用场景和期望行为

### 提交 Pull Request

1. Fork 本仓库并创建你的分支：
```bash
git checkout -b feature/your-feature-name
```

2. 进行代码修改，确保：
   - 代码风格与现有代码保持一致
   - 新功能附带必要的说明或注释
   - 运行现有测试确保没有破坏原有功能：`python -m pytest tests/`

3. 提交并推送你的分支：
```bash
git commit -m "feat: 描述你的改动"
git push origin feature/your-feature-name
```

4. 在 GitHub 上创建 Pull Request，描述你的改动内容和原因。

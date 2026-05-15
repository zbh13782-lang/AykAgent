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
- Redis (可选，用于短期记忆)

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/zbh13782-lang/AykAgent.git
cd Aykagent
```

2. 创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
# 或使用 uv
uv sync
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

# Tavily 搜索 API (可选)
TAVILY_API_KEY=your_tavily_api_key_here

# 工作目录 (可选)
WORKDIR=./workspace

# Redis 配置 (可选，可以用docker拉（见docker-compose），也可以直接连接本地)
CHECKPOINTER=redis
REDIS_URL=redis://localhost:6379/0

# 短期记忆配置（可选），settings里面已经写好默认
SHORT_MEMORY_COMPACT_TURNS=50
SHORT_MEMORY_COMPACT_CHARS=50000
SHORT_MEMORY_COMPACT_KEEP_TURNS=5
```

## 接入 GitHub Remote MCP Server

项目已支持按环境变量动态加载 GitHub MCP 工具。默认关闭，不影响现有内置工具。

1. 安装依赖（若尚未安装）：
```bash
uv sync
# 或
pip install -e .
```

2. 在 `.env` 中启用并配置（一定要配置好token，同时管理好你的token权限！）：
MCP_GITHUB_URL默认官方是https://api.githubcopilot.com/mcp/
```env
MCP_ENABLE_GITHUB=true
MCP_GITHUB_URL=<你的 GitHub MCP Server URL>
MCP_GITHUB_TOKEN=<可选，若服务端要求 Bearer Token>
MCP_GITHUB_TOOL_ALLOWLIST=tool_a,tool_b
```



3. 启动：
先通过docker启动redis
```bash
docker compose up -d
```

随后启动程序

```bash
python main.py
```

说明：
- 若 `MCP_ENABLE_GITHUB=false`，则只使用内置工具。
- 若配置了 `MCP_GITHUB_TOOL_ALLOWLIST`，仅会加载名单中的 MCP 工具，但如果ai使用了token里面没有开放的权限就会报错，这里注意设置好token权限

### 交互命令

- 直接输入消息与 AI 对话
- 输入 `exit` 退出程序
- 输入 `/compact` 手动触发短期记忆压缩（当前会话）

## 内置工具

- `read_file` - 读取文件内容
- `write_file` - 写入文件内容
- `edit_file` - 编辑文件（替换指定内容）
- `run_bash` - 执行 bash 命令
- `web_search` - 网络搜索（使用 Tavily API）
- `save_memory` - 保存记忆
- `recall_memory` - 回忆记忆
- `run_subagent` - 分配任务给子智能体

## 项目结构

```
Aykagent/
├── Aykagent/       # Ayk 智能助手主入口
├── agent/          # 智能体核心逻辑
│   ├── model.py    # 模型构建
│   └── Agent.py    # 智能体定义
├── tools/          # 工具系统
│   ├── register.py # 工具注册
│   ├── builtins/   # 内置工具
│   │   ├── task.py      # 子任务分配
│   │   ├── memory_tools.py # 记忆管理工具
│   │   ├── edit_file.py # 文件编辑
│   │   ├── run_bash.py  # Bash 命令执行
│   │   ├── read_file.py # 文件读取
│   │   ├── web_search.py # 网络搜索
│   │   └── write_file.py # 文件写入
│   └── mcp/        # MCP 客户端
│       └── github_tools.py # GitHub MCP 工具集成
├── skills/         # 技能系统
│   ├── loader.py   # 技能加载器
│   └── feng-ge/    # 风格技能示例
├── memory/         # 记忆管理
│   ├── memory_manager.py      # 长期记忆管理
│   ├── short_memory_manager.py # 短期记忆管理
│   └── checkpointer.py        # 检查点管理
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

## 贡献

欢迎提交 Issue 和 Pull Request！

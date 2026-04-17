# Ayk 智能助手

一个基于 LangGraph 的多工具智能助手，支持文件操作、命令执行、网络搜索等功能，并具备子任务协作能力。

## ✨ 特性

- 🤖 **智能对话**: 基于 LangGraph 构建的强大 Agent 系统
- 🛠️ **丰富工具**: 集成文件操作、命令执行、网络搜索等多种实用工具
- 🔄 **任务协作**: 支持子 Agent 分工协作，处理复杂任务
- 💾 **记忆功能**: 内置对话记忆，支持上下文连续对话
- 🌐 **网络搜索**: 集成 Tavily 搜索引擎，获取实时信息
- 🌤️ **天气查询**: 支持实时天气查询功能

## 🚀 快速开始

### 环境要求

- Python >= 3.10
- uv (推荐) 或 pip

### 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -e .
```

### 配置环境变量

创建 `.env` 文件并配置以下环境变量：

```bash
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Tavily 搜索 API (可选，用于网络搜索功能)
TAVILY_API_KEY=your_tavily_api_key

# 工作目录 (可选)
WORKDIR=./workspace
```

### 运行

```bash
# 使用 uv
uv run python main.py

# 或使用 pip
python main.py
```

## 📁 项目结构

```
.
├── agent/              # Agent 相关模块
│   ├── model.py       # 模型构建
│   └── Agent.py       # Agent 定义
├── tools/             # 工具模块
│   ├── builtins/      # 内置工具
│   │   ├── task.py    # 子任务工具
│   │   ├── edit_file.py
│   │   ├── read_file.py
│   │   ├── run_bash.py
│   │   ├── web_search.py
│   │   └── write_file.py
│   ├── origin/        # 原始工具
│   │   └── get_weather.py
│   └── register.py    # 工具注册
├── config/            # 配置模块
│   └── settings.py    # 配置管理
├── prompts/           # 提示词模块
│   └── prompt.py      # 系统提示词
├── utils/             # 工具函数
│   ├── safe_file.py   # 文件安全操作
│   └── text.py        # 文本处理
├── main.py            # 主程序入口
├── pyproject.toml     # 项目配置
└── README.md          # 项目说明
```

## 🛠️ 可用工具

### 内置工具

- **run_bash**: 执行安全的 bash 命令
- **read_file**: 读取文件内容
- **write_file**: 写入文件内容
- **edit_file**: 编辑文件
- **web_search**: 网络搜索 (需要 Tavily API)

### 原始工具

- **get_weather**: 获取天气信息

### 高级功能

- **run_subagent**: 分配任务给子 Agent 处理

## 💡 使用示例

### 基本对话

```
You> 你好
AI> 你好！我是 Ayk 智能助手，有什么我可以帮助你的吗？
```

### 文件操作

```
You> 创建一个名为 test.txt 的文件，内容是 "Hello World"
AI> 已成功创建文件 test.txt，内容为 "Hello World"
```

### 网络搜索

```
You> 搜索最新的 AI 技术发展
AI> [搜索结果...]
```

### 天气查询

```
You> 查询北京天气
AI> 北京今天天气晴朗，温度 25°C...
```

### 复杂任务

```
You> 帮我分析一下当前目录下的所有 Python 文件
AI> [会自动调用子 Agent 来完成这个复杂任务]
```

## 🔧 配置说明

### OpenAI 配置

- `OPENAI_API_KEY`: OpenAI API 密钥
- `OPENAI_CHAT_MODEL`: 使用的模型名称 (如 gpt-4o-mini, gpt-4 等)
- `OPENAI_BASE_URL`: API 基础 URL

### Tavily 配置

- `TAVILY_API_KEY`: Tavily 搜索 API 密钥，用于网络搜索功能

### 工作目录

- `WORKDIR`: 指定工作目录，文件操作将在此目录下进行

### 短期记忆 / Redis（可选）

默认情况下短期记忆（LangGraph checkpointer）使用进程内存储，进程退出即丢失。如果希望跨进程 / 多会话保留短期上下文，可以启用 Redis 后端。

仓库根目录提供了 `docker-compose.yml`（`redis:8-alpine` + AOF 持久化 + 健康检查，仅监听 `127.0.0.1`）。
选用 Redis 8 是因为 `langgraph-checkpoint-redis` 依赖 `RedisJSON` / `RediSearch` 模块，Redis 8 官方镜像已内置这些模块，无需再使用 `redis-stack`。

```bash
# 1. 在 .env 中设置强密码
echo "REDIS_PASSWORD=$(openssl rand -hex 24)" >> .env

# 2. 启动 Redis
docker compose up -d

# 3. 健康检查
docker compose ps
docker compose exec redis redis-cli -a "$REDIS_PASSWORD" ping   # 应返回 PONG
```

相关环境变量（见 `.env.example`）：

- `CHECKPOINTER_BACKEND`: `memory`（默认）或 `redis`
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_PASSWORD`：分散配置
- `REDIS_URL`：完整连接串，若配置则优先于分散变量
- `SHORT_MEMORY_TTL`: 短期记忆过期秒数，默认 `86400`（24 小时），设为 `0` 表示不过期

> 注意：当前 `main.py` 仍默认使用内存 checkpointer，代码层接入 Redis 的改动将在后续 PR 中引入；此 PR 只提供基础设施。

## 🏗️ 技术架构

本项目基于以下技术栈构建：

- **LangGraph**: 用于构建复杂的 Agent 工作流
- **LangChain**: 提供核心的 LLM 集成和工具调用功能
- **OpenAI API**: 提供语言模型能力
- **Tavily**: 提供网络搜索能力

## 📝 开发计划

- [ ] 添加更多实用工具
- [ ] 优化错误处理机制
- [ ] 添加工具调用缓存
- [ ] 改进用户交互界面
- [ ] 增加单元测试和集成测试
- [ ] 支持更多语言模型

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Tavily](https://tavily.com/)

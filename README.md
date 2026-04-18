# Harness

一个基于 LangChain 和 LangGraph 的智能 AI 智能体系统，具备记忆管理、工具调用和技能扩展能力。

## 特性

- 🤖 **智能对话**: 基于 OpenAI GPT 模型的自然语言交互
- 🧠 **记忆管理**: 支持短期和长期记忆，自动记忆压缩
- 🛠️ **工具系统**: 可扩展的工具调用能力
- 📚 **技能系统**: 灵活的技能提示机制
- 💾 **会话持久化**: 基于 Redis 的检查点机制
- 🔍 **网络搜索**: 集成 Tavily 搜索 API

## 系统要求

- Python 3.10+
- Redis (可选，用于短期记忆)

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>

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
# OpenAI 配置
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

## 使用方法

启动智能体：
```bash
python main.py
```

### 交互命令

- 直接输入消息与 AI 对话
- 输入 `exit` 退出程序
- 输入 `/compact` 手动触发短期记忆压缩（当前会话）

## 项目结构

```
Harness/
├── agent/          # 智能体核心逻辑
│   ├── model.py    # 模型构建
│   └── Agent.py    # 智能体定义
├── tools/          # 工具系统
│   ├── register.py # 工具注册
│   ├── builtins/   # 内置工具
│   └── mcp/        # MCP 客户端
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
│   └── settings.py # 配置管理
├── utils/          # 工具函数
│   ├── text.py     # 文本处理
│   ├── thread_id.py # 线程ID生成
│   └── safe_file.py # 安全文件操作
├── main.py         # 主程序入口
└── tests/          # 测试文件
```


## 依赖项

- langchain >= 1.2.15
- langchain-community >= 0.4.1
- langchain-core >= 1.2.28
- langchain-openai >= 0.3.17
- langgraph >= 0.2.70
- langgraph-checkpoint-redis >= 0.4.1
- langsmith >= 0.1.147
- python-dotenv >= 1.2.2
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0

## 贡献

欢迎提交 Issue 和 Pull Request！


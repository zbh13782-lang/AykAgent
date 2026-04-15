## 最小 LangGraph Tool Demo

这个 demo 展示一个最小可运行的 Agent：

- 框架：LangGraph（ReAct Agent）
- 模型：ChatOpenAI
- 工具：get_weather（Mock 天气查询）

### 1) 安装依赖

```bash
uv sync
```

### 2) 配置环境变量

```bash
export OPENAI_API_KEY="<your-openai-api-key>"
# 可选，默认 gpt-4.1-mini
# export OPENAI_MODEL="gpt-4.1-mini"

# 可选：如果你想看 LangSmith tracing
# export LANGSMITH_TRACING=true
# export LANGSMITH_API_KEY="<your-langsmith-api-key>"
# export LANGSMITH_PROJECT="harness-min-skill-demo"
```

### 3) 运行

```bash
# 使用默认问题
uv run python main.py

# 自定义输入
uv run python main.py "帮我查北京天气"
```

### 4) 预期效果

当输入包含天气查询时，Agent 会调用 get_weather 工具并返回结果。

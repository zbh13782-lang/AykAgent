# LangGraph Tool Demo

一个简单的 LangGraph Agent 示例，展示工具调用功能。

## 快速开始

安装依赖：
```bash
uv sync
```

配置环境变量：
```bash
export OPENAI_API_KEY="<your-openai-api-key>"
```

运行：
```bash
uv run python main.py
uv run python main.py "帮我查北京天气"
```

## 项目结构

```
main.py    # 主程序
tools.py   # 工具定义
graph.py   # LangGraph 构建
```

## 我的想法

这个项目展示了 LangGraph 的核心能力，但可以进一步优化：

1. 工具扩展性：当前只有一个天气工具，可以添加更多实用工具，比如搜索、计算、文件操作等
2. 错误处理：需要更完善的异常处理机制，特别是工具调用失败时的降级策略
3. 性能优化：考虑添加工具调用的缓存机制，避免重复查询
4. 用户体验：可以添加更友好的交互界面，比如进度提示、结果格式化等
5. 测试覆盖：需要添加单元测试和集成测试，确保各个组件的稳定性

LangGraph 的优势在于将复杂的 Agent 逻辑可视化，通过图结构管理状态流转，这对于构建多步骤、多工具的智能应用非常有价值。

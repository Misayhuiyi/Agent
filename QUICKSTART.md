# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- pydantic (数据验证)
- python-dotenv (环境变量管理)
- tiktoken (Token计数)
- openai (可选，用于LLM支持)

## 2. 配置环境

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的API密钥：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-3.5-turbo
```

注意：如果不配置API密钥，系统会使用简单模式运行（无LLM支持）。

## 3. 运行测试

```bash
python tests/test_simple.py
```

## 4. 基础使用

### 方式1：交互式对话

```bash
python main.py
```

### 方式2：单次问答

```bash
python main.py "帮我计算 123 + 456"
```

### 方式3：Python代码

```python
from agent_assistant import create_assistant

# 创建助手
assistant = create_assistant()

# 提问
response = assistant.ask("查询技术部员工")
print(response)

# 启动交互式对话
assistant.chat()
```

## 5. 运行示例

```bash
# 基础示例
python examples/basic_usage.py

# 高级示例
python examples/advanced_usage.py
```

## 6. 自定义工具

```python
from agent_assistant import create_assistant
from agent_assistant.tools.base import BaseTool, ToolResult, ToolParameter
from typing import List

class MyCustomTool(BaseTool):
    def _get_name(self) -> str:
        return "my_tool"
    
    def _get_description(self) -> str:
        return "我的自定义工具"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="input",
                type="string",
                description="输入参数",
                required=True
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        input_data = kwargs.get("input")
        # 处理逻辑
        result = f"处理结果: {input_data}"
        return ToolResult(success=True, result=result)

# 添加自定义工具
assistant = create_assistant()
assistant.add_tool(MyCustomTool())
```

## 7. 功能特性

### ReAct架构
- 思考（Thought）：分析问题
- 行动（Action）：调用工具
- 观察（Observation）：查看结果
- 循环直到得出答案

### 内置工具
1. **计算器**：数学运算
2. **数据查询**：查询结构化数据
3. **文档检索**：语义和关键词检索

### 对话管理
- 滑动窗口策略
- Token限制
- 轮数限制

## 8. 常见问题

**Q: 没有API密钥怎么办？**
A: 系统支持无LLM模式运行，使用简单规则进行推理。

**Q: 如何添加更多工具？**
A: 继承BaseTool类，实现必要方法，然后使用assistant.add_tool()添加。

**Q: 如何处理长对话？**
A: 已内置滑动窗口策略，自动管理历史消息。

## 9. 下一步

- 查看 [README.md](README.md) 了解详细文档
- 运行 [examples](examples/) 查看更多示例
- 自定义工具扩展功能
- 配置LLM支持智能推理

## 10. 项目结构

```
Agent/
├── agent_assistant/          # 核心代码
│   ├── core/                 # 核心模块
│   │   ├── agent.py          # ReAct Agent
│   │   ├── conversation_manager.py  # 对话管理
│   │   └── prompt_templates.py      # Prompt模板
│   ├── tools/                # 工具模块
│   │   ├── base.py           # 工具基类
│   │   ├── calculator.py     # 计算器
│   │   ├── data_query.py     # 数据查询
│   │   └── document_retrieval.py     # 文档检索
│   ├── assistant.py          # 主助手类
│   └── model_client.py       # 模型客户端
├── examples/                 # 示例代码
├── tests/                    # 测试代码
├── main.py                   # 主程序
├── requirements.txt          # 依赖列表
└── README.md                 # 项目文档
```

开始使用吧！
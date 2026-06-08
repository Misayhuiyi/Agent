# 基于 ReAct 架构的工具调用智能问答助手

一个功能强大的智能问答助手，基于 ReAct（Reasoning and Acting）架构，支持意图识别、多步推理与工具自动调用。

## 🌟 核心特性

- **ReAct 架构**：实现思考-行动-观察的循环推理机制
- **意图识别**：自动识别用户问题的类型和意图
- **多步推理**：支持复杂问题的拆解与分步执行
- **工具自动调用**：智能选择和调用合适的工具
- **对话历史管理**：滑动窗口策略，解决长对话 Token 超限问题
- **思维链优化**：精心设计的 Prompt 模板，提升任务完成率

## 📦 内置工具

1. **计算器工具**（calculator）
   - 支持基本数学运算：加减乘除、幂运算、开方等
   - 支持常用数学函数：sin, cos, tan, log, exp 等

2. **数据查询工具**（data_query）
   - 查询结构化数据：用户、产品、订单等
   - 支持条件筛选和字段选择

3. **文档检索工具**（document_retrieval）
   - 语义检索：基于向量相似度的智能检索
   - 关键词检索：基于关键词匹配的快速检索

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-3.5-turbo
```

### 基础使用

```python
from agent_assistant import create_assistant

# 创建助手实例
assistant = create_assistant()

# 提问
response = assistant.ask("帮我计算 123 + 456")
print(response)

# 启动交互式对话
assistant.chat()
```

### 命令行使用

```bash
# 交互式对话
python main.py

# 单次问答
python main.py 帮我计算 123 + 456
```

## 📚 详细示例

### 示例1：基础使用

```python
from agent_assistant import create_assistant

assistant = create_assistant(verbose=True)

# 数学计算
response = assistant.ask("计算 sqrt(144) + 5 * 3")
# 输出: 27.0

# 数据查询
response = assistant.ask("查询技术部的员工信息")
# 输出: 技术部员工列表

# 文档检索
response = assistant.ask("公司的请假制度是什么？")
# 输出: 员工年假为5-15天...
```

### 示例2：自定义工具

```python
from agent_assistant import create_assistant
from agent_assistant.tools.base import BaseTool, ToolResult, ToolParameter
from typing import List

class WeatherTool(BaseTool):
    """天气查询工具"""
    
    def _get_name(self) -> str:
        return "weather"
    
    def _get_description(self) -> str:
        return "查询指定城市的天气信息"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="city",
                type="string",
                description="城市名称",
                required=True
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        city = kwargs.get("city")
        # 实现天气查询逻辑
        weather_info = f"{city}今天晴天，温度20-25℃"
        return ToolResult(success=True, result=weather_info)

# 添加自定义工具
assistant = create_assistant()
assistant.add_tool(WeatherTool())

response = assistant.ask("北京今天天气怎么样？")
```

### 示例3：对话历史管理

```python
from agent_assistant import create_assistant

assistant = create_assistant(
    max_history_tokens=4000,  # 最大历史token数
    max_history_turns=10      # 最大对话轮数
)

# 多轮对话
assistant.ask("查询技术部有多少员工")
assistant.ask("他们的平均工资是多少？")  # 会引用上一轮的上下文

# 查看对话历史
history = assistant.get_history()

# 清空历史
assistant.clear_history()
```

## 🏗️ 项目结构

```
Agent/
├── agent_assistant/
│   ├── __init__.py
│   ├── assistant.py          # 主助手类
│   ├── model_client.py        # 模型客户端封装
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py           # ReAct Agent核心实现
│   │   ├── conversation_manager.py  # 对话历史管理
│   │   └── prompt_templates.py       # Prompt模板
│   └── tools/
│       ├── __init__.py
│       ├── base.py            # 工具基类
│       ├── calculator.py      # 计算器工具
│       ├── data_query.py     # 数据查询工具
│       └── document_retrieval.py  # 文档检索工具
├── examples/
│   ├── basic_usage.py         # 基础使用示例
│   └── advanced_usage.py      # 高级功能示例
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖列表
├── .env.example              # 环境变量示例
└── README.md                 # 项目文档
```

## 🔧 核心组件说明

### 1. ReAct Agent

ReAct Agent 是核心组件，实现了以下功能：

- **思考（Thought）**：分析当前问题，决定下一步行动
- **行动（Action）**：选择并调用合适的工具
- **观察（Observation）**：观察工具返回的结果
- **循环**：根据观察结果继续思考，直到得出最终答案

### 2. 对话历史管理

采用滑动窗口策略管理对话历史：

- **Token 限制**：限制历史消息的总 Token 数
- **轮数限制**：限制对话轮数
- **智能保留**：始终保留系统提示词

### 3. Prompt 模板

精心设计的 Prompt 模板：

- **ReAct 系统提示词**：引导模型按照 ReAct 框架思考
- **意图识别提示词**：识别用户问题的类型和意图
- **问题拆解提示词**：将复杂问题拆解为子问题
- **错误恢复提示词**：处理工具调用失败的情况

## 🎯 使用场景

1. **智能客服**：自动回答用户问题，查询数据
2. **数据分析助手**：帮助用户查询和分析数据
3. **知识库问答**：基于文档库回答问题
4. **任务自动化**：自动执行多步骤任务

## 🔌 扩展开发

### 添加新工具

继承 `BaseTool` 类并实现必要方法：

```python
from agent_assistant.tools.base import BaseTool, ToolResult, ToolParameter
from typing import List

class MyTool(BaseTool):
    def _get_name(self) -> str:
        return "my_tool"
    
    def _get_description(self) -> str:
        return "工具描述"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="param1",
                type="string",
                description="参数描述",
                required=True
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        # 实现工具逻辑
        result = "工具执行结果"
        return ToolResult(success=True, result=result)
```

### 自定义 Prompt

修改 `prompt_templates.py` 中的模板：

```python
from agent_assistant.core.prompt_templates import PromptTemplates

# 自定义系统提示词
custom_prompt = PromptTemplates.REACT_SYSTEM_PROMPT.format(
    tools_info="你的工具信息"
)
```

## 📊 性能优化

1. **Token 优化**：滑动窗口策略避免 Token 超限
2. **缓存机制**：可添加结果缓存提升响应速度
3. **并行调用**：支持多个工具并行调用（需自行实现）

## 🐛 常见问题

**Q: 如何处理工具调用失败？**
A: Agent 会自动进入错误恢复流程，尝试其他方法或给出友好提示。

**Q: 如何支持更多模型？**
A: 实现 `model_client.py` 中的接口，或直接传入兼容 OpenAI API 的客户端。

**Q: 如何处理长对话？**
A: 已内置滑动窗口策略，自动管理对话历史。

## 📝 开发计划

- [ ] 支持更多模型（Claude, 文心一言等）
- [ ] 添加流式输出支持
- [ ] 实现工具调用缓存
- [ ] 添加 Web UI 界面
- [ ] 支持多 Agent 协作

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题或建议，请提交 Issue。
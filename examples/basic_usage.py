"""
示例：基础使用
"""
from agent_assistant import create_assistant


def basic_example():
    """基础使用示例"""
    print("=" * 60)
    print("示例1：基础使用")
    print("=" * 60)
    
    # 创建助手实例
    assistant = create_assistant(verbose=True)
    
    # 提问
    questions = [
        "帮我计算 123 + 456",
        "查询技术部的员工信息",
        "公司请假制度是什么？",
        "查询价格大于1000的产品"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)
        response = assistant.ask(question)
        print(f"回答: {response}")
        print("=" * 60)


def interactive_example():
    """交互式对话示例"""
    print("\n" + "=" * 60)
    print("示例2：交互式对话")
    print("=" * 60)
    
    # 创建助手实例
    assistant = create_assistant(verbose=False)
    
    # 启动交互式对话
    assistant.chat()


def custom_tool_example():
    """自定义工具示例"""
    print("\n" + "=" * 60)
    print("示例3：自定义工具")
    print("=" * 60)
    
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
                    description="城市名称，例如：北京、上海",
                    required=True
                )
            ]
        
        def execute(self, **kwargs) -> ToolResult:
            city = kwargs.get("city", "")
            
            # 模拟天气数据
            weather_data = {
                "北京": "晴天，温度15-25℃，空气质量良好",
                "上海": "多云，温度18-26℃，有轻微雾霾",
                "广州": "小雨，温度20-28℃，湿度较高"
            }
            
            if city in weather_data:
                return ToolResult(
                    success=True,
                    result={"city": city, "weather": weather_data[city]}
                )
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"未找到城市 '{city}' 的天气信息"
                )
    
    # 创建助手并添加自定义工具
    assistant = create_assistant(verbose=True)
    assistant.add_tool(WeatherTool())
    
    # 使用自定义工具
    question = "北京今天天气怎么样？"
    print(f"\n问题: {question}")
    print("-" * 60)
    response = assistant.ask(question)
    print(f"回答: {response}")


def history_management_example():
    """对话历史管理示例"""
    print("\n" + "=" * 60)
    print("示例4：对话历史管理")
    print("=" * 60)
    
    assistant = create_assistant(verbose=False)
    
    # 多轮对话
    questions = [
        "查询技术部有多少员工",
        "他们的平均工资是多少？",
        "查询价格最贵的产品是什么",
        "这个产品有库存吗？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n第{i}轮对话:")
        print(f"用户: {question}")
        response = assistant.ask(question)
        print(f"助手: {response}")
        
        # 显示对话历史状态
        state = assistant.get_agent_state()
        print(f"对话历史: {state['conversation_summary']['total_messages']} 条消息, "
              f"{state['conversation_summary']['total_tokens']} tokens")
    
    # 清空历史
    print("\n清空对话历史...")
    assistant.clear_history()
    state = assistant.get_agent_state()
    print(f"清空后: {state['conversation_summary']['total_messages']} 条消息")


if __name__ == "__main__":
    # 运行所有示例
    basic_example()
    # interactive_example()  # 取消注释以运行交互式示例
    custom_tool_example()
    history_management_example()
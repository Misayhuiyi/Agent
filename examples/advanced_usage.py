"""
示例：高级功能
"""
from agent_assistant import create_assistant
from agent_assistant.tools.base import BaseTool, ToolResult, ToolParameter
from typing import List
import json


class DatabaseTool(BaseTool):
    """数据库查询工具（模拟）"""
    
    def _get_name(self) -> str:
        return "database_query"
    
    def _get_description(self) -> str:
        return "执行SQL查询（模拟），支持SELECT语句"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="sql",
                type="string",
                description="SQL查询语句",
                required=True
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="返回结果数量限制",
                required=False,
                default=10
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        sql = kwargs.get("sql", "").strip()
        limit = kwargs.get("limit", 10)
        
        # 模拟数据库查询
        if "SELECT" not in sql.upper():
            return ToolResult(
                success=False,
                result=None,
                error="只支持SELECT查询"
            )
        
        # 模拟数据
        mock_data = [
            {"id": 1, "name": "产品A", "sales": 1000, "region": "华东"},
            {"id": 2, "name": "产品B", "sales": 1500, "region": "华北"},
            {"id": 3, "name": "产品C", "sales": 800, "region": "华南"},
        ]
        
        return ToolResult(
            success=True,
            result=mock_data[:limit],
            metadata={"sql": sql, "rows_affected": len(mock_data[:limit])}
        )


class APITool(BaseTool):
    """API调用工具（模拟）"""
    
    def _get_name(self) -> str:
        return "api_call"
    
    def _get_description(self) -> str:
        return "调用外部API（模拟），支持GET和POST请求"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="endpoint",
                type="string",
                description="API端点，例如：/users, /products",
                required=True
            ),
            ToolParameter(
                name="method",
                type="string",
                description="HTTP方法",
                required=False,
                default="GET",
                enum=["GET", "POST"]
            ),
            ToolParameter(
                name="data",
                type="string",
                description="请求数据（JSON格式）",
                required=False
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        endpoint = kwargs.get("endpoint", "")
        method = kwargs.get("method", "GET")
        data = kwargs.get("data")
        
        # 模拟API响应
        mock_responses = {
            "/users": [
                {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
                {"id": 2, "name": "李四", "email": "lisi@example.com"},
            ],
            "/products": [
                {"id": 1, "name": "笔记本电脑", "price": 5999},
                {"id": 2, "name": "手机", "price": 3999},
            ]
        }
        
        if endpoint in mock_responses:
            return ToolResult(
                success=True,
                result={
                    "status": 200,
                    "data": mock_responses[endpoint]
                },
                metadata={"endpoint": endpoint, "method": method}
            )
        else:
            return ToolResult(
                success=False,
                result=None,
                error=f"未知的API端点: {endpoint}"
            )


def advanced_tools_example():
    """高级工具示例"""
    print("=" * 60)
    print("示例：高级工具使用")
    print("=" * 60)
    
    # 创建助手并添加高级工具
    assistant = create_assistant(verbose=True)
    assistant.add_tool(DatabaseTool())
    assistant.add_tool(APITool())
    
    # 复杂查询
    questions = [
        "查询销售数据，按地区分组",
        "调用用户API获取用户列表",
        "计算销售总额：1000 + 1500 + 800"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)
        response = assistant.ask(question)
        print(f"回答: {response}\n")


def multi_step_reasoning_example():
    """多步推理示例"""
    print("\n" + "=" * 60)
    print("示例：多步推理")
    print("=" * 60)
    
    assistant = create_assistant(verbose=True)
    
    # 复杂问题需要多步推理
    question = """
    我需要了解以下信息：
    1. 技术部有哪些员工？
    2. 他们的平均工资是多少？
    3. 请假制度是怎样的？
    """
    
    print(f"问题: {question}")
    print("-" * 60)
    response = assistant.ask(question)
    print(f"回答: {response}\n")


def error_handling_example():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例：错误处理")
    print("=" * 60)
    
    assistant = create_assistant(verbose=True)
    
    # 故意提问会失败的问题
    questions = [
        "查询不存在的表 xyz",
        "计算 1/0",  # 除零错误
        "检索文档，但查询为空"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)
        response = assistant.ask(question)
        print(f"回答: {response}\n")


def conversation_context_example():
    """对话上下文示例"""
    print("\n" + "=" * 60)
    print("示例：对话上下文理解")
    print("=" * 60)
    
    assistant = create_assistant(verbose=False)
    
    # 连续对话，展示上下文理解
    conversation = [
        ("查询技术部的员工", "查询技术部员工"),
        ("他们中谁的工资最高？", "基于上一次查询结果分析"),
        ("这个员工的详细信息是什么？", "引用之前的上下文"),
    ]
    
    for i, (question, note) in enumerate(conversation, 1):
        print(f"\n第{i}轮对话 ({note}):")
        print(f"用户: {question}")
        response = assistant.ask(question)
        print(f"助手: {response}")


if __name__ == "__main__":
    advanced_tools_example()
    multi_step_reasoning_example()
    error_handling_example()
    conversation_context_example()
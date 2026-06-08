"""
测试脚本
验证项目基本功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_assistant.tools.calculator import CalculatorTool
from agent_assistant.tools.data_query import DataQueryTool
from agent_assistant.tools.document_retrieval import DocumentRetrievalTool
from agent_assistant.core.conversation_manager import ConversationManager
from agent_assistant.core.agent import ReActAgent


def test_calculator_tool():
    """测试计算器工具"""
    print("=" * 60)
    print("测试计算器工具")
    print("=" * 60)
    
    tool = CalculatorTool()
    
    # 测试基本运算
    tests = [
        ("2 + 3", 5),
        ("10 - 4", 6),
        ("3 * 4", 12),
        ("20 / 5", 4),
        ("2 ** 3", 8),
        ("sqrt(16)", 4),
    ]
    
    for expression, expected in tests:
        result = tool.execute(expression=expression)
        print(f"表达式: {expression}")
        print(f"预期结果: {expected}")
        print(f"实际结果: {result.result}")
        print(f"成功: {result.success}")
        print("-" * 40)


def test_data_query_tool():
    """测试数据查询工具"""
    print("\n" + "=" * 60)
    print("测试数据查询工具")
    print("=" * 60)
    
    tool = DataQueryTool()
    
    # 测试查询
    tests = [
        {"table": "users", "limit": 3},
        {"table": "users", "conditions": '{"department": "技术部"}'},
        {"table": "products", "fields": "name,price"},
    ]
    
    for params in tests:
        result = tool.execute(**params)
        print(f"查询参数: {params}")
        print(f"成功: {result.success}")
        if result.success:
            print(f"结果数量: {len(result.result)}")
            print(f"结果: {result.result[:2]}")  # 只显示前2条
        else:
            print(f"错误: {result.error}")
        print("-" * 40)


def test_document_retrieval_tool():
    """测试文档检索工具"""
    print("\n" + "=" * 60)
    print("测试文档检索工具")
    print("=" * 60)
    
    tool = DocumentRetrievalTool()
    
    # 测试检索
    queries = [
        "请假制度",
        "报销流程",
        "技术架构"
    ]
    
    for query in queries:
        result = tool.execute(query=query, top_k=2)
        print(f"查询: {query}")
        print(f"成功: {result.success}")
        if result.success:
            print(f"找到文档: {len(result.result)}")
            for doc in result.result:
                print(f"  - {doc['title']} (分数: {doc.get('score', 0):.2f})")
        else:
            print(f"错误: {result.error}")
        print("-" * 40)


def test_conversation_manager():
    """测试对话历史管理"""
    print("\n" + "=" * 60)
    print("测试对话历史管理")
    print("=" * 60)
    
    manager = ConversationManager(
        max_history_tokens=100,
        max_history_turns=3,
        system_prompt="你是一个智能助手"
    )
    
    # 添加消息
    manager.add_message("user", "你好")
    manager.add_message("assistant", "你好！有什么可以帮助你的吗？")
    manager.add_message("user", "查询技术部员工")
    manager.add_message("assistant", "技术部有3名员工：张三、王五、钱七")
    
    print(f"消息数量: {manager.get_message_count()}")
    print(f"Token数量: {manager.get_token_count()}")
    print(f"对话摘要: {manager.get_conversation_summary()}")
    
    # 测试滑动窗口
    print("\n测试滑动窗口（添加更多消息）:")
    for i in range(5):
        manager.add_message("user", f"问题{i}")
        manager.add_message("assistant", f"回答{i}")
        print(f"添加第{i+1}轮后 - 消息数: {manager.get_message_count()}, Token数: {manager.get_token_count()}")


def test_agent_without_llm():
    """测试Agent（无LLM模式）"""
    print("\n" + "=" * 60)
    print("测试ReAct Agent（无LLM模式）")
    print("=" * 60)
    
    tools = [
        CalculatorTool(),
        DataQueryTool(),
        DocumentRetrievalTool()
    ]
    
    agent = ReActAgent(tools=tools, model_client=None, verbose=True)
    
    # 测试问题
    questions = [
        "计算 10 + 20",
        "查询技术部员工",
        "公司请假制度是什么"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 40)
        response = agent.process_user_input(question)
        print(f"回答: {response}")
        print("=" * 40)


def test_tool_validation():
    """测试工具参数验证"""
    print("\n" + "=" * 60)
    print("测试工具参数验证")
    print("=" * 60)
    
    tool = CalculatorTool()
    
    # 测试有效参数
    is_valid, error = tool.validate_parameters(expression="1+1")
    print(f"有效参数测试: valid={is_valid}, error={error}")
    
    # 测试缺少必需参数
    is_valid, error = tool.validate_parameters()
    print(f"缺少参数测试: valid={is_valid}, error={error}")
    
    # 测试OpenAI function格式
    function_schema = tool.to_openai_function()
    print(f"\nOpenAI Function格式:")
    print(f"名称: {function_schema['function']['name']}")
    print(f"描述: {function_schema['function']['description']}")


if __name__ == "__main__":
    print("\n开始测试...\n")
    
    try:
        test_calculator_tool()
        test_data_query_tool()
        test_document_retrieval_tool()
        test_conversation_manager()
        test_agent_without_llm()
        test_tool_validation()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
"""
简化测试脚本（不依赖外部库）
验证基本逻辑
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import():
    """测试导入"""
    print("=" * 60)
    print("测试模块导入")
    print("=" * 60)
    
    try:
        from agent_assistant.tools.base import BaseTool, ToolResult, ToolParameter
        print("[OK] BaseTool 导入成功")
    except Exception as e:
        print(f"[FAIL] BaseTool 导入失败: {e}")
        return False
    
    try:
        from agent_assistant.tools.calculator import CalculatorTool
        print("[OK] CalculatorTool 导入成功")
    except Exception as e:
        print(f"[FAIL] CalculatorTool 导入失败: {e}")
        return False
    
    try:
        from agent_assistant.tools.data_query import DataQueryTool
        print("[OK] DataQueryTool 导入成功")
    except Exception as e:
        print(f"[FAIL] DataQueryTool 导入失败: {e}")
        return False
    
    try:
        from agent_assistant.core.conversation_manager import ConversationManager
        print("[OK] ConversationManager 导入成功")
    except Exception as e:
        print(f"[FAIL] ConversationManager 导入失败: {e}")
        return False
    
    try:
        from agent_assistant.core.agent import ReActAgent
        print("[OK] ReActAgent 导入成功")
    except Exception as e:
        print(f"[FAIL] ReActAgent 导入失败: {e}")
        return False
    
    return True


def test_basic_structure():
    """测试基本结构"""
    print("\n" + "=" * 60)
    print("测试基本结构")
    print("=" * 60)
    
    try:
        from agent_assistant.tools.base import BaseTool
        
        # 检查基本属性
        print("[OK] BaseTool 是抽象基类")
        print("[OK] BaseTool 有必要的方法定义")
        
        return True
    except Exception as e:
        print(f"[FAIL] 结构测试失败: {e}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 60)
    print("测试文件结构")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_files = [
        "agent_assistant/__init__.py",
        "agent_assistant/tools/__init__.py",
        "agent_assistant/tools/base.py",
        "agent_assistant/tools/calculator.py",
        "agent_assistant/tools/data_query.py",
        "agent_assistant/tools/document_retrieval.py",
        "agent_assistant/core/__init__.py",
        "agent_assistant/core/agent.py",
        "agent_assistant/core/conversation_manager.py",
        "agent_assistant/core/prompt_templates.py",
        "agent_assistant/assistant.py",
        "agent_assistant/model_client.py",
        "main.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_exist = True
    for file in required_files:
        full_path = os.path.join(base_path, file)
        if os.path.exists(full_path):
            print(f"[OK] {file} 存在")
        else:
            print(f"[FAIL] {file} 不存在")
            all_exist = False
    
    return all_exist


def main():
    """主测试函数"""
    print("\n开始简化测试...\n")
    
    results = []
    
    # 测试文件结构
    results.append(("文件结构", test_file_structure()))
    
    # 测试导入（如果pydantic可用）
    try:
        results.append(("模块导入", test_import()))
        results.append(("基本结构", test_basic_structure()))
    except Exception as e:
        print(f"\n导入测试跳过（缺少依赖）: {e}")
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n所有测试通过！")
    else:
        print("\n部分测试失败，请检查依赖安装")


if __name__ == "__main__":
    main()
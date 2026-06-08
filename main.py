"""
主程序入口
"""
from agent_assistant import create_assistant
import sys


def main():
    """主函数"""
    print("=" * 60)
    print("基于ReAct架构的工具调用智能问答助手")
    print("=" * 60)
    
    # 创建助手
    assistant = create_assistant(verbose=True)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 单次问答模式
        question = " ".join(sys.argv[1:])
        print(f"\n问题: {question}")
        print("-" * 60)
        response = assistant.ask(question)
        print(f"回答: {response}")
    else:
        # 交互式对话模式
        assistant.chat()


if __name__ == "__main__":
    main()
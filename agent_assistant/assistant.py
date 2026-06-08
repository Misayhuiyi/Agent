"""
智能问答助手主程序
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

from .core.agent import ReActAgent
from .core.conversation_manager import ConversationManager
from .tools.base import BaseTool
from .tools.calculator import CalculatorTool
from .tools.data_query import DataQueryTool
from .tools.document_retrieval import DocumentRetrievalTool
from .model_client import ModelClient


class Assistant:
    """智能问答助手"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        max_history_tokens: int = 4000,
        max_history_turns: int = 10,
        custom_tools: Optional[List[BaseTool]] = None,
        verbose: bool = False
    ):
        """
        初始化智能问答助手
        
        Args:
            api_key: API密钥（如不提供，从环境变量读取）
            base_url: API基础URL
            model_name: 模型名称
            max_history_tokens: 历史消息最大token数
            max_history_turns: 历史消息最大轮数
            custom_tools: 自定义工具列表
            verbose: 是否输出详细日志
        """
        # 加载环境变量
        load_dotenv()
        
        # 初始化工具
        self.tools = [
            CalculatorTool(),
            DataQueryTool(),
            DocumentRetrievalTool()
        ]
        
        # 添加自定义工具
        if custom_tools:
            self.tools.extend(custom_tools)
        
        # 初始化模型客户端
        self.model_client = None
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        
        try:
            self.model_client = ModelClient(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )
        except Exception as e:
            print(f"警告: 模型客户端初始化失败: {e}")
            print("将使用简单模式运行（无LLM支持）")
        
        # 初始化Agent
        self.agent = ReActAgent(
            tools=self.tools,
            model_client=self.model_client,
            verbose=verbose
        )
        
        # 更新对话管理器配置
        self.agent.conversation_manager.max_history_tokens = max_history_tokens
        self.agent.conversation_manager.max_history_turns = max_history_turns
    
    def ask(self, question: str) -> str:
        """
        提问
        
        Args:
            question: 用户问题
            
        Returns:
            助手回答
        """
        return self.agent.process_user_input(question)
    
    def chat(self) -> None:
        """启动交互式对话"""
        print("=" * 60)
        print("智能问答助手（基于ReAct架构）")
        print("=" * 60)
        print("可用工具：")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")
        print("\n输入 'quit' 或 'exit' 退出")
        print("输入 'clear' 清空对话历史")
        print("输入 'history' 查看对话历史")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n用户: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\n再见！")
                    break
                
                if user_input.lower() == 'clear':
                    self.agent.clear_history()
                    print("对话历史已清空")
                    continue
                
                if user_input.lower() == 'history':
                    history = self.agent.get_conversation_history()
                    print("\n对话历史：")
                    for i, msg in enumerate(history, 1):
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')
                        print(f"{i}. [{role}]: {content[:100]}...")
                    continue
                
                # 处理问题
                response = self.ask(user_input)
                print(f"\n助手: {response}")
                
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {str(e)}")
    
    def get_history(self) -> List[dict]:
        """获取对话历史"""
        return self.agent.get_conversation_history()
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.agent.clear_history()
    
    def get_agent_state(self) -> dict:
        """获取Agent状态"""
        return self.agent.get_agent_state()
    
    def add_tool(self, tool: BaseTool) -> None:
        """添加工具"""
        self.tools.append(tool)
        self.agent.tools[tool.name] = tool
    
    def remove_tool(self, tool_name: str) -> bool:
        """移除工具"""
        if tool_name in self.agent.tools:
            del self.agent.tools[tool_name]
            self.tools = [t for t in self.tools if t.name != tool_name]
            return True
        return False


def create_assistant(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model_name: str = "gpt-3.5-turbo",
    verbose: bool = False
) -> Assistant:
    """
    创建智能问答助手实例
    
    Args:
        api_key: API密钥
        base_url: API基础URL
        model_name: 模型名称
        verbose: 是否输出详细日志
        
    Returns:
        Assistant实例
    """
    return Assistant(
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        verbose=verbose
    )
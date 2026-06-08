"""
对话历史管理器
支持滑动窗口策略，解决长对话Token超限问题
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import tiktoken


@dataclass
class Message:
    """消息类"""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None  # 工具名称（当role为tool时）
    tool_call_id: Optional[str] = None  # 工具调用ID
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        msg = {"role": self.role, "content": self.content}
        if self.name:
            msg["name"] = self.name
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        return msg


class ConversationManager:
    """对话历史管理器"""
    
    def __init__(
        self,
        max_history_tokens: int = 4000,
        max_history_turns: int = 10,
        model_name: str = "gpt-3.5-turbo",
        system_prompt: Optional[str] = None
    ):
        """
        初始化对话管理器
        
        Args:
            max_history_tokens: 历史消息最大token数
            max_history_turns: 历史消息最大轮数
            model_name: 模型名称（用于计算token）
            system_prompt: 系统提示词
        """
        self.max_history_tokens = max_history_tokens
        self.max_history_turns = max_history_turns
        self.model_name = model_name
        self.system_prompt = system_prompt
        
        # 尝试加载tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # 如果模型不支持，使用cl100k_base（GPT-3.5/GPT-4的编码）
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # 消息历史
        self.messages: List[Message] = []
        
        # 添加系统提示词
        if system_prompt:
            self.add_message("system", system_prompt)
    
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        return len(self.encoding.encode(text))
    
    def add_message(
        self,
        role: str,
        content: str,
        name: Optional[str] = None,
        tool_call_id: Optional[str] = None
    ) -> Message:
        """添加消息"""
        token_count = self.count_tokens(content)
        
        message = Message(
            role=role,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            token_count=token_count
        )
        
        self.messages.append(message)
        
        # 应用滑动窗口策略
        self._apply_sliding_window()
        
        return message
    
    def _apply_sliding_window(self):
        """应用滑动窗口策略"""
        # 保留系统消息
        system_messages = [m for m in self.messages if m.role == "system"]
        other_messages = [m for m in self.messages if m.role != "system"]
        
        # 策略1: 限制消息轮数
        if len(other_messages) > self.max_history_turns * 2:  # 每轮包含user和assistant
            # 保留最近的消息
            other_messages = other_messages[-(self.max_history_turns * 2):]
        
        # 策略2: 限制token总数
        total_tokens = sum(m.token_count for m in other_messages)
        
        while total_tokens > self.max_history_tokens and len(other_messages) > 2:
            # 移除最早的消息对（user + assistant）
            removed_tokens = other_messages[0].token_count
            other_messages.pop(0)
            total_tokens -= removed_tokens
            
            # 如果移除的是user消息，也要移除对应的assistant消息
            if other_messages and other_messages[0].role == "assistant":
                total_tokens -= other_messages[0].token_count
                other_messages.pop(0)
        
        # 重新组合消息
        self.messages = system_messages + other_messages
    
    def get_messages(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """获取消息列表"""
        messages = self.messages
        if not include_system:
            messages = [m for m in messages if m.role != "system"]
        return [m.to_dict() for m in messages]
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """获取最近n条消息"""
        return [m.to_dict() for m in self.messages[-n:]]
    
    def clear_history(self, keep_system: bool = True):
        """清空历史"""
        if keep_system:
            self.messages = [m for m in self.messages if m.role == "system"]
        else:
            self.messages = []
    
    def get_token_count(self) -> int:
        """获取当前总token数"""
        return sum(m.token_count for m in self.messages)
    
    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        user_messages = [m for m in self.messages if m.role == "user"]
        assistant_messages = [m for m in self.messages if m.role == "assistant"]
        tool_messages = [m for m in self.messages if m.role == "tool"]
        
        return {
            "total_messages": len(self.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "tool_messages": len(tool_messages),
            "total_tokens": self.get_token_count(),
            "max_tokens": self.max_history_tokens,
            "max_turns": self.max_history_turns
        }
    
    def export_history(self) -> List[Dict[str, Any]]:
        """导出历史记录"""
        return [
            {
                "role": m.role,
                "content": m.content,
                "name": m.name,
                "tool_call_id": m.tool_call_id,
                "timestamp": m.timestamp.isoformat(),
                "token_count": m.token_count
            }
            for m in self.messages
        ]
    
    def import_history(self, history: List[Dict[str, Any]]):
        """导入历史记录"""
        self.messages = []
        for item in history:
            message = Message(
                role=item["role"],
                content=item["content"],
                name=item.get("name"),
                tool_call_id=item.get("tool_call_id"),
                timestamp=datetime.fromisoformat(item["timestamp"]),
                token_count=item["token_count"]
            )
            self.messages.append(message)
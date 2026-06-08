"""
模型客户端封装
支持OpenAI和其他兼容API
"""
from typing import Optional, Dict, Any, List
import os
from openai import OpenAI


class ModelClient:
    """模型客户端封装"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo"
    ):
        """
        初始化模型客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("请提供API密钥或设置OPENAI_API_KEY环境变量")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            模型响应文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"模型调用失败: {str(e)}")
    
    def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        发送带函数调用的聊天请求
        
        Args:
            messages: 消息列表
            functions: 函数列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            包含响应和函数调用的字典
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "function_call": None
            }
            
            if message.function_call:
                result["function_call"] = {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            
            return result
        except Exception as e:
            raise Exception(f"模型调用失败: {str(e)}")
"""
工具基类定义
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool = Field(description="执行是否成功")
    result: Any = Field(description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str = Field(description="参数名称")
    type: str = Field(description="参数类型")
    description: str = Field(description="参数描述")
    required: bool = Field(default=True, description="是否必需")
    default: Optional[Any] = Field(default=None, description="默认值")
    enum: Optional[List[str]] = Field(default=None, description="枚举值")


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self):
        self.name: str = self._get_name()
        self.description: str = self._get_description()
        self.parameters: List[ToolParameter] = self._get_parameters()
    
    @abstractmethod
    def _get_name(self) -> str:
        """获取工具名称"""
        pass
    
    @abstractmethod
    def _get_description(self) -> str:
        """获取工具描述"""
        pass
    
    @abstractmethod
    def _get_parameters(self) -> List[ToolParameter]:
        """获取工具参数列表"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass
    
    def to_openai_function(self) -> Dict[str, Any]:
        """转换为OpenAI Function Calling格式"""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default
            
            properties[param.name] = prop
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """验证参数"""
        param_dict = {p.name: p for p in self.parameters}
        
        # 检查必需参数
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return False, f"缺少必需参数: {param.name}"
        
        # 检查参数类型和值
        for key, value in kwargs.items():
            if key not in param_dict:
                return False, f"未知参数: {key}"
            
            param = param_dict[key]
            if param.enum and value not in param.enum:
                return False, f"参数 {key} 的值必须是 {param.enum} 之一"
        
        return True, None
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
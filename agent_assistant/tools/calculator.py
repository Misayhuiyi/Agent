"""
计算器工具
"""
from typing import List
from .base import BaseTool, ToolResult, ToolParameter
import re


class CalculatorTool(BaseTool):
    """简单计算工具，支持基本数学运算"""
    
    def _get_name(self) -> str:
        return "calculator"
    
    def _get_description(self) -> str:
        return "执行基本数学计算，支持加减乘除、幂运算、开方等。输入数学表达式，返回计算结果。"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="数学表达式，例如: '2 + 3 * 4', 'sqrt(16)', '2 ** 10'",
                required=True
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        """执行计算"""
        expression = kwargs.get("expression", "").strip()
        
        if not expression:
            return ToolResult(
                success=False,
                result=None,
                error="表达式不能为空"
            )
        
        try:
            # 安全的数学函数映射
            safe_dict = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'sqrt': lambda x: x ** 0.5,
                'log': lambda x: __import__('math').log(x),
                'log10': lambda x: __import__('math').log10(x),
                'exp': lambda x: __import__('math').exp(x),
                'sin': lambda x: __import__('math').sin(x),
                'cos': lambda x: __import__('math').cos(x),
                'tan': lambda x: __import__('math').tan(x),
                'pi': __import__('math').pi,
                'e': __import__('math').e,
            }
            
            # 验证表达式只包含允许的字符
            allowed_chars = set('0123456789+-*/.() %^,abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            if not all(c in allowed_chars for c in expression):
                return ToolResult(
                    success=False,
                    result=None,
                    error="表达式包含不允许的字符"
                )
            
            # 替换 ^ 为 **
            expression = expression.replace('^', '**')
            
            # 执行计算
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            return ToolResult(
                success=True,
                result=result,
                metadata={"expression": expression}
            )
            
        except ZeroDivisionError:
            return ToolResult(
                success=False,
                result=None,
                error="除零错误"
            )
        except SyntaxError:
            return ToolResult(
                success=False,
                result=None,
                error="表达式语法错误"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"计算错误: {str(e)}"
            )
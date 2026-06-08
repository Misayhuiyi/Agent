"""
数据查询工具
"""
from typing import List, Dict, Any, Optional
from .base import BaseTool, ToolResult, ToolParameter
import json


class DataQueryTool(BaseTool):
    """数据查询工具，支持结构化数据查询"""
    
    def __init__(self):
        super().__init__()
        # 示例数据库
        self.database = {
            "users": [
                {"id": 1, "name": "张三", "age": 28, "department": "技术部", "salary": 15000},
                {"id": 2, "name": "李四", "age": 32, "department": "市场部", "salary": 12000},
                {"id": 3, "name": "王五", "age": 25, "department": "技术部", "salary": 13000},
                {"id": 4, "name": "赵六", "age": 35, "department": "人事部", "salary": 14000},
                {"id": 5, "name": "钱七", "age": 29, "department": "技术部", "salary": 16000},
            ],
            "products": [
                {"id": 1, "name": "笔记本电脑", "price": 5999, "stock": 100, "category": "电子产品"},
                {"id": 2, "name": "手机", "price": 3999, "stock": 200, "category": "电子产品"},
                {"id": 3, "name": "键盘", "price": 299, "stock": 500, "category": "配件"},
                {"id": 4, "name": "鼠标", "price": 199, "stock": 600, "category": "配件"},
                {"id": 5, "name": "显示器", "price": 1999, "stock": 80, "category": "电子产品"},
            ],
            "orders": [
                {"id": 1, "user_id": 1, "product_id": 1, "quantity": 2, "status": "completed"},
                {"id": 2, "user_id": 2, "product_id": 3, "quantity": 5, "status": "pending"},
                {"id": 3, "user_id": 3, "product_id": 2, "quantity": 1, "status": "completed"},
                {"id": 4, "user_id": 1, "product_id": 4, "quantity": 3, "status": "shipped"},
            ]
        }
    
    def _get_name(self) -> str:
        return "data_query"
    
    def _get_description(self) -> str:
        return "查询结构化数据，支持用户、产品、订单等数据的查询和筛选。"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="table",
                type="string",
                description="要查询的表名",
                required=True,
                enum=["users", "products", "orders"]
            ),
            ToolParameter(
                name="conditions",
                type="string",
                description="查询条件，JSON格式，例如: {\"department\": \"技术部\", \"age\": {\">=\": 25}}",
                required=False
            ),
            ToolParameter(
                name="fields",
                type="string",
                description="要返回的字段列表，逗号分隔，例如: \"name,age,salary\"。不指定则返回所有字段。",
                required=False
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
        """执行数据查询"""
        table = kwargs.get("table")
        conditions_str = kwargs.get("conditions")
        fields_str = kwargs.get("fields")
        limit = kwargs.get("limit", 10)
        
        # 检查表是否存在
        if table not in self.database:
            return ToolResult(
                success=False,
                result=None,
                error=f"表 '{table}' 不存在。可用的表: {list(self.database.keys())}"
            )
        
        data = self.database[table].copy()
        
        # 应用查询条件
        if conditions_str:
            try:
                conditions = json.loads(conditions_str)
                data = self._apply_conditions(data, conditions)
            except json.JSONDecodeError:
                return ToolResult(
                    success=False,
                    result=None,
                    error="条件格式错误，必须是有效的JSON"
                )
        
        # 选择字段
        if fields_str:
            fields = [f.strip() for f in fields_str.split(",")]
            data = [{k: v for k, v in item.items() if k in fields} for item in data]
        
        # 限制结果数量
        if limit > 0:
            data = data[:limit]
        
        return ToolResult(
            success=True,
            result=data,
            metadata={
                "table": table,
                "count": len(data),
                "conditions": conditions_str,
                "fields": fields_str
            }
        )
    
    def _apply_conditions(self, data: List[Dict], conditions: Dict) -> List[Dict]:
        """应用查询条件"""
        result = []
        
        for item in data:
            match = True
            for key, value in conditions.items():
                if key not in item:
                    match = False
                    break
                
                # 支持操作符
                if isinstance(value, dict):
                    for op, val in value.items():
                        if op == "==":
                            if item[key] != val:
                                match = False
                                break
                        elif op == "!=":
                            if item[key] == val:
                                match = False
                                break
                        elif op == ">":
                            if item[key] <= val:
                                match = False
                                break
                        elif op == ">=":
                            if item[key] < val:
                                match = False
                                break
                        elif op == "<":
                            if item[key] >= val:
                                match = False
                                break
                        elif op == "<=":
                            if item[key] > val:
                                match = False
                                break
                else:
                    if item[key] != value:
                        match = False
                        break
            
            if match:
                result.append(item)
        
        return result
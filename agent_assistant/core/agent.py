"""
ReAct Agent核心框架
实现意图识别、多步推理与工具自动调用
"""
from typing import List, Dict, Any, Optional, Tuple
import re
import json
from dataclasses import dataclass
from enum import Enum

from .conversation_manager import ConversationManager
from .prompt_templates import PromptTemplates
from ..tools.base import BaseTool, ToolResult


class AgentState(Enum):
    """Agent状态"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    FINISHED = "finished"
    ERROR = "error"


@dataclass
class AgentStep:
    """Agent执行步骤"""
    step_type: str  # thought, action, observation
    content: str
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_result: Optional[ToolResult] = None


class ReActAgent:
    """ReAct智能体"""
    
    def __init__(
        self,
        tools: List[BaseTool],
        model_client: Any = None,
        max_iterations: int = 10,
        verbose: bool = True
    ):
        """
        初始化ReAct Agent
        
        Args:
            tools: 工具列表
            model_client: 模型客户端（OpenAI/Anthropic等）
            max_iterations: 最大迭代次数
            verbose: 是否输出详细日志
        """
        self.tools = {tool.name: tool for tool in tools}
        self.model_client = model_client
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # 初始化对话管理器
        self.conversation_manager = ConversationManager(
            system_prompt=PromptTemplates.REACT_SYSTEM_PROMPT.format(
                tools_info=PromptTemplates.format_tools_info(tools)
            )
        )
        
        # Agent状态
        self.state = AgentState.IDLE
        self.current_steps: List[AgentStep] = []
        self.iteration_count = 0
    
    def set_model_client(self, client: Any):
        """设置模型客户端"""
        self.model_client = client
    
    def process_user_input(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            Agent的响应
        """
        # 添加用户消息到历史
        self.conversation_manager.add_message("user", user_input)
        
        # 重置状态
        self.state = AgentState.THINKING
        self.current_steps = []
        self.iteration_count = 0
        
        # 开始ReAct循环
        final_answer = self._react_loop(user_input)
        
        # 添加助手响应到历史
        self.conversation_manager.add_message("assistant", final_answer)
        
        return final_answer
    
    def _react_loop(self, question: str) -> str:
        """ReAct主循环"""
        context = ""
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            if self.verbose:
                print(f"\n{'='*50}")
                print(f"迭代 {self.iteration_count}/{self.max_iterations}")
                print(f"{'='*50}")
            
            # 思考阶段
            thought = self._think(question, context)
            if self.verbose:
                print(f"思考: {thought}")
            
            self.current_steps.append(AgentStep(
                step_type="thought",
                content=thought
            ))
            
            # 检查是否得出最终答案
            if "最终答案：" in thought or "最终答案:" in thought:
                self.state = AgentState.FINISHED
                # 提取最终答案
                answer_match = re.search(r'最终答案[：:]\s*(.+)', thought, re.DOTALL)
                if answer_match:
                    return answer_match.group(1).strip()
                return thought
            
            # 行动阶段
            action, action_input = self._decide_action(question, thought, context)
            
            if action is None:
                # 无法决定行动，直接给出答案
                return self._generate_final_answer(question, context)
            
            if self.verbose:
                print(f"行动: {action}")
                print(f"行动输入: {action_input}")
            
            # 执行工具
            observation = self._execute_tool(action, action_input)
            if self.verbose:
                print(f"观察: {observation}")
            
            self.current_steps.append(AgentStep(
                step_type="action",
                content=f"{action}({action_input})",
                tool_name=action,
                tool_input=action_input
            ))
            
            self.current_steps.append(AgentStep(
                step_type="observation",
                content=observation
            ))
            
            # 更新上下文
            context += f"\n思考: {thought}\n行动: {action}\n行动输入: {action_input}\n观察: {observation}\n"
        
        # 达到最大迭代次数
        return self._generate_final_answer(question, context)
    
    def _think(self, question: str, context: str) -> str:
        """思考阶段"""
        if self.model_client is None:
            # 使用简单的规则进行思考
            return self._simple_think(question, context)
        
        # 使用LLM进行思考
        prompt = self._build_thought_prompt(question, context)
        
        try:
            response = self.model_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个智能助手，正在使用ReAct框架解决问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if self.verbose:
                print(f"思考阶段错误: {e}")
            return self._simple_think(question, context)
    
    def _simple_think(self, question: str, context: str) -> str:
        """简单思考逻辑（无LLM时使用）"""
        # 基于关键词的简单推理
        question_lower = question.lower()
        
        # 检查是否已经获取了工具执行结果（观察阶段）
        if context:
            # 如果上下文中包含工具执行结果，说明已经有答案了
            if "观察:" in context and "结果：" in context:
                # 提取结果作为最终答案
                result_start = context.rfind("结果：") + 3
                result = context[result_start:].strip()
                return f"基于已收集的信息，我现在可以给出最终答案了。最终答案：{result}"
        
        if any(kw in question_lower for kw in ["计算", "加", "减", "乘", "除", "等于"]):
            return "我需要使用计算器工具来解决这个问题。"
        elif any(kw in question_lower for kw in ["查询", "数据", "用户", "产品", "订单"]):
            return "我需要使用数据查询工具来获取相关信息。"
        elif any(kw in question_lower for kw in ["文档", "制度", "流程", "规定"]):
            return "我需要使用文档检索工具来查找相关信息。"
        elif context and len(context) > 100:
            return "基于已收集的信息，我现在可以给出最终答案了。最终答案："
        else:
            return "让我分析一下这个问题，看看需要什么工具。"
    
    def _decide_action(
        self,
        question: str,
        thought: str,
        context: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """决定行动"""
        if self.model_client is None:
            return self._simple_decide_action(question, thought, context)
        
        # 使用LLM决定行动
        prompt = self._build_action_prompt(question, thought, context)
        
        try:
            response = self.model_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个智能助手，需要选择工具并提取参数。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # 解析行动和参数
            action_match = re.search(r'行动[：:]\s*(\w+)', content)
            input_match = re.search(r'行动输入[：:]\s*(\{.+?\})', content, re.DOTALL)
            
            if action_match:
                action = action_match.group(1)
                action_input = {}
                
                if input_match:
                    try:
                        action_input = json.loads(input_match.group(1))
                    except:
                        pass
                
                return action, action_input
            
        except Exception as e:
            if self.verbose:
                print(f"决定行动错误: {e}")
        
        return self._simple_decide_action(question, thought, context)
    
    def _simple_decide_action(
        self,
        question: str,
        thought: str,
        context: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """简单行动决策（无LLM时使用）"""
        question_lower = question.lower()
        
        # 计算器
        if "计算器" in thought or any(kw in question_lower for kw in ["计算", "加", "减", "乘", "除"]):
            # 提取数学表达式
            expr_match = re.search(r'[\d\+\-\*\/\.\(\)\s]+', question)
            if expr_match:
                return "calculator", {"expression": expr_match.group(0).strip()}
        
        # 数据查询
        if "数据查询" in thought or any(kw in question_lower for kw in ["查询", "数据"]):
            # 简单参数提取
            params = {"table": "users", "limit": 5}
            
            if "技术部" in question:
                params["conditions"] = '{"department": "技术部"}'
            elif "产品" in question_lower:
                params["table"] = "products"
            
            return "data_query", params
        
        # 文档检索
        if "文档检索" in thought or any(kw in question_lower for kw in ["文档", "制度", "流程"]):
            return "document_retrieval", {"query": question, "top_k": 3}
        
        # 如果有上下文但没有明确的工具，返回None
        if context:
            return None, None
        
        # 默认使用文档检索
        return "document_retrieval", {"query": question, "top_k": 3}
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """执行工具"""
        if tool_name not in self.tools:
            return f"错误：工具 '{tool_name}' 不存在。可用工具：{list(self.tools.keys())}"
        
        tool = self.tools[tool_name]
        
        # 验证参数
        is_valid, error_msg = tool.validate_parameters(**tool_input)
        if not is_valid:
            return f"参数验证失败：{error_msg}"
        
        # 执行工具
        result = tool.execute(**tool_input)
        
        if result.success:
            # 格式化结果
            if isinstance(result.result, list):
                return f"找到 {len(result.result)} 条结果：\n{json.dumps(result.result, ensure_ascii=False, indent=2)}"
            elif isinstance(result.result, dict):
                return f"结果：\n{json.dumps(result.result, ensure_ascii=False, indent=2)}"
            else:
                return f"结果：{result.result}"
        else:
            return f"工具执行失败：{result.error}"
    
    def _build_thought_prompt(self, question: str, context: str) -> str:
        """构建思考提示"""
        prompt = f"问题：{question}\n\n"
        
        if context:
            prompt += f"已收集的信息：\n{context}\n\n"
        
        prompt += "请思考下一步应该做什么。如果已经有足够的信息，请给出最终答案。"
        return prompt
    
    def _build_action_prompt(
        self,
        question: str,
        thought: str,
        context: str
    ) -> str:
        """构建行动提示"""
        tools_info = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        prompt = f"""问题：{question}

思考：{thought}

可用工具：
{tools_info}

请选择一个工具并提供参数。

格式：
行动：[工具名称]
行动输入：{{"参数名": "参数值"}}"""
        
        return prompt
    
    def _generate_final_answer(self, question: str, context: str) -> str:
        """生成最终答案"""
        if self.model_client is None:
            # 简单答案生成
            if context:
                return f"基于收集到的信息：{context}\n\n这是我能找到的相关信息。"
            else:
                return "抱歉，我无法找到足够的信息来回答这个问题。"
        
        # 使用LLM生成答案
        prompt = PromptTemplates.get_final_answer_prompt(question, context)
        
        try:
            response = self.model_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个智能助手，请基于收集的信息给出准确、有帮助的答案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if self.verbose:
                print(f"生成答案错误: {e}")
            return "抱歉，生成答案时出现错误。"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_manager.get_messages()
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_manager.clear_history(keep_system=True)
        self.current_steps = []
        self.state = AgentState.IDLE
    
    def get_agent_state(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "state": self.state.value,
            "iteration_count": self.iteration_count,
            "steps_count": len(self.current_steps),
            "conversation_summary": self.conversation_manager.get_conversation_summary()
        }
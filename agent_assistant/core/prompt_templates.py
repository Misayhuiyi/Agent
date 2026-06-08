"""
Prompt模板管理
优化的思维链Prompt，提升任务完成率、降低模型幻觉
"""
from typing import List, Dict, Any, Optional


class PromptTemplates:
    """Prompt模板集合"""
    
    # ReAct系统提示词（优化版）
    REACT_SYSTEM_PROMPT = """你是一个智能助手，使用ReAct（Reasoning and Acting）框架来解决问题。

你的工作流程：
1. **思考（Thought）**：分析当前问题，决定下一步行动
2. **行动（Action）**：选择并调用合适的工具
3. **观察（Observation）**：观察工具返回的结果
4. **重复**：根据观察结果继续思考，直到得出最终答案

重要原则：
- 每次只执行一个工具调用
- 仔细分析工具返回的结果
- 如果工具调用失败，尝试其他方法
- 避免重复相同的操作
- 当有足够信息时，直接给出最终答案

输出格式：
思考：[你的推理过程]
行动：[工具名称]
行动输入：{{"参数名": "参数值"}}

或当任务完成时：
思考：[最终推理]
最终答案：[答案内容]

可用工具：
{tools_info}"""
    
    # 简化的ReAct提示词
    REACT_SIMPLE_PROMPT = """你是一个智能助手。请使用以下格式解决问题：

思考：分析问题并决定下一步
行动：工具名称
行动输入：工具参数（JSON格式）
观察：工具返回结果
...（重复思考-行动-观察）
思考：我现在知道最终答案了
最终答案：答案

可用工具：
{tools_info}

开始！

问题：{question}"""
    
    # 意图识别提示词
    INTENT_RECOGNITION_PROMPT = """分析用户问题的意图和类型。

问题类型：
- 信息查询：用户想了解某些信息
- 数据分析：用户需要对数据进行分析或计算
- 任务执行：用户需要执行某个操作
- 对话交流：普通的对话或闲聊

用户问题：{question}

请分析：
1. 问题类型：
2. 主要意图：
3. 可能需要的工具：
4. 复杂度评估（简单/中等/复杂）："""
    
    # 问题拆解提示词
    PROBLEM_DECOMPOSITION_PROMPT = """将复杂问题拆解为多个简单的子问题。

原始问题：{question}

请将问题拆解为：
1. 子问题1：
   - 描述：
   - 所需工具：
   - 执行顺序：

2. 子问题2：
   - 描述：
   - 所需工具：
   - 执行顺序：

..."""
    
    # 思维链推理提示词
    CHAIN_OF_THOUGHT_PROMPT = """让我们一步步思考这个问题。

问题：{question}

请按照以下步骤推理：
1. 首先，理解问题的核心是什么
2. 然后，识别需要哪些信息或工具
3. 接着，逐步执行必要的操作
4. 最后，综合所有信息得出结论

推理过程："""
    
    # 工具选择提示词
    TOOL_SELECTION_PROMPT = """根据用户问题选择最合适的工具。

可用工具：
{tools_info}

用户问题：{question}

请分析：
1. 问题需要什么类型的信息或操作？
2. 哪个工具最适合解决这个问题？
3. 需要传递什么参数？
4. 是否需要多个工具配合使用？

选择的工具："""
    
    # 错误恢复提示词
    ERROR_RECOVERY_PROMPT = """工具调用失败，请分析原因并尝试其他方法。

原始问题：{question}
失败的工具：{tool_name}
错误信息：{error_message}

请分析：
1. 失败的可能原因是什么？
2. 是否可以使用其他工具或方法？
3. 是否需要调整参数？

建议的下一步行动："""
    
    # 答案综合提示词
    ANSWER_SYNTHESIS_PROMPT = """根据收集到的信息，生成最终答案。

原始问题：{question}

收集到的信息：
{collected_info}

请：
1. 整理和总结收集到的信息
2. 确保答案直接回应原始问题
3. 如果信息不足，明确指出
4. 提供清晰、准确、有帮助的答案

最终答案："""
    
    @staticmethod
    def format_react_prompt(
        question: str,
        tools_info: str,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """格式化ReAct提示词"""
        prompt = PromptTemplates.REACT_SIMPLE_PROMPT.format(
            tools_info=tools_info,
            question=question
        )
        
        if history:
            history_text = "\n\n历史对话：\n"
            for msg in history[-5:]:  # 只包含最近5条
                role = msg.get("role", "")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"
            prompt = history_text + "\n" + prompt
        
        return prompt
    
    @staticmethod
    def format_tools_info(tools: List[Any]) -> str:
        """格式化工具信息"""
        tools_text = ""
        for i, tool in enumerate(tools, 1):
            tools_text += f"\n{i}. {tool.name}\n"
            tools_text += f"   描述：{tool.description}\n"
            
            if hasattr(tool, 'parameters') and tool.parameters:
                tools_text += "   参数：\n"
                for param in tool.parameters:
                    required = "必需" if param.required else "可选"
                    tools_text += f"   - {param.name} ({param.type}, {required}): {param.description}\n"
        
        return tools_text
    
    @staticmethod
    def get_thought_prompt(context: str, question: str) -> str:
        """获取思考提示"""
        return f"""当前上下文：
{context}

问题：{question}

请思考下一步应该做什么："""
    
    @staticmethod
    def get_action_prompt(available_tools: List[str]) -> str:
        """获取行动提示"""
        tools_list = ", ".join(available_tools)
        return f"""可用工具：{tools_list}

请选择一个工具并提供参数：
行动：[工具名称]
行动输入：{{"参数名": "参数值"}}"""
    
    @staticmethod
    def get_final_answer_prompt(question: str, reasoning: str) -> str:
        """获取最终答案提示"""
        return f"""问题：{question}

推理过程：
{reasoning}

请给出最终答案："""
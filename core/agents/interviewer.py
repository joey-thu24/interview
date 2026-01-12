from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re
import random
from core.data.real_questions import get_real_questions

class InterviewerAgent:
    def __init__(self, llm):
        self.llm = llm

    def conduct_interview(self, history, context):
        """
        主面试逻辑控制器 (CoT Deep Thinking)
        :param history: 聊天记录 list
        :param context: dict, 包含 mode, topic, jd
        """
        # 1. 如果是第一次交互 (History 为空或仅有System)，则进行开场
        if not history or len(history) == 0:
            return self._generate_opening(context)

        # 2. 如果最后一条是用户回答，则进行 "评估 + 追问/新题"
        last_msg = history[-1]
        if last_msg.get("role") == "human":
            # 获取用户最后一句回答
            user_answer = last_msg.get("content", "")
            
            # 使用 CoT 深度思考用户的回答
            evaluation = self._evaluate_and_plan(history, context)
            
            return evaluation
        
        return "请继续回答。"

    def _generate_opening(self, context):
        topic = context.get("topic", "通用技术")
        return f"您好，我是您的 AI 面试官。今天我们将进行 {topic} 方向的模拟面试。请准备好后，简单通过打字做一个自我介绍。"

    def _evaluate_and_plan(self, history, context):
        """
        深度评估用户回答，并决定下一步动作
        """
        system_prompt = """你是一位资深、严厉但公正的技术面试官 (Google L5/L6 级别)。
你正在进行一场全中文的模拟面试。

当前上下文:
模式: {mode}
主题: {topic}
岗位描述: {jd}

用户的最后一句回答是针对上一轮问题的。
请按以下步骤进行 **深度思考 (Chain of Thought)**：

1. **深度解析**: 用户的回答是否触及了问题的底层原理？是否有逻辑漏洞？是否只是背诵八股文而没有理解？
2. **评分判定**: 给出一个 0-100 的分数。
3. **决策下一步**: 
    - 如果回答得很浅 -> 追问底层原理 (Follow-up)。
    - 如果回答错误 -> 指出错误并纠正，然后出新题 (New Question)。
    - 如果回答完美 -> 给予肯定，然后出更难的新题 (New Question)。
    - 如果是自我介绍 -> 针对介绍中的亮点进行提问。

**输出要求**:
不要输出思考过程的 JSON，直接以面试官的身份输出 **回复内容**。
回复格式：
[反馈与点评] (请一针见血，不要客套)
[分割线或换行]
[下一个问题] (必须具体、有挑战性)

请保持全中文回复，专业术语可以用英文。
"""
        # 构建 Prompt
        # 截取最近 4 轮对话作为 Context
        history_text = "\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in history[-8:]])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", f"历史对话:\n{history_text}\n\n[面试官请回复]:")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        try:
            response = chain.invoke({
                "mode": context.get("mode", "专项练习"),
                "topic": context.get("topic", "未知"),
                "jd": context.get("jd", "无")
            })
            return response
        except Exception as e:
            return f"（系统错误：{str(e)}）请继续回答..."

    def generate_final_report(self, history):
        """
        生成最终深度总结报告
        """
        system_prompt = """你是一位资深技术专家。面试已结束，请对候选人进行全方位的深度画像。

请进行 **Step-by-Step 思考**：
1. 回顾整个面试过程，候选人在哪些领域（OS/网络/数据库/算法）表现出色？
2. 哪些回答暴露了原理性认知缺失？
3. 沟通是否清晰？逻辑是否严密？

请输出严格的 JSON 格式：
{
    "total_score": 0-100,
    "summary": "深度的综合评价，不少于 100 字，言辞恳切。",
    "strengths": ["亮点1", "亮点2", "亮点3"],
    "weaknesses": ["致命弱点1", "弱点2", "弱点3"],
    "suggestions": ["具体的学习建议1 (例如推荐读什么书)", "建议2", "建议3"]
}

注意：JSON 必须合法，Key 必须用双引号。
"""
        history_text = "\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in history])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", f"面试记录:\n{history_text}\n\n请生成深度报告 (JSON):")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({})
        
        try:
            match = re.search(r"\{[\s\S]*\}", result.strip())
            clean = match.group(0) if match else result
            return json.loads(clean)
        except Exception as e:
            return {
                "total_score": 0, 
                "summary": f"生成报告时发生错误，请重试。错误: {str(e)}", 
                "strengths": [], 
                "weaknesses": [], 
                "suggestions": []
            }

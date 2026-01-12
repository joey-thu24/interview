from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

from core.data.real_questions import get_real_questions
import random

class InterviewerAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_question(self, topic, difficulty="中等", history=[], jd_text=None):
        """
        生成面试题目
        :param jd_text: 可选，JD 内容。如果存在，则基于 JD 出题。
        """
        
        # 1. JD 模式 (优先)
        if jd_text:
            return self._generate_from_jd(jd_text, difficulty, history)
            
        # 2. 真题库模式 (概率触发，例如 70% 概率抽真题，增加惊喜感)
        # 检查历史是否已经问过，避免重复
        asked_questions = [h['content'] for h in history if h['role']=='assistant']
        real_candidates = get_real_questions(topic)
        # 过滤掉已经问过的（简单的字符串包含匹配）
        available_real = [q for q in real_candidates if q['question'] not in str(asked_questions)]
        
        if available_real and random.random() < 0.7:
            # 抽选真题
            selected = random.choice(available_real)
            prefix = f"【🚀 {selected['company']} {selected['year']} 真题】"
            return f"{prefix} {selected['question']}"
            
        # 3. LLM 生成模式 (兜底)
        system_prompt = """你是一位资深的{topic}技术面试官。
请根据候选人的面试历史，提出一个新的、有挑战性的面试题。
难度等级：{difficulty}。

请只输出问题本身，不要包含任何寒暄。
如果历史记录中已经有了类似问题，请换一个角度或换一个知识点。
"""
        # 将历史对话整理为 context string
        # history items are dicts with 'role' and 'content'
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-6:]]) if history else "无"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", f"历史对话：\n{history_text}\n\n请出题：")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"topic": topic, "difficulty": difficulty})

    def _generate_from_jd(self, jd_text, difficulty, history):
        """
        基于 JD 生成定制问题
        """
        system_prompt = """你是一位严厉的面试官。你手里有一份该职位的 JD（职位描述）。
请根据 JD 中的核心要求（关键技术栈、业务场景、加分项），向候选人提出面试问题。

JD 内容：
{jd_text}

难度等级：{difficulty}。
要求：只输出问题本身。问题必须与 JD 紧密相关，考察候选人是否真的匹配该岗位。
"""
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-6:]]) if history else "无"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", f"历史对话：\n{history_text}\n\n请基于 JD 出题：")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"jd_text": jd_text, "difficulty": difficulty})


    def generate_final_report(self, history):
        """
        面试结束后生成综合报告
        """
        system_prompt = """你是一位面试官。面试已结束，请根据以下对话历史，给出一份面试总结报告。
        
请输出 JSON 格式：
- "total_score": 0-100 总分
- "summary": 总体表现评价
- "strengths": [亮点1, 亮点2]
- "weaknesses": [不足1, 不足2]
- "suggestions": [改进建议1, 建议2]
"""
        # 转换历史记录为文本
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", f"面试记录：\n{history_text}\n\n请生成报告。")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({})
        
        import json
        import re
        try:
            match = re.search(r"\{[\s\S]*\}", result.strip())
            clean = match.group(0) if match else result
            return json.loads(clean)
        except:
            return {"summary": "报告生成失败", "error": result}

    def evaluate_response(self, topic, question, user_answer):
        """
        评价用户的回答
        """
        system_prompt = """你是一位公正的面试官。请评价候选人对于问题 "{question}" 的回答。
回答内容："{user_answer}"

请输出一段 JSON，包含：
- "score": 0-100 的评分
- "feedback": 简短的评价（指出亮点和不足）
- "reference": 参考答案要点
- "follow_up": 如果回答还可以，可以给出一个追问问题；如果回答太差，则为空。
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "请评价。")
        ])
        
        # 实际项目中这里应该用 JsonOutputParser，为了演示方便先用 Str处理
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"topic": topic, "question": question, "user_answer": user_answer})
        
        # 简单清洗
        try:
            # 尝试提取 JSON 部分
            match = re.search(r"\{[\s\S]*\}", result.strip())
            if match:
                clean_response = match.group(0)
            else:
                clean_response = result.replace("```json", "").replace("```", "").strip()
            
            return json.loads(clean_response)
        except Exception as e:
            print(f"JSON Parse Error in Interviewer: {e}")
            return {
                "score": 60,
                "feedback": "解析评分失败，但你的回答已被记录。",
                "reference": "无",
                "follow_up": None,
                "raw": result
            }

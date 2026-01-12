from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

class SupervisorAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_daily_plan(self, user_profile, recent_weaknesses=None):
        """
        根据用户画像和历史进度生成今日计划
        :param user_profile: dict, 包含 target_role(目标岗位), days_left(剩余天数), current_level(当前水平)
        :param recent_weaknesses: list, 最近面试暴露的弱点
        """
        
        # 将弱点列表转换为字符串
        weakness_str = "无"
        if recent_weaknesses and len(recent_weaknesses) > 0:
            weakness_str = "; ".join(recent_weaknesses)
        
        system_prompt = """你是一位严厉但负责任的计算机面试学习监督导师。
你的任务是根据学生的目标和剩余时间，制定今天的详细学习计划。

🔥 重点关注：
学生在最近的模拟面试中暴露了以下短板：【{weakness_str}】。
请务必在今天的计划中安排 1-2 个任务来专门复习这些薄弱点。

请输出 JSON 格式，包含以下字段：
- "encouragement": 一句简短的鼓励，**必须明确提到今天要重点复习刚才提到的某个短板**。
- "tasks": 一个列表，包含 3-5 个具体的学习任务。每个任务包含 "topic"(主题), "description"(详细描述), "estimated_time"(预估时间)

学生情况：
目标岗位：{target_role}
距离面试剩余：{days_left} 天
当前水平评估：{current_level}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "请生成今天的学习计划。")
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "target_role": user_profile.get("target_role", "后端工程师"),
                "days_left": user_profile.get("days_left", 30),
                "current_level": user_profile.get("current_level", "初级"),
                "weakness_str": weakness_str
            })
            
            # 使用正则提取 JSON，增强鲁棒性
            import re
            json_match = re.search(r"\{[\s\S]*\}", response.strip())
            
            if json_match:
                clean_response = json_match.group(0)
            else:
                # Fallback: 简单的清洗
                clean_response = response.replace("```json", "").replace("```", "").strip()
                
            return json.loads(clean_response)
        except Exception as e:
            # 打印原始响应以便调试
            print(f"JSON Parse Error: {e}")
            if 'response' in locals():
                print(f"Raw Response: {response}")

            return {
                "encouragement": "系统繁忙，但学习不能停！请复习昨天的错题。",
                "tasks": [{"topic": "复习", "description": "系统暂时无法生成新计划，请自主复习。", "estimated_time": "30min"}],
                "error": str(e)
            }

    def generate_roadmap(self, user_profile):
        """
        生成长期学习路线图
        """
        system_prompt = """你是一位专业的计算机学习规划师。
请根据学生的目标岗位和当前水平，制定一份阶段性的学习路线图（Roadmap）。
距离面试还有 {days_left} 天。

请输出 JSON 格式，包含一个 "phases" 列表，每个阶段包含：
- "phase_name": 阶段名称 (e.g. 基础夯实)
- "duration": 建议天数
- "goals": [目标1, 目标2]
- "key_topics": [知识点1, 知识点2]
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "请生成学习路线图。")
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "target_role": user_profile.get("target_role", "后端工程师"),
                "days_left": user_profile.get("days_left", 30)
            })
            
            # 使用正则提取 JSON
            import re
            json_match = re.search(r"\{[\s\S]*\}", response.strip())
            clean_response = json_match.group(0) if json_match else response
            return json.loads(clean_response)
        except Exception as e:
             return {"phases": [], "error": str(e)}

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

class AnalystAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze_progress(self, sessions, study_stats):
        """
        综合分析面试记录和学习数据
        """
        # 整理面试数据
        session_summary = []
        for s in sessions:
            try:
                # 尝试解析 topics
                # 这里假设 s.topic 是单一主题，为了丰富维度，我们让 llm 归类
                session_summary.append(f"- 主题: {s.topic}, 得分: {s.score}")
            except:
                pass
        
        history_text = "\n".join(session_summary) if session_summary else "暂无面试记录"

        system_prompt = """你是一位计算机教育专家和数据分析师。
请根据学生的面试历史和学习打卡数据，生成一份能力评估报告。

输入数据：
面试记录：
{history_text}

学习数据：
累计打卡天数：{total_days}
任务完成率：{completion_rate:.1f}%

请输出 JSON 格式，包含：
1. "radar_chart": 必须包含以下5个维度的评分 (0-100)：
   - "基础知识": (根据CS基础、网络、OS等表现)
   - "算法能力": (根据算法、数据结构表现)
   - "工程实践": (根据框架、数据库、设计模式表现)
   - "表达逻辑": (根据面试反馈中的沟通表现，若无详细数据则给根据整体预估)
   - "对标匹配度": (相对于目标岗位的匹配程度)
2. "trend_analysis": 一句关于进步趋势的简评。
3. "key_suggestion": 针对当前最弱维度的切实建议。

如果数据不足，请根据现有信息进行合理估算。
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "请开始分析")
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "history_text": history_text,
                "total_days": study_stats.get("total_days", 0),
                "completion_rate": study_stats.get("completion_rate", 0)
            })
            
            # 正则提取 JSON
            match = re.search(r"\{[\s\S]*\}", response.strip())
            clean_str = match.group(0) if match else response
            return json.loads(clean_str)
        except Exception as e:
            # Fallback 数据
            return {
                "radar_chart": {"基础知识": 60, "算法能力": 60, "工程实践": 60, "表达逻辑": 60, "对标匹配度": 60},
                "trend_analysis": "数据不足，暂无法分析趋势。",
                "key_suggestion": "请多进行几次模拟面试以积累数据。",
                "error": str(e)
            }

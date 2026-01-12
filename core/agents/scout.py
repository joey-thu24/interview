from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import random

class ScoutAgent:
    def __init__(self, llm):
        self.llm = llm

    def hunt_jobs(self, role_keyword):
        """
        模拟岗位嗅探功能。
        由于无法直接联网爬取实时招聘网站，这里我们返回精选的高质量JD模拟数据。
        这些数据结构模拟了真实爬虫的结果。
        """
        # 模拟的高质量JD库
        mock_jobs = [
            {
                "company": "ByteDance (TikTok)",
                "title": "后端开发专家 (Golang/Python)",
                "salary": "35k-65k·16薪",
                "location": "北京/上海",
                "tags": ["高并发", "国际化", "核心业务"],
                "content": """
                岗位职责：
                1. 负责抖音/TikTok核心业务后端研发；
                2. 参与高并发架构设计与优化，保障系统稳定性；
                3. 解决海量数据下的存储与计算难题。
                任职要求：
                1. 3年以上后端开发经验，精通 Go/Python/Java 任一语言；
                2. 深入理解 MySQL、Redis、MQ 等中间件原理；
                3. 有大规模微服务架构经验者优先；
                4. 具备优秀的系统设计能力和代码品味。
                """
            },
            {
                "company": "Tencent (WeChat)",
                "title": "微信支付-后台开发工程师",
                "salary": "30k-55k",
                "location": "深圳/广州",
                "tags": ["金融级", "国民应用", "C++"],
                "content": """
                工作职责：
                1. 负责微信支付核心交易系统的设计与实现；
                2. 确保金融级系统的资金安全与数据一致性；
                3. 持续优化系统性能，应对春节红包等流量洪峰。
                岗位要求：
                1. 扎实的计算机基础，精通 C++/Java；
                2. 熟悉 Linux 系统编程、网络编程；
                3. 对分布式一致性协议（Paxos/Raft）有深入理解；
                4. 严谨的逻辑思维，对数据敏感。
                """
            },
            {
                "company": "Alibaba (Cloud)",
                "title": "阿里云-弹性计算研发专家",
                "salary": "40k-70k",
                "location": "杭州",
                "tags": ["云计算", "底层技术", "虚拟化"],
                "content": """
                职位描述：
                1. 负责阿里云 ECS 弹性计算控制面研发；
                2. 攻克云计算资源调度、异构计算等技术难题；
                3. 参与开源社区贡献 (K8s, OpenStack equivalent)。
                职位要求：
                1. 5年以上研发经验，熟悉云计算体系架构；
                2. 精通 Java/Go，熟悉 Docker/K8s 原理；
                3. 具备优秀的抽象设计能力，追求极致的技术深度。
                """
            },
             {
                "company": "Mihoyo (米哈游)",
                "title": "游戏服务器后端 (Global)",
                "salary": "30k-60k·16薪",
                "location": "上海",
                "tags": ["二次元", "全球服", "Golang"],
                "content": """
                职责：
                1. 负责米哈游全球化游戏服务器后端逻辑开发；
                2. 优化全球同服的网络架构。
                要求：
                1. 热爱游戏，有丰富的游戏游玩经历；
                2. 熟悉 TCP/UDP 网络协议，熟悉 Protobuf；
                3. 熟悉 Golang 开发，能够编写高性能网络服务。
                """
            }
        ]
        
        # 简单过滤
        results = [j for j in mock_jobs if role_keyword.lower() in j['title'].lower() or role_keyword.lower() in j['content'].lower()]
        
        # 如果没搜到，为了演示，随机返回几个
        if not results:
            results = random.sample(mock_jobs, 2)
            
        return results

    def analyze_jd(self, jd_text):
        """
        利用 LLM 对 JD 进行深度剖析，减少信息差。
        分析维度：
        1. 真实薪资估算 (Based on market data knowledge in LLM)
        2. 潜在坑点/红线 (PUA 预警, 维护老代码, 只有运维杂活等)
        3. 简历匹配策略 (如何修改简历来命中该 JD)
        4. 面试难度预估
        """
        system_prompt = """你是一位互联网职场内幕专家。你的任务是分析给定的职位描述 (JD)，挖掘字面意思背后的"内幕信息"，帮助求职者减少信息差。

请输出 JSON 格式，包含以下字段：
- estimated_salary: 针对该岗位的一线城市市场薪资预估范围（如果JD未写）。
- tech_stack_keywords: 核心技术栈关键词列表。
- red_flags: List[str], 潜在的坑或风险点（例如 "抗压能力强" 可能暗示 996，"维护旧系统" 暗示技术栈老旧）。如果没有明显坑点，返回空列表。
- resume_tips: List[str], 针对该JD，简历上应该重点突出的 3 个亮点建议。
- difficulty_score: 1-100 的整数，预估面试难度。
- insider_comment: 一句简短犀利的内幕点评 (例如 "核心部门，值得去", "可能是外包坑，慎重")。

注意：输出必须是纯 JSON 字符串，不要包含 markdown 标记。
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", f"请分析以下这篇 JD：\n\n{jd_text}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            res = chain.invoke({})
            # 清理可能存在的 markdown code block
            cleaned = res.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception as e:
            return {
                "error": f"分析失败: {str(e)}",
                "estimated_salary": "无法评估",
                "red_flags": [],
                "resume_tips": ["请仔细阅读 JD"],
                "difficulty_score": 50,
                "insider_comment": "AI 暂时无法分析此 JD"
            }

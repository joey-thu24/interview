# 🎓 AI Interview Assistant (AI 面试官)

这是一个基于 **DeepSeek (SiliconFlow)** 大模型驱动的智能面试辅助系统。它不仅仅是一个聊天机器人，而是具备 **"产品经理思维"** 的求职利器。我们通过多 Agent 协作（Supervisor, Interviewer, Analyst），为你提供从 **JD 解析**、**真题模拟** 到 **能力分析** 的全流程闭环服务。

## 🚀 核心亮点 (Killer Features)

### 1. 🎯 JD 定向突击 (JD Assault Mode)
别再盲目刷题了！直接粘贴目标岗位的 **JD (职位描述)**，系统会立即分析该岗位的核心硬技能（Hard Skills）和软技能（Soft Skills），并以此为核心对你进行高强度的针对性面试。
> *场景：明天要去面试某大厂的后端岗位，把 JD 扔进去，立刻生成针对性考题。*

### 2. 🏛️ 大厂真题题库 (Real Question Database)
内置了经过筛选的互联网大厂（字节跳动、腾讯、阿里等）高频面试真题。在非 JD 模式下，面试官 Agent 会结合你的期望岗位，从题库中抽取 **真实出现过** 的题目进行考核，而非 LLM 胡编乱造的问题。

### 3. 🧠 智能长短期规划 (Supervisor Agent)
不再是简单的 To-Do List。Supervisor Agent 会根据你每天的练习表现、薄弱环节（如 "Redis 持久化" 回答不佳），自动调整第二天的复习计划，形成 **"练习-反馈-再复习"** 的有效闭环。

### 4. 📊 深度能力分析 (Analyst Dashboard)
基于你的历史对话，自动生成能力雷达图和趋势分析。
- **面试表现打分**：从技术深度、逻辑清晰度、沟通能力多维度评分。
- **趋势追踪**：直观看到自己是否在变强。

## 🛠️ 技术栈 (Tech Stack)

- **LLM/Model**: DeepSeek-V2.5 / DeepSeek-V3 (via SiliconFlow API)
- **Framework**: Python 3.10+
- **Frontend**: Streamlit (构建快速交互式 Web UI)
- **Backend Logic**: LangChain (Agent 编排, Prompt 管理)
- **Database**: SQLite + SQLAlchemy (轻量级数据持久化，无论是对话记录还是用户计划)
- **Utils**: Regex-based JSON Parser (解决大模型输出格式不稳定的鲁棒性方案)

## 📂 项目结构

```
root/
├── app/
│   ├── main.py              # Streamlit 主入口 (UI & 交互逻辑)
│   └── components/          # UI 组件 (Sidebar, Chat bubbles)
├── core/
│   ├── agents/              # 核心智能体
│   │   ├── supervisor.py    # 规划与监督 Agent
│   │   ├── interviewer.py   # 面试官 Agent (含 JD 解析 & 真题逻辑)
│   │   └── analyst.py       # 数据分析 Agent
│   ├── data/                # 静态数据资产
│   │   ├── real_questions.py# 大厂真题库
│   │   └── templates.py     # 黄金学习路线模板
│   ├── llm.py               # LLM 初始化与 SiliconFlow 配置
│   └── config.py            # 全局配置
├── database/
│   ├── crud.py              # 数据库增删改查
│   └── models.py            # SQLAlchemy 数据模型
├── requirements.txt         # 项目依赖
└── .env                     # 环境变量 (API Key)
```

## ⚡ 快速开始 (Quick Start)

### 1. 环境准备
确保已安装 Python 3.10+。

```bash
# 1. 克隆项目或下载代码
git clone ...

# 2. 创建并激活虚拟环境 (推荐)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key
在项目根目录创建一个 `.env` 文件，填入你的 SiliconFlow (硅基流动) API Key：

```ini
OPENAI_API_KEY=sk-xxxxxx  # 你的 SiliconFlow API Key
OPENAI_API_BASE=https://api.siliconflow.cn/v1
```

### 3. 启动应用
```bash
streamlit run app/main.py
```
启动后，浏览器会自动打开 `http://localhost:8501`。

## 📅 当前进度 (Current Status)

- [x] **基础架构搭建**: 数据库连接、Agent 基类、Streamlit 框架。
- [x] **三大核心 Agent**:
    - **Supervisor**: 具备记忆功能的每日计划生成。
    - **Interviewer**: 支持 **JD 模式** 和 **真题模式** 的混合面试逻辑。
    - **Analyst**: 基于历史数据生成评分报告。
- [x] **产品化特性**:
    - 职位描述 (JD) 解析器。
    - 预置 "后端/算法" 黄金学习路线模板。
    - 错误恢复机制 (Regex JSON Parser)。

## 🔜 以此为基础，你可以继续：
1. **完善前端 UI**: 美化聊天界面，增加语音输入/输出。
2. **扩展题库**: 增加更多技术栈（前端、测试、运维）的真题。
3. **RAG 增强**: 允许上传 PDF 简历，结合简历内容进行提问。

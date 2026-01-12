import streamlit as st
import os
import sys

# 添加项目根目录到 system path，以便导入 core 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 数据库初始化
from database.models import init_db, SessionLocal
from database import crud

# UI Components
from app.components.ui import load_custom_css, render_header
from app.components.charts import render_radar_chart

@st.cache_resource
def init_database():
    init_db()

init_database()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

# 尝试导入核心模块
try:
    from core.llm import get_llm
    from core.agents.supervisor import SupervisorAgent
    from core.agents.interviewer import InterviewerAgent
    from core.agents.analyst import AnalystAgent
    from core.agents.scout import ScoutAgent # New Agent
    from core.data.templates import get_template_names, get_template
except ImportError:
    st.error("核心模块导入失败，请检查目录结构或依赖。")

st.set_page_config(
    page_title="AI 面试助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 加载自定义样式
load_custom_css()
# 自定义头部
render_header()

# st.title("🎓 AI 面试辅助学习助手") # Replaced by render_header

# Sidebar 设置
st.sidebar.title("用户信息设置")
target_role = st.sidebar.text_input("目标岗位", "后端开发工程师")
days_left = st.sidebar.number_input("距离面试天数", 1, 365, 30)
current_level = st.sidebar.selectbox("当前水平", ["转行小白", "应届入门", "有经验", "专家"])

# 实例化 LLM 和 Agent
@st.cache_resource
def load_agents():
    try:
        llm = get_llm()
        return SupervisorAgent(llm), InterviewerAgent(llm), AnalystAgent(llm), ScoutAgent(llm)
    except Exception as e:
        return None, None, None, None

supervisor, interviewer, analyst, scout = load_agents()

# 主界面选项卡
tab1, tab2, tab3, tab4 = st.tabs(["📅 学习监督", "🤖 模拟面试", "📊 进度分析", "🔭 机会嗅探"])

with tab1:
    st.header(f"学习规划与监督 ({target_role})")
    
    if supervisor is None:
        st.warning("⚠️ 未检测到有效配置 (OpenAI API key)。请在 .env 文件中配置。")
    else:
        db = get_db()
        
        # Sub-tabs for Planning and Supervision
        plan_tab1, plan_tab2 = st.tabs(["📋 今日监督", "🗺️ 长期规划"])
        
        # --- 今日监督 ---
        with plan_tab1:
            # 1. 检查今日是否已有计划
            today_plan = crud.get_today_plan(db)
            
            if today_plan:
                 st.success(f"💡 {today_plan.encouragement}")
                 st.subheader("今日待办")
                 
                 tasks = today_plan.content if today_plan.content else []
                 updated = False
                 for idx, task in enumerate(tasks):
                     is_done = task.get("status") == "completed"
                     new_status = st.checkbox(
                         f"**{task['topic']}** : {task['description']} ({task['estimated_time']})", 
                         value=is_done,
                         key=f"plan_task_{today_plan.id}_{idx}"
                     )
                     
                     if new_status != is_done:
                         tasks[idx]["status"] = "completed" if new_status else "pending"
                         updated = True
                
                 if updated:
                     crud.update_plan_status(db, today_plan.id, tasks)
                     st.rerun() 
                     
                  # 打卡进度条
                 completed_count = sum(1 for t in tasks if t.get("status") == "completed")
                 total_count = len(tasks)
                 if total_count > 0:
                     progress = completed_count / total_count
                     st.progress(progress, text=f"今日进度: {int(progress*100)}%")
            else:
                st.info("👋 早安！新的一天开始了。")
                if st.button("生成今日学习计划", type="primary"):
                    
                    # 关键修改：获取最近的弱点
                    weaknesses = crud.get_recent_weaknesses(db)
                    
                    if weaknesses:
                        st.caption(f"🎯 检测到最近的短板: {', '.join(weaknesses[:2])}...")
                        
                    with st.spinner("Agent 正在分析你的面试表现并规划今日任务..."):
                        user_profile = {
                            "target_role": target_role,
                            "days_left": days_left,
                            "current_level": current_level
                        }
                        plan = supervisor.generate_daily_plan(user_profile, recent_weaknesses=weaknesses)
                    
                    if "error" in plan:
                        st.error(f"生成失败: {plan.get('error')}")
                    else:
                        tasks_with_status = []
                        for t in plan.get("tasks", []):
                            t["status"] = "pending"
                            tasks_with_status.append(t)
                            
                        crud.create_daily_plan(db, tasks_with_status, plan.get("encouragement"))
                        st.rerun()

        # --- 长期规划 ---
        with plan_tab2:
            st.subheader("阶段性学习路线图")
            
            # 1. 模板选择区 (MVP的核心优化：解决冷启动空白问题)
            st.markdown("#### 🛠️ 快速启动：选择黄金路线模板")
            selected_template_name = st.selectbox(
                "选择预置的专家路线图 (推荐)", 
                ["请选择..."] + get_template_names()
            )
            
            if selected_template_name != "请选择...":
                if st.button("应用此模板"):
                    template_data = get_template(selected_template_name)
                    st.session_state.roadmap = template_data
                    st.success(f"已加载《{selected_template_name}》专家路线！")
                    st.rerun()

            st.divider()

            if "roadmap" not in st.session_state:
                st.session_state.roadmap = None
                
            if st.session_state.roadmap:
                roadmap = st.session_state.roadmap
                if "error" in roadmap:
                     st.error(roadmap['error'])
                else:
                    for phase in roadmap.get("phases", []):
                        with st.expander(f"📌 {phase['phase_name']} ({phase['duration']})", expanded=True):
                            st.write("**目标:** " + ", ".join(phase['goals']))
                            # 这里可以把由 AI 生成的，和模板固定的结合起来
                            st.info("**核心考点:** " + ", ".join(phase['key_topics']))
            else:
                st.info("👈 请在上方选择一个模板，或点击下方按钮让 AI 从零规划")
                
            if st.button("让 AI 根据当前情况重新定制路线"):
                with st.spinner("正在规划长期路线..."):
                     user_profile = {
                        "target_role": target_role,
                        "days_left": days_left
                    }
                     st.session_state.roadmap = supervisor.generate_roadmap(user_profile)
                     st.rerun()
        
        db.close()

with tab2:
    st.header("🤖 模拟面试实战")
    
    if interviewer is None:
        st.warning("请配置 API Key")
    else:
        # Session State
        if "interview_session_id" not in st.session_state:
            st.session_state.interview_session_id = None
        
        # 布局：左侧控制，右侧聊天
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("面试设置")
            
            # --- 模式选择 (New!) ---
            mode = st.radio("面试模式", ["📚 专项练习", "🔥 JD 突击"], index=0)
            
            jd_text = None
            topic = "General" # Default
            
            if mode == "📚 专项练习":
                topic = st.selectbox("面试主题", ["计算机网络", "操作系统", "Python 基础", "MySQL", "系统设计"])
            else:
                st.info("请将招聘软件上的职位描述(JD)粘贴到下方：")
                jd_text = st.text_area("JD 内容", height=150, placeholder="例如：熟练掌握 K8s, 有高并发经验...")
                topic = "JD 定制" # 存入数据库时的 topic 标记
            
            difficulty = st.select_slider("难度", options=["简单", "中等", "困难"])
            
            # 开始按钮
            if st.button("🚀 开始新面试", type="primary"):
                if mode == "🔥 JD 突击" and not jd_text:
                    st.error("请先粘贴 JD 内容！")
                else:
                    db = get_db()
                    session = crud.create_interview_session(db, topic)
                    # 如果由于 JD 模式，我们可以把 JD 存入 session 的某个字段，或者第一条 system message
                    # 这里简化处理：存入 session_state
                    st.session_state.current_jd = jd_text if mode == "🔥 JD 突击" else None
                    
                    st.session_state.interview_session_id = session.id
                    db.close()
                    st.rerun()
                
            # 结束按钮
            if st.session_state.interview_session_id:
                st.divider()
                if st.button("🏁 结束面试 & 生成报告"):
                     # 触发生成报告逻辑
                     st.session_state.show_report = True
                     st.rerun()

        with col2:
            if st.session_state.get("show_report", False):
                # 显示报告模式
                st.subheader("📊 面试总结报告")
                db = get_db()
                session = db.query(crud.InterviewSession).get(st.session_state.interview_session_id)
                
                if not session.feedback:
                    with st.spinner("正在分析面试表现..."):
                         report = interviewer.generate_final_report(session.messages)
                         # 存入数据库 (简化处理，直接存feedback字段)
                         import json
                         crud.update_session_feedback(db, session.id, report.get("total_score", 0), json.dumps(report))
                         session = db.query(crud.InterviewSession).get(session.id)
                
                # 展示报告
                import json
                try:
                    rep = json.loads(session.feedback)
                    st.metric("综合得分", rep.get("total_score"))
                    st.info(rep.get("summary"))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.success("Bests (亮点)")
                        for s in rep.get("strengths", []):
                            st.write(f"- {s}")
                    with c2:
                        st.error("To Improve (不足)")
                        for w in rep.get("weaknesses", []):
                            st.write(f"- {w}")
                            
                    st.warning("**改进建议**")
                    for sug in rep.get("suggestions", []):
                        st.write(f"👉 {sug}")
                        
                except:
                    st.error("报告加载失败")
                    
                if st.button("返回面试"):
                    st.session_state.show_report = False
                    st.rerun()
                
                db.close()
                
            elif st.session_state.interview_session_id:
                # 正常面试聊天模式
                db = get_db()
                session = db.query(crud.InterviewSession).get(st.session_state.interview_session_id)
                
                # 显示历史对话
                chat_container = st.container(height=500)
                messages = session.messages if session.messages else []
                
                with chat_container:
                     for msg in messages:
                        is_ai = msg["role"] == "assistant"
                        with st.chat_message(msg["role"], avatar="🤖" if is_ai else "🧑‍💻"):
                            content = msg["content"]
                            # 尝试美化反馈部分 (简单的解析逻辑)
                            if is_ai and "---SEPARATOR---" in content:
                                parts = content.split("---SEPARATOR---")
                                if len(parts) > 1:
                                    feedback_part = parts[0].strip()
                                    question_part = parts[1].strip()
                                    
                                    # 渲染反馈为折叠区域，避免刷屏
                                    with st.expander("🧐 查看上一题点评", expanded=False):
                                        st.markdown(feedback_part)
                                    st.markdown(question_part)
                                else:
                                    st.markdown(content)
                            elif is_ai and "**面试官反馈**" in content:
                                # Fallback for old messages or partials
                                st.markdown(content)
                            else:
                                st.markdown(content)
                
                # 自动流转逻辑
                if not messages:
                    # Case 0: 刚开始，AI先说话
                    with st.spinner("面试官正在准备题目..."):
                         # 检查 session_state 是否有 current_jd
                         current_jd = st.session_state.get("current_jd")
                         # 这里的 topic 应该是当前 session 的 topic，而不是左侧 selectbox 的（因为 session 可能是历史的）
                         # 但为了简单，先从 DB 取出的 session.topic 一般是准确的
                         
                         q = interviewer.generate_question(session.topic, difficulty, jd_text=current_jd)
                         crud.add_message_to_session(db, session.id, "assistant", q)
                         st.rerun()
                
                last_role = messages[-1]["role"] if messages else None
                
                if last_role == "user":
                    # Case 1: 用户刚回答完 -> AI 评价并出新题
                    # ...
                    
                    with st.spinner("面试官正在记录并思考..."):
                        last_user_msg = messages[-1]["content"]
                        last_ai_q = messages[-2]["content"] if len(messages)>=2 else ""
                        
                        # 1. 获取评价
                        eval_res = interviewer.evaluate_response(session.topic, last_ai_q, last_user_msg)
                        
                        # 2. 构造回复 (点评 + 下一题)
                        feedback_str = f"> **面试官反馈**: {eval_res.get('feedback')}\n\n"
                        
                        if eval_res.get("follow_up"):
                             next_q = f"{feedback_str}---SEPARATOR---\n**追问**：{eval_res.get('follow_up')}"
                        else:
                             # 同样传入 jd
                             current_jd = st.session_state.get("current_jd")
                             new_q = interviewer.generate_question(session.topic, difficulty, history=messages, jd_text=current_jd)
                             next_q = f"{feedback_str}---SEPARATOR---\n**下一题**：\n{new_q}"
                        
                        crud.add_message_to_session(db, session.id, "assistant", next_q)
                        st.rerun()
                
                # 用户输入区
                if prompt := st.chat_input("请输入回答..."):
                    crud.add_message_to_session(db, session.id, "user", prompt)
                    st.rerun()
                
                db.close()
            else:
                st.info("👈 请在左侧选择主题并点击 '开始新面试'")

with tab3:
    st.header("📊 进度与能力分析")
    
    if analyst is None:
         st.warning("请配置 API Key")
    else:
        db = get_db()
        
        # 1. 基础统计
        stats = crud.get_study_stats(db)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("累计学习天数", f"{stats['total_days']} 天")
        with c2:
            st.metric("任务完成率", f"{stats['completion_rate']:.1f}%")
        with c3:
            finished_sessions = crud.get_all_finished_sessions(db)
            st.metric("完成面试场次", f"{len(finished_sessions)} 场")
            
        st.divider()
        
        # 2. AI 深度分析
        if st.button("🔄 生成/更新 能力评估报告"):
            with st.spinner("分析师正在查阅你的所有档案..."):
                report = analyst.analyze_progress(finished_sessions, stats)
                st.session_state.analysis_report = report
        
        if "analysis_report" in st.session_state:
            report = st.session_state.analysis_report
            
            # 雷达图数据准备
            radar_data = report.get("radar_chart", {})
            if radar_data:
                st.subheader("能力维度评分")
                render_radar_chart(radar_data)
            
            st.info(f"📈 **趋势分析**: {report.get('trend_analysis')}")
            st.success(f"💡 **核心建议**: {report.get('key_suggestion')}")
            
        else:
             st.info("点击按钮开始分析数据")
             
        db.close()

with tab4:
    st.header("🔭 机会嗅探 & 岗位情报分析")
    st.markdown("这里是 **信息差粉碎机**。我们会帮你找到高质量 JD，并利用 AI 挖掘其背后的真实薪资、潜在坑点和通关秘籍。")
    
    if scout is None:
        st.warning("⚠️ Agent 未就绪")
    else:
        # Search Box
        col1, col2 = st.columns([3, 1])
        with col1:
            search_kw = st.text_input("输入你想寻找的方向 (例如: Golang, 推荐算法, 外企)", "Golang")
        with col2:
            st.write("") 
            st.write("")
            do_search = st.button("🔍 开始嗅探", type="primary")
            
        if "scout_results" not in st.session_state:
            st.session_state.scout_results = []
            
        if do_search:
            with st.spinner(f"正在全网探测 '{search_kw}' 相关的高质量机会..."):
                results = scout.hunt_jobs(search_kw)
                st.session_state.scout_results = results
                
        # Display Results
        if st.session_state.scout_results:
            st.subheader(f"找到 {len(st.session_state.scout_results)} 个精选机会")
            
            for idx, job in enumerate(st.session_state.scout_results):
                with st.expander(f"🏢 {job['company']} | {job['title']} | {job['salary']}"):
                    st.write(f"📍 **地点**: {job['location']}")
                    st.write(f"🏷️ **标签**: {', '.join(job['tags'])}")
                    st.caption("📜 职位描述摘要:")
                    st.text(job['content'].strip())
                    
                    # Analysis Button
                    btn_key = f"analyze_btn_{idx}"
                    if st.button("🕵️‍♂️ 揭秘此岗位 (AI 深度分析)", key=btn_key):
                        with st.spinner("正在调用 Insider Agent 进行背景调查..."):
                            analysis = scout.analyze_jd(job['content'])
                            
                            st.markdown("### 🕵️‍♂️ 侦探报告")
                            
                            # 2 columns for quick stats
                            ac1, ac2, ac3 = st.columns(3)
                            with ac1:
                                st.metric("💰 真实薪资预估", analysis.get('estimated_salary', 'N/A'))
                            with ac2:
                                diff = analysis.get('difficulty_score', 50)
                                color = "red" if diff > 80 else "orange" if diff > 50 else "green"
                                st.markdown(f"**面试难度**: :{color}[{diff}/100]")
                            with ac3:
                                st.markdown(f"**毒舌点评**: *{analysis.get('insider_comment')}*")
                            
                            st.divider()
                            
                            # Red Flags
                            if analysis.get('red_flags'):
                                st.error("🚩 **风险预警 (Red Flags)**")
                                for flag in analysis['red_flags']:
                                    st.write(f"- {flag}")
                            else:
                                st.success("✅ 未发现明显深坑")
                                
                            # Resume Tips
                            st.info("📝 **简历修改建议 (Resume Tips)**")
                            for tip in analysis.get('resume_tips', []):
                                st.write(f"👉 {tip}")

# 底部简单的 Dashboard 概览
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="连续打卡天数", value="3 天", delta="1")
with col2:
    st.metric(label="已完成模拟面试", value="5 场")
with col3:
    st.metric(label="综合能力评分", value="A-", delta="up")

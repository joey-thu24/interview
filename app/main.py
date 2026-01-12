import streamlit as st
import sys
import os
import json

# Path hack
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.models import init_db, SessionLocal, InterviewSession
from core.auth import init_admin_user, get_user_by_username
from database import crud
from core.agents.interviewer import InterviewerAgent
from core.llm import get_llm
from components.ui import load_custom_css

# --- Page Config ---
st.set_page_config(page_title="AI 面试官", page_icon="🤖", layout="wide")
load_custom_css()

# --- Auto Login & Admin Setup ---
if "logged_in" not in st.session_state:
    # Initialize DB and Admin User
    try:
        init_db()
        db = SessionLocal()
        init_admin_user(db)
        
        # Auto-login as admin
        admin_user = get_user_by_username(db, "admin")
        if admin_user:
            st.session_state.logged_in = True
            st.session_state.user_id = admin_user.id
            st.session_state.username = admin_user.username
        db.close()
    except Exception as e:
        st.error(f"System Init Failed: {e}")

# --- Resources ---
def get_db():
    return SessionLocal()

@st.cache_resource
def get_interviewer():
    try:
        return InterviewerAgent(get_llm())
    except:
        return None

interviewer = get_interviewer()

# --- State ---
if "interview_session_id" not in st.session_state:
    st.session_state.interview_session_id = None
if "current_jd" not in st.session_state:
    st.session_state.current_jd = None

# --- Main Interface ---

# Logic: Setup vs Chat
if not st.session_state.interview_session_id:
    # ==========================================
    # Phase 1: Setup Screen (Mobile Friendly)
    # ==========================================
    st.markdown("## 🤖 AI 模拟面试官")
    st.info("👋 欢迎！我是你的专属面试教练。请在下方配置面试环境，随后我们将开始一对一的深度对练。")
    
    with st.container(border=True):
        st.subheader("🎯 面试配置")
        
        mode = st.radio("选择模式", ["专项练习", "JD 模拟"], horizontal=True)
        
        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.select_slider("难度等级", ["简单", "中等", "困难"], value="中等")
        
        topic = "计算机网络"
        jd_text = None
        
        if mode == "专项练习":
            with col2:
                topic = st.selectbox("核心知识点", ["计算机网络", "操作系统", "MySQL", "Redis", "Python", "Golang", "Java", "系统设计", "大模型基础"])
        else:
            jd_text = st.text_area("📄 粘贴职位描述 (JD)", height=150, placeholder="请在此粘贴你想要应聘的岗位 JD，我会根据要求定制问题...")
            topic = "JD 定制"

        st.write("") # Spacer
        if st.button("🚀 开始面试", type="primary", use_container_width=True):
            if mode == "JD 模拟" and not jd_text:
                st.error("请务必填写 JD 内容")
            else:
                db = get_db()
                sess = crud.create_interview_session(db, st.session_state.user_id, topic)
                st.session_state.interview_session_id = sess.id
                st.session_state.current_jd = jd_text
                db.close()
                st.rerun()

else:
    # ==========================================
    # Phase 2: Chat Interface
    # ==========================================
    
    # Sidebar Controls
    with st.sidebar:
        st.subheader("控制台")
        if st.button("🏁 结束并生成报告", type="primary", use_container_width=True):
            st.session_state.show_report = True
            st.rerun()
            
        st.divider()
        st.caption("如果要切换话题，请先结束当前面试。")
        if st.button("返回首页"):
             st.session_state.interview_session_id = None
             st.rerun()
    
    # Report View
    if st.session_state.get("show_report", False):
        st.title("📑 面试评估报告")
        db = get_db()
        sess = db.get(InterviewSession, st.session_state.interview_session_id)
        
        if not sess.feedback and interviewer:
            with st.spinner("🧠 面试官正在深度复盘整场面试..."):
                rep = interviewer.generate_final_report(sess.messages)
                crud.update_session_feedback(db, sess.id, rep.get("total_score", 0), json.dumps(rep))
                sess = db.get(InterviewSession, sess.id)
        
        if sess.feedback:
            try:
                data = json.loads(sess.feedback)
                
                # Score Card
                c1, c2, c3 = st.columns(3)
                c1.metric("最终得分", data.get("total_score"))
                c2.metric("对话轮次", int(len(sess.messages)/2))
                
                st.info(f"**综合评价**: {data.get('summary')}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                     st.success("✅ 亮点 (Strengths)")
                     for i in data.get("strengths", []): st.write(f"- {i}")
                with col_b:
                     st.error("⚠️ 不足 (Weaknesses)")
                     for i in data.get("weaknesses", []): st.write(f"- {i}")
                
                st.markdown("### 💡 进阶建议")
                for s in data.get("suggestions", []): st.write(f"👉 {s}")

            except:
                st.error("报告解析失败")
        
        if st.button("⬅️ 开始新一轮面试", use_container_width=True):
             st.session_state.show_report = False
             st.session_state.interview_session_id = None
             st.rerun()
             
        db.close()

    # Active Chat
    else:
        st.subheader("正在面试中...")
        
        db = get_db()
        sess = db.get(InterviewSession, st.session_state.interview_session_id)
        msgs = sess.messages if sess.messages else []
        
        # Chat Container
        chat_container = st.container()
        
        with chat_container:
            for m in msgs:
                is_ai = m["role"] == "assistant" or m["role"] == "ai"
                avatar = "🤖" if is_ai else "🧑‍💻"
                with st.chat_message(m["role"], avatar=avatar):
                    st.write(m["content"])
        
        # AI Turn
        if not msgs or msgs[-1]["role"] == "human" or msgs[-1]["role"] == "user":
             if interviewer:
                 with st.chat_message("assistant", avatar="🤖"):
                     with st.spinner("面试官思考中..."):
                         # Context for AI
                         context = {
                             "mode": "通用", # Simplified for now
                             "topic": sess.topic,
                             "jd": st.session_state.current_jd
                         }
                         
                         response = interviewer.conduct_interview(msgs, context)
                         st.write(response)
                         
                         # Save to DB
                         crud.add_message_to_session(db, sess.id, "ai", response)
                         # Rerun to update state
                         st.rerun()

        # User Input
        if prompt := st.chat_input("请输入你的回答..."):
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(prompt)
            crud.add_message_to_session(db, sess.id, "human", prompt)
            st.rerun()
            
        db.close()

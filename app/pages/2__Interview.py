import streamlit as st
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database.models import SessionLocal, InterviewSession
from database import crud
from core.agents.interviewer import InterviewerAgent
from core.llm import get_llm
from components.ui import load_custom_css

st.set_page_config(page_title="模拟面试", page_icon="", layout="wide")
load_custom_css()

# --- Login Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("请先在主页登录。")
    st.info("前往 [主页](/)")
    st.stop()

def get_db():
    return SessionLocal()

@st.cache_resource
def get_interviewer():
    try:
        return InterviewerAgent(get_llm())
    except:
        return None

interviewer = get_interviewer()

st.title(" 模拟面试")

if "interview_session_id" not in st.session_state:
    st.session_state.interview_session_id = None
if "current_jd" not in st.session_state:
    st.session_state.current_jd = None

# Layout
col_conf, col_chat = st.columns([1, 3])

with col_conf:
    st.subheader(" 面试设置")
    mode = st.radio("模式", ["专项练习", "JD 模拟"], index=0)
    
    topic = "计算机网络"
    jd_text = None
    
    if mode == "专项练习":
        topic = st.selectbox("选择知识点", ["计算机网络", "操作系统", "MySQL", "Redis", "Python", "Golang", "Java", "系统设计", "大模型基础"])
    else:
        topic = "JD 定制" 
        jd_text = st.text_area("粘贴职位描述 (JD)", height=200, placeholder="在此处粘贴职位描述...")
    
    difficulty = st.select_slider("难度", ["简单", "中等", "困难"], value="中等")
    
    if st.button(" 开始面试", type="primary", use_container_width=True):
        if mode == "JD 模拟" and not jd_text:
            st.error("请先输入职位描述")
        else:
            db = get_db()
            sess = crud.create_interview_session(db, st.session_state.user_id, topic)
            st.session_state.interview_session_id = sess.id
            st.session_state.current_jd = jd_text
            db.close()
            st.rerun()

    if st.session_state.interview_session_id:
        st.divider()
        if st.button(" 结束并生成报告", use_container_width=True):
            st.session_state.show_report = True
            st.rerun()

with col_chat:
    if st.session_state.get("show_report", False):
        st.subheader(" 面试评估报告")
        db = get_db()
        sess = db.query(InterviewSession).get(st.session_state.interview_session_id)
        
        if not sess.feedback and interviewer:
            with st.spinner("AI 面试官正在整理面试笔记..."):
                rep = interviewer.generate_final_report(sess.messages)
                crud.update_session_feedback(db, sess.id, rep.get("total_score", 0), json.dumps(rep))
                sess = db.query(InterviewSession).get(sess.id)
        
        if sess.feedback:
            try:
                data = json.loads(sess.feedback)
                c1, c2 = st.columns(2)
                c1.metric("最终得分", data.get("total_score"))
                st.info(data.get("summary"))
                
                col_a, col_b = st.columns(2)
                with col_a:
                     st.success("亮点 (Pros)")
                     for i in data.get("strengths", []): st.write(f"- {i}")
                with col_b:
                     st.error("不足 (Cons)")
                     for i in data.get("weaknesses", []): st.write(f"- {i}")
            except:
                st.error("报告解析失败")
        
        if st.button("开始新面试"):
             st.session_state.show_report = False
             st.session_state.interview_session_id = None
             st.rerun()

    elif st.session_state.interview_session_id:
        # Chat interface
        db = get_db()
        sess = db.query(InterviewSession).get(st.session_state.interview_session_id)
        
        # Display history
        if sess.messages:
             for msg in sess.messages:
                 role = "assistant" if msg["role"] == "ai" else "user"
                 with st.chat_message(role):
                     st.write(msg["content"])
        
        # Determine if it is AI turn (intro or response)
        last_role = sess.messages[-1]["role"] if sess.messages else None
        
        if not last_role or last_role == "human":
             # AI needs to speak
             with st.chat_message("assistant"):
                 with st.spinner("面试官思考中..."):
                     context = {"mode": mode, "topic": topic, "jd": st.session_state.current_jd}
                     response = interviewer.conduct_interview(sess.messages, context)
                     st.write(response)
                     
                     # Save
                     crud.add_message(db, sess.id, "ai", response)
                     # Force refresh to update history state
                     st.rerun()
                     
        # User input
        if prompt := st.chat_input("回答面试官的问题..."):
            with st.chat_message("user"):
                st.write(prompt)
            crud.add_message(db, sess.id, "human", prompt)
            st.rerun()
        
        db.close()
    else:
        st.info(" 请在左侧配置并开始新的模拟面试")
        st.markdown("""
        ###  面试小贴士
        1. **STAR 原则**: 回答行为面试题时，遵循 Situation (情境), Task (任务), Action (行动), Result (结果)。
        2. **主要考察点**:
           - 基础知识深度
           - 系统设计能力
           - 沟通清晰度
        3. **准备**: 确保你的麦克风和网络正常 (未来版本将支持语音模式)
        """)

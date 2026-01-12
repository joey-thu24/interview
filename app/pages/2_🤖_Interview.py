import streamlit as st
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from database.models import SessionLocal, InterviewSession
from database import crud
from core.agents.interviewer import InterviewerAgent
from core.llm import get_llm
from components.ui import load_custom_css

st.set_page_config(page_title="Mock Interview", page_icon="🤖", layout="wide")
load_custom_css()

# --- Login Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login from the main page first.")
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

st.title("🤖 Mock Interview")

if "interview_session_id" not in st.session_state:
    st.session_state.interview_session_id = None
if "current_jd" not in st.session_state:
    st.session_state.current_jd = None

# Layout
col_conf, col_chat = st.columns([1, 3])

with col_conf:
    st.subheader("⚙️ Settings")
    mode = st.radio("Mode", ["Topic Practice", "JD Simulation"], index=0)
    
    topic = "Computer Network"
    jd_text = None
    
    if mode == "Topic Practice":
        topic = st.selectbox("Select Topic", ["Computer Network", "OS", "MySQL", "Redis", "Python", "Go", "Java", "System Design"])
    else:
        topic = "JD Customized" 
        jd_text = st.text_area("Paste JD", height=200, placeholder="Paste job description here...")
    
    difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        if mode == "JD Simulation" and not jd_text:
            st.error("Please input JD first")
        else:
            db = get_db()
            sess = crud.create_interview_session(db, st.session_state.user_id, topic)
            st.session_state.interview_session_id = sess.id
            st.session_state.current_jd = jd_text
            db.close()
            st.rerun()

    if st.session_state.interview_session_id:
        st.divider()
        if st.button("🏁 End & Report", use_container_width=True):
            st.session_state.show_report = True
            st.rerun()

with col_chat:
    if st.session_state.get("show_report", False):
        st.subheader("📑 面试评估报告")
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
                
                st.markdown("### 💡 改进建议")
                for s in data.get("suggestions", []): st.write(f"👉 {s}")

            except:
                st.error("报告解析失败")
        
        if st.button("返回"):
            st.session_state.show_report = False
            st.rerun()
            
        db.close()

    elif st.session_state.interview_session_id:
        # Chat Interface
        db = get_db()
        sess = db.query(InterviewSession).get(st.session_state.interview_session_id)
        msgs = sess.messages if sess.messages else []
        
        chat_box = st.container(height=600)
        
        with chat_box:
            for m in msgs:
                is_ai = m["role"] == "assistant"
                with st.chat_message(m["role"], avatar="🤖" if is_ai else "🧑‍💻"):
                    content = m["content"]
                    if is_ai and "---SEPARATOR---" in content:
                        parts = content.split("---SEPARATOR---")
                        with st.expander("🧐 上一题点评", expanded=False):
                            st.markdown(parts[0])
                        st.markdown(parts[1])
                    else:
                        st.markdown(content)
        
        # Logic
        if not msgs:
             if interviewer:
                 with st.spinner("面试官正在准备题目..."):
                     q = interviewer.generate_question(sess.topic, difficulty, jd_text=st.session_state.current_jd)
                     crud.add_message_to_session(db, sess.id, "assistant", q)
                     st.rerun()
        
        elif msgs[-1]["role"] == "user":
             if interviewer:
                 with st.spinner("面试官正在记录并思考..."):
                     last_usr = msgs[-1]["content"]
                     last_ai = msgs[-2]["content"] if len(msgs) > 1 else ""
                     
                     eval_res = interviewer.evaluate_response(sess.topic, last_ai, last_usr)
                     
                     feedback = f"**点评**: {eval_res.get('feedback')}"
                     next_q_text = ""
                     
                     if eval_res.get("follow_up"):
                         next_q_text = f"**追问**: {eval_res.get('follow_up')}"
                     else:
                         new_q = interviewer.generate_question(sess.topic, difficulty, msgs, st.session_state.current_jd)
                         next_q_text = f"**下一题**: {new_q}"
                     
                     full_resp = f"{feedback}\n\n---SEPARATOR---\n\n{next_q_text}"
                     crud.add_message_to_session(db, sess.id, "assistant", full_resp)
                     st.rerun()

        if prompt := st.chat_input("输入回答..."):
            crud.add_message_to_session(db, sess.id, "user", prompt)
            st.rerun()
            
        db.close()
    else:
        st.info("👈 请在左侧配置并开始新的面试。")

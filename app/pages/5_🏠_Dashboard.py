import streamlit as st
import sys
import os

# Path hack (adjusted for pages folder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from database.models import init_db, SessionLocal
from core.auth import verify_password, get_user_by_username, create_user
from database import crud
from components.ui import load_custom_css

# --- Config ---
st.set_page_config(page_title="CS 仪表盘", page_icon="🏠", layout="wide")
load_custom_css()

# --- Auth Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("请先在主页完成自动登录。")
    st.switch_page("main.py")

# --- Dashboard (Main App) ---
# Sidebar Profile
with st.sidebar:
    st.title(f"👋 你好, {st.session_state.username}")
    if st.button("退出登录"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()

st.title("📊 个人仪表盘")

db = SessionLocal()
try:
    user_id = st.session_state.user_id
    stats = crud.get_study_stats(db, user_id)
    today_plan = crud.get_today_plan(db, user_id)
finally:
    db.close()

# Metrics
c1, c2, c3 = st.columns(3)
c1.metric("累计学习天数", f"{stats['total_days']} 天")
c2.metric("模拟面试场次", f"{stats.get('finished_sessions', 0)}")

todo_count = 0
if today_plan and today_plan.content:
    content = today_plan.content
    if isinstance(content, list):
            todo_count = len(content)
    elif isinstance(content, str):
            todo_count = 1 

c3.metric("今日待办任务", todo_count)

st.divider()

# Navigation Cards
st.subheader("🚀 你的 PDCA 闭环")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**📅 1. Plan (规划)**")
    st.write("设定今日学习路线")
    if st.button("进入规划", key="btn_plan"):
            st.switch_page("pages/1_📅_Plan.py")
            
with col2:
    st.warning("**📝 2. Do (执行)**")
    st.write("深度学习核心知识")
    if st.button("查阅知识库", key="btn_lib"):
            st.switch_page("pages/3_📚_Library.py")
            
with col3:
    st.success("**🎤 3. Check (检验)**")
    st.write("AI 模拟面试")
    if st.button("开始模拟面试", key="btn_interview"):
        st.switch_page("main.py")

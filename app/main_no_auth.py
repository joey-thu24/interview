import streamlit as st
import sys
import os

# Ensure core modules are found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.ui import load_custom_css
from database.models import init_db
from database import crud

# 初始化
st.set_page_config(
    page_title="AI 面试官 - 仪表盘",
    page_icon="🎓",
    layout="wide",
)
init_db()
load_custom_css()

def get_db():
    from database.models import SessionLocal
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

st.title("🎓 仪表盘 (Dashboard)")
st.markdown("欢迎回来。这是你的面试备战指挥中心。")

# 简单数据概览
db = get_db()
stats = crud.get_study_stats(db)
today_plan = crud.get_today_plan(db)
db.close()

# 顶部卡片
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("累计学习", f"{stats['total_days']} 天")
with c2:
    st.metric("模拟面试", f"{stats['finished_sessions']} 场")
with c3:
    pending = 0
    if today_plan and today_plan.content:
        pending = sum(1 for t in today_plan.content if t.get("status") != "completed")
    st.metric("今日待办", f"{pending} 项")

st.divider()

# 快捷入口
st.subheader("🚀 快速导航")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📅 每日规划", use_container_width=True):
        st.switch_page("pages/1_📅_Plan.py")
with col2:
    if st.button("🤖 模拟面试", use_container_width=True):
         st.switch_page("pages/2_🤖_Interview.py")
with col3:
    if st.button("📚 核心知识库", use_container_width=True):
         st.switch_page("pages/3_📚_Library.py")
with col4:
    if st.button("🔭 机会侦探", use_container_width=True):
         st.switch_page("pages/4_🔭_Scout.py")

st.divider()

if today_plan and today_plan.encouragement:
    st.info(f"💡 今日寄语: {today_plan.encouragement}")
else:
    st.info("👋 今天还没有生成计划，去 [每日规划] 设置今天的目标吧。")

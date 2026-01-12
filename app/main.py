import streamlit as st
import sys
import os

# Path hack
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.models import init_db, SessionLocal
from core.auth import verify_password, get_user_by_username, create_user, init_admin_user
from database import crud
from components.ui import load_custom_css

# --- Config & Init ---
st.set_page_config(page_title="CS Career Copilot", page_icon="🎓", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Init DB & Admin
try:
    init_db()
    db = SessionLocal()
    init_admin_user(db) # Ensure admin/admin exists
    db.close()
except Exception as e:
    st.error(f"Initialization Failed: {e}")

load_custom_css()

# --- Auth Functions ---
def login_form():
    st.subheader("登录你的工作台")
    with st.form("login_form"):
        # Pre-fill admin credentials for convenience
        username = st.text_input("用户名", value="admin")
        password = st.text_input("密码", type="password", value="admin")
        submitted = st.form_submit_button("登录", type="primary", use_container_width=True)
        
        if submitted:
            db = SessionLocal()
            try:
                user = get_user_by_username(db, username)
                if user and verify_password(password, user.password_hash):
                    st.session_state.logged_in = True
                    st.session_state.username = user.username
                    st.session_state.user_id = user.id
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
            finally:
                db.close()
    st.caption("默认账号: admin / admin")

def register_form():
    st.subheader("注册新账号")
    with st.form("register_form"):
        new_user = st.text_input("设置用户名")
        new_pass = st.text_input("设置密码", type="password")
        confirm_pass = st.text_input("确认密码", type="password")
        submitted = st.form_submit_button("立即注册", type="primary", use_container_width=True)
        
        if submitted:
            if new_pass != confirm_pass:
                st.error("两次输入的密码不一致！")
                return
            if not new_user or not new_pass:
                st.error("请填写完整信息。")
                return
            
            db = SessionLocal()
            try:
                if get_user_by_username(db, new_user):
                    st.error("该用户名已被注册。")
                    return
                
                user = create_user(db, new_user, new_pass)
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.user_id = user.id
                st.success("注册成功！")
                st.rerun()
            except Exception as e:
                st.error(f"注册失败: {e}")
            finally:
                db.close()

# --- Dashboard (Main App) ---
def main_app():
    # Sidebar Profile
    with st.sidebar:
        st.title(f"👋 你好, {st.session_state.username}")
        if st.button("退出登录"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
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
        # Check if content is a list (JSON) or something else
        content = today_plan.content
        if isinstance(content, list):
             todo_count = len(content)
        elif isinstance(content, str):
             # basic fallback if simple string
             todo_count = 1 
    
    c3.metric("今日待办任务", todo_count)

    st.divider()

    # Navigation Cards
    st.subheader("🚀 你的 PDCA 闭环")
    
    col1, col2, col3, col4 = st.columns(4)
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
        if st.button("开始面试", key="btn_mock"):
             st.switch_page("pages/2_🤖_Interview.py")
             
    with col4:
        st.error("**🔭 4. Act (行动)**")
        st.write("市场机会洞察")
        if st.button("职位侦探", key="btn_scout"):
             st.switch_page("pages/4_🔭_Scout.py")

# --- Router ---
if not st.session_state.logged_in:
    st.title("🎓 CS Career Copilot")
    
    # CSS for login
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["登录", "注册"])
        with tab1:
            login_form()
        with tab2:
            register_form()
else:
    main_app()

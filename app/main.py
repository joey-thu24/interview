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
    st.subheader("Login to your workspace")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
        
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
                    st.error("Invalid username or password")
            finally:
                db.close()
    st.caption("Default: admin / admin")

def register_form():
    st.subheader("Create New Account")
    with st.form("register_form"):
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
        
        if submitted:
            if new_pass != confirm_pass:
                st.error("Passwords do not match!")
                return
            if not new_user or not new_pass:
                st.error("Please fill in all fields.")
                return
            
            db = SessionLocal()
            try:
                if get_user_by_username(db, new_user):
                    st.error("Username already exists.")
                    return
                
                user = create_user(db, new_user, new_pass)
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.user_id = user.id
                st.success("Account created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating account: {e}")
            finally:
                db.close()

# --- Dashboard (Main App) ---
def main_app():
    # Sidebar Profile
    with st.sidebar:
        st.title(f"👋 Hi, {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()
        st.divider()
    
    st.title("📊 Dashboard")
    
    db = SessionLocal()
    try:
        user_id = st.session_state.user_id
        stats = crud.get_study_stats(db, user_id)
        today_plan = crud.get_today_plan(db, user_id)
    finally:
        db.close()

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Study Days", f"{stats['total_days']} Days")
    c2.metric("Interview Sessions", f"{stats.get('finished_sessions', 0)}")
    
    todo_count = 0
    if today_plan and today_plan.content:
        # Check if content is a list (JSON) or something else
        content = today_plan.content
        if isinstance(content, list):
             todo_count = len(content)
        elif isinstance(content, str):
             # basic fallback if simple string
             todo_count = 1 
    
    c3.metric("Today's Tasks", todo_count)

    st.divider()

    # Navigation Cards
    st.subheader("🚀 Your PDCA Cycle")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("**📅 1. Plan**")
        st.write("Set your roadmap")
        if st.button("Go to Plan", key="btn_plan"):
             st.switch_page("pages/1_📅_Plan.py")
             
    with col2:
        st.warning("**📝 2. Do**")
        st.write("Learn & Record")
        if st.button("Go to Library", key="btn_lib"):
             st.switch_page("pages/3_📚_Library.py")
             
    with col3:
        st.success("**🎤 3. Check**")
        st.write("Mock Interview")
        if st.button("Start Interview", key="btn_mock"):
             st.switch_page("pages/2_🤖_Interview.py")
             
    with col4:
        st.error("**🔭 4. Act**")
        st.write("Market Scout")
        if st.button("Go to Scout", key="btn_scout"):
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
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_form()
        with tab2:
            register_form()
else:
    main_app()

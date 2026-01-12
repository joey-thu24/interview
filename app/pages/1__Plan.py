import streamlit as st
import sys
import os

# Path hack
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database.models import SessionLocal
from database import crud
from core.agents.supervisor import SupervisorAgent
from core.llm import get_llm
from components.ui import load_custom_css
from core.data.templates import get_template_names, get_template

st.set_page_config(page_title="每日规划", page_icon="", layout="wide")
load_custom_css()

# --- Login Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login from the main page first.")
    st.info("Go to [Main Page](/)")
    st.stop()
    
user_id = st.session_state.user_id

def get_db():
    db = SessionLocal()
    return db

st.title(" 学习规划与监督")

# Sidebar
target_role = st.sidebar.selectbox(
    "目标岗位", 
    ["后端开发工程师", "算法工程师 (大模型方向)", "数据科学家", "前端开发工程师", "全栈工程师", "机器学习工程师", "DevOps"]
)
days_left = st.sidebar.number_input("距离面试天数", 1, 365, 30)
current_level = st.sidebar.selectbox("当前水平", ["转行小白", "应届入门", "有经验", "专家"])

@st.cache_resource
def get_agent():
    try:
        return SupervisorAgent(get_llm())
    except Exception as e:
        return None

supervisor = get_agent()
db = get_db()

tab1, tab2 = st.tabs([" 今日待办", " 长期路线"])

with tab1:
    today_plan = crud.get_today_plan(db, user_id)
    
    if today_plan:
        st.success(f" {today_plan.date} | {today_plan.encouragement}")
        
        # Determine tasks content
        if today_plan.content and isinstance(today_plan.content, list):
            tasks = today_plan.content
        else:
            tasks = []
            
        updated = False
        
        st.subheader("今日待办清单")
        
        for idx, task in enumerate(tasks):
            col_a, col_b = st.columns([0.05, 0.95])
            is_done = task.get("status") == "completed"
            
            with col_a:
                # Unique key using plan ID and index
                new_status = st.checkbox("DONE", value=is_done, key=f"t_{today_plan.id}_{idx}", label_visibility="collapsed")
            
            with col_b:
                if is_done:
                    st.markdown(f"~~**{task["topic"]}**: {task["description"]}~~")
                else:
                    st.markdown(f"**{task["topic"]}**: {task["description"]} ({task["estimated_time"]})")
            
            if new_status != is_done:
                tasks[idx]["status"] = "completed" if new_status else "pending"
                updated = True

        if updated:
            crud.update_plan_status(db, today_plan.id, tasks)
            st.rerun()

        # Progress
        if tasks:
            done_cnt = sum(1 for t in tasks if t.get("status") == "completed")
            st.progress(done_cnt / len(tasks), text=f"完成进度: {done_cnt}/{len(tasks)}")

    else:
        st.write("美好的一天，从规划开始。")
        if st.button("生成今日计划", type="primary"):
            if not supervisor:
                st.error("LLM Agent 初始化失败，请检查配置。")
            else:
                with st.spinner("AI 正在分析昨日数据并规划今日任务..."):
                    weaknesses = crud.get_recent_weaknesses(db, user_id)
                    user_profile = {"target_role": target_role, "days_left": days_left, "current_level": current_level}
                    plan = supervisor.generate_daily_plan(user_profile, recent_weaknesses=weaknesses)
                    
                    if "error" in plan:
                        st.error(plan["error"])
                    else:
                        tasks_raw = plan.get("tasks", [])
                        # Normalize
                        final_tasks = [{"topic": t.get("topic",""), "description": t.get("description",""), "estimated_time": t.get("estimated_time","30min"), "status": "pending"} for t in tasks_raw]
                        crud.create_daily_plan(db, user_id, final_tasks, plan.get("encouragement"))
                        st.rerun()

with tab2:
    st.subheader("职业发展路线图")
    
    if "roadmap" not in st.session_state:
        st.session_state.roadmap = None

    selected_template = st.selectbox("选择推荐路线模板", ["自定义"] + get_template_names())
    
    if selected_template != "自定义":
        if st.button("预览并应用模板"):
            st.session_state.roadmap = get_template(selected_template)
            st.success("模板已加载！")

    if st.session_state.roadmap:
        rm = st.session_state.roadmap
        # Handle case where phases might be in different format
        phases = rm.get("phases", [])
        if phases:
            for phase in phases:
                 with st.expander(f" {phase.get("phase_name", "Phase")} ({phase.get("duration","?")})"):
                     st.write(f"**目标**: {", ".join(phase.get("goals",[]))}")
                     st.write(f"**重点**: {", ".join(phase.get("key_topics",[]))}")
    else:
        st.info("暂无路线图")

    if st.button("让 AI 从零规划 (Beta)", help="使用 DeepSeek 思考你的专属路线"):
        if not supervisor:
            st.error("API Key missing")
        else:
             with st.spinner("正在深度规划中..."):
                 st.session_state.roadmap = supervisor.generate_roadmap({"target_role": target_role, "days_left": days_left})
                 st.rerun()

db.close()

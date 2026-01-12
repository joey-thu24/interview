import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from database import crud
from core.agents.scout import ScoutAgent
from core.llm import get_llm
from components.ui import load_custom_css

st.set_page_config(page_title="Job Scout", page_icon="🔭", layout="wide")
load_custom_css()

# --- Login Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login from the main page first.")
    st.stop()

@st.cache_resource
def get_scout():
    try:
        return ScoutAgent(get_llm())
    except:
        return None

scout = get_scout()

st.title("🔭 Job Scout")
st.markdown("This is your **Information Asymmetry Destroyer**. We find high-quality JDs and use LLMs to dig out true salary ranges, potential pitfalls, and cheat codes.")

col1, col2 = st.columns([3, 1])
with col1:
    search_kw = st.selectbox(
        "求职方向", 
        ["Golang 后端", "Python 算法", "大模型算法工程师", "机器学习", "Java 后端", "React 前端", "数据挖掘"],
        index=0
    )
    # search_kw = st.text_input("Direction (e.g. Golang, Recommendation Algo, Remote)", "Golang")
with col2:
    st.write("") 
    st.write("")
    do_search = st.button("🔍 开始侦察", type="primary", use_container_width=True)

if "scout_results" not in st.session_state:
    st.session_state.scout_results = []
    
if do_search and scout:
    with st.spinner(f"正在全网探测 '{search_kw}' 相关的高质量机会..."):
        results = scout.hunt_jobs(search_kw)
        st.session_state.scout_results = results

if st.session_state.scout_results:
    st.subheader(f"找到 {len(st.session_state.scout_results)} 个精选机会")
    
    for idx, job in enumerate(st.session_state.scout_results):
        with st.expander(f"🏢 {job.get('company','Unknown')} | {job.get('title','Job')} | {job.get('salary','Negotiable')}", expanded=False):
            st.write(f"📍 **地点**: {job.get('location','Remote')}")
            st.write(f"🏷️ **标签**: {', '.join(job.get('tags',[]))}")
            st.caption("📜 职位描述摘要:")
            st.text(job.get('content','').strip())
            
            if st.button("🕵️‍♂️ 揭秘此岗位 (AI 深度分析)", key=f"btn_{idx}"):
                if scout:
                    with st.spinner("侦探正在调查背景..."):
                        analysis = scout.analyze_jd(job.get('content',''))
                        
                        st.markdown("### 🕵️‍♂️ 侦探报告")
                        
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
                        
                        if analysis.get('red_flags'):
                            st.error("🚩 **风险预警 (Red Flags)**")
                            for flag in analysis['red_flags']:
                                st.write(f"- {flag}")
                        else:
                            st.success("✅ 未发现明显深坑")
                            
                        st.info("📝 **简历修改建议**")
                        for tip in analysis.get('resume_tips', []):
                            st.write(f"👉 {tip}")

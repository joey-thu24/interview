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
    search_kw = st.text_input("Direction (e.g. Golang, Recommendation Algo, Remote)", "Golang")
with col2:
    st.write("") 
    st.write("")
    do_search = st.button("🔍 Scout Now", type="primary", use_container_width=True)

if "scout_results" not in st.session_state:
    st.session_state.scout_results = []
    
if do_search and scout:
    with st.spinner(f"Scouting global opportunities for '{search_kw}'..."):
        results = scout.hunt_jobs(search_kw)
        st.session_state.scout_results = results

if st.session_state.scout_results:
    st.subheader(f"Found {len(st.session_state.scout_results)} Opportunities")
    
    for idx, job in enumerate(st.session_state.scout_results):
        with st.expander(f"🏢 {job.get('company','Unknown')} | {job.get('title','Job')} | {job.get('salary','Negotiable')}", expanded=False):
            st.write(f"📍 **Location**: {job.get('location','Remote')}")
            st.write(f"🏷️ **Tags**: {', '.join(job.get('tags',[]))}")
            st.caption("📜 Description Snippet:")
            st.text(job.get('content','').strip())
            
            if st.button("🕵️‍♂️ Investigate (Deep Analysis)", key=f"btn_{idx}"):
                if scout:
                    with st.spinner("Detective is investigating background..."):
                        analysis = scout.analyze_jd(job.get('content',''))
                        
                        st.markdown("### 🕵️‍♂️ Detective Report")
                        
                        ac1, ac2, ac3 = st.columns(3)
                        with ac1:
                            st.metric("💰 Real Salary Est.", analysis.get('estimated_salary', 'N/A'))
                        with ac2:
                            diff = analysis.get('difficulty_score', 50)
                            color = "red" if diff > 80 else "orange" if diff > 50 else "green"
                            st.markdown(f"**Difficulty**: :{color}[{diff}/100]")
                        with ac3:
                             st.markdown(f"**Sarcastic Comment**: *{analysis.get('insider_comment')}*")
                        
                        st.divider()
                        
                        if analysis.get('red_flags'):
                            st.error("🚩 **Red Flags**")
                            for flag in analysis['red_flags']:
                                st.write(f"- {flag}")
                        else:
                            st.success("✅ No obvious traps found")
                            
                        st.info("📝 **Resume Tips**")
                        for tip in analysis.get('resume_tips', []):
                            st.write(f"👉 {tip}")

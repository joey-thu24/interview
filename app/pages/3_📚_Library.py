import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from components.ui import load_custom_css
from core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="Library", page_icon="📚", layout="wide")
load_custom_css()

# --- Login Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login from the main page first.")
    st.stop()

st.title("📚 Core Knowledge Library")
st.markdown("Deep technical breakdown instead of rote memorization. Search existing content or ask AI to **Research** a new topic on the spot.")

# Simulated Knowledge Base
DEFAULT_DOCS = {
    "Redis Persistence": """
# Redis Persistence: RDB vs AOF

Critical interview topic. The core trade-off is **Data Safety** vs **Performance**.

## 1. RDB (Redis Database)
Snapshotting. Dumps memory to disk at intervals.
- **Pros**: Compact file, fast recovery, good for backups.
- **Cons**: Data loss since last snapshot.
- **Gotchas**: COW (Copy-on-Write) during `bgsave` causes memory usage spikes.

## 2. AOF (Append Only File)
Logging. Records every write operation.
- **Pros**: Safer (`appendfsync always/everysec`).
- **Cons**: Larger file, slower recovery.
- **Optimization**: AOF Rewrite (bgrewriteaof) compresses logs.

## 3. Hybrid (Redis 4.0+)
Combines both. RDB header + AOF body during rewrite.
""",
    "HTTPS Handshake": """
# HTTPS TLS 1.2 Handshake Flow

1. **Client Hello**: Protocol version, Cipher suites, Random1.
2. **Server Hello**: Selected Protocol/Cipher, Random2.
3. **Certificate**: Server sends public key cert.
4. **Server Key Exchange** (Optional): For DH.
5. **Client Key Exchange**: Client verifies cert, generates Pre-Master Secret, encrypts with Server Public Key.
6. **Change Cipher Spec**: Both generate Session Key from Random1+2+Pre-Master.
7. **Encrypted Handshake Message**: Verify integrity.
""",
    "System Design: Flash Sale": """
# Flash Sale System Design (Sekill)

## 1. Traffic Shaping
- CAPTCHA: Flatten the request curve.
- MQ: Asynchronous processing.

## 2. Static Content
- CDN: Cache HTML/CSS/JS at edge.

## 3. Prevent Overselling
- **Redis**: `decr key` atomic op.
- **Lua**: Ensure atomicity.
- **DB Lock**: Optimistic lock `update stock ... where num > 0`.

## 4. Fallback
- Rate Limiting
- Circuit Breaking
"""
}

# Session State for User Docs
if "user_docs" not in st.session_state:
    st.session_state.user_docs = {}

all_docs = {**DEFAULT_DOCS, **st.session_state.user_docs}

# UI Layout
col_list, col_content = st.columns([1, 3])

with col_list:
    st.subheader("📑 Catalog")
    
    # Tool: AI Researcher
    with st.expander("🕵️‍♂️ AI Researcher", expanded=True):
        new_topic = st.text_input("Enter Topic", placeholder="e.g. Raft Consensus, Zero Copy")
        if st.button("Generate Deep Note", type="primary", use_container_width=True):
             if not new_topic:
                 st.error("Please enter a topic")
             else:
                 with st.spinner(f"Researching {new_topic}..."):
                     try:
                         llm = get_llm()
                         prompt = ChatPromptTemplate.from_template("""
You are a technical expert. Write a deep technical note on "{topic}".
Requirements:
1. Clear structure: Core Concept, Mechanics/Implementation, Pros/Cons, Interview Q&A.
2. Use Markdown.
3. Deep dive, no surface level fluff. Include OS-level details if relevant.
                         """)
                         chain = prompt | llm | StrOutputParser()
                         content = chain.invoke({"topic": new_topic})
                         st.session_state.user_docs[new_topic] = content
                         st.rerun()
                     except Exception as e:
                         st.error(f"Generation Failed: {e}")

    st.markdown("---")
    selected_doc = st.radio("Articles", list(all_docs.keys()), label_visibility="collapsed")

with col_content:
    if selected_doc:
        st.header(selected_doc)
        st.markdown(all_docs[selected_doc])
        
        # Action Buttons
        c1, c2 = st.columns([1, 6])
        with c1:
            if st.button("🗑️ Delete"):
                 if selected_doc in st.session_state.user_docs:
                     del st.session_state.user_docs[selected_doc]
                     st.rerun()
                 else:
                     st.error("Cannot delete default docs")
    else:
        st.info("👈 Select or Generate an article")

import streamlit as st

def load_custom_css():
    st.markdown("""
        <style>
        /* 全局字体优化 */
        .stApp {
            font-family: 'Inter', 'Helvetica Neue', sans-serif;
        }
        
        /* 侧边栏美化 */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #e9ecef;
        }
        
        /* 聊天气泡优化 */
        .stChatMessage {
            background-color: transparent;
            border-bottom: 1px solid #f0f2f6;
            padding: 1rem 0;
        }
        .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
             /* User message styling can go here if needed */
        }
        
        /* 按钮美化 */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Tabs 优化 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #495057;
            font-size: 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e7f5ff;
            color: #1971c2;
            font-weight: bold;
        }
        
        /* Metric 卡片美化 */
        [data-testid="stMetricValue"] {
            font-size: 24px;
            color: #228be6;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #1a1a1a;">🎓 AI Interview Pro</h1>
        <p style="color: #666; font-size: 1.1rem;">DeepSeek 驱动的沉浸式面试模拟系统</p>
    </div>
    """, unsafe_allow_html=True)

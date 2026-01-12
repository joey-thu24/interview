import streamlit as st

def load_custom_css():
    st.markdown("""
        <style>
        /* 全局字体与排版优化 */
        .stApp {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* 移动端适配优化 (Mobile Friendly) */
        @media (max-width: 640px) {
            .block-container {
                padding-top: 2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            h1 {
                font-size: 1.6rem !important;
            }
            h2 {
                font-size: 1.4rem !important;
            }
            h3 {
                font-size: 1.2rem !important;
            }
            .stButton button {
                width: 100%; /* 移动端按钮全宽 */
                margin-top: 0.5rem;
            }
            /* 隐藏不必要的留白 */
            .stVerticalBlock {
                gap: 0.5rem !important;
            }
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
        
        /* 按钮统一风格 */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .stButton button:hover {
            transform: translateY(-1px);
        }
        
        /* 卡片式设计 */
        div.css-1r6slb0 {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        </style>
    """, unsafe_allow_html=True)

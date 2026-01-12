import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None

def render_radar_chart(scores_dict):
    """
    渲染能力雷达图
    :param scores_dict: e.g. {"Python": 80, "Network": 60, "Algorithm": 90}
    """
    if not scores_dict:
        st.warning("暂无数据")
        return

    if not go:
        st.bar_chart(scores_dict)
        return

    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    # 闭合雷达图
    categories += [categories[0]]
    values += [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='当前能力',
        line_color='#228be6',
        opacity=0.7
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="gray")
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_trend_chart(history_data):
    """
    渲染历史趋势图
    history_data: [{"date": "2023-10-01", "score": 75}, ...]
    """
    if not history_data:
        return
        
    df = pd.DataFrame(history_data)
    if px:
        fig = px.line(df, x="date", y="score", title="面试表现趋势", markers=True)
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df, x="date", y="score")

"""
Reusable KPI Cards Component for Streamlit Dashboard.
"""
import streamlit as st

def render_kpi_card(title: str, value: str, subtitle: str = "", border_color: str = "#e2e8f0"):
    html = f"""
    <div style="background:#ffffff; border:1px solid {border_color}; border-radius:8px; padding:12px 16px; margin-bottom:10px; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
        <div style="font-size:0.75rem; font-weight:600; text-transform:uppercase; color:#64748b; letter-spacing:0.04em;">{title}</div>
        <div style="font-size:1.6rem; font-weight:700; color:#0f172a; margin-top:2px;">{value}</div>
        <div style="font-size:0.75rem; color:#94a3b8; margin-top:2px;">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

"""
Main Streamlit Application for Mining Supply Chain Digital Twin Platform.
"Resilience-Driven Digital Twin for Supply Chain Disruption in Underground Mining:
A System Dynamics and Multi-Agent Simulation of Critical Spare Parts Logistics"
"""
import streamlit as st
from pathlib import Path

# Streamlit Page Configuration (Wide scientific layout)
st.set_page_config(
    page_title="Mining Digital Twin — Supply Chain Resilience",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and inject custom CSS
CSS_PATH = Path(__file__).resolve().parent / "styles" / "custom.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database tables and initial seed data if needed
from database.connection import create_all_tables
from database.seed.data_seeder import seed_database

try:
    create_all_tables()
    seed_database(force=False)
except Exception:
    pass

# Import Login View
from app.views.login_view import render_login_view

# --- AUTHENTICATION GATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    render_login_view()
    st.stop()

# --- IMPORT SYSTEM VIEWS (Only loaded after authentication) ---
from app.views.dashboard_view import render_dashboard
from app.views.mine_view import render_mine_view
from app.views.supply_chain_view import render_supply_chain_view
from app.views.digital_twin_view import render_digital_twin_view
from app.views.simulation_view import render_simulation_view
from app.views.resilience_view import render_resilience_view
from app.views.eda_view import render_eda_view
from app.views.ml_view import render_ml_view
from app.views.statistics_view import render_statistics_view
from app.views.hypothesis_view import render_hypothesis_view
from app.views.recommendations_view import render_recommendations_view
from app.views.reports_view import render_reports_view
from app.views.users_view import render_users_view
from app.views.log_view import render_log_view

# User profile details
user_name = st.session_state.get("user_full_name", "Sofia Contreras")
actual_username = st.session_state.get("username", "admin")
actual_user_role = st.session_state.get("user_role", "ADMIN")

role_map = {
    "ADMIN": "Administrador",
    "INVESTIGADOR": "Investigador Científico",
    "OPERADOR": "Operador Minero",
    "INGENIERO": "Ingeniero",
    "SUPERVISOR": "Supervisor",
    "TECNICO": "Técnico"
}
display_role = role_map.get(actual_user_role, actual_user_role.capitalize())
user_email = f"{actual_username}@minera.com"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    # Injected CSS ensuring individual button cards match the reference screenshot
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] div.stButton {
        margin-bottom: 7px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 9px 12px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        color: #334155 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        min-height: 42px !important;
        transition: all 0.15s ease-in-out !important;
    }
    section[data-testid="stSidebar"] div.stButton > button p {
        color: #334155 !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        margin: 0 !important;
        text-align: center !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        border-color: #94a3b8 !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.07) !important;
        transform: translateY(-1px);
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
    section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #f0f7ff !important;
        border: 1.8px solid #2563eb !important;
        box-shadow: 0 2px 5px rgba(37, 99, 235, 0.15) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
    section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] p {
        color: #1d4ed8 !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Dark User Profile Card matching screenshot
    st.markdown(f"""
    <div style="background-color: #243347; border-radius: 8px; padding: 14px 16px; margin-top: -10px; margin-bottom: 18px; color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.12);">
        <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1.05rem; color: #ffffff;">
            <span style="color: #a78bfa; font-size: 1.2rem;">👤</span>
            <span>{user_name}</span>
        </div>
        <div style="color: #cbd5e1; font-size: 0.9rem; margin-top: 6px; font-weight: 500;">
            {display_role}
        </div>
        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 2px;">
            {user_email}
        </div>
    </div>
    """, unsafe_allow_html=True)

    active_role = actual_user_role

    # 2. Main Menu Heading matching screenshot
    st.markdown("""
    <div style="font-size: 1.02rem; font-weight: 700; color: #1e293b; margin: 10px 0 10px 0; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.15rem;">📋</span> <span>Menú Principal</span>
    </div>
    """, unsafe_allow_html=True)

    # 3. Navigation Menu Cards matching requested structure
    full_menu = [
        "📊 Dashboard",
        "🔧 Gemelo Digital",
        "🏭 Mina y Equipos (BOM)",
        "📦 Cadena de Suministro (SDI)",
        "🧪 Simulación (SD + ABM)",
        "🛡️ Laboratorio de Resiliencia",
        "⚙️ Motor de Inteligencia Artificial",
        "🎯 Evaluación de Hipótesis (H0 vs H1)",
        "💡 Recomendaciones de Decisión",
        "📑 Reportes y Exportación"
    ]

    if active_role == "OPERADOR":
        allowed_menus = [
            "📊 Dashboard",
            "🔧 Gemelo Digital",
            "🏭 Mina y Equipos (BOM)",
            "📦 Cadena de Suministro (SDI)",
            "💡 Recomendaciones de Decisión",
            "📑 Reportes y Exportación"
        ]
    elif active_role == "INVESTIGADOR":
        allowed_menus = [
            "📊 Dashboard",
            "🔧 Gemelo Digital",
            "🧪 Simulación (SD + ABM)",
            "🛡️ Laboratorio de Resiliencia",
            "⚙️ Motor de Inteligencia Artificial",
            "🎯 Evaluación de Hipótesis (H0 vs H1)",
            "💡 Recomendaciones de Decisión",
            "📑 Reportes y Exportación"
        ]
    else:
        allowed_menus = full_menu

    if "current_page" not in st.session_state or st.session_state["current_page"] not in allowed_menus:
        st.session_state["current_page"] = allowed_menus[0]

    for item in allowed_menus:
        is_active = (st.session_state["current_page"] == item)
        btn_type = "primary" if is_active else "secondary"
        if st.button(item, key=f"nav_{item}", use_container_width=True, type=btn_type):
            st.session_state["current_page"] = item
            st.rerun()

    selected_page = st.session_state["current_page"]

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # 4. Cerrar Sesión colocado al final del sidebar
    if st.button("🚪 Cerrar Sesión", key="btn_logout_sidebar", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("username", None)
        st.session_state.pop("user_role", None)
        st.session_state.pop("user_full_name", None)
        st.session_state.pop("current_page", None)
        st.rerun()

# --- PAGE ROUTER ---
if selected_page == "📊 Dashboard":
    render_dashboard()
elif selected_page == "🔧 Gemelo Digital":
    render_digital_twin_view()
elif selected_page == "🏭 Mina y Equipos (BOM)":
    render_mine_view()
elif selected_page == "📦 Cadena de Suministro (SDI)":
    render_supply_chain_view()
elif selected_page == "🧪 Simulación (SD + ABM)":
    render_simulation_view()
elif selected_page == "🛡️ Laboratorio de Resiliencia":
    render_resilience_view()
elif selected_page == "⚙️ Motor de Inteligencia Artificial":
    render_ml_view()
elif selected_page == "🎯 Evaluación de Hipótesis (H0 vs H1)":
    render_hypothesis_view()
elif selected_page == "💡 Recomendaciones de Decisión":
    render_recommendations_view()
elif selected_page == "📑 Reportes y Exportación":
    render_reports_view()

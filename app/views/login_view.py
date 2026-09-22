"""
Login View: High-fidelity login screen matching the industrial digital twin interface design.
"""
import streamlit as st
from backend.services.auth_service import AuthService

def render_login_view():
    # Hide sidebar completely while on the login page for an authentic centered login experience
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        /* Style Streamlit form to match the white card in the reference screenshot */
        div[data-testid="stForm"] {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 24px 30px 20px 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
        }
        div[data-testid="stTextInput"] input {
            background-color: #f1f5f9 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            color: #1e293b !important;
            font-size: 0.95rem !important;
        }
        div[data-testid="stTextInput"] label {
            font-weight: 500 !important;
            color: #334155 !important;
            font-size: 0.95rem !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            padding: 7px 16px !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            border-color: #94a3b8 !important;
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Centered Header
    st.markdown("""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; gap: 14px;">
            <span style="font-size: 2.8rem;">⛏️</span>
            <h1 style="font-size: 2.4rem; font-weight: 800; color: #1e3a5f; letter-spacing: -0.01em; margin: 0;">
                SISTEMA DE GEMELOS DIGITALES
            </h1>
        </div>
        <div style="font-size: 1.35rem; font-weight: 600; color: #64748b; margin-top: 8px;">
            Minería Subterránea — Cadena de Suministro y Resiliencia
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered Layout
    col_l, col_center, col_r = st.columns([1, 1.45, 1])

    with col_center:
        # 1. Main Login Form Card
        with st.form("login_form", clear_on_submit=False):
            st.markdown("""
            <div style="font-size: 1.45rem; font-weight: 700; color: #1e293b; margin-bottom: 16px;">
                🔐 Iniciar Sesión
            </div>
            """, unsafe_allow_html=True)

            username_input = st.text_input("Usuario", placeholder="Ingrese su usuario", key="login_user")
            password_input = st.text_input("Contraseña", placeholder="Ingrese su contraseña", type="password", key="login_pass")
            
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Ingresar")

            if submit_button:
                user_info = AuthService.authenticate(username_input, password_input)
                if user_info:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user_info["username"]
                    st.session_state["user_role"] = user_info["rol"]
                    st.session_state["user_full_name"] = user_info["nombre_completo"]
                    st.success(f"¡Bienvenido, {user_info['nombre_completo']}!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verifique su usuario y contraseña.")

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

        # 2. Demo Users Blue Card (Pixel-accurate match to reference image)
        st.markdown("""
        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #0284c7; font-size: 1.05rem; margin-bottom: 12px;">
                Usuarios de demostración:
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.95rem;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: #0284c7; font-size: 1.1rem; line-height: 1;">•</span>
                    <span style="font-size: 1.1rem;">👤</span>
                    <span style="font-weight: 600; color: #0284c7;">Administrador:</span>
                    <span style="color: #0284c7;">admin / admin123</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: #0284c7; font-size: 1.1rem; line-height: 1;">•</span>
                    <span style="font-size: 1.1rem;">👷</span>
                    <span style="font-weight: 600; color: #0284c7;">Ingeniero:</span>
                    <span style="color: #0284c7;">ingeniero / inge123</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: #0284c7; font-size: 1.1rem; line-height: 1;">•</span>
                    <span style="font-size: 1.1rem;">📋</span>
                    <span style="font-weight: 600; color: #0284c7;">Supervisor:</span>
                    <span style="color: #0284c7;">supervisor / super123</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: #0284c7; font-size: 1.1rem; line-height: 1;">•</span>
                    <span style="font-size: 1.1rem;">🔧</span>
                    <span style="font-weight: 600; color: #0284c7;">Técnico:</span>
                    <span style="color: #0284c7;">tecnico / tec123</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: #0284c7; font-size: 1.1rem; line-height: 1;">•</span>
                    <span style="font-size: 1.1rem;">🔬</span>
                    <span style="font-weight: 600; color: #0284c7;">Investigador:</span>
                    <span style="color: #0284c7;">investigador / investigador123</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Quick 1-Click Access Buttons
        st.caption("⚡ Acceso Rápido con 1 Clic:")
        c_q1, c_q2, c_q3, c_q4 = st.columns(4)
        with c_q1:
            if st.button("👑 Admin", use_container_width=True, key="quick_admin"):
                user_info = AuthService.authenticate("admin", "admin123")
                st.session_state["authenticated"] = True
                st.session_state["username"] = user_info["username"]
                st.session_state["user_role"] = user_info["rol"]
                st.session_state["user_full_name"] = user_info["nombre_completo"]
                st.rerun()
        with c_q2:
            if st.button("👷 Ingeniero", use_container_width=True, key="quick_inge"):
                user_info = AuthService.authenticate("ingeniero", "inge123")
                st.session_state["authenticated"] = True
                st.session_state["username"] = user_info["username"]
                st.session_state["user_role"] = user_info["rol"]
                st.session_state["user_full_name"] = user_info["nombre_completo"]
                st.rerun()
        with c_q3:
            if st.button("📋 Supervisor", use_container_width=True, key="quick_super"):
                user_info = AuthService.authenticate("supervisor", "super123")
                st.session_state["authenticated"] = True
                st.session_state["username"] = user_info["username"]
                st.session_state["user_role"] = user_info["rol"]
                st.session_state["user_full_name"] = user_info["nombre_completo"]
                st.rerun()
        with c_q4:
            if st.button("🔬 Investigador", use_container_width=True, key="quick_inv"):
                user_info = AuthService.authenticate("investigador", "investigador123")
                st.session_state["authenticated"] = True
                st.session_state["username"] = user_info["username"]
                st.session_state["user_role"] = user_info["rol"]
                st.session_state["user_full_name"] = user_info["nombre_completo"]
                st.rerun()

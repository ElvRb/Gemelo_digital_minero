"""
Users and RBAC Management View: Manage users, roles, system privileges, and active sessions.
"""
import streamlit as st
import pandas as pd
from database.connection import get_db_session
from database.models import Usuario, Rol

def render_users_view():
    st.markdown("""
    <div class="section-banner">
        <h2>👥 GESTIÓN DE USUARIOS Y CONTROL DE ACCESO (RBAC)</h2>
        <p>Administración de cuentas corporativas, perfiles de acceso operacional, credenciales y auditoría de seguridad.</p>
    </div>
    """, unsafe_allow_html=True)

    session = get_db_session()
    try:
        users = session.query(Usuario).all()
        roles = session.query(Rol).all()

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.metric("Total de Usuarios Registrados", len(users))
        with col_k2:
            st.metric("Roles RBAC Configurados", len(roles))
        with col_k3:
            active_count = sum(1 for u in users if u.activo)
            st.metric("Cuentas Activas", active_count)

        st.markdown("---")

        st.subheader("Directorio de Usuarios del Sistema")
        user_rows = []
        for u in users:
            user_rows.append({
                "ID": u.id,
                "Usuario": u.username,
                "Nombre Completo": u.nombre_completo,
                "Correo Electrónico": u.email,
                "Rol": u.rol.nombre if u.rol else "SIN ROL",
                "Estado": "🟢 Activo" if u.activo else "🔴 Inactivo",
                "Fecha Creación": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "N/A"
            })

        df_users = pd.DataFrame(user_rows)
        st.dataframe(df_users, use_container_width=True)

        st.markdown("---")
        st.subheader("Matriz de Permisos por Rol")
        perm_data = {
            "Módulo": [
                "Dashboard Ejecutivo",
                "Gemelo Digital en Vivo",
                "Mantenimiento y Equipos",
                "Análisis Predictivo (SD + ABM)",
                "Motor de Inteligencia Artificial",
                "Reportes y Exportación",
                "Repuestos e Inventarios",
                "Gestión de Usuarios",
                "Bitácora y Auditoría"
            ],
            "ADMIN": ["✅ Lectura / Escritura"] * 9,
            "INVESTIGADOR": [
                "✅ Lectura", "✅ Lectura / Control", "✅ Lectura", "✅ Ejecución Completa",
                "✅ Entrenamiento / Test", "✅ Exportación", "✅ Lectura", "❌ Sin Acceso", "✅ Lectura"
            ],
            "OPERADOR": [
                "✅ Monitoreo", "✅ Telemetría", "✅ Registro Falla", "❌ Sin Acceso",
                "❌ Sin Acceso", "✅ Reporte Diario", "✅ Solicitud Repuesto", "❌ Sin Acceso", "❌ Sin Acceso"
            ]
        }
        st.dataframe(pd.DataFrame(perm_data), use_container_width=True)

    finally:
        session.close()

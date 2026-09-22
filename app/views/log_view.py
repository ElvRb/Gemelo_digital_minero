"""
Audit Log and Event Trail View: Bitácora de operaciones, sincronización del Gemelo Digital y eventos críticos.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database.connection import get_db_session
from database.models import DigitalTwinState, Equipo, Mantenimiento, FallaEquipo

def render_log_view():
    st.markdown("""
    <div class="section-banner">
        <h2>📝 BITÁCORA Y REGISTRO DE EVENTOS DEL SISTEMA</h2>
        <p>Trazabilidad histórica de eventos operacionales, sincronizaciones de telemetría y snapshots del Gemelo Digital.</p>
    </div>
    """, unsafe_allow_html=True)

    session = get_db_session()
    try:
        snapshots = session.query(DigitalTwinState).order_by(DigitalTwinState.created_at.desc()).limit(50).all()
        mantenimientos = session.query(Mantenimiento).order_by(Mantenimiento.fecha_programada.desc()).limit(50).all()
        fallas = session.query(FallaEquipo).order_by(FallaEquipo.fecha_falla.desc()).limit(50).all()

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.metric("Snapshots Registrados", len(snapshots))
        with col_k2:
            st.metric("Eventos de Mantenimiento", len(mantenimientos))
        with col_k3:
            st.metric("Fallas Auditadas", len(fallas))

        st.markdown("---")

        tab_snap, tab_maint, tab_fallas = st.tabs([
            "📸 Historial de Snapshots (Digital Twin)",
            "🔧 Bitácora de Mantenimientos",
            "⚠️ Registro de Fallas y Paradas"
        ])

        with tab_snap:
            st.subheader("Snapshots del Gemelo Digital")
            if snapshots:
                snap_rows = []
                for s in snapshots:
                    snap_rows.append({
                        "ID": s.id,
                        "Nombre Estado": s.nombre_estado,
                        "Origen": s.origen_datos,
                        "Disponibilidad (%)": f"{s.disponibilidad_flota_pct}%",
                        "Stockouts Activos": s.stockouts_activos,
                        "Fecha Creación": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "N/A",
                        "Notas": s.notas or "Snapshot sincronizado"
                    })
                st.dataframe(pd.DataFrame(snap_rows), use_container_width=True)
            else:
                st.info("No hay snapshots registrados actualmente.")

        with tab_maint:
            st.subheader("Bitácora de Órdenes de Mantenimiento")
            if mantenimientos:
                maint_rows = []
                for m in mantenimientos:
                    eq = session.query(Equipo).filter(Equipo.id == m.equipo_id).first()
                    maint_rows.append({
                        "ID": m.id,
                        "Equipo": eq.codigo if eq else f"EQ-{m.equipo_id}",
                        "Tipo": m.tipo.value if hasattr(m.tipo, "value") else str(m.tipo),
                        "Fecha Programada": m.fecha_programada.strftime("%Y-%m-%d") if m.fecha_programada else "N/A",
                        "Estado": m.estado.value if hasattr(m.estado, "value") else str(m.estado),
                        "Costo Total (USD)": f"${m.costo_total_usd:,.2f}" if m.costo_total_usd else "$0.00"
                    })
                st.dataframe(pd.DataFrame(maint_rows), use_container_width=True)
            else:
                st.info("No hay mantenimientos registrados actualmente.")

        with tab_fallas:
            st.subheader("Registro de Paradas No Programadas por Falla")
            if fallas:
                falla_rows = []
                for f in fallas:
                    eq = session.query(Equipo).filter(Equipo.id == f.equipo_id).first()
                    falla_rows.append({
                        "ID": f.id,
                        "Equipo": eq.codigo if eq else f"EQ-{f.equipo_id}",
                        "Descripción": f.descripcion_falla,
                        "Fecha Falla": f.fecha_falla.strftime("%Y-%m-%d %H:%M") if f.fecha_falla else "N/A",
                        "Duración Parada (h)": f.duracion_parada_horas
                    })
                st.dataframe(pd.DataFrame(falla_rows), use_container_width=True)
            else:
                st.info("No hay fallas registradas actualmente.")

    finally:
        session.close()

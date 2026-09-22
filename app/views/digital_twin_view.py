"""
Digital Twin State and Sychronization Inspector View.
Highlights the physical-to-digital bridge and captures state snapshots.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from backend.services.digital_twin_service import DigitalTwinService
from database.connection import get_db_session
from database.models import DigitalTwinState

def render_digital_twin_view():
    st.markdown("""
    <div class="section-banner">
        <h2>ESTADO DEL GEMELO DIGITAL (DIGITAL TWIN CORE)</h2>
        <p>Espejo digital sincronizado del mundo físico subterráneo y punto de partida para experimentos What-If.</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Conceptual Architecture Diagram
    st.markdown("""
    ```text
    ┌──────────────────────┐        Telemetría, ERP       ┌──────────────────────────┐         What-If          ┌───────────────────────┐
    │     MUNDO FÍSICO     │ ───────────────────────────> │      GEMELO DIGITAL      │ ───────────────────────> │       SIMULACIÓN      │
    │  (Mina Real Andina)  │   Eventos de Mantenimiento   │  (Estado Sincronizado)   │    Ramificación de     │ (SD + ABM + Escenarios│
    │ 33 Equipos, Almacén  │   Consumo de Repuestos       │ Indicadores, Stocks, MTBF│       Escenarios       │   de Resiliencia)     │
    └──────────────────────┘                              └──────────────────────────┘                          └───────────────────────┘
    ```
    """)

    # 2. Live Digital State Inspection
    latest_state = DigitalTwinService.get_latest_state()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Disponibilidad Flota", f"{latest_state['disponibilidad_flota_pct']}%")
    with c2:
        st.metric("Equipos Operativos", f"{latest_state['equipos_operativos']} / {latest_state['equipos_total']}")
    with c3:
        st.metric("Stockouts Activos", f"{latest_state['stockouts_activos']}")
    with c4:
        st.metric("Fill Rate Global", f"{latest_state['fill_rate_pct']}%")

    st.markdown("---")

    # 3. Snapshot Trigger
    col_snap1, col_snap2 = st.columns([2, 1])
    with col_snap1:
        snap_nombre = st.text_input("Nombre de Snapshot:", value=f"SNAPSHOT_{datetime.utcnow().strftime('%Y%m%d_%H%M')}")
        snap_notas = st.text_input("Notas de contexto:", value="Snapshot congelado para análisis de resiliencia")
    with col_snap2:
        st.write("")
        st.write("")
        if st.button("📸 Congelar Snapshot del Gemelo Digital", type="primary"):
            res = DigitalTwinService.capture_snapshot(nombre=snap_nombre, notas=snap_notas)
            st.success(f"Snapshot guardado exitosamente con ID #{res['id']}.")

    # 4. Snapshots History Table
    st.subheader("📜 Historial de Estados Congelados del Gemelo Digital")
    session = get_db_session()
    try:
        snapshots = session.query(DigitalTwinState).order_by(DigitalTwinState.snapshot_timestamp.desc()).all()
        if snapshots:
            snap_rows = [
                {
                    "ID": s.id,
                    "Fecha y Hora (UTC)": s.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Nombre": s.nombre_estado,
                    "Origen": s.origen_datos,
                    "Disp. Flota (%)": s.disponibilidad_flota_pct,
                    "Stockouts": s.stockouts_activos,
                    "Fill Rate (%)": s.fill_rate_pct,
                    "Downtime Acumulado (h)": s.downtime_acumulado_horas,
                    "Notas": s.notas
                }
                for s in snapshots
            ]
            st.dataframe(pd.DataFrame(snap_rows), use_container_width=True)
        else:
            st.info("No hay snapshots registrados en la base de datos.")
    finally:
        session.close()

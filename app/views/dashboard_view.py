"""
Dashboard View: Executive KPIs, Mine Topology 3D, and Real-Time Asset Overview.
"""
import streamlit as st
import plotly.express as px
from backend.services.supply_chain_service import SupplyChainService
from backend.services.digital_twin_service import DigitalTwinService
from app.components.mine_3d import create_mine_3d_figure
from app.components.kpi_cards import render_kpi_card

def render_dashboard():
    st.markdown("""
    <div class="section-banner">
        <h2>CENTRO DE CONTROL Y MONITOREO — DIGITAL TWIN MINERO</h2>
        <p>Monitoreo en tiempo real del estado de la mina subterránea, confiabilidad de flota y logística de repuestos críticos.</p>
    </div>
    """, unsafe_allow_html=True)

    kpis = SupplyChainService.get_kpis()
    health_scores = DigitalTwinService.calculate_equipment_health_scores()

    # 1. KPI Cards Grid (Row 1)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_kpi_card("Disponibilidad Flota", f"{kpis['disponibilidad_flota_pct']}%", f"{kpis['equipos_operativos']} / {kpis['equipos_total']} equipos")
    with col2:
        render_kpi_card("Stockouts Activos", f"{kpis['stockouts_activos']}", "Quiebres de stock críticos", border_color="#fca5a5" if kpis['stockouts_activos'] > 0 else "#e2e8f0")
    with col3:
        render_kpi_card("Downtime Acumulado", f"{int(kpis['downtime_acumulado_horas'])} h", "Tiempo total detenido")
    with col4:
        render_kpi_card("Fill Rate Almacén", f"{kpis['fill_rate_pct']}%", f"Nivel servicio: {kpis['nivel_servicio_pct']}%")
    with col5:
        render_kpi_card("Pérdida Producción", f"${kpis['perdida_produccion_usd']:,.0f}", "USD acumulado estimado", border_color="#fca5a5")

    # Row 2 (Secondary KPIs)
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        render_kpi_card("MTBF Promedio", f"{kpis['mtbf_promedio_horas']} h", "Mean Time Between Failures")
    with col_b:
        render_kpi_card("MTTR Promedio", f"{kpis['mttr_promedio_horas']} h", "Mean Time To Repair")
    with col_c:
        render_kpi_card("Lead Time Promedio", f"{kpis['lead_time_promedio_dias']} días", "Repuestos críticos")
    with col_d:
        render_kpi_card("Órdenes Pendientes", f"{kpis['ordenes_pendientes']}", "En tránsito o aduana")

    st.markdown("---")

    # 2. Main Visual Layout: 3D Mine Topography & Equipment Status Distribution
    c_left, c_right = st.columns([1.5, 1.0])

    with c_left:
        st.subheader("🌐 Topología Subterránea 3D y Salud de Flota")
        st.caption("Mina Subterránea Titán Andino — Cotas (-120m a -480m), pique de extracción y nodos de flota.")
        
        legend_html = f"""
        <div style="display: flex; flex-wrap: wrap; gap: 14px; align-items: center; padding: 6px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; margin: 6px 0 8px 0; font-size: 0.82rem; font-weight: 600;">
            <span><span style="color: #10b981; font-size: 1.1rem;">●</span> OPERATIVO ({kpis['equipos_operativos']})</span>
            <span><span style="color: #f59e0b; font-size: 1.1rem;">●</span> MANTENIMIENTO ({kpis['equipos_mantenimiento']})</span>
            <span><span style="color: #ef4444; font-size: 1.1rem;">◆</span> FALLADO ({kpis['equipos_fallados']})</span>
            <span><span style="color: #334155; font-size: 1.1rem;">┆</span> Pique Vertical (-480m)</span>
        </div>
        """
        st.markdown(legend_html, unsafe_allow_html=True)
        fig_3d = create_mine_3d_figure(health_scores)
        st.plotly_chart(fig_3d, use_container_width=True, config={"displaylogo": False})

    with c_right:
        st.subheader("📊 Estado de Equipos y Salud de Activos")
        
        status_counts = {
            "OPERATIVO": kpis["equipos_operativos"],
            "MANTENIMIENTO": kpis["equipos_mantenimiento"],
            "FALLADO": kpis["equipos_fallados"],
            "FUERA_DE_SERVICIO": kpis["equipos_fuera_servicio"]
        }
        fig_pie = px.pie(
            names=list(status_counts.keys()),
            values=list(status_counts.values()),
            color=list(status_counts.keys()),
            color_discrete_map={
                "OPERATIVO": "#10b981",
                "MANTENIMIENTO": "#f59e0b",
                "FALLADO": "#ef4444",
                "FUERA_DE_SERVICIO": "#64748b"
            },
            hole=0.45
        )
        fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=250)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("##### ⚠️ Equipos Críticos en Alerta Inmediata")
        critical_alerts = [e for e in health_scores if e["estado"] in ("FALLADO", "MANTENIMIENTO") or e["salud_pct"] < 50.0]
        if critical_alerts:
            for eq in critical_alerts:
                badge = "🔴 FALLADO" if eq["estado"] == "FALLADO" else "🟡 MANTENIMIENTO"
                st.markdown(f"**{eq['codigo']} — {eq['nombre']}** | {badge} | Salud: **{eq['salud_pct']}%**")
        else:
            st.success("Toda la flota opera dentro de parámetros normales.")

    # 3. Bottom Table: Live Supplier Dependency Matrix Summary
    st.subheader("⚡ Resumen de Dependencia de Proveedores y Riesgo Monopólico")
    sdi_data = SupplyChainService.calculate_supplier_dependency_index()
    sdi_summary = [
        {
            "Código": r["repuesto_codigo"],
            "Repuesto": r["repuesto_nombre"],
            "Stock": r["stock_actual"],
            "Lead Time (días)": r["lead_time_promedio"],
            "Proveedor Dominante": r["dominant_supplier"],
            "Cuota (%)": f"{r['max_supplier_share_pct']}%",
            "Riesgo Proveedor Único": r["single_source_risk"]
        }
        for r in sdi_data
    ]
    st.dataframe(sdi_summary, use_container_width=True)

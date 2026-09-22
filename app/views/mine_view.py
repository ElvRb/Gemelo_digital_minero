"""
Mine Equipment, Critical Spare Parts, and BOM Architecture View.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from database.connection import get_db_session
from database.models import Equipo, Repuesto, BOMEquipo, CategoriaRepuesto
from backend.services.digital_twin_service import DigitalTwinService

def render_mine_view():
    st.markdown("""
    <div class="section-banner">
        <h2>INFRAESTRUCTURA DE MINA Y GESTIÓN DE ACTIVOS</h2>
        <p>Catálogo de equipos pesados subterráneos, repuestos críticos de alto impacto y Bill of Materials (BOM).</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🚜 Flota de Equipos Subterráneos",
        "⚙️ Repuestos Críticos",
        "📋 Bill of Materials (BOM)",
        "📈 Curvas de Degradación Weibull"
    ])

    session = get_db_session()
    try:
        equipos = session.query(Equipo).all()
        repuestos = session.query(Repuesto).all()
        bom_list = session.query(BOMEquipo).all()

        # TAB 1: Flota de Equipos
        with tab1:
            st.subheader(f"Inventario de Flota Pesada ({len(equipos)} Equipos)")
            
            filter_tipo = st.selectbox(
                "Filtrar por Tipo de Equipo:",
                ["TODOS"] + sorted(list(set(e.tipo_equipo.nombre for e in equipos if e.tipo_equipo)))
            )
            filtered_eq = [e for e in equipos if filter_tipo == "TODOS" or (e.tipo_equipo and e.tipo_equipo.nombre == filter_tipo)]
            
            eq_table = [
                {
                    "Código": e.codigo,
                    "Nombre": e.nombre,
                    "Tipo": e.tipo_equipo.nombre if e.tipo_equipo else "N/A",
                    "Modelo": e.modelo,
                    "Fabricante": e.fabricante,
                    "Estado": e.estado,
                    "Horas Op.": f"{e.horas_operacion:,.0f} h",
                    "MTBF": f"{e.mtbf_horas:.0f} h",
                    "MTTR": f"{e.mttr_horas:.0f} h",
                    "Nivel Cota Z": f"{e.posicion_z} m"
                }
                for e in filtered_eq
            ]
            st.dataframe(pd.DataFrame(eq_table), use_container_width=True)

        # TAB 2: Repuestos Críticos
        with tab2:
            st.subheader("Catálogo de Repuestos Críticos (3-6 meses de Lead Time)")
            st.info("Nota metodológica: Se excluyen consumibles menores (tornillos, arandelas, grasas) y se priorizan componentes electromecánicos e hidráulicos de alto impacto en el downtime.")

            rep_table = [
                {
                    "Código": r.codigo,
                    "Descripción": r.nombre,
                    "Categoría": r.categoria.nombre if r.categoria else "N/A",
                    "Costo Unitario (USD)": f"${r.costo_unitario_usd:,.2f}",
                    "Lead Time Base": f"{r.lead_time_promedio_dias:.0f} días",
                    "Tasa Falla (λ)": r.tasa_falla_lambda,
                    "Stock Actual": r.stock_actual,
                    "Stock Seguridad": r.stock_seguridad,
                    "Punto Reorden (ROP)": r.punto_reorden,
                    "Apto 3D": "Sí" if r.permite_impresion_3d else "No",
                    "Apto Taller Local": "Sí" if r.permite_reparacion_local else "No"
                }
                for r in repuestos
            ]
            st.dataframe(pd.DataFrame(rep_table), use_container_width=True)

        # TAB 3: BOM (Bill of Materials)
        with tab3:
            st.subheader("Estructura Jerárquica: Equipo → Subsistema → Repuesto Crítico")
            eq_selected = st.selectbox("Seleccionar Equipo para desglosar BOM:", [e.codigo for e in equipos])
            
            eq_obj = session.query(Equipo).filter_by(codigo=eq_selected).first()
            if eq_obj:
                st.markdown(f"**BOM de {eq_obj.codigo} — {eq_obj.nombre}** ({eq_obj.modelo})")
                bom_items = session.query(BOMEquipo).filter_by(equipo_id=eq_obj.id).all()
                if bom_items:
                    bom_table = [
                        {
                            "Subsistema": b.subsistema,
                            "Repuesto Requerido": b.repuesto.nombre if b.repuesto else "N/A",
                            "Código Repuesto": b.repuesto.codigo if b.repuesto else "N/A",
                            "Cantidad": b.cantidad,
                            "Criticidad Subsistema": b.criticidad_subsistema,
                            "Stock Almacén": b.repuesto.stock_actual if b.repuesto else 0,
                            "Lead Time Reposición": f"{b.repuesto.lead_time_promedio_dias} días" if b.repuesto else "N/A"
                        }
                        for b in bom_items
                    ]
                    st.dataframe(pd.DataFrame(bom_table), use_container_width=True)
                else:
                    st.warning(f"No hay componentes BOM registrados para {eq_selected}.")

        # TAB 4: Curvas Weibull
        with tab4:
            st.subheader("Análisis de Degradación y Confiabilidad Weibull (β = 2.2)")
            st.markdown("La probabilidad acumulada de falla sigue $F(t) = 1 - e^{-(t / \\eta)^\\beta}$, reflejando la fase de desgaste acelerado por abrasión y roca dura.")
            
            t_hours = np.linspace(0, 1500, 150)
            fig_w = px.line()
            
            for eq in equipos[:6]:
                eta = max(100.0, eq.mtbf_horas * 1.25)
                f_t = 1.0 - np.exp(-((t_hours / eta) ** 2.2))
                fig_w.add_scatter(x=t_hours, y=f_t, mode="lines", name=f"{eq.codigo} ({eq.tipo_equipo.nombre if eq.tipo_equipo else ''})")

            fig_w.update_layout(
                title="<b>Curvas de Falla Acumulada Weibull para Equipos Seleccionados</b>",
                xaxis_title="Horas de Operación Acumuladas en Ciclo (t)",
                yaxis_title="Probabilidad de Falla F(t)",
                height=450
            )
            st.plotly_chart(fig_w, use_container_width=True)

    finally:
        session.close()

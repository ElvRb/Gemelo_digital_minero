"""
Resilience Lab: Disruption Scenarios and Resilience Strategy Benchmark.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simulation.system_dynamics.sd_simulator import SDSimulator

def render_resilience_view():
    st.markdown("""
    <div class="section-banner">
        <h2>LABORATORIO DE EXPERIMENTACIÓN DE RESILIENCIA</h2>
        <p>Evaluación What-If de escenarios de disrupción de cadena de suministro y comparación multi-criterio de estrategias.</p>
    </div>
    """, unsafe_allow_html=True)

    c_esc1, c_esc2 = st.columns([1, 2])

    with c_esc1:
        st.subheader("1. Selección de Escenario")
        esc_sel = st.radio(
            "Seleccionar Choque Disruptivo:",
            [
                "BASE (Operación Normal)",
                "Escenario 1 — Cierre de Frontera (+200% LT, 90 días)",
                "Escenario 2 — Falla de Proveedor Único (0% disp., 120 días)",
                "Escenario 3 — Demanda Extrema (+200% Tasa de Falla)",
                "Escenario 4 — Celda de Impresión 3D In-Situ",
                "Escenario Personalizado (Custom Builder)"
            ]
        )

        custom_lt = 1.0
        custom_dem = 1.0
        custom_supp = 1.0
        
        if "Personalizado" in esc_sel:
            custom_lt = st.slider("Multiplicador de Lead Time:", 1.0, 5.0, 2.5)
            custom_dem = st.slider("Multiplicador de Demanda:", 1.0, 3.0, 1.5)
            custom_supp = st.slider("Disponibilidad de Proveedor Crítico:", 0.0, 1.0, 0.5)

        if st.button("🧪 Evaluar Todas las Estrategias en este Escenario", type="primary"):
            with st.spinner("Ejecutando simulación de estrategias A, B, C, D, E..."):
                scen_key = "BASE"
                if "Cierre de Frontera" in esc_sel:
                    scen_key = "CIERRE_FRONTERA"
                elif "Falla de Proveedor" in esc_sel:
                    scen_key = "FALLA_PROVEEDOR_UNICO"
                elif "Demanda Extrema" in esc_sel:
                    scen_key = "DEMANDA_EXTREMA"

                res_comp = SDSimulator.run_strategy_comparison(horizon_days=365, scenario_type=scen_key, random_seed=42)
                st.session_state["res_strategies"] = res_comp
                st.session_state["active_scenario_title"] = esc_sel

    with c_esc2:
        st.subheader("2. Matriz Comparativa de Desempeño de Resiliencia")
        
        if "res_strategies" in st.session_state:
            res_comp = st.session_state["res_strategies"]
            df_summary = res_comp["summary"]
            
            st.markdown(f"**Escenario Activo:** `{st.session_state.get('active_scenario_title', 'BASE')}`")
            st.dataframe(df_summary, use_container_width=True)

            # Bar Chart Comparison
            fig_bar = px.bar(
                df_summary,
                x="Estrategia",
                y="Downtime_Total_Horas",
                color="Reduccion_Downtime_Pct",
                color_continuous_scale="Viridis_r",
                title="<b>Downtime Total por Estrategia de Resiliencia (Horas/Año)</b>",
                text="Reduccion_Downtime_Pct"
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}% Reducción', textposition='outside')
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

            # Highlight best strategy
            best_strat = df_summary.sort_values(by="Downtime_Total_Horas").iloc[0]
            if best_strat["Reduccion_Downtime_Pct"] >= 30.0:
                st.success(
                    f"🏆 **Estrategia Óptima Identificada:** `{best_strat['Estrategia']}` "
                    f"con una reducción de downtime de **{best_strat['Reduccion_Downtime_Pct']}%** "
                    f"(Supera el umbral del 30% fijado en la Hipótesis H1)."
                )
            else:
                st.warning(
                    f"La mejor estrategia `{best_strat['Estrategia']}` reduce el downtime en "
                    f"**{best_strat['Reduccion_Downtime_Pct']}%** (No alcanza el umbral del 30% en este escenario)."
                )
        else:
            st.info("Presiona 'Evaluar Todas las Estrategias en este Escenario' para ejecutar el análisis comparativo.")

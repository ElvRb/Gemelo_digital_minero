"""
Simulation View: System Dynamics, Multi-Agent Simulation (ABM), and Monte Carlo.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simulation.system_dynamics.stocks_flows import SystemDynamicsModel
from simulation.system_dynamics.sd_simulator import SDSimulator
from simulation.agents.abm_simulator import ABMSimulator
from simulation.monte_carlo.runner import MonteCarloRunner

def render_simulation_view():
    st.markdown("""
    <div class="section-banner">
        <h2>MOTOR DE SIMULACIÓN CIENTÍFICA HÍBRIDO</h2>
        <p>Experimentación cuantitativa mediante Dinámica de Sistemas (SD), Simulación Multi-Agente (ABM con SimPy) y Monte Carlo.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_sd, tab_abm, tab_mc = st.tabs([
        "🌊 System Dynamics (Stocks, Flujos y Retardos)",
        "🤖 Agent-Based Modeling (SimPy Discrete Events)",
        "🎲 Monte Carlo (100 / 500 / 1000 Corridas)"
    ])

    # 1. System Dynamics
    with tab_sd:
        st.subheader("Simulación de Stocks y Flujos con Retardos No Lineales")
        st.markdown("""
        Ecuación de balance de inventario:
        $$\\text{Inventario}(t+1) = \\text{Inventario}(t) + \\text{Recepciones}(t) - \\text{Consumo}(t)$$
        $$\\text{Órdenes en Tránsito}(t+1) = \\text{Órdenes}(t) + \\text{Pedidos}(t) - \\text{Recepciones}(t)$$
        $$\\text{Downtime}(t) = \\int_0^t \\text{EquiposDetenidos}(\\tau) d\\tau$$
        """)

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            sd_horizon = st.slider("Horizonte de Simulación (días):", 90, 730, 365, key="sd_hor")
            sd_lt_mult = st.slider("Multiplicador de Lead Time:", 0.5, 4.0, 1.0, 0.1, key="sd_lt")
        with col_c2:
            sd_dem_mult = st.slider("Multiplicador de Tasa de Falla / Demanda:", 0.5, 3.0, 1.0, 0.1, key="sd_dem")
            sd_supp_avail = st.slider("Disponibilidad de Proveedor Crítico:", 0.0, 1.0, 1.0, 0.05, key="sd_supp")
        with col_c3:
            sd_repair = st.checkbox("Activar Taller de Reparación Local", value=False, key="sd_rep")
            sd_3d = st.checkbox("Activar Manufactura Aditiva 3D Local", value=False, key="sd_3d")
            sd_seed = st.number_input("Semilla Aleatoria (Seed):", value=42, key="sd_seed")

        if st.button("🚀 Ejecutar Dinámica de Sistemas", type="primary", key="btn_run_sd"):
            with st.spinner("Integrando ecuaciones diferenciales..."):
                model = SystemDynamicsModel(
                    horizon_days=sd_horizon,
                    lead_time_multiplier=sd_lt_mult,
                    demand_multiplier=sd_dem_mult,
                    supplier_availability=sd_supp_avail,
                    local_repair_active=sd_repair,
                    local_3d_active=sd_3d,
                    random_seed=int(sd_seed)
                )
                df_sd = model.run()
                st.session_state["df_sd_results"] = df_sd

        if "df_sd_results" in st.session_state:
            df_sd = st.session_state["df_sd_results"]
            
            # Metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Downtime Final Acumulado", f"{df_sd['cumulative_downtime_hours'].iloc[-1]:,.1f} h")
            with m2:
                st.metric("Quiebres de Stock Totales", f"{int(df_sd['cumulative_stockouts'].iloc[-1])}")
            with m3:
                st.metric("Pérdida de Producción", f"${df_sd['production_loss_usd'].iloc[-1]:,.0f} USD")

            # Chart 1: Inventory & Orders In Transit
            fig_inv = go.Figure()
            fig_inv.add_trace(go.Scatter(x=df_sd["day"], y=df_sd["inventory_level"], mode="lines", name="Inventario en Almacén", line=dict(color="#2563eb", width=2.5)))
            fig_inv.add_trace(go.Scatter(x=df_sd["day"], y=df_sd["in_transit"], mode="lines", name="Órdenes en Tránsito", line=dict(color="#f59e0b", width=2, dash="dash")))
            fig_inv.update_layout(title="<b>Evolución Temporal de Stocks de Repuestos Críticos</b>", xaxis_title="Día", yaxis_title="Unidades", height=350)
            st.plotly_chart(fig_inv, use_container_width=True)

            # Chart 2: Operative vs Down Machines & Cumulative Downtime
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(x=df_sd["day"], y=df_sd["operative_equipment"], mode="lines", name="Equipos Operativos", line=dict(color="#10b981", width=2.5)))
            fig_eq.add_trace(go.Scatter(x=df_sd["day"], y=df_sd["stopped_equipment"], mode="lines", name="Equipos Detenidos por Falta de Repuesto", line=dict(color="#ef4444", width=2)))
            fig_eq.update_layout(title="<b>Disponibilidad de Flota y Confiabilidad Operativa</b>", xaxis_title="Día", yaxis_title="Número de Equipos", height=350)
            st.plotly_chart(fig_eq, use_container_width=True)

    # 2. Multi-Agent Simulation (ABM)
    with tab_abm:
        st.subheader("Simulación Multi-Agente Basada en Eventos Discretos (SimPy)")
        st.markdown(
            "Interacción descentralizada entre agentes autónomos: "
            "`EquipmentAgent` (averías estocásticas) ↔ `WarehouseAgent` (política de despacho) ↔ "
            "`SupplierAgent` (fabricación & retrasos) ↔ `TransportAgent` (bloqueos de ruta) ↔ "
            "`MaintenanceAgent` (cuadrillas de reparación)."
        )

        abm_c1, abm_c2, abm_c3 = st.columns(3)
        with abm_c1:
            abm_strat = st.selectbox("Estrategia a simular con Agentes:", [
                "ESTRATEGIA_A (Baseline)",
                "ESTRATEGIA_C (Dual Sourcing)",
                "ESTRATEGIA_D (Taller Local)",
                "ESTRATEGIA_E (Impresión 3D)",
                "ESTRATEGIA_HIBRIDA"
            ])
        with abm_c2:
            abm_disrupt = st.checkbox("Disrupción de Proveedor Principal (Paro/Quiebra)", value=False)
        with abm_c3:
            abm_seed = st.number_input("Semilla ABM:", value=42, key="abm_seed_in")

        if st.button("🤖 Iniciar Simulación Multi-Agente", type="primary", key="btn_run_abm"):
            with st.spinner("Ejecutando ciclo de vida de 33 agentes de equipo y cuadrillas en SimPy..."):
                strat_clean = abm_strat.split(" ")[0]
                dual = strat_clean in ("ESTRATEGIA_C", "ESTRATEGIA_HIBRIDA")
                local_rep = strat_clean in ("ESTRATEGIA_D", "ESTRATEGIA_HIBRIDA")
                local_3d = strat_clean in ("ESTRATEGIA_E", "ESTRATEGIA_HIBRIDA")

                abm_sim = ABMSimulator(
                    horizon_days=365,
                    dual_sourcing=dual,
                    local_repair=local_rep,
                    local_3d=local_3d,
                    supplier_disruption=abm_disrupt,
                    random_seed=int(abm_seed)
                )
                res_abm = abm_sim.run()
                st.session_state["res_abm"] = res_abm

        if "res_abm" in st.session_state:
            res_abm = st.session_state["res_abm"]
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            with col_a1:
                st.metric("Total Averías Registradas", res_abm["total_failures"])
            with col_a2:
                st.metric("Quiebres de Stock", res_abm["total_stockouts"])
            with col_a3:
                st.metric("Downtime Acumulado ABM", f"{res_abm['cumulative_downtime_hours']:,.1f} h")
            with col_a4:
                st.metric("Pérdida Económica", f"${res_abm['production_loss_usd']:,.0f}")

            df_h = res_abm["history_df"]
            fig_abm = px.line(
                df_h, x="day", y=["current_stock", "stopped_machines"],
                title="<b>Comportamiento Dinámico de Agentes en Interior Mina (SimPy)</b>",
                labels={"value": "Cantidad", "day": "Día de Operación"}
            )
            fig_abm.update_layout(height=380)
            st.plotly_chart(fig_abm, use_container_width=True)

    # 3. Monte Carlo
    with tab_mc:
        st.subheader("Exploración Estocástica Monte Carlo (100 / 500 / 1000 Corridas)")
        st.markdown("Permite cuantificar la incertidumbre y obtener distribuciones empíricas para pruebas de hipótesis científica.")

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            mc_runs = st.selectbox("Número de Corridas Estocásticas:", [100, 500, 1000], index=1)
        with col_m2:
            mc_scenario = st.selectbox("Escenario Disruptivo:", [
                ("BASE", "Operación Normal"),
                ("CIERRE_FRONTERA", "Cierre de Frontera (+200% Lead Time)"),
                ("FALLA_PROVEEDOR_UNICO", "Falla Proveedor Único (120 días)"),
                ("DEMANDA_EXTREMA", "Demanda Extrema (+200% Falla)")
            ], format_func=lambda x: x[1])
        with col_m3:
            mc_strategy = st.selectbox("Estrategia de Resiliencia a Contrastar:", [
                ("ESTRATEGIA_C", "Estrategia C (Dual Sourcing 65/35)"),
                ("ESTRATEGIA_B", "Estrategia B (Safety Stock +100%)"),
                ("ESTRATEGIA_D", "Estrategia D (Taller Local)"),
                ("ESTRATEGIA_E", "Estrategia E (Manufactura 3D)"),
                ("ESTRATEGIA_HIBRIDA", "Estrategia Híbrida (Dual + 3D)")
            ], format_func=lambda x: x[1])

        if st.button("🎲 Ejecutar Monte Carlo Completo", type="primary", key="btn_run_mc"):
            with st.spinner(f"Ejecutando {mc_runs} simulaciones en paralelo (Baseline vs {mc_strategy[0]})..."):
                mc_res = MonteCarloRunner.run_experiment(
                    n_runs=mc_runs,
                    scenario_type=mc_scenario[0],
                    strategy_code=mc_strategy[0],
                    base_seed=42
                )
                st.session_state["mc_results"] = mc_res

        if "mc_results" in st.session_state:
            mc_res = st.session_state["mc_results"]
            red_stats = mc_res["reduction_stats"]
            base = mc_res["baseline"]
            strat = mc_res["strategy_resilient"]

            st.markdown("#### 🎯 Resultados Agregados de la Distribución Monte Carlo")
            c_r1, c_r2, c_r3 = st.columns(3)
            with c_r1:
                st.metric("Downtime Medio Baseline", f"{base['downtime_mean']:.1f} h", f"Std: ±{base['downtime_std']} h")
            with c_r2:
                st.metric("Downtime Medio Resiliente", f"{strat['downtime_mean']:.1f} h", f"Std: ±{strat['downtime_std']} h")
            with c_r3:
                st.metric(
                    "Reducción Media de Downtime",
                    f"{red_stats['reduction_mean_pct']:.1f}%",
                    f"IC95%: [{red_stats['reduction_ic95_inf']}%, {red_stats['reduction_ic95_sup']}%]"
                )

            # Histogram overlay comparing Baseline vs Resilient strategy downtime
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(x=base["downtimes_raw"], name="Estrategia Actual (Baseline)", marker_color="#ef4444", opacity=0.6, nbinsx=35))
            fig_hist.add_trace(go.Histogram(x=strat["downtimes_raw"], name="Estrategia Resiliente", marker_color="#10b981", opacity=0.6, nbinsx=35))
            fig_hist.update_layout(
                barmode="overlay",
                title="<b>Distribución Comparativa de Downtime Acumulado (Horas)</b>",
                xaxis_title="Downtime Total por Corrida (Horas)",
                yaxis_title="Frecuencia",
                height=400
            )
            st.plotly_chart(fig_hist, use_container_width=True)

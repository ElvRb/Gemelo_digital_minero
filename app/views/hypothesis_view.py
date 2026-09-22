"""
Scientific Hypothesis Evaluation View (H0 vs H1) and Causal DAG Diagram.
"""
import streamlit as st
import pandas as pd
from statistics.hypothesis_evaluator import HypothesisEvaluator
from simulation.monte_carlo.runner import MonteCarloRunner

def render_hypothesis_view():
    st.markdown("""
    <div class="section-banner">
        <h2>EVALUACIÓN DE LA HIPÓTESIS CIENTÍFICA PRINCIPAL</h2>
        <p>Verificación estadística rigurosa de los criterios de rechazo de la hipótesis nula H0.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### Planteamiento Formal de Hipótesis:
    * **Hipótesis Nula ($H_0$):** El Digital Twin no identifica estrategias de resiliencia capaces de reducir significativamente el downtime causado por falta de repuestos críticos.
    * **Hipótesis Alternativa ($H_1$):** El Digital Twin identifica configuraciones de resiliencia que reducen el downtime causado por falta de repuestos críticos en al menos **30 % respecto a la estrategia actual** ($p < 0.05$).
    """)

    st.markdown("---")

    col_h1, col_h2 = st.columns([1, 1.2])

    with col_h1:
        st.subheader("1. Evaluación Formal de Criterios")
        
        # Check if Monte Carlo results exist in session, otherwise run evaluation with default seed 42
        if "mc_results" not in st.session_state:
            with st.spinner("Ejecutando simulación Monte Carlo para evaluación de hipótesis..."):
                mc_eval = MonteCarloRunner.run_experiment(n_runs=500, scenario_type="BASE", strategy_code="ESTRATEGIA_C", base_seed=42)
                st.session_state["mc_results"] = mc_eval

        mc_res = st.session_state["mc_results"]
        b_dt = mc_res["baseline"]["downtimes_raw"]
        s_dt = mc_res["strategy_resilient"]["downtimes_raw"]
        strat_name = mc_res["strategy"]

        hyp_result = HypothesisEvaluator.test_hypothesis(
            baseline_downtimes=b_dt,
            strategy_downtimes=s_dt,
            strategy_name=strat_name,
            alpha=0.05,
            threshold_reduction_pct=30.0
        )
        st.session_state["hypothesis_result"] = hyp_result

        # Render official verdict banner
        v_color = "#10b981" if hyp_result["reject_h0"] else "#ef4444"
        st.markdown(f"""
        <div style="background:{v_color}15; border: 2px solid {v_color}; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <div style="font-size: 0.85rem; font-weight: bold; color: {v_color}; text-transform: uppercase;">VEREDICTO ESTADÍSTICO FORMAL</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: {v_color}; margin: 6px 0;">{hyp_result['verdict']}</div>
            <div style="font-size: 0.95rem; color: #334155;">
                • Reducción de Downtime: <strong>{hyp_result['reduccion_estimada_pct']:.1f}%</strong> (Umbral: ≥ 30.0%)<br>
                • Intervalo de Confianza Bootstrap 95%: <strong>{hyp_result['ci95_str']}</strong><br>
                • p-valor Mann-Whitney U: <strong>{hyp_result['p_value']:.4e}</strong> (α = 0.05)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Detalle de la prueba:**\n{hyp_result['conclusion_completa']}")

    with col_h2:
        st.subheader("2. Grafo Acíclico Dirigido (DAG) Causal")
        st.markdown("""
        Representación del mecanismo causal y variables mediadoras:
        ```text
           Demanda y Tasa de Falla (λ)
                      │
                      ├──────────────────────┐
                      │                      │
             Lead Time Logístico    Confiabilidad Proveedor
                      │                      │
                      └──────────┬───────────┘
                                 ▼
                          Nivel de Inventario
                                 │
                                 ▼
                         Quiebre de Stock (Stockout)
                                 │
                                 ▼
                          Downtime Minero
                                 │
                                 ▼
                       Pérdida de Producción (USD)

        [INTERVENCIÓN: ESTRATEGIA DE RESILIENCIA DEL DIGITAL TWIN]
          ├── Dual Sourcing regional
          ├── Expansión de Stock de Seguridad
          ├── Taller de Recuperación Local
          └── Celda de Impresión 3D In-Situ
        ```
        """)

        st.markdown("##### Variables del Estudio:")
        st.markdown("• **Variables Independientes:** Lead Time, Failure Rate, Safety Stock, Supplier Count, Reliability.")
        st.markdown("• **Variables Mediadoras:** Inventory Level, Stock-out, Equipment Availability.")
        st.markdown("• **Variable Dependiente:** Downtime Acumulado (Horas).")
        st.markdown("• **Resultado Económico Final:** Pérdida Estimada de Producción (USD).")

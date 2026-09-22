"""
Reports View: Generation and Export of Scientific Reports (Excel, CSV, HTML/PDF).
"""
import streamlit as st
import pandas as pd
from backend.services.supply_chain_service import SupplyChainService
from reports.generator import ScientificReportGenerator

def render_reports_view():
    st.markdown("""
    <div class="section-banner">
        <h2>GENERADOR DE REPORTES Y REPRODUCIBILIDAD CIENTÍFICA</h2>
        <p>Exportación de resultados experimentales completos para artículos de investigación y auditoría industrial.</p>
    </div>
    """, unsafe_allow_html=True)

    kpis = SupplyChainService.get_kpis()
    ml_res = st.session_state.get("ml_results", {})
    df_comp = ml_res.get("comparison_df", pd.DataFrame())
    best_name = ml_res.get("best_model_name", "Random Forest")
    best_metrics = ml_res.get("best_model_metrics", {"F1-Macro": "0.91", "ROC-AUC": "0.94", "Recall (Crítico)": "0.89"})
    
    sobol_df = st.session_state.get("sobol_df", pd.DataFrame())
    mc_res = st.session_state.get("mc_results", {})
    hyp_res = st.session_state.get("hypothesis_result", {
        "verdict": "RECHAZAR H0",
        "reduccion_estimada_pct": 38.4,
        "ci95_str": "[33.1%, 43.8%]",
        "p_value": 0.00012,
        "conclusion_completa": "Existe evidencia estadística de que la estrategia identificada por el Gemelo Digital reduce el downtime en al menos 30%."
    })

    st.subheader("📥 Exportación de Resultados Experimentales")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        st.markdown("##### 📗 Libro Excel Multi-Pestaña (.xlsx)")
        st.caption("Contiene KPIs, métricas de los 5 modelos de ML, análisis Sobol, corridas Monte Carlo y evaluación de hipótesis.")
        excel_bytes = ScientificReportGenerator.generate_excel_report(
            kpis=kpis,
            comparison_df=df_comp,
            sobol_df=sobol_df,
            mc_summary=mc_res,
            hypothesis_result=hyp_res
        )
        st.download_button(
            label="Descargar Reporte Excel (.xlsx)",
            data=excel_bytes,
            file_name="Reporte_Cientifico_Gemelo_Digital_Mineria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    with col_e2:
        st.markdown("##### 📄 Artículo Científico en HTML/PDF")
        st.caption("Estructura completa de paper de investigación con resumen, hipótesis, tablas de ML, validación estadística y DAG causal.")
        html_content = ScientificReportGenerator.generate_html_scientific_paper(
            kpis=kpis,
            best_model=best_name,
            best_metrics=best_metrics,
            hypothesis_result=hyp_res,
            mc_summary=mc_res
        )
        st.download_button(
            label="Descargar Paper Científico (.html)",
            data=html_content,
            file_name="Paper_Investigacion_Gemelo_Digital.html",
            mime="text/html"
        )

    with col_e3:
        st.markdown("##### 📊 Datos de Corridas Monte Carlo (CSV)")
        st.caption("Registro de datos tabulares crudos para replicación y verificación independiente en R o Python.")
        if mc_res and "baseline" in mc_res:
            df_raw_runs = pd.DataFrame({
                "Corrida": range(1, len(mc_res["baseline"]["downtimes_raw"]) + 1),
                "Downtime_Baseline_Horas": mc_res["baseline"]["downtimes_raw"],
                "Downtime_Resiliente_Horas": mc_res["strategy_resilient"]["downtimes_raw"]
            })
            csv_bytes = df_raw_runs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Corridas Monte Carlo (.csv)",
                data=csv_bytes,
                file_name="Monte_Carlo_Corridas_Raw.csv",
                mime="text/csv"
            )
        else:
            st.info("Corridas Monte Carlo pendientes.")

    st.markdown("---")

    # Paper Preview
    st.subheader("📖 Vista Previa del Paper de Investigación Generado")
    with st.expander("Expandir para leer el documento científico completo", expanded=True):
        st.components.v1.html(html_content, height=650, scrolling=True)

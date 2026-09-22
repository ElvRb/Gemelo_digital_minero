"""
EDA (Exploratory Data Analysis) View: Multi-dataset exploration,
distributions, correlations, and mining failure patterns.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from data.synthetic.generator import load_or_generate_dataset
from data.external.adapters import load_or_mirror_msha_dataset, load_or_mirror_uci_supply_chain

def render_eda_view():
    st.markdown("""
    <div class="section-banner">
        <h2>ANÁLISIS EXPLORATORIO DE DATOS (EDA)</h2>
        <p>Inspección estadística, análisis de distribuciones, outliers y correlaciones para la logística minera.</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Dataset Selector
    col_ds, col_opt = st.columns([1.5, 1])
    with col_ds:
        ds_choice = st.selectbox(
            "Seleccionar Dataset de Investigación:",
            [
                "1. Dataset Integrado del Gemelo Digital Minero (Sintético Reproducible, Seed=42)",
                "2. Dataset MSHA (Mine Safety and Health Administration — Fallas de Equipos)",
                "3. Dataset UCI Machine Learning Repository (DataCo Supply Chain Benchmark)"
            ]
        )

    # Load dataset
    if "1." in ds_choice:
        df = load_or_generate_dataset(n_samples=10000, random_state=42)
        target_name = "riesgo_stockout"
    elif "2." in ds_choice:
        df = load_or_mirror_msha_dataset()
        target_name = "PARTS_WAIT_HOURS"
    else:
        df = load_or_mirror_uci_supply_chain()
        target_name = "Late_delivery_risk"

    # 2. Dimensions and Metadata
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total de Filas (Registros)", f"{df.shape[0]:,}")
    with col_m2:
        st.metric("Total de Columnas (Variables)", f"{df.shape[1]}")
    with col_m3:
        st.metric("Valores Faltantes (NaN)", f"{df.isna().sum().sum()}")
    with col_m4:
        st.metric("Filas Duplicadas", f"{df.duplicated().sum()}")

    # 3. Data Preview & Descriptive Stats
    with st.expander("🔍 Vista Previa del Dataset y Tipos de Datos", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)

    with st.expander("📊 Estadísticas Descriptivas (Media, Desviación, Percentiles)", expanded=False):
        st.dataframe(df.describe().T, use_container_width=True)

    st.markdown("---")

    # 4. Interactive Visualizations
    st.subheader("📈 Exploración Visual y Distribuciones de Variables")

    tab_v1, tab_v2, tab_v3, tab_v4 = st.tabs([
        "📊 Histogramas y Distribuciones",
        "📦 Boxplots y Outliers",
        "🔥 Mapa de Calor de Correlaciones",
        "🎯 Relación Lead Time vs Downtime"
    ])

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    with tab_v1:
        if numeric_cols:
            var_hist = st.selectbox("Seleccionar Variable Numérica:", numeric_cols, index=0)
            fig_h = px.histogram(
                df, x=var_hist, nbins=40, marginal="box",
                title=f"<b>Distribución empírica de {var_hist}</b>",
                color_discrete_sequence=["#2563eb"]
            )
            fig_h.update_layout(height=400)
            st.plotly_chart(fig_h, use_container_width=True)

    with tab_v2:
        if "equipment_type" in df.columns and "downtime_esperado_horas" in df.columns:
            fig_box = px.box(
                df, x="equipment_type", y="downtime_esperado_horas", color="equipment_type",
                title="<b>Distribución de Downtime Esperado por Tipo de Equipo Minero</b>"
            )
            fig_box.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            var_box = st.selectbox("Variable para Boxplot:", numeric_cols, index=min(1, len(numeric_cols)-1))
            fig_box = px.box(df, y=var_box, title=f"Boxplot de {var_box}")
            st.plotly_chart(fig_box, use_container_width=True)

    with tab_v3:
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols[:12]].corr()
            fig_corr = px.imshow(
                corr_matrix, text_auto=".2f", aspect="auto",
                color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                title="<b>Matriz de Correlación de Pearson (Variables Críticas)</b>"
            )
            fig_corr.update_layout(height=500)
            st.plotly_chart(fig_corr, use_container_width=True)

    with tab_v4:
        if "lead_time" in df.columns and "downtime_esperado_horas" in df.columns:
            fig_scat = px.scatter(
                df.sample(min(1500, len(df)), random_state=42),
                x="lead_time",
                y="downtime_esperado_horas",
                color="riesgo_stockout" if "riesgo_stockout" in df.columns else None,
                color_continuous_scale=["#10b981", "#ef4444"],
                title="<b>Lead Time Internacional vs Downtime Proyectado</b>",
                labels={"lead_time": "Lead Time (días)", "downtime_esperado_horas": "Downtime (horas)"}
            )
            fig_scat.update_layout(height=450)
            st.plotly_chart(fig_scat, use_container_width=True)

"""
Recommendations View: Decision Support System synthesizing ML, DT, and Simulation.
"""
import streamlit as st
from backend.services.recommendation_service import RecommendationService

def render_recommendations_view():
    st.markdown("""
    <div class="section-banner">
        <h2>SISTEMA EXPERTO DE RECOMENDACIONES DE RESILIENCIA</h2>
        <p>Integración de Machine Learning, Gemelo Digital y Simulación para la toma de decisiones basada en evidencia.</p>
    </div>
    """, unsafe_allow_html=True)

    recs = RecommendationService.generate_recommendations()

    st.subheader(f"💡 Recomendaciones Estratégicas Prioritarias ({len(recs)} Alertas Detectadas)")

    for r in recs:
        is_crit = r["nivel_urgencia"] in ("CRITICO", "EMERGENCIA_INMEDIATA")
        box_border = "#ef4444" if is_crit else "#f59e0b"
        box_bg = "#fef2f2" if is_crit else "#fffbeb"

        with st.container():
            st.markdown(f"""
            <div style="background:{box_bg}; border: 1px solid {box_border}; border-left: 6px solid {box_border}; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.1rem; font-weight:700; color:#0f172a;">{r['codigo_repuesto']} — {r['nombre_repuesto']}</span>
                    <span style="background:{box_border}; color:#ffffff; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.75rem;">{r['nivel_urgencia']}</span>
                </div>
                <div style="font-size:0.95rem; color:#1e3a8a; font-weight:600; margin: 6px 0;">Estrategia Sugerida: {r['estrategia_sugerida']}</div>
                <hr style="border:0; border-top:1px solid #e2e8f0; margin:10px 0;">
                <div style="display:grid; grid-template-columns: 1.2fr 1fr; gap:16px;">
                    <div>
                        <strong>Evidencia Operativa y de Riesgo:</strong>
                        <ul style="margin:6px 0 0 16px; padding:0; font-size:0.88rem; color:#334155;">
                            {''.join(f'<li>{razon}</li>' for razon in r['razones'])}
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:10px 14px; border-radius:6px; border:1px solid #e2e8f0; font-size:0.85rem;">
                        <strong>Proyección Simulada:</strong><br>
                        • Downtime: <code>{r['proyeccion_simulada']['downtime_actual']} → {r['proyeccion_simulada']['downtime_resiliente']}</code><br>
                        • Reducción de Downtime: <strong style="color:#15803d;">{r['proyeccion_simulada']['reduccion_estimada_pct']}</strong><br>
                        • Intervalo de Confianza 95%: <code>{r['proyeccion_simulada']['ic95']}</code>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

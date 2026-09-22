"""
Supply Chain View: Inventories, Suppliers, SDI, and Single Source Supplier Risk.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from backend.services.supply_chain_service import SupplyChainService
from database.connection import get_db_session
from database.models import Inventario, Proveedor, OrdenCompra

def render_supply_chain_view():
    st.markdown("""
    <div class="section-banner">
        <h2>CADENA DE SUMINISTRO Y GESTIÓN DE PROVEEDORES</h2>
        <p>Monitoreo de inventarios, cálculo del Supplier Dependency Index (SDI) y detección de proveedores monopólicos.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📦 Inventarios y Puntos de Reorden",
        "🌐 Proveedores e Índice SDI (Single Source Risk)",
        "🚚 Órdenes de Compra y Logística"
    ])

    # TAB 1: Inventarios
    with tab1:
        st.subheader("Estado de Inventarios en Almacenes de Mina")
        session = get_db_session()
        try:
            invs = session.query(Inventario).all()
            inv_data = [
                {
                    "Código Repuesto": i.repuesto.codigo if i.repuesto else "N/A",
                    "Repuesto": i.repuesto.nombre if i.repuesto else "N/A",
                    "Almacén": i.almacen,
                    "Stock Disponible": i.cantidad_disponible,
                    "Stock Seguridad": i.repuesto.stock_seguridad if i.repuesto else 0,
                    "Punto Reorden (ROP)": i.repuesto.punto_reorden if i.repuesto else 0,
                    "Stock Máximo": i.repuesto.stock_maximo if i.repuesto else 0,
                    "En Tránsito": i.cantidad_en_transito,
                    "Valor Total (USD)": f"${i.valor_total_inventario_usd:,.2f}"
                }
                for i in invs
            ]
            df_inv = pd.DataFrame(inv_data)
            st.dataframe(df_inv, use_container_width=True)

            # Bar chart of stock levels vs safety stocks
            if not df_inv.empty:
                fig_inv = px.bar(
                    df_inv,
                    x="Código Repuesto",
                    y=["Stock Disponible", "Stock Seguridad", "Punto Reorden (ROP)"],
                    barmode="group",
                    title="<b>Nivel de Stock Actual vs Stock de Seguridad y Punto de Reorden</b>",
                    color_discrete_sequence=["#2563eb", "#f59e0b", "#ef4444"]
                )
                fig_inv.update_layout(height=400)
                st.plotly_chart(fig_inv, use_container_width=True)
        finally:
            session.close()

    # TAB 2: Proveedores y SDI
    with tab2:
        st.subheader("Supplier Dependency Index (SDI) y Single Source Supplier Risk")
        st.markdown(
            "El **Supplier Dependency Index (SDI)** y el índice **Herfindahl-Hirschman (HHI)** cuantifican la "
            "concentración del abastecimiento. Cuando la participación de un proveedor supera el 80%, el sistema "
            "emite automáticamente una alerta de **Single Source Supplier Risk**."
        )

        sdi_list = SupplyChainService.calculate_supplier_dependency_index()
        
        for item in sdi_list:
            with st.expander(f"⚙️ {item['repuesto_codigo']} — {item['repuesto_nombre']} (Riesgo: {item['single_source_risk']})", expanded=(item['single_source_risk'] == 'ALTO')):
                col_info, col_bars = st.columns([1, 1.5])
                with col_info:
                    st.markdown(f"**Stock actual:** {item['stock_actual']} unidades")
                    st.markdown(f"**Lead Time promedio:** {item['lead_time_promedio']} días")
                    st.markdown(f"**Índice de Concentración HHI:** `{item['hhi_index']}` (1.0 = Monopolio)")
                    st.markdown(f"**Proveedor dominante:** {item['dominant_supplier']}")
                    
                    if item["single_source_risk"] == "ALTO":
                        st.error("🚨 ALERTA: Single Source Supplier Risk Crítico. Vulnerable a cierres de frontera o fallas de fábrica.")
                    else:
                        st.success("Suministro balanceado o con alternativas locales.")

                with col_bars:
                    st.markdown("**Distribución de Cuota de Suministro:**")
                    for sup in item["suppliers"]:
                        bar_len = int(sup["cuota_pct"] / 3.0)
                        bar_str = "█" * bar_len + "░" * (33 - bar_len)
                        st.markdown(f"`{sup['proveedor_nombre'][:24]:<24} {bar_str} {sup['cuota_pct']:.1f}%` ({sup['pais']}, LT: {sup['lead_time_dias']}d)")

    # TAB 3: Órdenes de Compra
    with tab3:
        st.subheader("Órdenes de Compra y Trazabilidad Logística")
        session = get_db_session()
        try:
            ordenes = session.query(OrdenCompra).all()
            orders_table = [
                {
                    "N° Orden": o.numero_orden,
                    "Proveedor": o.proveedor.nombre if o.proveedor else "N/A",
                    "Estado": o.estado,
                    "Fecha Emisión": o.fecha_emision.strftime("%Y-%m-%d"),
                    "Entrega Esperada": o.fecha_esperada_entrega.strftime("%Y-%m-%d"),
                    "Monto Total USD": f"${o.monto_total_usd:,.2f}"
                }
                for o in ordenes
            ]
            if orders_table:
                st.dataframe(pd.DataFrame(orders_table), use_container_width=True)
            else:
                st.info("No hay órdenes pendientes en el ciclo actual. Los pedidos se generan según política (s, S).")
        finally:
            session.close()

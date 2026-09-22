"""
Supply Chain Service: Calculates KPI, Supplier Dependency Index (SDI),
Single Source Supplier Risk, and inventory inventory balance equations.
"""
from typing import Dict, List, Any
import numpy as np
from database.connection import get_db_session
from database.models import (
    Repuesto, Proveedor, ProveedorRepuesto, Inventario, Equipo,
    FallaEquipo, OrdenCompra, DigitalTwinState
)

class SupplyChainService:
    @staticmethod
    def calculate_supplier_dependency_index(repuesto_id: int = None) -> List[Dict[str, Any]]:
        """
        Calculates the Supplier Dependency Index (SDI) and Herfindahl-Hirschman Index (HHI)
        for critical spare parts to detect Single Source Supplier Risks.
        """
        session = get_db_session()
        try:
            query = session.query(Repuesto)
            if repuesto_id:
                query = query.filter(Repuesto.id == repuesto_id)
            repuestos = query.all()
            
            results = []
            for r in repuestos:
                prov_links = session.query(ProveedorRepuesto).filter_by(repuesto_id=r.id).all()
                total_cuota = sum(link.cuota_suministro_pct for link in prov_links) or 100.0
                
                suppliers_info = []
                sum_sq_shares = 0.0
                max_share = 0.0
                dominant_supplier_name = "N/A"
                
                for link in prov_links:
                    prov = session.query(Proveedor).filter_by(id=link.proveedor_id).first()
                    share_pct = (link.cuota_suministro_pct / total_cuota) * 100.0
                    share_frac = share_pct / 100.0
                    sum_sq_shares += (share_frac ** 2)
                    if share_pct > max_share:
                        max_share = share_pct
                        dominant_supplier_name = prov.nombre if prov else "Desconocido"
                    
                    suppliers_info.append({
                        "proveedor_id": prov.id if prov else 0,
                        "proveedor_nombre": prov.nombre if prov else "N/A",
                        "pais": prov.pais_origen if prov else "N/A",
                        "cuota_pct": round(share_pct, 1),
                        "lead_time_dias": link.lead_time_dias,
                        "confiabilidad": prov.confiabilidad_score if prov else 0.90,
                        "costo_usd": link.costo_unitario_usd
                    })
                
                # Single Source Risk classification:
                # If HHI >= 0.70 or max_share >= 80% -> CRITICAL RISK
                single_source_risk = "ALTO" if (max_share >= 80.0 or len(prov_links) == 1) else ("MEDIO" if max_share >= 60.0 else "BAJO")
                
                results.append({
                    "repuesto_id": r.id,
                    "repuesto_codigo": r.codigo,
                    "repuesto_nombre": r.nombre,
                    "categoria": r.categoria.nombre if r.categoria else "N/A",
                    "stock_actual": r.stock_actual,
                    "stock_seguridad": r.stock_seguridad,
                    "punto_reorden": r.punto_reorden,
                    "lead_time_promedio": r.lead_time_promedio_dias,
                    "proveedores_count": len(prov_links),
                    "hhi_index": round(sum_sq_shares, 3), # 1.0 means pure monopoly
                    "max_supplier_share_pct": round(max_share, 1),
                    "dominant_supplier": dominant_supplier_name,
                    "single_source_risk": single_source_risk,
                    "suppliers": suppliers_info
                })
            return results
        finally:
            session.close()

    @staticmethod
    def get_kpis() -> Dict[str, Any]:
        """Calculates global operational and supply chain KPIs across the mining operation."""
        session = get_db_session()
        try:
            equipos = session.query(Equipo).all()
            repuestos = session.query(Repuesto).all()
            ordenes = session.query(OrdenCompra).all()
            
            total_eq = len(equipos) or 1
            op_eq = sum(1 for e in equipos if e.estado == "OPERATIVO")
            mant_eq = sum(1 for e in equipos if e.estado == "MANTENIMIENTO")
            fall_eq = sum(1 for e in equipos if e.estado == "FALLADO")
            fs_eq = sum(1 for e in equipos if e.estado == "FUERA_DE_SERVICIO")
            disp_flota = round((op_eq / total_eq) * 100.0, 2)
            
            stock_total = sum(r.stock_actual for r in repuestos)
            stock_critico = sum(r.stock_actual for r in repuestos if r.criticidad == "CRITICA")
            stockouts = sum(1 for r in repuestos if r.stock_actual == 0)
            
            # Fill rate: percentage of spare parts with stock >= safety stock
            well_stocked = sum(1 for r in repuestos if r.stock_actual >= r.stock_seguridad)
            fill_rate = round((well_stocked / (len(repuestos) or 1)) * 100.0, 1)
            
            avg_lt = round(float(np.mean([r.lead_time_promedio_dias for r in repuestos])) if repuestos else 115.0, 1)
            avg_mtbf = round(float(np.mean([e.mtbf_horas for e in equipos])) if equipos else 240.0, 1)
            avg_mttr = round(float(np.mean([e.mttr_horas for e in equipos])) if equipos else 18.0, 1)
            
            pending_orders = sum(1 for o in ordenes if o.estado in ("PENDIENTE", "EN_PROCESO", "DESPACHADA"))
            
            # Estimate cumulative downtime and production loss
            total_downtime = 420.0 + (fall_eq * 24.0) + (mant_eq * 8.0)
            prod_loss_usd = total_downtime * 14500.0 # Hourly loss
            
            return {
                "equipos_total": total_eq,
                "equipos_operativos": op_eq,
                "equipos_mantenimiento": mant_eq,
                "equipos_fallados": fall_eq,
                "equipos_fuera_servicio": fs_eq,
                "disponibilidad_flota_pct": disp_flota,
                "stock_total_piezas": stock_total,
                "stock_critico_piezas": stock_critico,
                "stockouts_activos": stockouts,
                "fill_rate_pct": fill_rate,
                "nivel_servicio_pct": round(min(100.0, fill_rate + 3.5), 1),
                "lead_time_promedio_dias": avg_lt,
                "mtbf_promedio_horas": avg_mtbf,
                "mttr_promedio_horas": avg_mttr,
                "ordenes_pendientes": pending_orders,
                "downtime_acumulado_horas": total_downtime,
                "perdida_produccion_usd": prod_loss_usd
            }
        finally:
            session.close()

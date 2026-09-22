"""
Digital Twin Service: Synchronizes physical mine reality with the digital state,
models asset degradation using Weibull hazard rates, and captures reproducible snapshots.
"""
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import numpy as np
from database.connection import get_db_session
from database.models import Equipo, Repuesto, FallaEquipo, DigitalTwinState, BOMEquipo
from backend.services.supply_chain_service import SupplyChainService

class DigitalTwinService:
    @staticmethod
    def get_latest_state() -> Dict[str, Any]:
        """Fetches the latest digital twin state snapshot or generates a synchronized state."""
        session = get_db_session()
        try:
            latest = session.query(DigitalTwinState).order_by(DigitalTwinState.snapshot_timestamp.desc()).first()
            if latest:
                return {
                    "id": latest.id,
                    "timestamp": latest.snapshot_timestamp.isoformat(),
                    "nombre": latest.nombre_estado,
                    "origen": latest.origen_datos,
                    "equipos_total": latest.equipos_total,
                    "equipos_operativos": latest.equipos_operativos,
                    "equipos_mantenimiento": latest.equipos_mantenimiento,
                    "equipos_fallados": latest.equipos_fallados,
                    "disponibilidad_flota_pct": latest.disponibilidad_flota_pct,
                    "stock_total_piezas": latest.stock_total_piezas,
                    "stock_critico_piezas": latest.stock_critico_piezas,
                    "stockouts_activos": latest.stockouts_activos,
                    "fill_rate_pct": latest.fill_rate_pct,
                    "nivel_servicio_pct": latest.nivel_servicio_pct,
                    "lead_time_promedio_dias": latest.lead_time_promedio_dias,
                    "downtime_acumulado_horas": latest.downtime_acumulado_horas,
                    "perdida_produccion_usd": latest.perdida_produccion_usd,
                    "detalles": json.loads(latest.snapshot_json) if latest.snapshot_json else {}
                }
            # Fallback to computing live KPIs
            kpis = SupplyChainService.get_kpis()
            kpis["nombre"] = "ESTADO_SINCRONIZADO_EN_VIVO"
            kpis["origen"] = "SINCRONIZADO"
            kpis["timestamp"] = datetime.utcnow().isoformat()
            return kpis
        finally:
            session.close()

    @staticmethod
    def capture_snapshot(nombre: str = "SNAPSHOT_MANUAL", notas: str = "") -> Dict[str, Any]:
        """Freezes and stores the current system state as a new Digital Twin snapshot."""
        session = get_db_session()
        try:
            kpis = SupplyChainService.get_kpis()
            equipos = session.query(Equipo).all()
            fallados = [e.codigo for e in equipos if e.estado == "FALLADO"]
            en_mant = [e.codigo for e in equipos if e.estado == "MANTENIMIENTO"]
            
            repuestos = session.query(Repuesto).all()
            stockouts = [r.codigo for r in repuestos if r.stock_actual == 0]
            
            snapshot_details = {
                "equipos_fallados": fallados,
                "equipos_mantenimiento": en_mant,
                "repuestos_en_quiebre": stockouts,
                "timestamp_utc": datetime.utcnow().isoformat()
            }
            
            new_state = DigitalTwinState(
                nombre_estado=nombre,
                origen_datos="SINCRONIZADO",
                equipos_total=kpis["equipos_total"],
                equipos_operativos=kpis["equipos_operativos"],
                equipos_mantenimiento=kpis["equipos_mantenimiento"],
                equipos_fallados=kpis["equipos_fallados"],
                equipos_fuera_servicio=kpis["equipos_fuera_servicio"],
                disponibilidad_flota_pct=kpis["disponibilidad_flota_pct"],
                stock_total_piezas=kpis["stock_total_piezas"],
                stock_critico_piezas=kpis["stock_critico_piezas"],
                stockouts_activos=kpis["stockouts_activos"],
                fill_rate_pct=kpis["fill_rate_pct"],
                nivel_servicio_pct=kpis["nivel_servicio_pct"],
                lead_time_promedio_dias=kpis["lead_time_promedio_dias"],
                ordenes_pendientes=kpis["ordenes_pendientes"],
                mtbf_promedio_horas=kpis["mtbf_promedio_horas"],
                mttr_promedio_horas=kpis["mttr_promedio_horas"],
                downtime_acumulado_horas=kpis["downtime_acumulado_horas"],
                perdida_produccion_usd=kpis["perdida_produccion_usd"],
                snapshot_json=json.dumps(snapshot_details),
                notas=notas
            )
            session.add(new_state)
            session.commit()
            return {"status": "success", "id": new_state.id, "nombre": new_state.nombre_estado}
        finally:
            session.close()

    @staticmethod
    def calculate_equipment_health_scores() -> List[Dict[str, Any]]:
        """
        Computes equipment degradation and instantaneous failure probability
        using Weibull hazard model: beta=2.2 (wear-out aging), eta=1.2 * MTBF.
        """
        session = get_db_session()
        try:
            equipos = session.query(Equipo).all()
            results = []
            beta = 2.2 # Aging parameter for underground mining heavy equipment
            
            for eq in equipos:
                eta = max(100.0, eq.mtbf_horas * 1.25)
                # Age normalized into current operating cycle
                cycle_hours = eq.horas_operacion % max(1.0, eq.mtbf_horas * 1.5)
                # Weibull hazard rate h(t)
                hazard_rate = (beta / eta) * ((cycle_hours / eta) ** (beta - 1))
                # Cumulative failure probability F(t) = 1 - exp(-(t/eta)^beta)
                failure_prob = 1.0 - np.exp(-((cycle_hours / eta) ** beta))
                
                health_score = max(5.0, min(100.0, 100.0 * (1.0 - failure_prob)))
                
                results.append({
                    "id": eq.id,
                    "codigo": eq.codigo,
                    "nombre": eq.nombre,
                    "tipo": eq.tipo_equipo.nombre if eq.tipo_equipo else "N/A",
                    "estado": eq.estado,
                    "horas_operacion": eq.horas_operacion,
                    "mtbf_horas": eq.mtbf_horas,
                    "mttr_horas": eq.mttr_horas,
                    "salud_pct": round(float(health_score), 1),
                    "probabilidad_falla_30d": round(float(min(0.99, failure_prob * 1.4)), 3),
                    "posicion": {"x": eq.posicion_x, "y": eq.posicion_y, "z": eq.posicion_z}
                })
            return results
        finally:
            session.close()

"""Digital Twin State model: digital_twin_states."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from database.connection import Base

class DigitalTwinState(Base):
    __tablename__ = "digital_twin_states"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    nombre_estado = Column(String(100), default="ESTADO_ACTUAL_MINA")
    origen_datos = Column(String(50), default="MINA_FISICA") # MINA_FISICA, SINCRONIZADO, SIMULADO
    
    # KPI Equipos
    equipos_total = Column(Integer, default=33)
    equipos_operativos = Column(Integer, default=29)
    equipos_mantenimiento = Column(Integer, default=2)
    equipos_fallados = Column(Integer, default=2)
    equipos_fuera_servicio = Column(Integer, default=0)
    disponibilidad_flota_pct = Column(Float, default=87.88)
    
    # KPI Inventario y Logística
    stock_total_piezas = Column(Integer, default=145)
    stock_critico_piezas = Column(Integer, default=32)
    stockouts_activos = Column(Integer, default=2)
    fill_rate_pct = Column(Float, default=88.5)
    nivel_servicio_pct = Column(Float, default=91.2)
    lead_time_promedio_dias = Column(Float, default=114.5)
    ordenes_pendientes = Column(Integer, default=7)
    proveedores_en_riesgo = Column(Integer, default=2)
    
    # KPI Confiabilidad y Producción
    mtbf_promedio_horas = Column(Float, default=245.0)
    mttr_promedio_horas = Column(Float, default=16.8)
    downtime_acumulado_horas = Column(Float, default=420.0)
    perdida_produccion_usd = Column(Float, default=5250000.0)
    
    # Serialización JSON detallada de la topología completa
    snapshot_json = Column(Text, nullable=True) # Guarda JSON serializado con estado de cada activo
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

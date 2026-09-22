"""Simulation models: escenarios, estrategias_resiliencia, parametros_simulacion, simulaciones, corridas, resultados."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database.connection import Base

class Escenario(Base):
    __tablename__ = "escenarios"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False) # ESC-01, ESC-02, ESC-03, ESC-04, ESC-CUSTOM
    nombre = Column(String(150), nullable=False)
    tipo = Column(String(50), nullable=False) # CIERRE_FRONTERA, FALLA_PROVEEDOR_UNICO, DEMANDA_EXTREMA, IMPRESION_3D_LOCAL, CUSTOM
    descripcion = Column(Text, nullable=True)
    duracion_dias = Column(Integer, default=90)
    factor_lead_time = Column(Float, default=1.0) # Ej. 3.0 para +200%
    factor_tasa_falla = Column(Float, default=1.0) # Ej. 2.0 para demanda extrema
    disponibilidad_proveedor_critico_pct = Column(Float, default=100.0) # Ej. 0.0 para falla de proveedor único
    capacidad_impresion_3d_activa = Column(Integer, default=0)
    parametros_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulaciones = relationship("Simulacion", back_populates="escenario")

class EstrategiaResiliencia(Base):
    __tablename__ = "estrategias_resiliencia"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False) # ESTRATEGIA_A, ESTRATEGIA_B, ESTRATEGIA_C, ESTRATEGIA_D, ESTRATEGIA_E, HIBRIDA
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    incremento_stock_seguridad_pct = Column(Float, default=0.0) # 0%, 50%, 100%
    dual_sourcing_activo = Column(Integer, default=0) # 1 si aplica dual sourcing
    cuota_dual_sourcing_primario_pct = Column(Float, default=100.0)
    reparacion_local_activa = Column(Integer, default=0)
    manufactura_3d_activa = Column(Integer, default=0)
    parametros_adicionales_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulaciones = relationship("Simulacion", back_populates="estrategia")

class ParametroSimulacion(Base):
    __tablename__ = "parametros_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), nullable=False, index=True)
    parametro = Column(String(100), nullable=False)
    valor = Column(String(255), nullable=False)
    tipo_dato = Column(String(50), default="float") # int, float, str, bool

    simulacion = relationship("Simulacion", back_populates="parametros")

class Simulacion(Base):
    __tablename__ = "simulaciones"

    id = Column(Integer, primary_key=True, index=True)
    codigo_experimento = Column(String(100), unique=True, nullable=False, index=True)
    escenario_id = Column(Integer, ForeignKey("escenarios.id"), nullable=False)
    estrategia_id = Column(Integer, ForeignKey("estrategias_resiliencia.id"), nullable=False)
    tipo_motor = Column(String(50), default="HIBRIDO_SD_ABM") # SYSTEM_DYNAMICS, ABM_SIMPY, HIBRIDO_SD_ABM
    corridas_totales = Column(Integer, default=500)
    horizonte_dias = Column(Integer, default=365)
    random_seed = Column(Integer, default=42)
    estado = Column(String(30), default="PENDIENTE") # PENDIENTE, EJECUTANDO, COMPLETADO, ERROR
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    tiempo_ejecucion_segundos = Column(Float, default=0.0)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    escenario = relationship("Escenario", back_populates="simulaciones")
    estrategia = relationship("EstrategiaResiliencia", back_populates="simulaciones")
    parametros = relationship("ParametroSimulacion", back_populates="simulacion", cascade="all, delete-orphan")
    corridas = relationship("CorridaSimulacion", back_populates="simulacion", cascade="all, delete-orphan")
    resultado = relationship("ResultadoSimulacion", back_populates="simulacion", uselist=False, cascade="all, delete-orphan")

class CorridaSimulacion(Base):
    __tablename__ = "corridas_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), nullable=False, index=True)
    numero_corrida = Column(Integer, nullable=False)
    seed_especifico = Column(Integer, nullable=False)
    downtime_total_horas = Column(Float, nullable=False)
    stockouts_total = Column(Integer, nullable=False)
    fill_rate_pct = Column(Float, nullable=False)
    inventario_promedio_piezas = Column(Float, default=0.0)
    costo_total_inventario_usd = Column(Float, default=0.0)
    costo_total_parada_usd = Column(Float, default=0.0)
    toneladas_produccion_perdidas = Column(Float, default=0.0)
    tiempo_promedio_espera_repuesto_dias = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulacion = relationship("Simulacion", back_populates="corridas")

class ResultadoSimulacion(Base):
    __tablename__ = "resultados_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), unique=True, nullable=False)
    downtime_medio_horas = Column(Float, nullable=False)
    downtime_std_horas = Column(Float, nullable=False)
    downtime_p5_horas = Column(Float, default=0.0)
    downtime_p95_horas = Column(Float, default=0.0)
    downtime_ic95_inferior = Column(Float, default=0.0)
    downtime_ic95_superior = Column(Float, default=0.0)
    stockouts_medio = Column(Float, default=0.0)
    fill_rate_medio_pct = Column(Float, default=0.0)
    costo_medio_usd = Column(Float, default=0.0)
    produccion_perdida_media_t = Column(Float, default=0.0)
    reduccion_downtime_vs_baseline_pct = Column(Float, default=0.0)
    reduccion_ic95_inf = Column(Float, default=0.0)
    reduccion_ic95_sup = Column(Float, default=0.0)
    metricas_completas_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulacion = relationship("Simulacion", back_populates="resultado")

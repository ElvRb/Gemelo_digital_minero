"""Statistical testing, predictions, and recommendations models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base

class PruebaEstadistica(Base):
    __tablename__ = "pruebas_estadisticas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_prueba = Column(String(100), unique=True, nullable=False) # FRIEDMAN, WILCOXON_HOLM, BOOTSTRAP_10K, KS_TEST, MANN_WHITNEY_U, SOBOL
    categoria = Column(String(50), nullable=False) # COMPARACION_MODELOS, VALIDACION_DT, RESILIENCIA_DOWNTIME, SENSIBILIDAD
    descripcion = Column(Text, nullable=True)
    hipotesis_nula_h0 = Column(Text, nullable=True)
    hipotesis_alternativa_h1 = Column(Text, nullable=True)
    nivel_significancia_alpha = Column(Float, default=0.05)
    created_at = Column(DateTime, default=datetime.utcnow)

    resultados = relationship("ResultadoEstadistico", back_populates="prueba")

class ResultadoEstadistico(Base):
    __tablename__ = "resultados_estadisticos"

    id = Column(Integer, primary_key=True, index=True)
    prueba_id = Column(Integer, ForeignKey("pruebas_estadisticas.id"), nullable=False, index=True)
    codigo_referencia = Column(String(100), nullable=False, index=True) # ID experimento ML o Simulación
    estadistico_valor = Column(Float, nullable=False)
    p_valor = Column(Float, nullable=True)
    p_valor_ajustado = Column(Float, nullable=True) # Para Holm-Bonferroni
    es_significativo = Column(Integer, default=0) # 1 si p < alpha
    ic95_inferior = Column(Float, nullable=True)
    ic95_superior = Column(Float, nullable=True)
    conclusion_texto = Column(Text, nullable=False)
    datos_detallados_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prueba = relationship("PruebaEstadistica", back_populates="resultados")

class Prediccion(Base):
    __tablename__ = "predicciones"

    id = Column(Integer, primary_key=True, index=True)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    probabilidad_riesgo_stockout = Column(Float, nullable=False)
    categoria_riesgo = Column(String(20), nullable=False) # BAJO, MEDIO, ALTO
    downtime_esperado_horas = Column(Float, default=0.0)
    factores_principales_json = Column(Text, nullable=True)
    modelo_usado = Column(String(100), default="XGBoost")
    fecha_prediccion = Column(DateTime, default=datetime.utcnow)

    repuesto = relationship("Repuesto")
    equipo = relationship("Equipo")

class Recomendacion(Base):
    __tablename__ = "recomendaciones"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(150), nullable=False)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    estrategia_sugerida = Column(String(100), nullable=False) # Dual Sourcing, Impresion 3D, Safety Stock, Taller Local
    justificacion = Column(Text, nullable=False)
    reduccion_downtime_estimada_pct = Column(Float, default=0.0)
    ic95_inf = Column(Float, default=0.0)
    ic95_sup = Column(Float, default=0.0)
    ahorro_estimado_usd = Column(Float, default=0.0)
    estado = Column(String(30), default="PROPUESTA") # PROPUESTA, APROBADA, IMPLEMENTADA, DESCARTADA
    created_at = Column(DateTime, default=datetime.utcnow)

    repuesto = relationship("Repuesto")
    equipo = relationship("Equipo")

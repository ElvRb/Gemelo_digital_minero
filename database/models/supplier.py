"""Supplier and supplier dependency models: proveedores, proveedor_repuesto, historial_lead_times."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, nullable=False, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    pais_origen = Column(String(100), default="Alemania") # Alemania, Suecia, EE.UU., Chile, Peru, China
    es_local = Column(Integer, default=0) # 1 si es taller/proveedor nacional, 0 si internacional
    confiabilidad_score = Column(Float, default=0.92) # 0.00 a 1.00 (probabilidad de cumplimiento)
    capacidad_mensual_unidades = Column(Integer, default=20)
    lead_time_base_dias = Column(Float, default=90.0)
    variabilidad_lead_time_dias = Column(Float, default=15.0)
    nivel_riesgo = Column(String(20), default="MEDIO") # BAJO, MEDIO, ALTO, CRITICO
    estado = Column(String(30), default="DISPONIBLE") # DISPONIBLE, RIESGO, INTERRUMPIDO, FALLIDO
    contacto_email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    repuestos_suministrados = relationship("ProveedorRepuesto", back_populates="proveedor", cascade="all, delete-orphan")
    ordenes = relationship("OrdenCompra", back_populates="proveedor")

class ProveedorRepuesto(Base):
    __tablename__ = "proveedor_repuesto"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=False, index=True)
    costo_unitario_usd = Column(Float, nullable=False)
    lead_time_dias = Column(Float, default=90.0)
    cuota_suministro_pct = Column(Float, default=100.0) # Participación histórica del proveedor (ej. 85%, 15%)
    es_proveedor_primario = Column(Integer, default=1)
    tiempo_garantia_meses = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow)

    proveedor = relationship("Proveedor", back_populates="repuestos_suministrados")
    repuesto = relationship("Repuesto", back_populates="proveedores_asociados")
    historial_lead_times = relationship("HistorialLeadTime", back_populates="proveedor_repuesto", cascade="all, delete-orphan")

class HistorialLeadTime(Base):
    __tablename__ = "historial_lead_times"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_repuesto_id = Column(Integer, ForeignKey("proveedor_repuesto.id"), nullable=False, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"), nullable=True)
    lead_time_prometido_dias = Column(Float, nullable=False)
    lead_time_real_dias = Column(Float, nullable=False)
    retraso_dias = Column(Float, default=0.0)
    cumplio_tiempo = Column(Integer, default=1) # 1 si cumplió, 0 si se retrasó
    disrupcion_registrada = Column(String(100), nullable=True) # Ninguna, Aduana, Cierre Frontera, Falla Fabril
    fecha_pedido = Column(DateTime, nullable=False)
    fecha_entrega = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    proveedor_repuesto = relationship("ProveedorRepuesto", back_populates="historial_lead_times")
    orden = relationship("OrdenCompra")

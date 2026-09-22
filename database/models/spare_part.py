"""Spare part and BOM models: categorias_repuesto, repuestos, bom_equipos."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class CategoriaRepuesto(Base):
    __tablename__ = "categorias_repuesto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False) # Hidraulica, Electrica, Transmision, etc.
    descripcion = Column(Text, nullable=True)
    es_critica = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    repuestos = relationship("Repuesto", back_populates="categoria")

class Repuesto(Base):
    __tablename__ = "repuestos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True) # Ej. PUMP-HYD-001, SEAL-AX-102
    nombre = Column(String(150), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_repuesto.id"), nullable=False)
    criticidad = Column(String(20), default="CRITICA") # CRITICA, ALTA, MEDIA
    unidad_medida = Column(String(20), default="UNIDAD")
    costo_unitario_usd = Column(Float, nullable=False, default=1500.0)
    lead_time_promedio_dias = Column(Float, nullable=False, default=90.0) # 90 a 180 días (3-6 meses)
    tasa_falla_lambda = Column(Float, default=0.035) # Tasa de falla mensual o por 1000 horas
    mtbf_horas = Column(Float, default=1200.0)
    stock_actual = Column(Integer, default=2)
    stock_minimo = Column(Integer, default=1)
    stock_maximo = Column(Integer, default=8)
    stock_seguridad = Column(Integer, default=2)
    punto_reorden = Column(Integer, default=3)
    consumo_mensual_promedio = Column(Float, default=0.8)
    permite_impresion_3d = Column(Integer, default=0) # 1 si es imprimible localmente, 0 si no
    permite_reparacion_local = Column(Integer, default=0) # 1 si se puede rectificar en taller mina
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categoria = relationship("CategoriaRepuesto", back_populates="repuestos")
    bom_asociaciones = relationship("BOMEquipo", back_populates="repuesto", cascade="all, delete-orphan")
    inventarios = relationship("Inventario", back_populates="repuesto", cascade="all, delete-orphan")
    proveedores_asociados = relationship("ProveedorRepuesto", back_populates="repuesto", cascade="all, delete-orphan")
    detalles_orden = relationship("OrdenCompraDetalle", back_populates="repuesto")

class BOMEquipo(Base):
    __tablename__ = "bom_equipos"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False, index=True)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=False, index=True)
    subsistema = Column(String(100), nullable=False) # Motor, Sistema Hidraulico, Tren de Potencia, etc.
    cantidad = Column(Integer, default=1)
    criticidad_subsistema = Column(String(20), default="ALTA") # VITAL, ESCENCIAL, AUXILIAR
    observaciones = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipo = relationship("Equipo", back_populates="bom_items")
    repuesto = relationship("Repuesto", back_populates="bom_asociaciones")

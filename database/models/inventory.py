"""Inventory models: inventarios, movimientos_inventario."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class Inventario(Base):
    __tablename__ = "inventarios"

    id = Column(Integer, primary_key=True, index=True)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=False, index=True)
    almacen = Column(String(100), default="ALMACEN_CENTRAL_SUPERFICIE") # ALMACEN_CENTRAL, TALLER_SUBTERRANEO_-240M
    cantidad_disponible = Column(Integer, default=0, nullable=False)
    cantidad_reservada = Column(Integer, default=0)
    cantidad_en_transito = Column(Integer, default=0)
    ubicacion_estante = Column(String(50), nullable=True) # Ej. RACK-B3-N2
    valor_total_inventario_usd = Column(Float, default=0.0)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    repuesto = relationship("Repuesto", back_populates="inventarios")
    movimientos = relationship("MovimientoInventario", back_populates="inventario", cascade="all, delete-orphan")

class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    inventario_id = Column(Integer, ForeignKey("inventarios.id"), nullable=False, index=True)
    tipo = Column(String(50), nullable=False) # ENTRADA, SALIDA_CONSUMO, TRANSFERENCIA, AJUSTE, RECEPCION_COMPRA
    cantidad = Column(Integer, nullable=False)
    stock_anterior = Column(Integer, nullable=False)
    stock_posterior = Column(Integer, nullable=False)
    equipo_destino_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    costo_unitario_usd = Column(Float, default=0.0)
    costo_total_usd = Column(Float, default=0.0)
    motivo = Column(String(255), nullable=True)
    usuario_registro = Column(String(50), default="SISTEMA")
    fecha = Column(DateTime, default=datetime.utcnow, index=True)

    inventario = relationship("Inventario", back_populates="movimientos")
    equipo_destino = relationship("Equipo")

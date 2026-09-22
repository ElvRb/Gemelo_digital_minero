"""Logistics and order models: transportistas, rutas, envios, ordenes_compra, recepciones, reparaciones."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class Transportista(Base):
    __tablename__ = "transportistas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    modalidad = Column(String(50), default="MULTIMODAL") # AEREO, MARITIMO, TERRESTRE_ANDINO, MULTIMODAL
    confiabilidad = Column(Float, default=0.90) # Probabilidad de cumplimiento en ruta
    probabilidad_retraso = Column(Float, default=0.15)
    retraso_promedio_dias = Column(Float, default=7.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    envios = relationship("Envio", back_populates="transportista")

class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False) # Ej. Puerto Hamburgo -> Puerto Callao -> Mina Subterránea
    origen = Column(String(100), nullable=False)
    destino = Column(String(100), default="Almacén Mina")
    distancia_km = Column(Float, default=12500.0)
    tiempo_transporte_dias = Column(Float, default=35.0)
    tiempo_aduana_dias = Column(Float, default=10.0)
    riesgo_bloqueo = Column(Float, default=0.10) # Probabilidad de cierre de paso o carretera
    created_at = Column(DateTime, default=datetime.utcnow)

    envios = relationship("Envio", back_populates="ruta")

class Envio(Base):
    __tablename__ = "envios"

    id = Column(Integer, primary_key=True, index=True)
    codigo_tracking = Column(String(100), unique=True, nullable=False, index=True)
    transportista_id = Column(Integer, ForeignKey("transportistas.id"), nullable=False)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"), nullable=False)
    estado = Column(String(50), default="EN_TRANSITO") # EN_ORIGEN, EN_TRANSITO, EN_ADUANA, RETRASADO, ENTREGADO
    fecha_despacho = Column(DateTime, nullable=False)
    fecha_entrega_estimada = Column(DateTime, nullable=False)
    fecha_entrega_real = Column(DateTime, nullable=True)
    retraso_acumulado_dias = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    transportista = relationship("Transportista", back_populates="envios")
    ruta = relationship("Ruta", back_populates="envios")
    orden = relationship("OrdenCompra", back_populates="envios")

class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"

    id = Column(Integer, primary_key=True, index=True)
    numero_orden = Column(String(50), unique=True, nullable=False, index=True) # Ej. OC-2026-0089
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)
    estado = Column(String(50), default="PENDIENTE") # PENDIENTE, EN_PROCESO, DESPACHADA, PARCIAL, COMPLETADA, CANCELADA
    monto_total_usd = Column(Float, default=0.0)
    fecha_emision = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_esperada_entrega = Column(DateTime, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
    lead_time_total_dias = Column(Float, default=90.0)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    proveedor = relationship("Proveedor", back_populates="ordenes")
    detalles = relationship("OrdenCompraDetalle", back_populates="orden", cascade="all, delete-orphan")
    envios = relationship("Envio", back_populates="orden", cascade="all, delete-orphan")

class OrdenCompraDetalle(Base):
    __tablename__ = "ordenes_compra_detalle"

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"), nullable=False, index=True)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=False, index=True)
    cantidad_solicitada = Column(Integer, nullable=False)
    cantidad_recibida = Column(Integer, default=0)
    precio_unitario_usd = Column(Float, nullable=False)
    subtotal_usd = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orden = relationship("OrdenCompra", back_populates="detalles")
    repuesto = relationship("Repuesto", back_populates="detalles_orden")
    recepciones = relationship("Recepcion", back_populates="detalle_orden", cascade="all, delete-orphan")

class Recepcion(Base):
    __tablename__ = "recepciones"

    id = Column(Integer, primary_key=True, index=True)
    detalle_orden_id = Column(Integer, ForeignKey("ordenes_compra_detalle.id"), nullable=False, index=True)
    cantidad_recibida = Column(Integer, nullable=False)
    conforme = Column(Integer, default=1) # 1 conforme, 0 defectuoso
    fecha_recepcion = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario_recepcion = Column(String(50), default="ALMACEN_USER")
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    detalle_orden = relationship("OrdenCompraDetalle", back_populates="recepciones")

class Reparacion(Base):
    __tablename__ = "reparaciones"

    id = Column(Integer, primary_key=True, index=True)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=False)
    equipo_origen_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    tipo_reparacion = Column(String(50), default="TALLER_LOCAL") # TALLER_LOCAL, MANUFACTURA_3D, REACONDICIONAMIENTO
    duracion_dias = Column(Float, default=5.0)
    costo_reparacion_usd = Column(Float, default=600.0)
    resultado = Column(String(50), default="EXITOSO") # EXITOSO, PARCIAL, NO_REPARABLE
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_termino = Column(DateTime, nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    repuesto = relationship("Repuesto")
    equipo_origen = relationship("Equipo")

"""Equipment models: tipos_equipo, equipos, fallas_equipo, mantenimientos."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from database.connection import Base

class EstadoEquipoEnum(str, enum.Enum):
    OPERATIVO = "OPERATIVO"
    MANTENIMIENTO = "MANTENIMIENTO"
    FALLADO = "FALLADO"
    FUERA_DE_SERVICIO = "FUERA_DE_SERVICIO"

class TipoEquipo(Base):
    __tablename__ = "tipos_equipo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False) # Scooptram, Jumbo, Ventilador, Bomba, etc.
    categoria = Column(String(50), default="CARGUIO_TRANSPORTE") # CARGUIO_TRANSPORTE, PERFORACION, SERVICIOS_MINA
    descripcion = Column(Text, nullable=True)
    costo_parada_hora_usd = Column(Float, default=5000.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipos = relationship("Equipo", back_populates="tipo_equipo")

class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True) # Ej. ST-01, JUM-02, FAN-01
    nombre = Column(String(100), nullable=False)
    tipo_equipo_id = Column(Integer, ForeignKey("tipos_equipo.id"), nullable=False)
    mina_id = Column(Integer, ForeignKey("minas.id"), nullable=False)
    zona_id = Column(Integer, ForeignKey("zonas_mina.id"), nullable=True)
    modelo = Column(String(100), nullable=False)
    fabricante = Column(String(100), nullable=False)
    estado = Column(String(30), default=EstadoEquipoEnum.OPERATIVO.value, index=True)
    criticidad = Column(String(20), default="ALTA") # ALTA, MEDIA, CRITICA
    mtbf_horas = Column(Float, default=240.0) # Mean Time Between Failures
    mttr_horas = Column(Float, default=18.0)  # Mean Time To Repair
    horas_operacion = Column(Float, default=1500.0)
    ultima_falla = Column(DateTime, nullable=True)
    proximo_mantenimiento = Column(DateTime, nullable=True)
    posicion_x = Column(Float, default=0.0)
    posicion_y = Column(Float, default=0.0)
    posicion_z = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tipo_equipo = relationship("TipoEquipo", back_populates="equipos")
    mina = relationship("Mina", back_populates="equipos")
    zona = relationship("ZonaMina", back_populates="equipos")
    bom_items = relationship("BOMEquipo", back_populates="equipo", cascade="all, delete-orphan")
    fallas = relationship("FallaEquipo", back_populates="equipo", cascade="all, delete-orphan")
    mantenimientos = relationship("Mantenimiento", back_populates="equipo", cascade="all, delete-orphan")

class FallaEquipo(Base):
    __tablename__ = "fallas_equipo"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False, index=True)
    repuesto_requerido_id = Column(Integer, ForeignKey("repuestos.id"), nullable=True)
    fecha_inicio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_resolucion = Column(DateTime, nullable=True)
    downtime_horas = Column(Float, default=0.0)
    causa = Column(String(255), nullable=False)
    severidad = Column(String(50), default="ALTA") # BAJA, MEDIA, ALTA, CATASTROFICA
    stockout_ocurrido = Column(Integer, default=0) # 1 si la falta de repuesto causó retraso, 0 si no
    tiempo_espera_repuesto_horas = Column(Float, default=0.0)
    costo_total_perdida_usd = Column(Float, default=0.0)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipo = relationship("Equipo", back_populates="fallas")
    repuesto_requerido = relationship("Repuesto")

class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    tipo = Column(String(50), default="PREVENTIVO") # PREVENTIVO, CORRECTIVO, PREDICTIVO
    estado = Column(String(50), default="PROGRAMADO") # PROGRAMADO, EN_PROCESO, COMPLETADO
    fecha_programada = Column(DateTime, nullable=False)
    fecha_ejecucion = Column(DateTime, nullable=True)
    duracion_horas = Column(Float, default=8.0)
    tecnico_responsable = Column(String(100), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipo = relationship("Equipo", back_populates="mantenimientos")

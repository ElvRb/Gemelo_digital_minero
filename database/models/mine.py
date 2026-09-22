"""Mine topology models: minas, niveles_mina, zonas_mina."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class Mina(Base):
    __tablename__ = "minas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    metodo_explotacion = Column(String(100), default="Sublevel Stoping / Cut and Fill")
    ubicacion = Column(String(255), nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    produccion_diaria_tpd = Column(Float, default=5000.0)  # Toneladas métricas por día
    costo_downtime_hora_usd = Column(Float, default=12500.0) # Costo global por hora de parada
    created_at = Column(DateTime, default=datetime.utcnow)

    niveles = relationship("NivelMina", back_populates="mina", cascade="all, delete-orphan")
    equipos = relationship("Equipo", back_populates="mina")

class NivelMina(Base):
    __tablename__ = "niveles_mina"

    id = Column(Integer, primary_key=True, index=True)
    mina_id = Column(Integer, ForeignKey("minas.id"), nullable=False)
    nombre = Column(String(50), nullable=False)   # Ej. Nivel -120m, Nivel -240m
    cota_z = Column(Float, nullable=False)        # Profundidad z (negativa)
    descripcion = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mina = relationship("Mina", back_populates="niveles")
    zonas = relationship("ZonaMina", back_populates="nivel", cascade="all, delete-orphan")

class ZonaMina(Base):
    __tablename__ = "zonas_mina"

    id = Column(Integer, primary_key=True, index=True)
    nivel_id = Column(Integer, ForeignKey("niveles_mina.id"), nullable=False)
    nombre = Column(String(100), nullable=False)  # Ej. Galería Norte, Taller Subterráneo, Frente 3B
    tipo = Column(String(50), default="PRODUCCION") # PRODUCCION, TALLER, VENTILACION, DRENAJE, ALMACEN
    coordenada_x = Column(Float, default=0.0)
    coordenada_y = Column(Float, default=0.0)
    coordenada_z = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    nivel = relationship("NivelMina", back_populates="zonas")
    equipos = relationship("Equipo", back_populates="zona")

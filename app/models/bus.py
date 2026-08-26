from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TipoAsiento(str, enum.Enum):
    economico = "economico"
    vip = "vip"
    cama = "cama"


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    placa = Column(String(20), nullable=False)
    descripcion = Column(String(150), nullable=True)  # ej: "Bus 2 pisos - 40 asientos"
    capacidad_asientos = Column(Integer, nullable=False)

    empresa = relationship("Empresa", back_populates="buses")
    asientos = relationship("AsientoPlantilla", back_populates="bus", cascade="all, delete-orphan")
    viajes = relationship("Viaje", back_populates="bus")


class AsientoPlantilla(Base):
    """
    Define la distribución física de asientos de un bus (plantilla fija).
    La disponibilidad real por viaje se maneja en AsientoViaje.
    """
    __tablename__ = "asientos_plantilla"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    numero = Column(String(10), nullable=False)  # ej: "12", "1A"
    piso = Column(Integer, default=1, nullable=False)  # 1 o 2 (bus de 2 pisos)
    fila = Column(Integer, nullable=False)
    columna = Column(Integer, nullable=False)
    tipo = Column(Enum(TipoAsiento), default=TipoAsiento.economico, nullable=False)

    bus = relationship("Bus", back_populates="asientos")

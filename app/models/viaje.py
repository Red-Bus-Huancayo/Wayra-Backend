from sqlalchemy import Column, Integer, Date, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EstadoAsiento(str, enum.Enum):
    disponible = "disponible"
    reservado = "reservado"  # bloqueado temporalmente mientras el usuario decide
    ocupado = "ocupado"      # confirmado


class Viaje(Base):
    """
    Instancia concreta de un Horario en una fecha determinada.
    Se genera con anticipación (ej: script diario) para que haya disponibilidad futura.
    """
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    horario_id = Column(Integer, ForeignKey("horarios.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    fecha = Column(Date, nullable=False, index=True)

    __table_args__ = (UniqueConstraint("horario_id", "fecha", name="uq_horario_fecha"),)

    horario = relationship("Horario", back_populates="viajes")
    bus = relationship("Bus", back_populates="viajes")
    asientos = relationship("AsientoViaje", back_populates="viaje", cascade="all, delete-orphan")


class AsientoViaje(Base):
    """
    Estado real de cada asiento para un viaje específico.
    Se genera copiando la plantilla de asientos del bus al crear el Viaje.
    """
    __tablename__ = "asientos_viaje"

    id = Column(Integer, primary_key=True, index=True)
    viaje_id = Column(Integer, ForeignKey("viajes.id"), nullable=False)
    asiento_plantilla_id = Column(Integer, ForeignKey("asientos_plantilla.id"), nullable=False)
    estado = Column(Enum(EstadoAsiento), default=EstadoAsiento.disponible, nullable=False)
    precio = Column(Numeric(10, 2), nullable=True)  # permite sobreescribir precio_base si aplica

    __table_args__ = (UniqueConstraint("viaje_id", "asiento_plantilla_id", name="uq_viaje_asiento"),)

    viaje = relationship("Viaje", back_populates="asientos")
    asiento_plantilla = relationship("AsientoPlantilla")

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class EstadoReserva(str, enum.Enum):
    pendiente = "pendiente"       # creada, esperando redirección a WhatsApp
    enviada = "enviada"           # el usuario fue redirigido a WhatsApp
    expirada = "expirada"         # pasó el tiempo límite sin confirmarse
    cancelada = "cancelada"
    confirmada = "confirmada"     # marcado manualmente (a futuro, por un admin)


# Tabla intermedia: una reserva puede incluir varios asientos
reserva_asiento = Table(
    "reserva_asiento",
    Base.metadata,
    Column("reserva_id", ForeignKey("reservas.id"), primary_key=True),
    Column("asiento_viaje_id", ForeignKey("asientos_viaje.id"), primary_key=True),
)


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    viaje_id = Column(Integer, ForeignKey("viajes.id"), nullable=False)

    # Datos del pasajero (sin necesidad de cuenta de usuario)
    nombre_pasajero = Column(String(150), nullable=False)
    telefono_pasajero = Column(String(20), nullable=False)

    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(Enum(EstadoReserva), default=EstadoReserva.pendiente, nullable=False)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    viaje = relationship("Viaje")
    asientos = relationship("AsientoViaje", secondary=reserva_asiento)

import enum
import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class EstadoSeguimiento(str, enum.Enum):
    activo = "activo"
    finalizado = "finalizado"  # el pasajero llegó a destino
    cancelado = "cancelado"


class TipoEvento(str, enum.Enum):
    paso_intermedio = "paso_intermedio"
    llegada = "llegada"


def generar_token() -> str:
    return uuid.uuid4().hex


class Seguimiento(Base):
    """
    Sesión "Ángel Guardián" ligada 1:1 a una Reserva confirmada.
    - `token`: identificador público (va en el link que el pasajero comparte
      con su familiar; no requiere que el familiar se registre).
    """
    __tablename__ = "seguimientos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False, unique=True)
    token = Column(String(32), unique=True, index=True, nullable=False, default=generar_token)
    estado = Column(Enum(EstadoSeguimiento), default=EstadoSeguimiento.activo, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    reserva = relationship("Reserva")
    eventos = relationship(
        "EventoSeguimiento",
        back_populates="seguimiento",
        cascade="all, delete-orphan",
        order_by="EventoSeguimiento.reportado_en",
    )


class EventoSeguimiento(Base):
    """
    Registro de que el dispositivo del pasajero detectó (vía GPS local, sin
    necesidad de datos móviles) que pasó cerca de un punto de referencia o
    que llegó a destino. `reportado_en` es el momento real del evento en el
    dispositivo; `sincronizado_en` es cuando el backend lo recibió (puede ser
    más tarde si el celular no tenía señal en el momento).
    """
    __tablename__ = "eventos_seguimiento"

    id = Column(Integer, primary_key=True, index=True)
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id"), nullable=False)
    punto_referencia_id = Column(Integer, ForeignKey("puntos_referencia.id"), nullable=True)
    tipo = Column(Enum(TipoEvento), nullable=False)
    latitud_reportada = Column(Float, nullable=True)
    longitud_reportada = Column(Float, nullable=True)
    reportado_en = Column(DateTime(timezone=True), nullable=False)
    sincronizado_en = Column(DateTime(timezone=True), server_default=func.now())

    seguimiento = relationship("Seguimiento", back_populates="eventos")
    punto_referencia = relationship("PuntoReferencia")

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Time
from sqlalchemy.orm import relationship

from app.core.database import Base


class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    origen = Column(String(100), nullable=False, index=True)
    destino = Column(String(100), nullable=False, index=True)
    duracion_estimada_min = Column(Integer, nullable=True)

    empresa = relationship("Empresa", back_populates="rutas")
    horarios = relationship("Horario", back_populates="ruta", cascade="all, delete-orphan")
    puntos_referencia = relationship(
        "PuntoReferencia",
        back_populates="ruta",
        cascade="all, delete-orphan",
        order_by="PuntoReferencia.orden",
    )


class Horario(Base):
    """
    Horario recurrente de una ruta (ej: todos los días sale a las 22:00).
    Los Viajes son instancias concretas de un Horario en una fecha específica.
    """
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    hora_salida = Column(Time, nullable=False)
    hora_llegada_estimada = Column(Time, nullable=True)
    precio_base = Column(Numeric(10, 2), nullable=False)

    ruta = relationship("Ruta", back_populates="horarios")
    bus = relationship("Bus")
    viajes = relationship("Viaje", back_populates="horario", cascade="all, delete-orphan")

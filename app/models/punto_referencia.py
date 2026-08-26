from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class PuntoReferencia(Base):
    """
    Punto de referencia (distrito/localidad) a lo largo de una Ruta.
    Se usa para armar el mini-mapa offline del "Ángel Guardián": el dispositivo
    del pasajero descarga estos puntos y usa el GPS local (sin datos móviles)
    para detectar cuándo está cerca de cada uno.
    """
    __tablename__ = "puntos_referencia"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    nombre = Column(String(150), nullable=False)  # ej: "Chupaca", "La Oroya"
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    orden = Column(Integer, nullable=False)  # posición en el trayecto (0 = origen, N = destino)
    radio_aviso_metros = Column(Integer, default=2000, nullable=False)
    es_destino_final = Column(Boolean, default=False, nullable=False)

    ruta = relationship("Ruta", back_populates="puntos_referencia")

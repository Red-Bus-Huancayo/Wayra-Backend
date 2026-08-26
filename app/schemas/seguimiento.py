from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.seguimiento import EstadoSeguimiento, TipoEvento
from app.schemas.punto_referencia import PuntoReferenciaOut


class SeguimientoOut(BaseModel):
    """Lo que recibe el pasajero al confirmar su reserva: token, link para compartir y el mini-mapa offline."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    token: str
    estado: EstadoSeguimiento
    puntos_ruta: list[PuntoReferenciaOut]


class EventoSeguimientoCreate(BaseModel):
    tipo: TipoEvento
    punto_referencia_id: int | None = None
    latitud_reportada: float | None = None
    longitud_reportada: float | None = None
    reportado_en: datetime  # momento real detectado en el dispositivo, aunque llegue tarde al backend


class EventoSeguimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoEvento
    punto_referencia_id: int | None
    reportado_en: datetime
    sincronizado_en: datetime


class EventoSeguimientoRespuesta(BaseModel):
    """Se devuelve tras registrar un evento: incluye el mensaje/link de WhatsApp
    que el dispositivo debe intentar enviar (de inmediato o guardado para reintentar
    apenas recupere señal, vía Background Sync en el service worker)."""
    evento: EventoSeguimientoOut
    whatsapp_url_pasajero: str
    mensaje: str
    seguimiento_finalizado: bool


class SeguimientoPublicoOut(BaseModel):
    """Lo que ve el familiar/contacto al abrir el link compartido — sin necesidad de registrarse."""
    model_config = ConfigDict(from_attributes=True)

    token: str
    estado: EstadoSeguimiento
    nombre_pasajero: str
    ultimo_evento: EventoSeguimientoOut | None
    ultimo_punto_nombre: str | None

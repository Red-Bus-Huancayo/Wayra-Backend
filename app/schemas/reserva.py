from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.reserva import EstadoReserva


class ReservaCreate(BaseModel):
    viaje_id: int
    asiento_viaje_ids: list[int]
    nombre_pasajero: str
    telefono_pasajero: str

    @field_validator("asiento_viaje_ids")
    @classmethod
    def al_menos_un_asiento(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("Debe seleccionar al menos un asiento")
        return v


class ReservaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    viaje_id: int
    nombre_pasajero: str
    telefono_pasajero: str
    total: float
    estado: EstadoReserva
    creado_en: datetime


class ReservaWhatsAppOut(BaseModel):
    reserva_id: int
    whatsapp_url: str
    mensaje: str
    # Datos del "Ángel Guardián" para que el frontend descargue el mini-mapa offline
    # y arme el link compartible para el familiar/contacto del pasajero.
    seguimiento_token: str
    seguimiento_link_familiar: str

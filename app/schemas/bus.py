from pydantic import BaseModel, ConfigDict

from app.models.bus import TipoAsiento
from app.models.viaje import EstadoAsiento


class AsientoPlantillaBase(BaseModel):
    numero: str
    piso: int = 1
    fila: int
    columna: int
    tipo: TipoAsiento = TipoAsiento.economico


class AsientoPlantillaCreate(AsientoPlantillaBase):
    pass


class AsientoPlantillaOut(AsientoPlantillaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class BusBase(BaseModel):
    placa: str
    descripcion: str | None = None
    capacidad_asientos: int


class BusCreate(BusBase):
    empresa_id: int
    asientos: list[AsientoPlantillaCreate] = []


class BusOut(BusBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa_id: int
    asientos: list[AsientoPlantillaOut] = []


class AsientoViajeOut(BaseModel):
    """Estado de un asiento para un viaje específico (lo que ve el usuario al elegir)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: EstadoAsiento
    precio: float | None = None
    asiento_plantilla: AsientoPlantillaOut

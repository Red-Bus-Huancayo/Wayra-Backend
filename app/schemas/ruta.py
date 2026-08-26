from datetime import time
from pydantic import BaseModel, ConfigDict

from app.schemas.empresa import EmpresaOut


class RutaBase(BaseModel):
    origen: str
    destino: str
    duracion_estimada_min: int | None = None


class RutaCreate(RutaBase):
    empresa_id: int


class RutaOut(RutaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa: EmpresaOut


class HorarioBase(BaseModel):
    hora_salida: time
    hora_llegada_estimada: time | None = None
    precio_base: float


class HorarioCreate(HorarioBase):
    ruta_id: int
    bus_id: int


class HorarioOut(HorarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ruta_id: int
    bus_id: int


class HorarioConEmpresaOut(HorarioBase):
    """Usado en resultados de búsqueda: incluye datos de la ruta/empresa para no hacer otro request."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    ruta: RutaOut

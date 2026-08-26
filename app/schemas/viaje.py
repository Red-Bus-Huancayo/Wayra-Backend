from datetime import date
from pydantic import BaseModel, ConfigDict

from app.schemas.ruta import HorarioConEmpresaOut


class ViajeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    horario: HorarioConEmpresaOut
    asientos_disponibles: int | None = None  # calculado, no viene directo del modelo

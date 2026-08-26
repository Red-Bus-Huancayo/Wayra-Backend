from pydantic import BaseModel, ConfigDict


class PuntoReferenciaBase(BaseModel):
    nombre: str
    latitud: float
    longitud: float
    orden: int
    radio_aviso_metros: int = 2000
    es_destino_final: bool = False


class PuntoReferenciaCreate(PuntoReferenciaBase):
    pass


class PuntoReferenciaOut(PuntoReferenciaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ruta_id: int

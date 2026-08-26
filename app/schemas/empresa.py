from pydantic import BaseModel, ConfigDict


class EmpresaBase(BaseModel):
    nombre: str
    whatsapp_numero: str
    logo_url: str | None = None


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaOut(EmpresaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool

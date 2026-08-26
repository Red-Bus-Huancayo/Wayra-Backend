from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaOut

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("", response_model=list[EmpresaOut])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(Empresa).filter(Empresa.activo.is_(True)).all()


@router.post("", response_model=EmpresaOut, status_code=201)
def crear_empresa(payload: EmpresaCreate, db: Session = Depends(get_db)):
    empresa = Empresa(**payload.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.get("/{empresa_id}", response_model=EmpresaOut)
def obtener_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

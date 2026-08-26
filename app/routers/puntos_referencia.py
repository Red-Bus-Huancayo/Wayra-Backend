from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ruta import Ruta
from app.models.punto_referencia import PuntoReferencia
from app.schemas.punto_referencia import PuntoReferenciaCreate, PuntoReferenciaOut

router = APIRouter(prefix="/rutas/{ruta_id}/puntos", tags=["Puntos de Referencia"])


@router.get("", response_model=list[PuntoReferenciaOut])
def listar_puntos(ruta_id: int, db: Session = Depends(get_db)):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return (
        db.query(PuntoReferencia)
        .filter(PuntoReferencia.ruta_id == ruta_id)
        .order_by(PuntoReferencia.orden)
        .all()
    )


@router.post("", response_model=PuntoReferenciaOut, status_code=201)
def crear_punto(ruta_id: int, payload: PuntoReferenciaCreate, db: Session = Depends(get_db)):
    """
    Registrar un punto de referencia (distrito/localidad) en la ruta.
    Recomendado: solo distritos/localidades principales, no anexos pequeños,
    para no generar avisos de más al pasajero.
    """
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    punto = PuntoReferencia(ruta_id=ruta_id, **payload.model_dump())
    db.add(punto)
    db.commit()
    db.refresh(punto)
    return punto

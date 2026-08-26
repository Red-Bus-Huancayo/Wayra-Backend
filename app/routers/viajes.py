from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.viaje import Viaje, AsientoViaje, EstadoAsiento
from app.models.ruta import Horario, Ruta
from app.schemas.viaje import ViajeOut
from app.schemas.bus import AsientoViajeOut

router = APIRouter(prefix="/viajes", tags=["Viajes"])


@router.get("", response_model=list[ViajeOut])
def buscar_viajes(
    origen: str = Query(...),
    destino: str = Query(...),
    fecha: date_type = Query(...),
    db: Session = Depends(get_db),
):
    """
    Búsqueda principal: origen + destino + fecha -> lista de viajes disponibles
    con conteo de asientos libres por viaje.
    """
    viajes = (
        db.query(Viaje)
        .join(Horario, Viaje.horario_id == Horario.id)
        .join(Ruta, Horario.ruta_id == Ruta.id)
        .options(joinedload(Viaje.horario).joinedload(Horario.ruta).joinedload(Ruta.empresa))
        .filter(
            Ruta.origen.ilike(f"%{origen}%"),
            Ruta.destino.ilike(f"%{destino}%"),
            Viaje.fecha == fecha,
        )
        .all()
    )

    resultado = []
    for viaje in viajes:
        disponibles = (
            db.query(AsientoViaje)
            .filter(
                AsientoViaje.viaje_id == viaje.id,
                AsientoViaje.estado == EstadoAsiento.disponible,
            )
            .count()
        )
        viaje_out = ViajeOut.model_validate(viaje)
        viaje_out.asientos_disponibles = disponibles
        resultado.append(viaje_out)

    return resultado


@router.get("/{viaje_id}", response_model=ViajeOut)
def obtener_viaje(viaje_id: int, db: Session = Depends(get_db)):
    viaje = (
        db.query(Viaje)
        .options(joinedload(Viaje.horario).joinedload(Horario.ruta).joinedload(Ruta.empresa))
        .filter(Viaje.id == viaje_id)
        .first()
    )
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    disponibles = (
        db.query(AsientoViaje)
        .filter(
            AsientoViaje.viaje_id == viaje.id,
            AsientoViaje.estado == EstadoAsiento.disponible,
        )
        .count()
    )
    viaje_out = ViajeOut.model_validate(viaje)
    viaje_out.asientos_disponibles = disponibles
    return viaje_out


@router.get("/{viaje_id}/asientos", response_model=list[AsientoViajeOut])
def mapa_asientos(viaje_id: int, db: Session = Depends(get_db)):
    """Devuelve el mapa completo de asientos (disponibles y ocupados) para armar el gráfico del bus."""
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    return (
        db.query(AsientoViaje)
        .options(joinedload(AsientoViaje.asiento_plantilla))
        .filter(AsientoViaje.viaje_id == viaje_id)
        .all()
    )

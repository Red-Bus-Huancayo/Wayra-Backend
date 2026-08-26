from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ruta import Ruta, Horario
from app.models.viaje import Viaje, AsientoViaje
from app.models.bus import AsientoPlantilla
from app.schemas.ruta import RutaCreate, RutaOut, HorarioCreate, HorarioOut
from app.schemas.viaje import ViajeOut

router = APIRouter(prefix="/rutas", tags=["Rutas"])


@router.get("", response_model=list[RutaOut])
def buscar_rutas(
    origen: str | None = Query(default=None),
    destino: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Ruta)
    if origen:
        query = query.filter(Ruta.origen.ilike(f"%{origen}%"))
    if destino:
        query = query.filter(Ruta.destino.ilike(f"%{destino}%"))
    return query.all()


@router.post("", response_model=RutaOut, status_code=201)
def crear_ruta(payload: RutaCreate, db: Session = Depends(get_db)):
    ruta = Ruta(**payload.model_dump())
    db.add(ruta)
    db.commit()
    db.refresh(ruta)
    return ruta


@router.get("/{ruta_id}", response_model=RutaOut)
def obtener_ruta(ruta_id: int, db: Session = Depends(get_db)):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta


@router.post("/horarios", response_model=HorarioOut, status_code=201)
def crear_horario(payload: HorarioCreate, db: Session = Depends(get_db)):
    horario = Horario(**payload.model_dump())
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario


@router.post("/horarios/{horario_id}/generar-viaje", response_model=ViajeOut, status_code=201)
def generar_viaje(horario_id: int, fecha: date_type, db: Session = Depends(get_db)):
    """
    Crea un Viaje concreto para una fecha, copiando la plantilla de asientos
    del bus asignado al horario. Se llama por adelantado (ej: script diario/cron)
    para abrir disponibilidad de fechas futuras.
    """
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    existente = (
        db.query(Viaje)
        .filter(Viaje.horario_id == horario_id, Viaje.fecha == fecha)
        .first()
    )
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un viaje para esa fecha")

    viaje = Viaje(horario_id=horario.id, bus_id=horario.bus_id, fecha=fecha)
    db.add(viaje)
    db.flush()

    plantillas = (
        db.query(AsientoPlantilla)
        .filter(AsientoPlantilla.bus_id == horario.bus_id)
        .all()
    )
    for plantilla in plantillas:
        db.add(AsientoViaje(
            viaje_id=viaje.id,
            asiento_plantilla_id=plantilla.id,
            precio=horario.precio_base,
        ))

    db.commit()
    db.refresh(viaje)

    viaje_out = ViajeOut.model_validate(viaje)
    viaje_out.asientos_disponibles = len(plantillas)
    return viaje_out

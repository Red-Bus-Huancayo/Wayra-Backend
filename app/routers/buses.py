from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.bus import Bus, AsientoPlantilla
from app.schemas.bus import BusCreate, BusOut

router = APIRouter(prefix="/buses", tags=["Buses"])


@router.post("", response_model=BusOut, status_code=201)
def crear_bus(payload: BusCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"asientos"})
    bus = Bus(**data)
    db.add(bus)
    db.flush()  # para tener bus.id antes de crear asientos

    for asiento_data in payload.asientos:
        asiento = AsientoPlantilla(bus_id=bus.id, **asiento_data.model_dump())
        db.add(asiento)

    db.commit()
    db.refresh(bus)
    return bus


@router.get("/{bus_id}", response_model=BusOut)
def obtener_bus(bus_id: int, db: Session = Depends(get_db)):
    bus = (
        db.query(Bus)
        .options(joinedload(Bus.asientos))
        .filter(Bus.id == bus_id)
        .first()
    )
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return bus
